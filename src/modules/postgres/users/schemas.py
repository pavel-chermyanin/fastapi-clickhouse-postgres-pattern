from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


# Базовые свойства пользователя
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: bool = True


# Свойства для создания пользователя через API
class UserCreate(UserBase):
    email: EmailStr
    password: str


# Свойства для обновления данных пользователя
class UserUpdate(UserBase):
    password: Optional[str] = None


# Свойства, хранящиеся в БД
class UserInDBBase(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Свойства для возврата клиенту
class User(UserInDBBase):
    pass
