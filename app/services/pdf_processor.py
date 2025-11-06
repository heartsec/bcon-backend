import io
import fitz  # PyMuPDF
from PIL import Image


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
        
        if pdf_document.page_count == 0:
            pdf_document.close()
            raise ValueError("PDF document has no pages")
        
        # Get first page
        first_page = pdf_document[0]
        
        # Calculate zoom factor from DPI (default is 72 DPI)
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)
        
        # Render page to pixmap
        pix = first_page.get_pixmap(matrix=mat)
        
        # Convert pixmap to PNG bytes
        png_data = pix.tobytes("png")
        
        pdf_document.close()
        
        return png_data
    
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
            
            # Try to open the PDF to verify it's valid
            pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
            page_count = pdf_document.page_count
            pdf_document.close()
            
            return page_count > 0
        except Exception:
            return False


# Singleton instance
pdf_service = PDFProcessingService()
