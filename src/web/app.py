import os
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from src.main import JiraAgent

# Initialize FastAPI app
app = FastAPI()

# Configure static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Convert DRY_RUN env to boolean
dry_run_env = os.getenv("DRY_RUN", "false").strip().lower() == "true"
agent = JiraAgent(dry_run=dry_run_env)

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/command")
async def handle_command(command: str = Form(...)):
    try:
        result = agent.process_command(command)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}