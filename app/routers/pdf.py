import uuid
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from app.models.schemas import FileProcessingResponse
from app.services.storage import storage_service
from app.services.pdf_processor import pdf_service
from app.services.cache import cache_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/pdf", tags=["PDF Processing"])


@router.post("/upload", response_model=FileProcessingResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file, extract the first page as an image, and save both to object storage.
    
    Args:
        file: PDF file to upload
        
    Returns:
        FileProcessingResponse with file processing ID and paths
    """
    # Validate file type
    if not file.content_type or "pdf" not in file.content_type.lower():
        raise HTTPException(
            status_code=400, 
            detail="Only PDF files are allowed"
        )
    
    try:
        # Read PDF file
        pdf_data = await file.read()
        
        # Validate PDF
        if not pdf_service.validate_pdf(pdf_data):
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF file"
            )
        
        # Generate unique file processing ID
        file_processing_id = str(uuid.uuid4())
        
        # Define paths in object storage
        pdf_path = f"{file_processing_id}/{file.filename}"
        image_path = f"{file_processing_id}/first_page.png"
        
        # Upload PDF to object storage
        pdf_uploaded = storage_service.upload_file(
            file_data=pdf_data,
            object_name=pdf_path,
            content_type="application/pdf"
        )
        
        if not pdf_uploaded:
            raise HTTPException(
                status_code=500,
                detail="Failed to upload PDF to storage"
            )
        
        # Extract first page as image
        try:
            image_data = pdf_service.extract_first_page_as_image(pdf_data)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to extract first page: {str(e)}"
            )
        
        # Upload image to object storage
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
        
        return FileProcessingResponse(
            file_processing_id=file_processing_id,
            pdf_path=pdf_path,
            image_path=image_path,
            message="PDF processed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during processing: {str(e)}"
        )
    finally:
        await file.close()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "PDF Processing API"}


@router.get("/files/{processing_id}/pdf")
async def get_original_pdf(processing_id: str):
    """
    下载原始 PDF 文件（带缓存）
    
    Args:
        processing_id: 文件处理 ID
        
    Returns:
        PDF 文件流，优先从缓存读取
    """
    try:
        file_path = f"{processing_id}/original.pdf"
        
        # 1. 尝试从缓存获取
        cached_file = cache_service.get(file_path, extension=".pdf")
        if cached_file:
            logger.info(f"Serving PDF from cache: {processing_id}")
            return FileResponse(
                cached_file,
                media_type="application/pdf",
                filename=f"{processing_id}.pdf"
            )
        
        # 2. 从 RustFS 下载
        logger.info(f"Downloading PDF from RustFS: {processing_id}")
        file_data = storage_service.download_file(file_path)
        
        if not file_data:
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        # 3. 写入缓存
        cached_file = cache_service.put(file_path, file_data, extension=".pdf")
        
        # 4. 返回文件
        return FileResponse(
            cached_file,
            media_type="application/pdf",
            filename=f"{processing_id}.pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get PDF: {str(e)}")


@router.get("/files/{processing_id}/preview")
async def get_preview_image(processing_id: str):
    """
    下载首页预览图（带缓存）
    
    Args:
        processing_id: 文件处理 ID
        
    Returns:
        PNG 图片流，优先从缓存读取
    """
    try:
        file_path = f"{processing_id}/first_page.png"
        
        # 1. 尝试从缓存获取
        cached_file = cache_service.get(file_path, extension=".png")
        if cached_file:
            logger.info(f"Serving preview from cache: {processing_id}")
            return FileResponse(
                cached_file,
                media_type="image/png",
                filename=f"{processing_id}_preview.png"
            )
        
        # 2. 从 RustFS 下载
        logger.info(f"Downloading preview from RustFS: {processing_id}")
        file_data = storage_service.download_file(file_path)
        
        if not file_data:
            raise HTTPException(status_code=404, detail="Preview image not found")
        
        # 3. 写入缓存
        cached_file = cache_service.put(file_path, file_data, extension=".png")
        
        # 4. 返回文件
        return FileResponse(
            cached_file,
            media_type="image/png",
            filename=f"{processing_id}_preview.png"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading preview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get preview: {str(e)}")


@router.get("/files/{processing_id}")
async def get_file_info(processing_id: str):
    """
    获取处理 ID 下的所有文件信息
    
    Args:
        processing_id: 文件处理 ID
        
    Returns:
        文件的下载端点和可用性信息
    """
    try:
        pdf_path = f"{processing_id}/original.pdf"
        preview_path = f"{processing_id}/first_page.png"
        
        pdf_exists = storage_service.file_exists(pdf_path)
        preview_exists = storage_service.file_exists(preview_path)
        
        if not pdf_exists and not preview_exists:
            raise HTTPException(status_code=404, detail="No files found for this processing ID")
        
        result = {
            "processing_id": processing_id,
            "files": {}
        }
        
        if pdf_exists:
            result["files"]["pdf"] = {
                "download_url": f"/api/pdf/files/{processing_id}/pdf",
                "available": True
            }
        
        if preview_exists:
            result["files"]["preview"] = {
                "download_url": f"/api/pdf/files/{processing_id}/preview",
                "available": True
            }
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get file info: {str(e)}")


@router.get("/cache/stats")
async def get_cache_stats():
    """
    获取缓存统计信息
    
    Returns:
        缓存使用情况统计
    """
    return cache_service.get_stats()


@router.post("/cache/clear")
async def clear_cache():
    """
    清空所有缓存
    
    Returns:
        操作结果
    """
    try:
        cache_service.clear()
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")
