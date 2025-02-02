from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, List, Optional
from pydantic import BaseModel
import logging

from ..config.settings import Settings
from ..core.agent import JiraAgent
from ..core.schemas import CommandResponseSchema

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

async def get_agent():
    """Dependency to get configured JiraAgent instance"""
    try:
        settings = Settings()
        agent = JiraAgent(settings)
        await agent.validate_connection()
        return agent
    except Exception as e:
        logger.error(f"Failed to initialize agent: {str(e)}")
        raise HTTPException(status_code=500, detail="Service initialization failed")

@router.post("/command", response_model=CommandResponseSchema)
async def process_command(
    request: CommandRequest,
    agent: JiraAgent = Depends(get_agent)
) -> Dict:
    """Process natural language command"""
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
async def list_projects(
    agent: JiraAgent = Depends(get_agent)
) -> List[Dict]:
    """List available Jira projects"""
    try:
        projects = await agent.get_projects()
        return [
            ProjectResponse(
                key=p.key,
                name=p.name,
                description=p.description
            ) for p in projects
        ]
    except Exception as e:
        logger.error(f"Failed to list projects: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check() -> Dict:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

@router.get("/status")
async def service_status(
    agent: JiraAgent = Depends(get_agent)
) -> Dict:
    """Check service status"""
    try:
        jira_status = await agent.check_jira_connection()
        llm_status = await agent.check_llm_connection()
        return {
            "jira": "connected" if jira_status else "disconnected",
            "llm": "connected" if llm_status else "disconnected"
        }
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))