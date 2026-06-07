"""SQLAlchemy 数据模型 - 9大业务模块

数据库表结构设计:
- 用户表: User
- 个人基本信息: PersonBasic, PersonHousehold, PersonContact
- 教育学业: PersonEducation, EducationRecords
- 家庭&社会: PersonFamily, SocialRelations
- 健康: PersonHealth
- 政治&党务: PersonPolitical
- 设备&账号: DeviceRecords, PlatformAccounts
- 奖惩&政审: RewardPunishment
- 工作从业: PersonWork, WorkHistory, WorkQualification
- 审计: AuditLog
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float,
    ForeignKey, Date, Enum, LargeBinary, Index, UniqueConstraint,
    create_engine, event
)
from sqlalchemy.orm import declarative_base, relationship, Session
from sqlalchemy.sql import func
import enum

Base = declarative_base()


class StatusEnum(str, enum.Enum):
    """审核状态"""
    DRAFT = "draft"  # 草稿
    PENDING = "pending"  # 待审核
    APPROVED = "approved"  # 已通过
    REJECTED = "rejected"  # 已驳回


class RoleEnum(str, enum.Enum):
    """用户角色"""
    USER = "user"  # 普通用户
    ADMIN = "admin"  # 管理员


# ==================== 用户管理 ====================

class User(Base):
    """用户表"""
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint('username', name='uq_username'),
        Index('idx_role', 'role'),
        Index('idx_is_active', 'is_active'),
    )

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # bcrypt hash
    display_name = Column(String(100))
    employee_id = Column(String(50), unique=True, nullable=True)
    email = Column(String(100), unique=True, nullable=True)
    phone = Column(String(20), nullable=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # 关系
    person = relationship("PersonBasic", back_populates="user", uselist=False, cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="operator")


# ==================== Part 1: 基础身份&户籍 ====================

class PersonBasic(Base):
    """自然人基础标识"""
    __tablename__ = "person_basic"
    __table_args__ = (
        UniqueConstraint('id_card_number', name='uq_id_card'),
        Index('idx_user_id', 'user_id'),
        Index('idx_status', 'status'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    
    # 基本信息
    name = Column(String(100), nullable=False, index=True)
    former_name = Column(String(100), nullable=True)  # 加密
    gender = Column(String(10), default="男")
    birth_date = Column(Date, nullable=True)
    age = Column(Integer, nullable=True)
    ethnicity = Column(String(20), default="汉族")
    nationality = Column(String(20), default="中国")
    
    # 证件信息
    id_card_type = Column(String(50), default="居民身份证")
    id_card_number = Column(String(50), nullable=True)  # 加密
    id_card_valid_period = Column(Date, nullable=True)
    id_card_issuer = Column(String(100), nullable=True)
    
    # 社会身份
    marital_status = Column(String(20), default="未婚")
    political_status = Column(String(50), default="群众")
    health_status = Column(String(20), default="良好")
    blood_type = Column(String(10), nullable=True)
    
    # 照片
    photo_main = Column(LargeBinary, nullable=True)  # 主照片
    
    # 状态
    status = Column(Enum(StatusEnum), default=StatusEnum.DRAFT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    review_remark = Column(Text, nullable=True)
    
    # 关系
    user = relationship("User", back_populates="person")
    household = relationship("PersonHousehold", back_populates="person", uselist=False, cascade="all, delete-orphan")
    contacts = relationship("PersonContact", back_populates="person", cascade="all, delete-orphan")
    education = relationship("PersonEducation", back_populates="person", uselist=False, cascade="all, delete-orphan")
    family = relationship("PersonFamily", back_populates="person", uselist=False, cascade="all, delete-orphan")
    health = relationship("PersonHealth", back_populates="person", uselist=False, cascade="all, delete-orphan")
    political = relationship("PersonPolitical", back_populates="person", uselist=False, cascade="all, delete-orphan")
    work = relationship("PersonWork", back_populates="person", uselist=False, cascade="all, delete-orphan")
    photos = relationship("PersonPhoto", back_populates="person", cascade="all, delete-orphan")


class PersonHousehold(Base):
    """户籍&籍贯信息"""
    __tablename__ = "person_household"
    __table_args__ = (Index('idx_person_id', 'person_id'),)

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey('person_basic.id'), unique=True, nullable=False)
    
    native_place = Column(String(100))  # 籍贯
    birth_place = Column(String(100))  # 出生地 (加密)
    household_type = Column(String(20), default="农业户口")
    household_police_station = Column(String(100))
    household_address = Column(String(200))
    
    current_address = Column(String(200), nullable=False)  # 现住址
    door_number = Column(String(50))  # 详细门牌号
    postal_code = Column(String(10))
    temp_address = Column(String(200))  # 临时地址
    emergency_address = Column(String(200))  # 紧急地址
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    person = relationship("PersonBasic", back_populates="household")


class PersonContact(Base):
    """多条联系方式记录"""
    __tablename__ = "person_contact"
    __table_args__ = (Index('idx_person_id', 'person_id'),)

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey('person_basic.id'), nullable=False)
    
    contact_type = Column(String(50))  # 类型: 手机、电话、邮箱等
    contact_value = Column(String(100), nullable=False)  # 加密
    remark = Column(String(100))
    is_primary = Column(Boolean, default=False)  # 主联系方式
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    person = relationship("PersonBasic", back_populates="contacts")


# ==================== Part 2: 教育学业 ====================

class PersonEducation(Base):
    """教育学业基础信息"""
    __tablename__ = "person_education"
    __table_args__ = (Index('idx_person_id', 'person_id'),)

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey('person_basic.id'), unique=True, nullable=False)
    
    highest_education = Column(String(50), default="本科")
    degree = Column(String(50), default="学士学位")
    study_years = Column(Integer)  # 学制
    study_mode = Column(String(50), default="全日制")
    study_status = Column(String(50), default="毕业")
    
    student_id = Column(String(50))
    graduation_cert_no = Column(String(100))  # 毕业证编号
    degree_cert_no = Column(String(100))  # 学位证编号
    xuexin_no = Column(String(100))  # 学信网编号
    graduation_date = Column(Date)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    person = relationship("PersonBasic", back_populates="education")
    records = relationship("EducationRecords", back_populates="person_education", cascade="all, delete-orphan")


class EducationRecords(Base):
    """教育履历 (多条)"""
    __tablename__ = "education_records"
    __table_args__ = (Index('idx_person_education_id', 'person_education_id'),)

    id = Column(Integer, primary_key=True, index=True)
    person_education_id = Column(Integer, ForeignKey('person_education.id'), nullable=False)
    
    start_date = Column(Date)
    end_date = Column(Date)
    school_name = Column(String(100))
    department = Column(String(100))
    major = Column(String(100))
    class_name = Column(String(50))
    school_position = Column(String(100))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    person_education = relationship("PersonEducation", back_populates="records")


# ==================== Part 3: 家庭&社会关系 ====================

class PersonFamily(Base):
    """家庭关系信息"""
    __tablename__ = "person_family"
    __table_args__ = (Index('idx_person_id', 'person_id'),)

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey('person_basic.id'), unique=True, nullable=False)
    
    marital_status = Column(String(20), default="未婚")
    spouse_name = Column(String(100))
    spouse_id = Column(String(50))  # 加密
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    person = relationship("PersonBasic", back_populates="family")
    members = relationship("FamilyMembers", back_populates="person_family", cascade="all, delete-orphan")
    social_relations = relationship("SocialRelations", back_populates="person_family", cascade="all, delete-orphan")


class FamilyMembers(Base):
    """家庭成员 (直系)"""
    __tablename__ = "family_members"
    __table_args__ = (Index('idx_person_family_id', 'person_family_id'),)

    id = Column(Integer, primary_key=True, index=True)
    person_family_id = Column(Integer, ForeignKey('person_family.id'), nullable=False)
    
    relation = Column(String(20))  # 关系: 父、母、配偶、子、女
    name = Column(String(100))
    age = Column(Integer)
    work_unit = Column(String(100))
    position = Column(String(100))
    political_status = Column(String(50))
    phone = Column(String(20))  # 加密
    address = Column(String(200))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    person_family = relationship("PersonFamily", back_populates="members")


class SocialRelations(Base):
    """社会关系 (扩展)"""
    __tablename__ = "social_relations"
    __table_args__ = (Index('idx_person_family_id', 'person_family_id'),)

    id = Column(Integer, primary_key=True, index=True)
    person_family_id = Column(Integer, ForeignKey('person_family.id'), nullable=False)
    
    relation = Column(String(20))  # 关系: 祖父母、外祖父母、兄妹、岳父母等
    name = Column(String(100))
    age = Column(Integer)
    work_unit = Column(String(100))
    position = Column(String(100))
    political_status = Column(String(50))
    phone = Column(String(20))  # 加密
    address = Column(String(200))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    person_family = relationship("PersonFamily", back_populates="social_relations")


# ==================== Part 4: 健康信息 ====================

class PersonHealth(Base):
    """健康信息"""
    __tablename__ = "person_health"
    __table_args__ = (Index('idx_person_id', 'person_id'),)

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey('person_basic.id'), unique=True, nullable=False)
    
    height = Column(Integer)  # cm
    weight = Column(Integer)  # kg
    blood_type = Column(String(10))
    eyesight = Column(String(20))
    health_status = Column(String(20), default="良好")
    
    disease_history = Column(Text)  # 既往病史
    allergy_history = Column(Text)  # 过敏史
    disability = Column(Text)  # 残疾情况
    vaccine_status = Column(String(50), default="无")  # 疫苗接种
    physical_exam_result = Column(Text)  # 体检结论
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    person = relationship("PersonBasic", back_populates="health")


# ==================== Part 5: 政治&党务 ====================

class PersonPolitical(Base):
    """政治面貌及人员身份"""
    __tablename__ = "person_political"
    __table_args__ = (Index('idx_person_id', 'person_id'),)

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey('person_basic.id'), unique=True, nullable=False)
    
    political_status = Column(String(50), default="群众")
    religion = Column(String(50), default="无")
    
    youth_league_join_date = Column(Date)  # 入团时间
    party_join_date = Column(Date)  # 入党时间
    party_formal_date = Column(Date)  # 转正时间
    party_branch = Column(String(100))  # 党团支部
    
    person_type = Column(String(50), default="在职人员")  # 人员身份类别
    united_front_status = Column(String(50), default="无")  # 统战身份: 侨胞、归侨等
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    person = relationship("PersonBasic", back_populates="political")


# ==================== Part 6: 设备&全网账号 ====================

class PersonPhoto(Base):
    """多规格证件照片"""
    __tablename__ = "person_photo"
    __table_args__ = (Index('idx_person_id', 'person_id'),)

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey('person_basic.id'), nullable=False)
    
    photo_type = Column(String(50))  # 类型: 一寸照、二寸照、证件照等
    photo_data = Column(LargeBinary, nullable=False)
    size_kb = Column(Integer)
    
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    person = relationship("PersonBasic", back_populates="photos")


class DeviceRecords(Base):
    """设备记录 (移动/PC设备)"""
    __tablename__ = "device_records"
    __table_args__ = (Index('idx_user_id', 'user_id'),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    device_type = Column(String(50))  # 类型: 手机、笔记本等
    model = Column(String(100))
    device_no = Column(String(100), unique=True, nullable=True)  # IMEI或设备编号
    os = Column(String(50))  # 操作系统
    bound_account = Column(String(100))  # 绑定账号
    
    registered_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime)


class PlatformAccounts(Base):
    """网络平台账号"""
    __tablename__ = "platform_accounts"
    __table_args__ = (Index('idx_user_id', 'user_id'),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    platform_category = Column(String(50))  # 分类: 社交、办公、生活、学习
    platform_name = Column(String(100))  # 平台名称
    account = Column(String(200))  # 账号
    account_type = Column(String(50))  # 账号类型: 手机号、邮箱等
    remark = Column(String(200))
    
    registered_at = Column(DateTime, default=datetime.utcnow)


# ==================== Part 7: 奖惩&政审 ====================

class RewardPunishment(Base):
    """奖惩与政审记录"""
    __tablename__ = "reward_punishment"
    __table_args__ = (Index('idx_user_id', 'user_id'),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    record_type = Column(String(50))  # 类型: 奖励、处分、违纪、违法等
    record_name = Column(String(100))
    record_date = Column(Date)
    issuer = Column(String(100))  # 颁发/执行单位
    remark = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)


# ==================== Part 8: 工作从业&社保 ====================

class PersonWork(Base):
    """工作从业信息"""
    __tablename__ = "person_work"
    __table_args__ = (Index('idx_user_id', 'user_id'),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    
    # 在岗信息
    current_employer = Column(String(200))
    employer_full_name = Column(String(200))
    employer_type = Column(String(100))  # 单位性质
    employer_address = Column(String(200))
    industry = Column(String(100))
    department = Column(String(100))
    position = Column(String(100))
    
    hire_date = Column(Date)
    employment_status = Column(String(50), default="在职")  # 在职、试用期、离职、待业
    
    # 社保信息
    social_insurance_status = Column(String(50))
    social_insurance_area = Column(String(100))
    provident_fund_account = Column(String(100))
    
    # 银行卡信息
    bank_name = Column(String(100))
    bank_account = Column(String(50))  # 加密
    account_holder = Column(String(100))
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    person = relationship("PersonBasic", back_populates="work")
    work_history = relationship("WorkHistory", back_populates="person_work", cascade="all, delete-orphan")
    qualifications = relationship("WorkQualification", back_populates="person_work", cascade="all, delete-orphan")


class WorkHistory(Base):
    """工作履历"""
    __tablename__ = "work_history"
    __table_args__ = (Index('idx_person_work_id', 'person_work_id'),)

    id = Column(Integer, primary_key=True, index=True)
    person_work_id = Column(Integer, ForeignKey('person_work.id'), nullable=False)
    
    start_date = Column(Date)
    end_date = Column(Date)
    company = Column(String(200))
    department = Column(String(100))
    position = Column(String(100))
    leave_reason = Column(String(200))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    person_work = relationship("PersonWork", back_populates="work_history")


class WorkQualification(Base):
    """职业资质"""
    __tablename__ = "work_qualification"
    __table_args__ = (Index('idx_person_work_id', 'person_work_id'),)

    id = Column(Integer, primary_key=True, index=True)
    person_work_id = Column(Integer, ForeignKey('person_work.id'), nullable=False)
    
    qualification_type = Column(String(50))  # 资格证、职称等
    qualification_name = Column(String(100))
    certificate_no = Column(String(100))
    issuer = Column(String(100))
    issue_date = Column(Date)
    expiry_date = Column(Date)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    person_work = relationship("PersonWork", back_populates="qualifications")


# ==================== Part 9: 出行&机动车 ====================

class TravelDocuments(Base):
    """出行&机动车信息"""
    __tablename__ = "travel_documents"
    __table_args__ = (Index('idx_user_id', 'user_id'),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    
    # 出行证件
    passport_no = Column(String(50))  # 加密
    hk_macao_pass_no = Column(String(50))  # 加密
    
    # 机动车
    vehicle_plate = Column(String(50))
    vehicle_license_no = Column(String(100))
    driver_license_no = Column(String(100))
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ==================== 审计日志 ====================

class AuditLog(Base):
    """审计日志"""
    __tablename__ = "audit_log"
    __table_args__ = (
        Index('idx_operator_id', 'operator_id'),
        Index('idx_action', 'action'),
        Index('idx_created_at', 'created_at'),
    )

    id = Column(Integer, primary_key=True, index=True)
    operator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    action = Column(String(100))  # 操作类型
    table_name = Column(String(50))  # 涉及表
    record_id = Column(Integer)  # 记录ID
    old_value = Column(Text)  # 旧值
    new_value = Column(Text)  # 新值
    remark = Column(Text)  # 备注
    ip_address = Column(String(50))
    user_agent = Column(String(200))
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # 关系
    operator = relationship("User", back_populates="audit_logs")
