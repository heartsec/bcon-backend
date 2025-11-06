from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import pdf
from app.config import settings

# Create FastAPI app
app = FastAPI(
    title="PDF Processing Backend",
    description="FastAPI backend for PDF upload, storage, and first-page extraction",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(pdf.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PDF Processing Backend API",
        "docs": "/docs",
        "health": "/api/pdf/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True
    )
