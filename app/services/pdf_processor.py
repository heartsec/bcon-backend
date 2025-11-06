import io
from pdf2image import convert_from_bytes
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
        # Convert first page of PDF to image
        images = convert_from_bytes(
            pdf_data,
            dpi=dpi,
            first_page=1,
            last_page=1
        )
        
        if not images:
            raise ValueError("Failed to extract first page from PDF")
        
        first_page_image = images[0]
        
        # Convert PIL Image to bytes
        img_byte_arr = io.BytesIO()
        first_page_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return img_byte_arr.read()
    
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
            # Try to read the PDF header
            if pdf_data[:4] != b'%PDF':
                return False
            
            # Try to convert first page to verify it's a valid PDF
            images = convert_from_bytes(
                pdf_data,
                dpi=72,
                first_page=1,
                last_page=1
            )
            return len(images) > 0
        except Exception:
            return False


# Singleton instance
pdf_service = PDFProcessingService()
