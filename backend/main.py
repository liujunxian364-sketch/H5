from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import news, error_memory, word_memory, iq_test, conversation
import os

app = FastAPI(title="移动学习平台API", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务（用于访问上传的图片）
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 注册路由
app.include_router(news.router, prefix="/api/news", tags=["资讯"])
app.include_router(error_memory.router, prefix="/api/error-memory", tags=["错题记忆"])
app.include_router(word_memory.router, prefix="/api/word-memory", tags=["单词速记"])
app.include_router(conversation.router, prefix="/api", tags=["考点答疑-对话管理"])  # 对话路由
# app.include_router(exam_qa.router, prefix="/api/exam-qa", tags=["考点答疑"])  # 已被conversation.router替代
app.include_router(iq_test.router, prefix="/api", tags=["学商速测"])

@app.get("/")
async def root():
    return {"message": "移动学习平台API服务运行中"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
