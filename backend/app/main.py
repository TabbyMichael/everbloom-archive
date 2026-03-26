from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api import life_events_router, gallery_router, tributes_router
from app.db.database import engine
from app.models import Base
import os

# Create database tables
Base.metadata.create_all(bind=engine)

# Create uploads directory
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="Everbloom Archive API",
    description="A digital archive for celebrating life and memories",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include routers
app.include_router(life_events_router)
app.include_router(gallery_router)
app.include_router(tributes_router)

@app.get("/")
def read_root():
    return {
        "message": "Everbloom Archive API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "life_events": "/life-events",
            "gallery": "/gallery",
            "tributes": "/tributes"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
