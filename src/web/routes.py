from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, List, Optional
from pydantic import BaseModel
import logging

from ..config.settings import Settings
from ..core.agent import JiraAgent
from ..core.schemas import CommandResponseSchema
from .dependencies import get_agent

# Initialize router, logging, and templates
router = APIRouter()
logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="templates")

class CommandRequest(BaseModel):
    """Command request schema"""
    command: str
    project: Optional[str] = None
    dry_run: bool = False

    class Config:
        schema_extra = {
            "example": {
                "command": "Create a bug ticket for the login page",
                "project": "PROJ",
                "dry_run": False
            }
        }

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the chatbot interface as the default home page."""
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/api/v1/commands")
async def process_command(
    request: CommandRequest,
    agent: JiraAgent = Depends(get_agent)
) -> Dict:
    """Process a natural language command"""
    try:
        result = await agent.process_command(
            command=request.command,
            project=request.project,
            dry_run=request.dry_run
        )
        return {
            "success": True,
            "message": result.message if hasattr(result, 'message') else str(result),
            "actions": result.actions if hasattr(result, 'actions') else []
        }
    except Exception as e:
        logger.error(f"Command processing failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Command processing failed: {str(e)}"
        )

@router.get("/api/v1/projects")
async def list_projects(
    agent: JiraAgent = Depends(get_agent)
) -> List[Dict]:
    """Get list of available Jira projects"""
    try:
        projects = await agent.get_projects()
        # Projects are already in dictionary format from the agent
        return projects
    except Exception as e:
        logger.error(f"Failed to fetch projects: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch projects: {str(e)}"
        )

@router.get("/health")
async def health_check(
    agent: JiraAgent = Depends(get_agent)
) -> Dict:
    """Health check endpoint""" 
    jira_ok = await agent.check_jira_connection()
    llm_ok = await agent.check_llm_connection()
    
    return {
        "status": "healthy",
        "jira": "connected" if jira_ok else "disconnected",
        "llm": "connected" if llm_ok else "disconnected"
    }

@router.get("/status")
async def service_status(
    agent: JiraAgent = Depends(get_agent)
) -> Dict:
    """Get detailed service status"""
    jira_ok = await agent.check_jira_connection()
    llm_ok = await agent.check_llm_connection()
    
    return {
        "status": "operational",
        "jira": "connected" if jira_ok else "disconnected",
        "llm": "connected" if llm_ok else "disconnected",
        "version": "1.0.0",
        "environment": Settings().env if hasattr(Settings(), 'env') else "production"
    }