"""
考点答疑 API 路由
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Request
from fastapi.responses import StreamingResponse
from typing import Optional, List
import os
import uuid
import json
import re
from datetime import datetime

from ..models.conversation import (
    Conversation,
    ConversationCreate,
    Message,
    MessageCreate
)
from ..services.dify_service import dify_service
from ..services.memory_store import memory_store

router = APIRouter(prefix="/exam-qa", tags=["考点答疑"])

# Dify 服务器基础 URL（用于图片路径转换）
DIFY_SERVER_URL = "http://deepseek.zkyc-ai.cn"

def convert_dify_image_urls(content: str) -> str:
    """
    将 Dify 返回的相对图片路径转换为完整 URL
    例如: /files/tools/xxx.png -> http://deepseek.zkyc-ai.cn/files/tools/xxx.png
    """
    if not content:
        return content
    
    # 匹配 Markdown 图片语法: ![alt](/files/...)
    pattern = r'!\[([^\]]*)\]\((/files/[^)]+)\)'
    
    def replace_url(match):
        alt_text = match.group(1)
        rel_path = match.group(2)
        full_url = f"{DIFY_SERVER_URL}{rel_path}"
        return f'![{alt_text}]({full_url})'
    
    return re.sub(pattern, replace_url, content)


# ==================== 对话会话管理 ====================

@router.get("/conversations", response_model=dict)
async def get_conversations():
    """获取对话列表"""
    conversations = memory_store.get_all_conversations()
    
    # 转换datetime为字符串
    result = []
    for conv in conversations:
        conv_data = conv.copy()
        conv_data["created_at"] = conv_data["created_at"].isoformat()
        conv_data["updated_at"] = conv_data["updated_at"].isoformat()
        result.append(conv_data)
    
    return {
        "code": 0,
        "data": result
    }


@router.post("/conversations", response_model=dict)
async def create_conversation(data: ConversationCreate):
    """创建新对话"""
    conversation = memory_store.create_conversation(title=data.title or "新对话")
    
    conv_data = conversation.copy()
    conv_data["created_at"] = conv_data["created_at"].isoformat()
    conv_data["updated_at"] = conv_data["updated_at"].isoformat()
    
    return {
        "code": 0,
        "data": conv_data
    }


@router.get("/conversations/{conversation_id}", response_model=dict)
async def get_conversation(conversation_id: str):
    """获取对话详情"""
    conversation = memory_store.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    conv_data = conversation.copy()
    conv_data["created_at"] = conv_data["created_at"].isoformat()
    conv_data["updated_at"] = conv_data["updated_at"].isoformat()
    
    return {
        "code": 0,
        "data": conv_data
    }


@router.delete("/conversations/{conversation_id}", response_model=dict)
async def delete_conversation(conversation_id: str):
    """删除对话"""
    success = memory_store.delete_conversation(conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    return {
        "code": 0,
        "message": "删除成功"
    }


# ==================== 消息管理 ====================

@router.get("/conversations/{conversation_id}/messages", response_model=dict)
async def get_messages(conversation_id: str, limit: Optional[int] = 20):
    """
    获取对话历史消息
    如果对话有 dify_conversation_id，则从 Dify 拉取历史
    否则从本地内存获取
    """
    conversation = memory_store.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    dify_conv_id = conversation.get("dify_conversation_id")
    
    # 如果有 Dify 对话 ID，从 Dify 拉取历史消息
    if dify_conv_id:
        try:
            print(f"[DEBUG] 从 Dify 拉取对话历史: {dify_conv_id}")
            dify_logs = await dify_service.get_conversation_logs(dify_conv_id, limit=limit or 20)
            
            # 【调试】保存原始响应到 JSON 文件
            debug_file = os.path.join(os.path.dirname(__file__), "..", "..", "dify_logs_debug.json")
            try:
                with open(debug_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "conversation_id": conversation_id,
                        "dify_conversation_id": dify_conv_id,
                        "timestamp": datetime.now().isoformat(),
                        "raw_response": dify_logs
                    }, f, ensure_ascii=False, indent=2)
                print(f"[DEBUG] 原始响应已保存到: {debug_file}")
            except Exception as e:
                print(f"[WARN] 保存调试文件失败: {e}")
            
            # 调试：打印 Dify 返回的原始数据结构
            print(f"[DEBUG] Dify 返回的 keys: {dify_logs.keys() if dify_logs else 'None'}")
            if dify_logs and "data" in dify_logs:
                print(f"[DEBUG] data 字段类型: {type(dify_logs['data'])}")
                print(f"[DEBUG] data 长度: {len(dify_logs['data']) if isinstance(dify_logs['data'], list) else 'not a list'}")
                if isinstance(dify_logs['data'], list) and len(dify_logs['data']) > 0:
                    print(f"[DEBUG] 第一条数据的 keys: {dify_logs['data'][0].keys()}")
            
            # 解析 Dify 返回的消息
            messages = []
            if dify_logs and "data" in dify_logs:
                for idx, item in enumerate(dify_logs["data"]):
                    print(f"[DEBUG] 处理第 {idx} 条消息，keys: {item.keys()}")
                    
                    # Dify 返回的格式: query (用户) 和 answer (AI)
                    # 添加用户消息
                    if "query" in item and item["query"]:
                        messages.append({
                            "id": f"dify_user_{item.get('id', idx)}",
                            "conversation_id": conversation_id,
                            "role": "user",
                            "content": item["query"],
                            "image_url": None,  # Dify 日志中可能包含文件信息，暂不处理
                            "dify_message_id": item.get("id"),
                            "created_at": item.get("created_at", "")
                        })
                        print(f"[DEBUG] 添加用户消息: {item['query'][:50]}...")
                    
                    # 添加 AI 回复
                    if "answer" in item and item["answer"]:
                        messages.append({
                            "id": f"dify_assistant_{item.get('id', idx)}",
                            "conversation_id": conversation_id,
                            "role": "assistant",
                            "content": item["answer"],
                            "image_url": None,
                            "dify_message_id": item.get("id"),
                            "created_at": item.get("created_at", "")
                        })
                        print(f"[DEBUG] 添加 AI 消息: {item['answer'][:50]}...")
            
            # 按时间排序（从旧到新）
            messages.sort(key=lambda x: x.get("created_at", ""))
            
            print(f"[DEBUG] ========================================")
            print(f"[DEBUG] 从 Dify 获取到 {len(messages)} 条消息")
            print(f"[DEBUG] 返回的消息列表:")
            for msg in messages:
                print(f"[DEBUG]   - {msg['role']}: {msg['content'][:30]}... (id: {msg['id']})")
            print(f"[DEBUG] ========================================")
            
            return {
                "code": 0,
                "data": messages
            }
        
        except Exception as e:
            print(f"[ERROR] ========================================")
            print(f"[ERROR] 从 Dify 拉取历史失败: {e}")
            import traceback
            traceback.print_exc()
            print(f"[ERROR] ========================================")
            # 降级到本地存储
            pass
    
    # 否则从本地内存获取
    messages = memory_store.get_messages(conversation_id, limit=limit)
    
    # 转换datetime为字符串
    result = []
    for msg in messages:
        msg_data = msg.copy()
        if hasattr(msg_data["created_at"], "isoformat"):
            msg_data["created_at"] = msg_data["created_at"].isoformat()
        result.append(msg_data)
    
    return {
        "code": 0,
        "data": result
    }


@router.post("/conversations/{conversation_id}/messages")
async def send_message(conversation_id: str, data: MessageCreate, request: Request):
    """
    发送消息（流式响应）
    返回 SSE 格式的流式数据
    """
    conversation = memory_store.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    # 保存用户消息
    user_message = memory_store.create_message(
        conversation_id=conversation_id,
        role="user",
        content=data.content,
        image_url=data.image_url
    )
    
    # 准备文件列表（如果有图片）
    files = None
    if data.image_url:
        try:
            # 将本地图片上传到 Dify
            print(f"[DEBUG] 开始上传图片到 Dify: {data.image_url}")
            
            # 获取本地文件路径
            if data.image_url.startswith('/uploads/'):
                # 移除开头的 /
                local_path = data.image_url[1:]  # uploads/exam_qa/xxx.png
                full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', local_path)
                full_path = os.path.normpath(full_path)
                
                print(f"[DEBUG] 本地文件路径: {full_path}")
                
                if os.path.exists(full_path):
                    # 上传到 Dify
                    upload_result = await dify_service.upload_file(full_path)
                    print(f"[DEBUG] Dify 上传结果: {upload_result}")
                    
                    # 使用 Dify 返回的文件信息
                    if upload_result and "id" in upload_result:
                        files = [{
                            "type": "image",
                            "transfer_method": "local_file",
                            "upload_file_id": upload_result["id"]
                        }]
                    else:
                        print(f"[DEBUG] Dify 上传失败，结果: {upload_result}")
                else:
                    print(f"[DEBUG] 本地文件不存在: {full_path}")
            else:
                print(f"[DEBUG] 图片 URL 格式不支持: {data.image_url}")
        except Exception as e:
            print(f"[DEBUG] 上传图片到 Dify 失败: {str(e)}")
            # 如果上传失败，继续发送消息但不带图片
            files = None
    
    # 定义流式响应生成器
    async def event_generator():
        assistant_content = ""
        dify_conv_id = conversation.get("dify_conversation_id")
        dify_msg_id = None
        full_content = ""  # 累积完整内容
        
        try:
            # 调用 Dify API 流式对话
            async for chunk in dify_service.chat_streaming(
                query=data.content,
                conversation_id=dify_conv_id,
                files=files
            ):
                event = chunk.get("event")
                print(f"[DEBUG] 收到事件: {event}")
                
                # Workflow 开始 - 提取 conversation_id
                if event == "workflow_started":
                    dify_conv_id = chunk.get("conversation_id")
                    dify_msg_id = chunk.get("message_id")
                    print(f"[DEBUG] conversation_id: {dify_conv_id}, message_id: {dify_msg_id}")
                
                # 从所有事件中尝试提取 answer 字段并累积
                if "answer" in chunk:
                    content = chunk.get("answer", "")
                    if content and content.strip():  # 只累积非空内容
                        full_content += content
                        print(f"[DEBUG] 累积内容，当前长度: {len(full_content)}")
                
                elif "data" in chunk:
                    chunk_data = chunk.get("data", {})
                    if "answer" in chunk_data:
                        content = chunk_data.get("answer", "")
                        if content and content.strip():  # 只累积非空内容
                            full_content += content
                            print(f"[DEBUG] 累积内容，当前长度: {len(full_content)}")
                
                # Workflow 结束 - 处理并发送完整内容
                if event == "workflow_finished":
                    # 确保获取最终的 conversation_id
                    if chunk.get("conversation_id"):
                        dify_conv_id = chunk.get("conversation_id")
                    
                    # 如果累积的内容为空，尝试从 workflow_data 获取
                    if not full_content:
                        workflow_data = chunk.get("data", {})
                        final_outputs = workflow_data.get("outputs", {})
                        full_content = final_outputs.get("answer", "")
                    
                    # 处理完整内容
                    if full_content:
                        # 1. 转换 Dify 图片路径
                        full_content = convert_dify_image_urls(full_content)
                        
                        # 2. 清理多余的空行（将3个及以上连续换行压缩为2个）
                        full_content = re.sub(r'\n{3,}', '\n\n', full_content)
                        
                        print(f"[DEBUG] 处理后内容长度: {len(full_content)}")
                        assistant_content = full_content
                        
                        # 3. 一次性发送完整内容
                        yield f"data: {json.dumps({'type': 'content', 'content': full_content}, ensure_ascii=False)}\n\n"
                    
                    # 获取完整答案
                    workflow_data = chunk.get("data", {})
                    final_outputs = workflow_data.get("outputs", {})
                    final_answer = final_outputs.get("answer", "")
                    
                    print(f"[DEBUG] workflow_finished - full_content 长度: {len(full_content)}, final_answer 长度: {len(final_answer)}")
                    
                    # 保存 AI 回复消息
                    assistant_message = memory_store.create_message(
                        conversation_id=conversation_id,
                        role="assistant",
                        content=assistant_content,
                        dify_message_id=dify_msg_id
                    )
                    
                    # 更新对话的 dify_conversation_id
                    if dify_conv_id and not conversation.get("dify_conversation_id"):
                        memory_store.update_conversation(
                            conversation_id,
                            dify_conversation_id=dify_conv_id
                        )
                    
                    # 如果对话标题是"新对话"，自动生成标题
                    if conversation.get("title") == "新对话" and data.content:
                        title = data.content[:20] + ("..." if len(data.content) > 20 else "")
                        memory_store.update_conversation(conversation_id, title=title)
                    
                    print(f"[DEBUG] 发送 done 事件")
                    yield f"data: {json.dumps({'type': 'done', 'message_id': assistant_message['id']}, ensure_ascii=False)}\n\n"
                
                # 错误处理
                elif event == "error":
                    error_msg = chunk.get("message", "未知错误")
                    yield f"data: {json.dumps({'type': 'error', 'message': error_msg}, ensure_ascii=False)}\n\n"
        
        except Exception as e:
            error_msg = f"调用 Dify API 失败: {str(e)}"
            print(f"Error: {error_msg}")
            yield f"data: {json.dumps({'type': 'error', 'message': error_msg}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 Nginx 缓冲
            "Content-Type": "text/event-stream; charset=utf-8"
        }
    )


# ==================== 图片上传 ====================

@router.post("/upload", response_model=dict)
async def upload_image(file: UploadFile = File(...)):
    """上传图片"""
    # 检查文件类型
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="只支持 JPG、PNG、WEBP 格式的图片")
    
    # 创建上传目录
    upload_dir = "uploads/exam_qa"
    os.makedirs(upload_dir, exist_ok=True)
    
    # 生成唯一文件名
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(upload_dir, filename)
    
    # 保存文件
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # 返回文件URL
    file_url = f"/uploads/exam_qa/{filename}"
    
    return {
        "code": 0,
        "data": {
            "url": file_url,
            "filename": filename
        }
    }


# ==================== Dify 对话历史 ====================

@router.get("/dify/logs/{conversation_id}", response_model=dict)
async def get_dify_logs(conversation_id: str):
    """
    从 Dify 获取对话历史记录
    用于恢复对话或查看完整历史
    """
    conversation = memory_store.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    dify_conv_id = conversation.get("dify_conversation_id")
    if not dify_conv_id:
        return {
            "code": 0,
            "data": {
                "messages": [],
                "has_more": False
            }
        }
    
    try:
        logs = await dify_service.get_conversation_logs(dify_conv_id)
        return {
            "code": 0,
            "data": logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取 Dify 日志失败: {str(e)}")

