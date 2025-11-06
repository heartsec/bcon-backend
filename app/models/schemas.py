from pydantic import BaseModel


class FileProcessingResponse(BaseModel):
    """Response model for file processing"""
    file_processing_id: str
    pdf_path: str
    image_path: str
    original_filename: str  # 原始文件名
    message: str
