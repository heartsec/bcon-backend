import io
import fitz  # PyMuPDF
from PIL import Image
from typing import Tuple


class PDFProcessingService:
    """Service for PDF processing operations"""
    
    @staticmethod
    def extract_first_page_as_image(pdf_data: bytes, dpi: int = 150) -> bytes:
        """
        Extract the first page of a PDF as a PNG image
        
        Args:
            pdf_data: PDF file content as bytes
            dpi: Resolution for the image (default: 150)
            
        Returns:
            PNG image data as bytes
        """
        # Open PDF from bytes
        pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
        
        try:
            # Get first page
            first_page = pdf_document[0]
            
            # Convert to pixmap (image)
            # Calculate zoom factor based on DPI (default is 72 DPI)
            zoom = dpi / 72
            matrix = fitz.Matrix(zoom, zoom)
            pixmap = first_page.get_pixmap(matrix=matrix)
            
            # Convert pixmap to PIL Image
            img_data = pixmap.tobytes("png")
            
            return img_data
            
        finally:
            pdf_document.close()
    
    @staticmethod
    def validate_pdf(pdf_data: bytes) -> bool:
        """
        Validate if the file is a valid PDF
        
        Args:
            pdf_data: PDF file content as bytes
            
        Returns:
            True if valid PDF, False otherwise
        """
        try:
            pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
            page_count = pdf_document.page_count
            pdf_document.close()
            return page_count > 0
        except Exception:
            return False


# Singleton instance
pdf_service = PDFProcessingService()
