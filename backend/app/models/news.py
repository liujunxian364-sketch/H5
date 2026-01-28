from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class NewsBase(BaseModel):
    title: str
    summary: str
    content: str
    image: Optional[str] = None

class NewsCreate(NewsBase):
    pass

class News(NewsBase):
    id: int
    views: int = 0
    createTime: str

    class Config:
        from_attributes = True

class NewsListResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: List[News]
    total: int

class NewsDetailResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[News] = None
