"""
FastAPI main application entry point.

This module can be mounted into a larger FastAPI application:
    from src.api.routes import router as ml_router
    app.include_router(ml_router, prefix="/ml")
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .config import get_settings
from .api.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="Toptama/Birge ML API",
        description="Transparent recommendation/ranking layer for marketplace deals",
        version="hackathon-v1",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include ML router
    app.include_router(router)
    
    # Startup event
    @app.on_event("startup")
    async def startup_event():
        settings = get_settings()
        logger.info(f"Starting ML API server (demo_mode={settings.is_demo_mode})")
    
    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down ML API server")
    
    return app


# Create app instance for uvicorn
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
