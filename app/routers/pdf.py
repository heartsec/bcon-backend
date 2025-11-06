import uuid
from fastapi import APIRouter, File, UploadFile, HTTPException
from app.models.schemas import FileProcessingResponse
from app.services.storage import storage_service
from app.services.pdf_processor import pdf_service


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
