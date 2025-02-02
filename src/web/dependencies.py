from fastapi import Depends
from src.core.agent import JiraAgent
from src.config.settings import Settings

_agent: JiraAgent = None

def get_agent() -> JiraAgent:
    global _agent
    if not _agent:
        _agent = JiraAgent(Settings())
    return _agent