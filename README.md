# PDF Processing Backend

FastAPI backend for PDF upload, RustFS object storage, and first-page image extraction.

## Features

- **PDF Upload**: Upload PDF files with automatic validation
- **Unique Processing ID**: Each upload generates a unique file processing ID
- **RustFS Object Storage**: Store PDFs in RustFS (S3-compatible) object storage
- **Image Extraction**: Extract first page of PDF as PNG image
- **Organized Storage**: Files are stored under their processing ID path

## Project Structure

```
bcon-backend/
├── app/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py         # Pydantic models
│   ├── routers/
│   │   ├── __init__.py
│   │   └── pdf.py             # PDF upload endpoints
│   └── services/
│       ├── __init__.py
│       ├── storage.py         # Object storage service
│       └── pdf_processor.py   # PDF processing service
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## Prerequisites

- Python 3.8+
- RustFS server (S3-compatible object storage)
- **Poppler-utils** (required for PDF processing)

### Installing Poppler on Linux

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y poppler-utils
```

**CentOS/RHEL/Rocky Linux:**
```bash
sudo yum install -y poppler-utils
```

**Arch Linux:**
```bash
sudo pacman -S poppler
```

**Alpine Linux (Docker):**
```bash
apk add --no-cache poppler-utils
```

### Verify Installation
```bash
pdftoppm -v
```

## Setup Instructions

### 1. Install System Dependencies (Linux)

First, install poppler-utils:

**Ubuntu/Debian:**
```bash
sudo apt-get update && sudo apt-get install -y poppler-utils
```

**CentOS/RHEL:**
```bash
sudo yum install -y poppler-utils
```

### 2. Create Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env` and update the values:

**Linux/macOS:**
```bash
cp .env.example .env
```

**Windows:**
```powershell
Copy-Item .env.example .env
```

Edit `.env` with your RustFS credentials:

```env
RUSTFS_ENDPOINT=http://192.168.1.100:9000
RUSTFS_ACCESS_KEY=rustfsadmin
RUSTFS_SECRET_KEY=rustfssecret
RUSTFS_BUCKET_NAME=pdf-processing
RUSTFS_REGION=us-east-1

APP_HOST=0.0.0.0
APP_PORT=8000
```

### 5. Start RustFS (if needed)

Refer to RustFS documentation for installation:
- Linux: https://docs.rustfs.com/zh/installation/linux/
- Windows: https://docs.rustfs.com/zh/installation/windows/
- Docker: https://docs.rustfs.com/zh/installation/docker/

Or use Docker for quick setup:

```powershell
docker run -p 9000:9000 -p 9001:9001 `
  -e "RUSTFS_ROOT_USER=rustfsadmin" `
  -e "RUSTFS_ROOT_PASSWORD=rustfssecret" `
  rustfs/rustfs server /data --console-address ":9001"
```

Access RustFS Console at: http://localhost:9001

## Running the Application

### Development Mode

**Linux/macOS:**
```bash
python3 main.py
```

**Windows:**
```powershell
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode (Docker)

Build and run using Docker:

```bash
# Build image
docker build -t bcon-backend .

# Run container
docker run -d \
  --name bcon-backend \
  -p 8000:8000 \
  --env-file .env \
  bcon-backend
```

Or use Docker Compose (create `docker-compose.yml`):

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped
```

Then run:
```bash
docker-compose up -d
```

### Access the API

- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/api/pdf/health

## API Endpoints

### POST /api/pdf/upload

Upload a PDF file for processing.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `file` (PDF file)

**Response:**
```json
{
  "file_processing_id": "uuid-string",
  "pdf_path": "uuid-string/filename.pdf",
  "image_path": "uuid-string/first_page.png",
  "message": "PDF processed successfully"
}
```

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/api/pdf/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/document.pdf"
```

### GET /api/pdf/health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "PDF Processing API"
}
```

## File Storage Structure

Files are stored in object storage with the following structure:

```
{bucket_name}/
└── {file_processing_id}/
    ├── {original_filename}.pdf
    └── first_page.png
```

Example:
```
pdf-processing/
└── 123e4567-e89b-12d3-a456-426614174000/
    ├── document.pdf
    └── first_page.png
```

## Dependencies

- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **pdf2image**: PDF to image conversion (requires poppler-utils)
- **Pillow**: Image processing
- **Boto3**: AWS S3 SDK (RustFS compatible)
- **Pydantic**: Data validation
- **python-multipart**: File upload support

**System Dependencies:**
- **poppler-utils**: Required by pdf2image for PDF rendering

## Development

### Install Development Dependencies

```powershell
pip install pytest pytest-asyncio httpx
```

### Running Tests

```powershell
pytest
```

## Error Handling

The API includes comprehensive error handling:
- Invalid file type validation
- PDF validation
- Storage upload failures
- Image extraction errors

All errors return appropriate HTTP status codes with descriptive messages.

## Production Considerations

1. **CORS**: Update CORS settings in `main.py` for production
2. **Environment**: Use proper `.env` file with secure credentials
3. **Storage**: Configure production RustFS credentials
4. **HTTPS**: Enable SSL/TLS for RustFS endpoints
5. **Authentication**: Add authentication middleware for production use
6. **RustFS Features**: Consider using RustFS advanced features like versioning, encryption, lifecycle management

## Additional Resources

- [RustFS Documentation](https://docs.rustfs.com/zh/)
- [RustFS Python SDK Guide](https://docs.rustfs.com/zh/developer/sdk/python.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## License

This project is for internal use.
