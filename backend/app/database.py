"""数据库连接和初始化管理

SQLAlchemy 配置、会话管理、数据库初始化脚本
"""

from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator
import logging

from app.config import get_settings
from app.models import Base

logger = logging.getLogger(__name__)
settings = get_settings()

# ==================== 数据库引擎配置 ====================

def get_database_url() -> str:
    """获取数据库 URL"""
    return settings.database_url


def create_db_engine():
    """创建数据库引擎"""
    db_url = get_database_url()
    
    # SQLite 特殊配置
    if "sqlite" in db_url:
        engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=settings.debug,
        )
        # SQLite 启用外键约束
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    
    # PostgreSQL/MySQL 配置
    else:
        engine = create_engine(
            db_url,
            echo=settings.debug,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={"connect_timeout": 10}
        )
    
    return engine


# 创建全局引擎和会话工厂
engine = create_db_engine()
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


# ==================== 数据库会话管理 ====================

def get_db() -> Generator[Session, None, None]:
    """获取数据库会话 (FastAPI 依赖注入)"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """上下文管理器形式的数据库会话"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


# ==================== 数据库初始化 ====================

def init_db():
    """初始化数据库 - 创建所有表"""
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")
    create_default_data()


def create_default_data():
    """创建默认数据 - 管理员用户"""
    from app.models import User, RoleEnum
    from app.security import get_password_hash
    
    db = SessionLocal()
    try:
        admin_exists = db.query(User).filter(
            User.role == RoleEnum.ADMIN
        ).first()
        
        if not admin_exists:
            admin = User(
                username="admin",
                password=get_password_hash("admin123"),
                display_name="系统管理员",
                employee_id="ADMIN001",
                email="admin@company.com",
                role=RoleEnum.ADMIN,
                is_active=True,
            )
            db.add(admin)
            db.commit()
            logger.info("Default admin user created")
        
    except Exception as e:
        logger.error(f"Error creating default data: {str(e)}")
        db.rollback()
    finally:
        db.close()


def drop_db():
    """删除所有表 (仅用于开发环境)"""
    if settings.debug:
        logger.warning("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("All tables dropped")
    else:
        raise RuntimeError("Cannot drop tables in production")


def reset_db():
    """重置数据库"""
    if settings.debug:
        logger.warning("Resetting database...")
        drop_db()
        init_db()
        logger.info("Database reset completed")
    else:
        raise RuntimeError("Cannot reset database in production")


# ==================== 数据库健康检查 ====================

def check_db_health() -> bool:
    """检查数据库连接"""
    try:
        with get_db_context() as db:
            db.execute("SELECT 1")
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False
