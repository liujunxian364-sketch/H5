from fastapi import APIRouter, Query, UploadFile, File, Form
from typing import Optional, List
import uuid
import os
from datetime import datetime
import json

router = APIRouter()

# 科目列表
SUBJECTS = ["语文", "数学", "英语", "物理", "化学", "生物", "历史", "地理", "政治"]

# 存储错题数据（实际项目中应使用数据库）
error_questions_db = []
error_id_counter = 1

# 创建上传目录
UPLOAD_DIR = "uploads/error_questions"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def mock_ocr_recognition(image_data: bytes, crop_data: Optional[dict] = None) -> List[str]:
    """
    模拟OCR识别和知识点提取
    实际项目中应调用大模型API进行OCR识别和知识点提取
    """
    # 这里返回模拟的知识点
    mock_knowledge_points = [
        "二次函数",
        "函数图像",
        "最值问题"
    ]
    return mock_knowledge_points

@router.get("/subjects")
async def get_subjects():
    """获取所有科目列表"""
    return {
        "code": 0,
        "message": "success",
        "data": SUBJECTS
    }

@router.post("/upload")
async def upload_error_question(
    file: UploadFile = File(...),
    subject: str = Form(...),
    crop_data: Optional[str] = Form(None)  # JSON字符串格式的裁剪数据
):
    """
    上传错题图片
    - 接收图片文件和科目
    - 可选：裁剪区域数据
    - 调用OCR识别知识点
    """
    global error_id_counter
    
    try:
        # 保存上传的图片
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        file_name = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, file_name)
        
        # 读取文件内容
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # 构建图片URL（实际项目中应使用OSS或CDN）
        image_url = f"/uploads/error_questions/{file_name}"
        
        # 解析裁剪数据
        crop_data_dict = None
        if crop_data:
            try:
                crop_data_dict = json.loads(crop_data)
            except:
                pass
        
        # 调用OCR识别知识点（这里使用模拟数据）
        knowledge_points = await mock_ocr_recognition(contents, crop_data_dict)
        
        # 创建错题记录
        error_question = {
            "id": error_id_counter,
            "image_url": image_url,
            "image_crop_data": crop_data_dict,
            "subject": subject,
            "knowledge_points": knowledge_points,
            "createTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        error_questions_db.append(error_question)
        error_id_counter += 1
        
        return {
            "code": 0,
            "message": "success",
            "data": error_question
        }
    except Exception as e:
        return {
            "code": 500,
            "message": f"上传失败: {str(e)}",
            "data": None
        }

@router.get("")
async def get_error_list(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=50),
    subject: Optional[str] = Query(None)
):
    """获取错题列表，支持科目筛选"""
    # 按科目筛选
    data = error_questions_db.copy()
    if subject:
        data = [e for e in data if e["subject"] == subject]
    
    # 按创建时间倒序排序
    data.sort(key=lambda x: x["createTime"], reverse=True)
    
    # 分页
    start = (page - 1) * pageSize
    end = start + pageSize
    paginated_data = data[start:end]
    
    return {
        "code": 0,
        "message": "success",
        "data": paginated_data,
        "total": len(data)
    }

@router.get("/{error_id}")
async def get_error_detail(error_id: int):
    """获取错题详情"""
    for error in error_questions_db:
        if error["id"] == error_id:
            return {
                "code": 0,
                "message": "success",
                "data": error
            }
    return {
        "code": 404,
        "message": "错题不存在",
        "data": None
    }

@router.delete("/{error_id}")
async def delete_error_question(error_id: int):
    """删除错题"""
    global error_questions_db
    for i, error in enumerate(error_questions_db):
        if error["id"] == error_id:
            # 删除图片文件
            image_path = error.get("image_url", "").replace("/uploads/error_questions/", "")
            if image_path:
                try:
                    full_path = os.path.join(UPLOAD_DIR, image_path)
                    if os.path.exists(full_path):
                        os.remove(full_path)
                except:
                    pass
            
            error_questions_db.pop(i)
            return {
                "code": 0,
                "message": "删除成功",
                "data": None
            }
    return {
        "code": 404,
        "message": "错题不存在",
        "data": None
    }

@router.get("/report/{subject}")
async def get_error_report(subject: str):
    """
    获取指定科目的错题报告
    实际项目中应调用工作流生成报告
    """
    # 筛选该科目的错题
    subject_errors = [e for e in error_questions_db if e["subject"] == subject]
    
    if not subject_errors:
        return {
            "code": 404,
            "message": "该科目暂无错题数据",
            "data": None
        }
    
    # 统计知识点
    knowledge_point_count = {}
    for error in subject_errors:
        for kp in error.get("knowledge_points", []):
            knowledge_point_count[kp] = knowledge_point_count.get(kp, 0) + 1
    
    # 按出现次数排序
    knowledge_points_list = [
        {"name": kp, "count": count}
        for kp, count in sorted(knowledge_point_count.items(), key=lambda x: x[1], reverse=True)
    ]
    
    # 生成分析报告（这里使用模拟数据，实际应调用大模型API）
    analysis = f"""
    根据您的{subject}错题分析：
    
    1. 错题总数：{len(subject_errors)}道
    
    2. 知识点分布：
    """
    for kp_data in knowledge_points_list[:5]:  # 前5个高频知识点
        analysis += f"   - {kp_data['name']}：{kp_data['count']}次\n"
    
    analysis += f"""
    
    3. 学习建议：
       - 重点关注高频知识点：{knowledge_points_list[0]['name'] if knowledge_points_list else '无'}
       - 建议加强练习相关题型
       - 定期复习已掌握的错题
    
    （注：此报告为模拟数据，实际报告由大模型工作流生成）
    """
    
    report = {
        "subject": subject,
        "total_count": len(subject_errors),
        "knowledge_points": knowledge_points_list,
        "analysis": analysis,
        "createTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return {
        "code": 0,
        "message": "success",
        "data": report
    }
