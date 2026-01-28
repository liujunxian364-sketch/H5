from fastapi import APIRouter, Query

router = APIRouter()

# 模拟数据
mock_exam_points = [
    {
        "id": 1,
        "title": "三角函数基本公式",
        "content": "三角函数的基本公式包括...",
        "subject": "数学",
        "createTime": "2024-01-15"
    }
]

@router.get("")
async def get_exam_point_list(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=50),
    subject: str = Query(None)
):
    data = mock_exam_points
    if subject:
        data = [e for e in data if e["subject"] == subject]
    return {
        "code": 0,
        "message": "success",
        "data": data,
        "total": len(data)
    }

@router.get("/{point_id}")
async def get_exam_point_detail(point_id: int):
    for point in mock_exam_points:
        if point["id"] == point_id:
            return {
                "code": 0,
                "message": "success",
                "data": point
            }
    return {
        "code": 404,
        "message": "考点不存在",
        "data": None
    }
