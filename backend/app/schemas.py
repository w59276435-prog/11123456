"""Pydantic 数据模型 - 请求/响应Schema

用于API数据验证、文档生成和类型检查
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional
from datetime import datetime, date
from enum import Enum


# ==================== 枚举类型 ====================

class StatusEnum(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class RoleEnum(str, Enum):
    USER = "user"
    ADMIN = "admin"


# ==================== 用户认证 ====================

class UserLogin(BaseModel):
    """用户登录请求"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=255)


class UserRegister(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=255)
    display_name: str = Field(..., max_length=100)
    employee_id: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)


class ChangePassword(BaseModel):
    """修改密码请求"""
    old_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('两次输入的密码不一致')
        return v


class TokenResponse(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int
    role: RoleEnum
    display_name: str


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    display_name: str
    employee_id: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    role: RoleEnum
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


# ==================== 个人信息 - 基础身份 ====================

class PersonBasicUpdate(BaseModel):
    """个人基础信息更新"""
    name: str = Field(..., min_length=1, max_length=100)
    former_name: Optional[str] = None
    gender: str = Field(default="男")
    birth_date: Optional[date] = None
    ethnicity: str = Field(default="汉族")
    id_card_type: str = Field(default="居民身份证")
    id_card_number: str = Field(..., min_length=15, max_length=50)
    id_card_valid_period: Optional[date] = None
    marital_status: str = Field(default="未婚")
    health_status: str = Field(default="良好")
    blood_type: Optional[str] = None


class PersonHouseholdUpdate(BaseModel):
    """户籍信息更新"""
    native_place: Optional[str] = None
    household_type: str = Field(default="农业户口")
    current_address: str = Field(..., min_length=1)
    postal_code: Optional[str] = None


class PersonContactCreate(BaseModel):
    """新增联系方式"""
    contact_type: str
    contact_value: str = Field(..., min_length=1, max_length=100)
    remark: Optional[str] = None
    is_primary: bool = False


class PersonContactResponse(PersonContactCreate):
    """联系方式响应"""
    id: int
    person_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== 个人信息 - 教育 ====================

class EducationRecordCreate(BaseModel):
    """教育履历新增"""
    start_date: date
    end_date: date
    school_name: str
    department: Optional[str] = None
    major: str
    class_name: Optional[str] = None
    school_position: Optional[str] = None


class EducationRecordResponse(EducationRecordCreate):
    """教育履历响应"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PersonEducationUpdate(BaseModel):
    """教育信息更新"""
    highest_education: str = Field(default="本科")
    degree: str = Field(default="学士学位")
    study_mode: str = Field(default="全日制")
    study_status: str = Field(default="毕业")
    graduation_date: Optional[date] = None
    education_records: List[EducationRecordCreate] = []


# ==================== 个人信息 - 家庭 ====================

class FamilyMemberCreate(BaseModel):
    """家庭成员新增"""
    relation: str
    name: str
    age: Optional[int] = None
    work_unit: Optional[str] = None
    position: Optional[str] = None
    political_status: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class SocialRelationCreate(BaseModel):
    """社会关系新增"""
    relation: str
    name: str
    age: Optional[int] = None
    work_unit: Optional[str] = None
    position: Optional[str] = None
    political_status: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class PersonFamilyUpdate(BaseModel):
    """家庭信息更新"""
    marital_status: str = Field(default="未婚")
    family_members: List[FamilyMemberCreate] = []
    social_relations: List[SocialRelationCreate] = []


# ==================== 个人信息 - 工作 ====================

class WorkHistoryCreate(BaseModel):
    """工作履历新增"""
    start_date: date
    end_date: date
    company: str
    department: Optional[str] = None
    position: str
    leave_reason: Optional[str] = None


class PersonWorkUpdate(BaseModel):
    """工作信息更新"""
    current_employer: str
    department: str
    position: str
    hire_date: date
    employment_status: str = Field(default="在职")
    bank_account: Optional[str] = None
    work_history: List[WorkHistoryCreate] = []


# ==================== 审核相关 ====================

class ReviewRequest(BaseModel):
    """审核请求"""
    person_id: int
    status: StatusEnum = Field(..., description="审核结果: approved/rejected")
    remark: Optional[str] = None


class PersonDetailResponse(BaseModel):
    """个人信息详情响应"""
    id: int
    user_id: int
    name: str
    gender: str
    birth_date: Optional[date]
    id_card_number: str  # 返回时脱敏
    status: StatusEnum
    created_at: datetime
    submitted_at: Optional[datetime]
    reviewed_at: Optional[datetime]
    review_remark: Optional[str]
    
    contacts: List[PersonContactResponse] = []

    class Config:
        from_attributes = True


# ==================== 管理员相关 ====================

class AdminUserCreate(BaseModel):
    """管理员新增用户"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(default="123456", min_length=8)
    display_name: str = Field(..., max_length=100)
    employee_id: Optional[str] = None
    role: RoleEnum = RoleEnum.USER


class AdminUserUpdate(BaseModel):
    """管理员编辑用户"""
    display_name: Optional[str] = None
    role: Optional[RoleEnum] = None
    is_active: Optional[bool] = None


class PendingPersonResponse(BaseModel):
    """待审核人员响应"""
    id: int
    name: str
    username: str
    employee_id: Optional[str]
    submitted_at: datetime
    status: StatusEnum

    class Config:
        from_attributes = True


# ==================== 统计相关 ====================

class StatsResponse(BaseModel):
    """统计数据响应"""
    total_users: int
    total_persons: int
    draft_count: int
    pending_count: int
    approved_count: int
    rejected_count: int
    active_users: int
    today_submissions: int


# ==================== 通用响应 ====================

class APIResponse(BaseModel):
    """通用API响应"""
    code: int = Field(..., description="状态码: 0成功, 非0为错误")
    message: str = Field(..., description="提示信息")
    data: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginationResponse(BaseModel):
    """分页响应"""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[dict]
