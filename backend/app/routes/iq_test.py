"""
学商速测 API 路由
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Optional
import httpx
import json
import os
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(prefix="/iq-test", tags=["学商速测"])

# MBTI API 配置
MBTI_API_URL = "https://rjedu.runjian.com/rptapi/mbti/questions"
MBTI_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3Njk1NjgzNzEsImV4cCI6MTc3MDQ1NzQwNCwidG9QbGF0Zm9ybSI6IjEiLCJ0eXBlIjoiMyIsInVzZXJJZCI6IjE1NDUyMjc5MDM0MzA5NjcyOTYifQ.SutQIt2pruALw_USi7wBIcq1O-cKXNrjItZ6FKon-NQ"

# 数据存储文件路径
STORAGE_DIR = "backend/app/services"
ANSWERS_FILE = os.path.join(STORAGE_DIR, "iq_test_answers.json")

# 确保存储目录存在
os.makedirs(STORAGE_DIR, exist_ok=True)


# ==================== 数据模型 ====================

class SubmitRequest(BaseModel):
    name: str
    birthDate: str
    academicYear: str
    birthTime: str  # 出生时间段，如 "04:00-10:00"
    answer: str  # 格式: "id,answer|id,answer|..."


class ContinueChatRequest(BaseModel):
    conversation_id: str  # Dify conversation ID
    query: str  # 用户新问题
    user_info: dict  # 用户信息


# ==================== 辅助函数 ====================

def load_answers():
    """从文件加载所有答案记录"""
    if os.path.exists(ANSWERS_FILE):
        try:
            with open(ANSWERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] 加载答案记录失败: {e}")
            return []
    return []


def save_answers(answers_list):
    """保存答案记录到文件"""
    try:
        with open(ANSWERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(answers_list, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[ERROR] 保存答案记录失败: {e}")
        return False


# ==================== API 路由 ====================

@router.get("/questions")
async def get_questions():
    """
    获取题目列表（从 MBTI API）
    """
    try:
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            response = await client.get(
                MBTI_API_URL,
                headers={"token": MBTI_TOKEN}
            )
            response.raise_for_status()
            
            # 获取原始数据
            data = response.json()
            
            # API 返回格式: { code: 200, result: { rows: [...] }, message: "Success" }
            if data.get("code") == 200 and "result" in data:
                questions = data["result"].get("rows", [])
                
                # 转换为前端需要的格式
                formatted_questions = []
                for q in questions:
                    formatted_questions.append({
                        "id": q.get("id"),
                        "question": q.get("title"),
                        "options": [
                            {
                                "label": option.get("item"),
                                "value": option.get("item"),
                                "text": option.get("content"),
                                "answer": option.get("answer")  # MBTI 答案类型
                            }
                            for option in q.get("selectItem", [])
                        ],
                        "index": q.get("index")
        })
                
    return {
        "code": 0,
        "message": "success",
                    "data": formatted_questions
    }
            else:
                return {
                    "code": -1,
                    "message": data.get("message", "获取题目失败"),
                    "data": []
                }
                
    except httpx.HTTPStatusError as e:
        print(f"[ERROR] MBTI API 返回错误: {e.response.status_code}")
        print(f"[ERROR] 响应内容: {e.response.text}")
        raise HTTPException(
            status_code=502,
            detail=f"获取题目失败: {e.response.text}"
        )
    except Exception as e:
        print(f"[ERROR] 获取题目失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取题目失败: {str(e)}")


@router.post("/submit")
async def submit_answers(data: SubmitRequest):
    """
    提交用户答案到 Dify 进行分析
    """
    try:
        # Dify API 配置
        dify_url = "https://deepseek.zkyc-ai.cn/v1/chat-messages"
        dify_api_key = "app-EyTZlz1Zn0SheEKkN2Capf1U"
        user_id = "1545227903430967296"
        
        # 格式化出生日期和时间段
        # birth_date 格式: "YYYY-MM-DD HH:MM-HH:MM"
        birth_date = f"{data.birthDate} {data.birthTime}"
        
        # 构建请求体
        payload = {
            "auto_generate_name": True,
            "conversation_id": "",
            "files": [],
            "inputs": {
                "name": data.name,  # 添加用户姓名
                "academic_year": data.academicYear,
                "answer": data.answer,
                "birth_date": birth_date,
                "token": MBTI_TOKEN
            },
            "query": "开始分析规划吧",
            "response_mode": "streaming",
            "user": user_id
        }
        
        print(f"[INFO] 提交答案到 Dify:")
        print(f"[INFO] 姓名: {data.name}")
        print(f"[INFO] 出生日期: {birth_date}")
        print(f"[INFO] 学年: {data.academicYear}")
        print(f"[INFO] 答案: {data.answer[:100]}...")
        print(f"[INFO] 完整payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        
        # 调用 Dify API（流式接收）
        async with httpx.AsyncClient(timeout=120.0, verify=False) as client:
            async with client.stream(
                "POST",
                dify_url,
                headers={
                    "Authorization": f"Bearer {dify_api_key}",
                    "Content-Type": "application/json"
                },
                json=payload
            ) as response:
                response.raise_for_status()
                
                # 处理 Dify 的流式响应
                full_response = ""
                conversation_id = ""
                
                # 逐行读取流式数据
                async for line in response.aiter_lines():
                    if line.startswith('data:'):
                        data_str = line[5:].strip()
                        if data_str:
                            try:
                                chunk_data = json.loads(data_str)
                                
                                # 提取 conversation_id
                                if "conversation_id" in chunk_data:
                                    conversation_id = chunk_data["conversation_id"]
                                
                                # 提取回答内容
                                if "answer" in chunk_data:
                                    full_response += chunk_data["answer"]
                                    
                                # 打印进度
                                print(f"[INFO] 已接收 {len(full_response)} 字符...")
                            except json.JSONDecodeError:
                                continue
            
                
                print(f"[INFO] Dify 分析完成，conversation_id: {conversation_id}")
                print(f"[INFO] 响应长度: {len(full_response)} 字符")
            
            # 保存结果到本地（可选）
            all_answers = load_answers()
            new_record = {
                "id": f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "name": data.name,
                "birthDate": data.birthDate,
                "academicYear": data.academicYear,
                "birthTime": data.birthTime,
                "answer": data.answer,
                "dify_conversation_id": conversation_id,
                "analysis": full_response,
                "submittedAt": datetime.now().isoformat()
            }
            all_answers.append(new_record)
            save_answers(all_answers)
            
            return {
                "code": 0,
                "message": "分析完成",
                "data": {
                    "id": new_record["id"],
                    "conversation_id": conversation_id,
                    "analysis": full_response
                }
            }
            
    except httpx.HTTPStatusError as e:
        print(f"[ERROR] Dify API 返回错误: {e.response.status_code}")
        print(f"[ERROR] 响应内容: {e.response.text}")
        raise HTTPException(
            status_code=502,
            detail=f"Dify API 错误: {e.response.text}"
        )
    except Exception as e:
        print(f"[ERROR] 提交答案失败: {e}")
        raise HTTPException(status_code=500, detail=f"提交答案失败: {str(e)}")


@router.get("/answers")
async def get_all_answers():
    """
    获取所有答案记录（用于调试/管理）
    """
    try:
        answers = load_answers()
        return {
            "code": 0,
            "message": "success",
            "data": answers
        }
    except Exception as e:
        print(f"[ERROR] 获取答案记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取答案记录失败: {str(e)}")


@router.get("/answers/{answer_id}")
async def get_answer_by_id(answer_id: str):
    """
    根据ID获取单个答案记录
    """
    try:
        answers = load_answers()
        for record in answers:
            if record.get("id") == answer_id:
                return {
                    "code": 0,
                    "message": "success",
                    "data": record
                }
        
        raise HTTPException(status_code=404, detail="答案记录不存在")
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 获取答案记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取答案记录失败: {str(e)}")


@router.post("/continue-chat")
async def continue_chat(data: ContinueChatRequest):
    """
    继续对话（普通返回）
    """
    try:
        # Dify API 配置
        dify_url = "https://deepseek.zkyc-ai.cn/v1/chat-messages"
        dify_api_key = "app-EyTZlz1Zn0SheEKkN2Capf1U"
        user_id = "1545227903430967296"
        
        # 构建请求体（和初始提交完全一样的格式）
        payload = {
            "auto_generate_name": True,
            "conversation_id": data.conversation_id,  # 使用已有的 conversation_id
            "files": [],
            "inputs": {
                "name": data.user_info.get("name", ""),
                "academic_year": data.user_info.get("academicYear", ""),
                "answer": data.user_info.get("answer", ""),  # 完整的答案字符串
                "birth_date": f"{data.user_info.get('birthDate', '')} {data.user_info.get('birthTime', '')}",
                "token": MBTI_TOKEN
            },
            "query": data.query,  # 用户的新问题
            "response_mode": "streaming",
            "user": user_id
        }
        
        print(f"[INFO] 继续对话: {data.query}")
        print(f"[INFO] conversation_id: {data.conversation_id}")
        print(f"[INFO] 完整payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        
        # 调用 Dify API，流式接收后返回完整结果
        async with httpx.AsyncClient(timeout=60.0, verify=False) as client:
            async with client.stream(
                "POST",
                dify_url,
                headers={
                    "Authorization": f"Bearer {dify_api_key}",
                    "Content-Type": "application/json"
                },
                json=payload
            ) as response:
                response.raise_for_status()
                
                full_content = ""
                async for line in response.aiter_lines():
                    if line.startswith('data:'):
                        data_str = line[5:].strip()
                        if data_str:
                            try:
                                chunk_data = json.loads(data_str)
                                
                                # 提取回答内容
                                if "answer" in chunk_data:
                                    full_content += chunk_data["answer"]
                                
                            except json.JSONDecodeError:
                                continue
                
                print(f"[INFO] 对话完成，响应长度: {len(full_content)} 字符")

    return {
        "code": 0,
        "message": "success",
        "data": {
                        "answer": full_content
                    }
                }
                    
    except httpx.HTTPStatusError as e:
        print(f"[ERROR] Dify API 返回错误: {e.response.status_code}")
        print(f"[ERROR] 响应内容: {e.response.text}")
        raise HTTPException(
            status_code=502,
            detail=f"Dify API 错误: {e.response.text}"
        )
    except Exception as e:
        print(f"[ERROR] 继续对话失败: {e}")
        raise HTTPException(status_code=500, detail=f"继续对话失败: {str(e)}")
