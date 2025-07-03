from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from uuid import uuid4
import asyncio
import time

from client_manager import SessionClientManager

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="CHANGE_ME_SECRET")
templates = Jinja2Templates(directory="templates")

session_clients = {}
SESSION_TIMEOUT = 900  # 15 minutes

def get_session_id(request: Request):
    session = request.session
    if "sid" not in session:
        session["sid"] = str(uuid4())
        session["last_active"] = time.time()
    else:
        session["last_active"] = time.time()
    return session["sid"]

@app.middleware("http")
async def session_timeout_middleware(request: Request, call_next):
    session = request.session
    if "last_active" in session and time.time() - session["last_active"] > SESSION_TIMEOUT:
        session.clear()
    return await call_next(request)

@app.get("/", response_class=HTMLResponse)
async def read_status(request: Request):
    sid = get_session_id(request)
    manager = session_clients.get(sid)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "clients": manager.clients if manager else [],
        "logs": manager.logs if manager else [],
    })

@app.post("/start")
async def start_post(
    request: Request,
    clients: int = Form(...),
    ip: str = Form(...),
    port: int = Form(...),
    interval: float = Form(...),
    operation: str = Form(...)
):
    sid = get_session_id(request)
    manager = SessionClientManager()
    session_clients[sid] = manager
    await manager.start_clients(clients, ip, port, interval, operation)
    return RedirectResponse("/", status_code=303)

@app.get("/stop")
async def stop_clients(request: Request):
    sid = get_session_id(request)
    if sid in session_clients:
        await session_clients[sid].stop_all()
        del session_clients[sid]
    return RedirectResponse("/", status_code=303)
