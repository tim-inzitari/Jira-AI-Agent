from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, List, Optional
from pydantic import BaseModel
import logging

from ..config.settings import Settings
from ..core.agent import JiraAgent
from ..core.schemas import CommandResponseSchema
from .dependencies import get_agent

# Initialize router and logging
router = APIRouter()
logger = logging.getLogger(__name__)

class CommandRequest(BaseModel):
    """Command request schema"""
    command: str
    project: Optional[str] = None
    dry_run: bool = False

    class Config:
        schema_extra = {
            "example": {
                "command": "Create a bug ticket for login page",
                "project": "PROJ",
                "dry_run": False
            }
        }

class ProjectResponse(BaseModel):
    """Project response schema"""
    key: str
    name: str
    description: Optional[str] = None

@router.post("/command", response_model=CommandResponseSchema)
async def process_command(
    request: CommandRequest,
    agent: JiraAgent = Depends(get_agent)
) -> Dict:
    """Process natural language command"""
    if not request.command.strip():
        raise HTTPException(status_code=422, detail="Command cannot be empty")
    logger.info(f"Processing command: {request.command}")
    try:
        result = await agent.process_command(
            command=request.command,
            project=request.project,
            dry_run=request.dry_run
        )
        return CommandResponseSchema(
            success=True,
            message="Command processed successfully",
            actions=result
        )
    except Exception as e:
        logger.error(f"Command processing failed: {str(e)}", exc_info=True)
        return CommandResponseSchema(
            success=False,
            message=str(e),
            errors=[str(e)]
        )

@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(agent: JiraAgent = Depends(get_agent)):
    """List Jira projects"""
    try:
        projects = await agent.get_projects()
        return [ProjectResponse(**project) for project in projects]
    except Exception as e:
        logger.error(f"Failed to list projects: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check(
    agent: JiraAgent = Depends(get_agent)
) -> Dict:
    """Health check endpoint"""
    jira_ok = await agent.check_jira_connection()
    llm_ok = await agent.check_llm_connection()
    
    if not (jira_ok and llm_ok):
        raise HTTPException(status_code=503, detail="Service unhealthy")
        
    return {
        "status": "healthy",
        "jira": "connected" if jira_ok else "disconnected",
        "llm": "connected" if llm_ok else "disconnected"
    }

@router.get("/status")
async def service_status(agent: JiraAgent = Depends(get_agent)):
    """Get service status"""
    jira_ok = await agent.check_jira_connection()
    llm_ok = await agent.check_llm_connection()
    return {
        "status": "operational",
        "jira": "connected" if jira_ok else "disconnected",
        "llm": "connected" if llm_ok else "disconnected"
    }