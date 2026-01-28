from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter()

# 模拟数据
mock_news = [
    {
        "id": 1,
        "title": "2024年考研英语备考攻略",
        "summary": "考研英语是很多同学的难点，本文将从词汇、阅读、写作三个方面为大家详细讲解备考技巧...",
        "content": """<p>考研英语是很多同学的难点，本文将从词汇、阅读、写作三个方面为大家详细讲解备考技巧。</p>
        <h2>一、词汇篇</h2>
        <p>词汇是英语学习的基础，考研英语要求掌握约5500个单词。</p>""",
        "image": "https://picsum.photos/400/200?random=1",
        "views": 1256,
        "createTime": "2024-01-15"
    },
    {
        "id": 2,
        "title": "高效记忆法：艾宾浩斯遗忘曲线的应用",
        "summary": "艾宾浩斯遗忘曲线告诉我们，记忆会随时间逐渐衰退，但通过科学的复习方法可以有效巩固记忆...",
        "content": "<p>艾宾浩斯遗忘曲线是记忆研究的重要成果...</p>",
        "image": "https://picsum.photos/400/200?random=2",
        "views": 892,
        "createTime": "2024-01-14"
    },
    {
        "id": 3,
        "title": "如何提高学习效率？这5个方法值得一试",
        "summary": "学习效率的高低直接影响学习成果，掌握正确的学习方法能让你事半功倍...",
        "content": "<p>学习效率是每个学生都关心的话题...</p>",
        "image": "https://picsum.photos/400/200?random=3",
        "views": 756,
        "createTime": "2024-01-13"
    }
]

@router.get("")
async def get_news_list(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=50)
):
    start = (page - 1) * pageSize
    end = start + pageSize
    data = mock_news[start:end]
    return {
        "code": 0,
        "message": "success",
        "data": data,
        "total": len(mock_news)
    }

@router.get("/{news_id}")
async def get_news_detail(news_id: int):
    for news in mock_news:
        if news["id"] == news_id:
            return {
                "code": 0,
                "message": "success",
                "data": news
            }
    return {
        "code": 404,
        "message": "资讯不存在",
        "data": None
    }
