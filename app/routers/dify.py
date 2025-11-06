"""Dify completion workflow endpoints"""
from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from app.models.schemas import DifyProcessResponse
from app.services.dify_service import dify_service
from app.services.storage import storage_service
from app.services.pdf_processor import pdf_service
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dify", tags=["dify"])


@router.post("/process-document", response_model=DifyProcessResponse)
async def process_document(
    file: UploadFile = File(..., description="PDF file to process"),
    user_id: str = Form(default="default-user", description="User identifier")
):
    """
    上传 PDF 文件，自动提取首页图片并使用 Dify 处理
    
    - **file**: PDF 文件 (必需)
    - **user_id**: 用户标识符 (可选，默认: "default-user")
    
    Returns the completion response and confirmation_record variable
    """
    try:
        # 1. 验证文件类型
        if not file.content_type or "pdf" not in file.content_type.lower():
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed"
            )
        
        logger.info(f"Processing PDF file: {file.filename}")
        
        # 2. 读取 PDF 文件
        pdf_data = await file.read()
        
        # 3. 验证 PDF
        if not pdf_service.validate_pdf(pdf_data):
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF file"
            )
        
        # 4. 生成唯一 ID
        file_processing_id = str(uuid.uuid4())
        
        # 5. 提取首页为图片
        logger.info(f"Extracting first page as image for: {file_processing_id}")
        try:
            image_data = pdf_service.extract_first_page_as_image(pdf_data)
        except Exception as e:
            logger.error(f"Failed to extract first page: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to extract first page: {str(e)}"
            )
        
        # 6. 上传图片到对象存储
        image_path = f"{file_processing_id}/first_page.png"
        image_uploaded = storage_service.upload_file(
            file_data=image_data,
            object_name=image_path,
            content_type="image/png"
        )
        
        if not image_uploaded:
            raise HTTPException(
                status_code=500,
                detail="Failed to upload image to storage"
            )
        
        # 7. 生成预览图片的公开 URL（使用 presigned URL）
        preview_url = storage_service.generate_presigned_url(
            object_name=image_path,
            expiration=3600  # 1小时有效期
        )
        
        if not preview_url:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate preview URL"
            )
        
        logger.info(f"Generated preview URL: {preview_url}")
        
        # 8. 调用 Dify 处理
        logger.info(f"Sending to Dify for analysis")
        result = await dify_service.process_document(
            preview_url=preview_url,
            user_id=user_id
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Dify processing failed: {result.get('error', 'Unknown error')}"
            )
        
        logger.info(f"Dify processing completed for: {file_processing_id}")
        
        return DifyProcessResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in process_document endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await file.close()

