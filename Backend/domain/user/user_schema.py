from pydantic import BaseModel, field_validator, EmailStr, validator
from pydantic_core.core_schema import FieldValidationInfo
from typing import Optional
import re


class UserCreate(BaseModel):
    user_id: str
    user_name: str
    password1: str
    password2: str
    email: EmailStr
    phone_number: str

    @field_validator('password1')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('비밀번호는 최소 6자리여야 합니다.')

        patterns = [
            re.compile(r"[a-zA-Z]"),  # 문자
            re.compile(r"\d"),        # 숫자
            re.compile(r"[^a-zA-Z0-9]")  # 특수문자
        ]

        valid_pattern_count = sum(bool(pattern.search(v)) for pattern in patterns)

        if valid_pattern_count < 2:
            raise ValueError('비밀번호는 문자, 숫자, 특수문자 중 2개 이상을 포함해야 합니다.')

        return v

    @field_validator('user_id', 'user_name', 'password1', 'password2', 'email')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('빈 값은 허용되지 않습니다.')
        return v

    @field_validator('password2')
    def passwords_match(cls, v, info: FieldValidationInfo):
        if 'password1' in info.data and v != info.data['password1']:
            raise ValueError('비밀번호가 일치하지 않습니다')
        return v
    
    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        pattern = re.compile(r'^01[016789][1-9]\d{6,7}$')
        if not pattern.match(v):
            raise ValueError('유효하지 않은 핸드폰 번호 형식입니다.')
        return v
    

class UserState(BaseModel):
    user_id: str
    user_name: str
    email : str
    phone_number : str
    profile_image : str
    profile_color: Optional[str]
    employment : bool
    state: bool
    attendance_type : bool


class UserUpdate(BaseModel):
    new_password: Optional[str] = None
    user_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    profile_color: Optional[str] = None
    employment: Optional[bool] = None
    state: Optional[bool] = None
    attendance_type: Optional[bool] = None

    @field_validator('new_password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('비밀번호는 최소 6자리여야 합니다.')

        patterns = [
            re.compile(r"[a-zA-Z]"),  # 문자
            re.compile(r"\d"),        # 숫자
            re.compile(r"[^a-zA-Z0-9]")  # 특수문자
        ]

        valid_pattern_count = sum(bool(pattern.search(v)) for pattern in patterns)

        if valid_pattern_count < 2:
            raise ValueError('비밀번호는 문자, 숫자, 특수문자 중 2개 이상을 포함해야 합니다.')

        return v

    @validator('phone_number', allow_reuse=True)
    def validate_phone_number(cls, v):
        if v is not None:
            pattern = re.compile(r'^01[016789][1-9]\d{6,7}$')
            if not pattern.match(v):
                raise ValueError('유효하지 않은 핸드폰 번호 형식입니다.')
        return v


class UserResponse(BaseModel):
    user_id: str
    user_name: str
    email: str
    phone_number: str
    profile_image: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    user_name: str
    email: str
    phone_number: str
    profile_image : str
    employment : bool
    state : bool
    attendance_type : bool
    admin : bool


class LoginFormData(BaseModel):
    user_id: str
    password: str