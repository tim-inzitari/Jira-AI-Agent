import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

from ..config.settings import Settings
from ..core.agent import JiraAgent, JiraError
from .routes import router
from ..utils.logging import setup_logging

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    # Initialize services
    setup_logging()
    settings = Settings()
    
    # Create FastAPI app
    app = FastAPI(
        title="Jira AI Agent",
        description="AI-powered Jira task management",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )
    
    # Configure middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Replace with settings.CORS_ORIGINS when implemented
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Static files and templates
    app.mount("/static", StaticFiles(directory="static"), name="static")
    app.templates = Jinja2Templates(directory="templates")
    
    # Initialize agent
    app.agent = JiraAgent(settings)
    
    # Register routes
    app.include_router(router, prefix="/api/v1", tags=["api"])
    
    # Add health check
    @app.get("/health", tags=["monitoring"])
    async def health_check():
        """Health check endpoint"""
        try:
            jira_status = await app.agent.check_jira_connection()
            llm_status = await app.agent.check_llm_connection()
            return {
                "status": "healthy",
                "services": {
                    "jira": "connected" if jira_status else "disconnected",
                    "llm": "connected" if llm_status else "disconnected"
                }
            }
        except Exception as e:
            logging.error(f"Health check failed: {str(e)}")
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "error": str(e)
                }
            )
    
    return app

# Create application instance
app = create_app()