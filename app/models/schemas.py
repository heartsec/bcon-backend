from pydantic import BaseModel
from typing import Optional, Any, Dict


class FileProcessingResponse(BaseModel):
    """Response model for file processing"""
    file_processing_id: str
    pdf_path: str
    image_path: str
    original_filename: str  # 原始文件名
    message: str


class DifyProcessResponse(BaseModel):
    """Response model for Dify document processing"""
    success: bool
    answer: Optional[str] = None
    confirmation_record: Optional[Any] = None
    conversation_id: Optional[str] = None
    message_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[int] = None
    error: Optional[str] = None
