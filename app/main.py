from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import asyncio
from client_manager import manager

app = FastAPI()
templates = Jinja2Templates(directory="templates")

log_lines = []

def log(message):
    print(message)
    log_lines.append(message)
    if len(log_lines) > 100:
        log_lines.pop(0)

@app.get("/", response_class=HTMLResponse)
async def read_status(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "clients": manager.clients,
        "logs": reversed(log_lines),
    })

@app.post("/start")
async def start_post(
    clients: int = Form(...),
    ip: str = Form(...),
    port: int = Form(...),
    interval: float = Form(...),
    operation: str = Form(...)
):
    manager.stop_all()
    manager.clients = []
    manager.tasks = []
    manager.start_clients(clients, ip, port, interval, operation)
    log(f"Started {clients} clients to {ip}:{port}, interval={interval}s, operation={operation}")
    return RedirectResponse("/", status_code=303)

@app.get("/stop")
async def stop_clients():
    manager.stop_all()
    log("Stopped all clients")
    return RedirectResponse("/", status_code=303)
