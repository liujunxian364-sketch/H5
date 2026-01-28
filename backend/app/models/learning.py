from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ErrorQuestion(BaseModel):
    id: int
    image_url: str  # 错题图片URL
    image_crop_data: Optional[dict] = None  # 图片裁剪区域数据（x, y, width, height）
    subject: str  # 科目：语文、数学、英语等
    knowledge_points: List[str]  # 知识点标签列表（由OCR识别）
    createTime: str

class ErrorQuestionCreate(BaseModel):
    image_url: str
    image_crop_data: Optional[dict] = None
    subject: str

class ErrorQuestionUpload(BaseModel):
    subject: str
    crop_data: Optional[dict] = None  # 裁剪数据

class ErrorReport(BaseModel):
    subject: str
    total_count: int  # 该科目错题总数
    knowledge_points: List[dict]  # 知识点统计
    analysis: str  # 分析报告内容
    createTime: str

class Word(BaseModel):
    id: int
    word: str
    phonetic: str
    meaning: str
    example: str
    createTime: str

class ExamPoint(BaseModel):
    id: int
    title: str
    content: str
    subject: str
    createTime: str

class IQQuestion(BaseModel):
    id: int
    question: str
    options: List[str]
    answer: int

class IQResult(BaseModel):
    score: int
    level: str
    analysis: str
