from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID

class TributeBase(BaseModel):
    author_name: str = Field(..., min_length=1, max_length=100)
    relation_to_deceased: Optional[str] = Field(None, max_length=100)
    message: str = Field(..., min_length=1)
    candle_lit: bool = False
    email: Optional[EmailStr] = None

class TributeCreate(TributeBase):
    pass

class TributeUpdate(BaseModel):
    author_name: Optional[str] = Field(None, min_length=1, max_length=100)
    relation_to_deceased: Optional[str] = Field(None, max_length=100)
    message: Optional[str] = Field(None, min_length=1)
    candle_lit: Optional[bool] = None
    approved: Optional[bool] = None
    email: Optional[EmailStr] = None

class Tribute(TributeBase):
    id: UUID
    approved: bool
    created_at: datetime
    
    class Config:
        orm_mode = True

class TributePublic(BaseModel):
    """Public view of tribute (hide sensitive info)"""
    id: UUID
    author_name: str
    relation_to_deceased: Optional[str] = None
    message: str
    candle_lit: bool
    created_at: datetime
    
    class Config:
        orm_mode = True
