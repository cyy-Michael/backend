from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, List
import shutil
import tempfile
import os
from app.services.resume_service import resume_service
from app.utils.logger import app_logger as logger

router = APIRouter()

@router.post("/upload", response_model=Dict[str, List[str]])
async def upload_resume(file: UploadFile = File(...)):
    """
    上传简历并进行智能分析
    目前支持 PDF 和图片格式
    """
    if not file:
        raise HTTPException(status_code=400, detail="未上传文件")
    
    # 检查文件类型
    allowed_types = ["application/pdf", "image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="仅支持 PDF 或图片格式 (JPG/PNG)")
    
    try:
        content = await file.read()
        
        # 如果是 PDF
        if file.content_type == "application/pdf":
             pass # 继续向下处理

        # 1. 内容提取
        text = ""
        
        if file.content_type == "application/pdf":
            # PDF 处理：转图片后 OCR
            try:
                text = await resume_service.extract_text_from_pdf(content)
            except Exception as e:
                logger.error(f"PDF extract failed: {e}")
                raise HTTPException(status_code=400, detail="PDF 解析失败，请尝试上传图片")
                
        elif file.content_type.startswith("image/"):
            # 图片处理：直接 OCR
            text = await resume_service.extract_text_from_image(content)
            
        if not text:
             raise HTTPException(status_code=400, detail="未能识别到文字，请确保文件清晰")

        # 2. LLM 分析
        result = await resume_service.analyze_resume_text(text)
        
        return result

    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")
