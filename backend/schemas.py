from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# ==========================================
# 1. User Schemas
# ==========================================
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    is_admin: bool


class PasswordReset(BaseModel):
    email: EmailStr
    new_password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    joined_date: str
    is_admin: bool = False

    class Config:
        populate_by_name = True


# ==========================================
# 2. PDF Document Schemas
# ==========================================
class PDFCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=150)
    description: str = Field(..., max_length=500)


class PDFResponse(BaseModel):
    id: str
    title: str
    description: str
    upload_date: str
    cloudinary_url: str
    public_id: Optional[str] = None
    file_name: Optional[str] = None
    sort_order: int = 0

    class Config:
        populate_by_name = True


# ==========================================
# 3. Discussion & Comment Schemas
# ==========================================
class DiscussionCreate(BaseModel):
    pdf_id: str
    message: str = Field(..., min_length=1, max_length=1000)


class DiscussionResponse(BaseModel):
    id: str
    pdf_id: str
    user_id: Optional[str] = None
    user_name: str
    is_admin: bool = False
    message: str
    timestamp: str

    class Config:
        populate_by_name = True


# ==========================================
# 4. FAQ Schemas
# ==========================================
class FAQCreate(BaseModel):
    query_type: str = Field(..., min_length=2, max_length=40)
    note_reference: Optional[str] = Field(None, max_length=150)
    heading: str = Field(..., min_length=3, max_length=160)
    details: str = Field(..., min_length=5, max_length=2000)
    answer: str = Field("", max_length=2000)


class FAQResponse(BaseModel):
    id: str
    query_type: str
    note_reference: Optional[str] = None
    heading: str
    details: str
    answer: str
    answer_by: Optional[str] = None
    user_name: str
    timestamp: str

    class Config:
        populate_by_name = True


# ==========================================
# 5. Admin Schemas
# ==========================================
class AdminLogin(BaseModel):
    username: str
    password: str