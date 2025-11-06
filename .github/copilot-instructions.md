# FastAPI PDF Processing Backend

## Project Requirements
- FastAPI backend with PDF upload functionality
- Generate unique file processing IDs for each upload
- Store PDFs in RustFS object storage (S3-compatible)
- Extract first page of PDF as PNG image
- Save extracted image to object storage under file processing ID path

## Progress Checklist

- [x] Verify that the copilot-instructions.md file in the .github directory is created.
- [x] Get project setup information
- [x] Scaffold the Project
- [x] Customize the Project
- [x] Install Required Extensions
- [x] Compile the Project
- [x] Create and Run Task
- [x] Launch the Project
- [x] Ensure Documentation is Complete

## Project Complete

The FastAPI backend project has been successfully created and migrated to RustFS with the following structure:

### Core Files Created:
- `main.py` - FastAPI application entry point
- `app/config.py` - Configuration management with RustFS environment variables
- `app/routers/pdf.py` - PDF upload endpoint
- `app/services/storage.py` - RustFS object storage service (boto3 SDK)
- `app/services/pdf_processor.py` - PDF processing and image extraction
- `app/models/schemas.py` - Pydantic response models
- `requirements.txt` - Python dependencies (now using boto3)
- `.env.example` - RustFS configuration template
- `README.md` - Complete documentation with RustFS setup

### Changes Made for RustFS:
- Replaced `minio` package with `boto3` (AWS S3 SDK)
- Updated configuration to use RustFS endpoints and credentials
- Modified storage service to use boto3 client with S3v4 signature
- Added presigned URL generation support
- Updated all documentation to reference RustFS

### Changes Made for Linux Compatibility:
- Replaced `PyMuPDF` with `pdf2image` (no compilation issues on Linux)
- Added `poppler-utils` as system dependency requirement
- Created `Dockerfile` with poppler-utils pre-installed
- Updated README with Linux-specific installation instructions
- Added Docker and Docker Compose deployment options

### Next Steps:
1. Create a Python virtual environment: `python -m venv venv`
2. Activate it: `.\venv\Scripts\Activate.ps1`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and configure RustFS credentials
5. Run the server: `python main.py` or `uvicorn main:app --reload`
6. Access API docs at: http://localhost:8000/docs

### RustFS Resources:
- Documentation: https://docs.rustfs.com/zh/
- Python SDK: https://docs.rustfs.com/zh/developer/sdk/python.html
