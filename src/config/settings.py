from pydantic import HttpUrl, EmailStr, Field, AnyUrl
from pydantic_settings import BaseSettings
from typing import Literal, Optional, Union

class Settings(BaseSettings):
    """Application configuration"""
    
    # Core Settings
    DRY_RUN: bool = Field(False, description="Enable dry-run mode")
    MAX_ISSUES_PER_REQUEST: int = Field(10, description="Maximum issues per request")
    
    # Ollama Settings
    OLLAMA_IP: str = Field("localhost", description="Ollama server IP address")
    OLLAMA_PORT: int = Field(11434, description="Ollama server port")
    OLLAMA_MODEL: str = Field("deepseek-r1:14b", description="Ollama model name")

    @property
    def OLLAMA_HOST(self) -> str:
        return f"http://{self.OLLAMA_IP}:{self.OLLAMA_PORT}"
    
    # Jira Settings
    JIRA_SERVER: HttpUrl = Field(..., description="Jira server URL")
    JIRA_USER: EmailStr = Field(..., description="Jira username/email")
    JIRA_TOKEN: Optional[str] = Field(..., description="Jira API token")
    PROTECTED_PROJECTS: str = Field("PROD,LIVE,ADMIN", description="Protected project keys")
    
    # LLM Settings
    LLM_PROVIDER: Literal["ollama", "openai"] = Field(
        "ollama", 
        description="LLM provider selection"
    )
    OPENAI_API_KEY: Optional[str] = Field(None, description="OpenAI API key")
    OPENAI_MODEL: str = Field("gpt-3.5-turbo", description="OpenAI model name")
    DEEPSEEK_MODEL: str = Field("deepseek-r1:14b", description="Deepseek model name")
    LLAMA_MODEL: str = Field("llama2-13b", description="Llama model name")

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore undefined variables