"""
Base API router for the Physical AI & Humanoid Robotics textbook platform.
This module defines the main API router and includes all sub-routers.
"""
from fastapi import APIRouter
from . import auth, rag, translation


# Create the main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(rag.router, prefix="/rag", tags=["rag"])
api_router.include_router(translation.router, prefix="/translation", tags=["translation"])


# Health check endpoint
@api_router.get("/health")
async def health_check():
    """
    Health check endpoint to verify API is running.
    """
    return {"status": "healthy", "service": "Physical AI & Humanoid Robotics Textbook API"}


# Root endpoint
@api_router.get("/")
async def root():
    """
    Root endpoint for the API.
    """
    return {
        "message": "Welcome to the Physical AI & Humanoid Robotics Textbook API",
        "version": "1.0.0",
        "endpoints": [
            "/auth - Authentication endpoints",
            "/rag - RAG system endpoints",
            "/translation - Translation endpoints",
            "/health - Health check"
        ]
    }