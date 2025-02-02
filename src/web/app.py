import logging
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

from ..config.settings import Settings
from ..core.agent import JiraAgent, JiraError
from .routes import router
from ..utils.logging import setup_logging
from .dependencies import get_agent

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
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Static files and templates
    app.mount("/static", StaticFiles(directory="static"), name="static")
    templates = Jinja2Templates(directory="templates")
    app.state.templates = templates  # Make templates available to routes
    
    # Initialize agent
    app.agent = JiraAgent(settings)
    
    # Register routes
    app.include_router(router)  # Remove the prefix to allow root route handling
    
    # Add health check
    @app.get("/health", tags=["monitoring"])
    async def health_check(agent: JiraAgent = Depends(get_agent)):
        """Health check endpoint"""
        try:
            jira_status = await agent.check_jira_connection()
            llm_status = await agent.check_llm_connection()
            if not (jira_status and llm_status):
                return JSONResponse(
                    status_code=503,
                    content={
                        "status": "unhealthy",
                        "jira": "connected" if jira_status else "disconnected",
                        "llm": "connected" if llm_status else "disconnected"
                    }
                )
            return {
                "status": "healthy",
                "jira": "connected",
                "llm": "connected"
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
    
    @app.options("/")
    async def cors_preflight():
        """Handle CORS preflight requests"""
        return JSONResponse(
            content={},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*"
            }
        )
        
    return app

# Create application instance
app = create_app()