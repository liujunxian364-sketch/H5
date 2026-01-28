from fastapi import APIRouter, Query

router = APIRouter()

# 模拟数据
mock_words = [
    {
        "id": 1,
        "word": "abandon",
        "phonetic": "/əˈbændən/",
        "meaning": "v. 放弃；抛弃",
        "example": "He abandoned his wife and children.",
        "createTime": "2024-01-15"
    },
    {
        "id": 2,
        "word": "ability",
        "phonetic": "/əˈbɪləti/",
        "meaning": "n. 能力；才能",
        "example": "She has the ability to solve complex problems.",
        "createTime": "2024-01-15"
    }
]

@router.get("")
async def get_word_list(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=50)
):
    start = (page - 1) * pageSize
    end = start + pageSize
    data = mock_words[start:end]
    return {
        "code": 0,
        "message": "success",
        "data": data,
        "total": len(mock_words)
    }

@router.get("/{word_id}")
async def get_word_detail(word_id: int):
    for word in mock_words:
        if word["id"] == word_id:
            return {
                "code": 0,
                "message": "success",
                "data": word
            }
    return {
        "code": 404,
        "message": "单词不存在",
        "data": None
    }
