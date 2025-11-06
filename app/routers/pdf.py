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
    logger.debug(f"Received PDF upload request: filename={file.filename}, content_type={file.content_type}")
    
    # Validate file type
    if not file.content_type or "pdf" not in file.content_type.lower():
        logger.warning(f"Invalid file type: {file.content_type}")
        raise HTTPException(
            status_code=400, 
            detail="Only PDF files are allowed"
        )
    
    try:
        # Read PDF file
        pdf_data = await file.read()
        logger.debug(f"Read PDF file, size: {len(pdf_data)} bytes")
        
        # Validate PDF
        if not pdf_service.validate_pdf(pdf_data):
            logger.error("PDF validation failed")
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF file"
            )
        
        # Generate unique file processing ID
        file_processing_id = str(uuid.uuid4())
        logger.debug(f"Generated file processing ID: {file_processing_id}")
        
        # Define paths in object storage (使用固定名称以便下载)
        pdf_path = f"{file_processing_id}/original.pdf"
        image_path = f"{file_processing_id}/first_page.png"
        logger.debug(f"Storage paths - PDF: {pdf_path}, Image: {image_path}")
        
        # Upload PDF to object storage
        logger.debug("Uploading PDF to storage...")
        pdf_uploaded = storage_service.upload_file(
            file_data=pdf_data,
            object_name=pdf_path,
            content_type="application/pdf"
        )
        
        if not pdf_uploaded:
            logger.error("Failed to upload PDF to storage")
            raise HTTPException(
                status_code=500,
                detail="Failed to upload PDF to storage"
            )
        
        logger.info(f"PDF uploaded successfully: {pdf_path}")
        
        # Extract first page as image
        logger.debug("Extracting first page as image...")
        try:
            image_data = pdf_service.extract_first_page_as_image(pdf_data)
            logger.debug(f"Image extracted, size: {len(image_data)} bytes")
        except Exception as e:
            logger.error(f"Failed to extract first page: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to extract first page: {str(e)}"
            )
        
        # Upload image to object storage
        logger.debug("Uploading image to storage...")
        image_uploaded = storage_service.upload_file(
            file_data=image_data,
            object_name=image_path,
            content_type="image/png"
        )
        
        if not image_uploaded:
            logger.error("Failed to upload image to storage")
            raise HTTPException(
                status_code=500,
                detail="Failed to upload image to storage"
            )
        
        logger.info(f"Image uploaded successfully: {image_path}")
        logger.info(f"PDF processing completed for ID: {file_processing_id}")
        
        return FileProcessingResponse(
            file_processing_id=file_processing_id,
            pdf_path=pdf_path,
            image_path=image_path,
            original_filename=file.filename,  # 保存原始文件名
            message="PDF processed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during PDF processing: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during processing: {str(e)}"
        )
    finally:
        await file.close()


@router.put("/upload", response_model=FileProcessingResponse)
async def upload_pdf_put(file: UploadFile = File(...)):
    """
    Upload a PDF file using PUT method (idempotent operation).
    Same functionality as POST /upload - creates a new processing ID each time.
    
    Args:
        file: PDF file to upload
        
    Returns:
        FileProcessingResponse with file processing ID and paths
    """
    # Reuse the same logic as POST upload
    return await upload_pdf(file)


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "PDF Processing API"}


@router.get("/files/{processing_id}/pdf")
async def get_original_pdf(processing_id: str, filename: str = None):
    """
    下载原始 PDF 文件（带缓存）
    
    Args:
        processing_id: 文件处理 ID
        filename: 可选的原始文件名（用于下载时的文件名）
        
    Returns:
        PDF 文件流，优先从缓存读取
    """
    try:
        file_path = f"{processing_id}/original.pdf"
        
        # 如果没有提供文件名，使用默认文件名
        download_filename = filename if filename else f"{processing_id}.pdf"
        logger.debug(f"Download filename: {download_filename}")
        
        # 1. 尝试从缓存获取
        cached_file = cache_service.get(file_path, extension=".pdf")
        if cached_file:
            logger.info(f"Serving PDF from cache: {processing_id}")
            return FileResponse(
                cached_file,
                media_type="application/pdf",
                filename=download_filename
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
            filename=download_filename
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
