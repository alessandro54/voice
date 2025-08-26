from fastapi import HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from app.services.telegram_service import TelegramService

from fastapi import FastAPI
from app.core.config import Settings

settings = Settings()
app = FastAPI()

telegram_service = TelegramService()

@app.middleware("http")
async def log_requests(req: Request, call_next):
    if req.url.path.startswith("/telegram"):
        print("[TG] hit", req.method, req.url.path)
    return await call_next(req)

@app.post("/telegram/webhook")
async def webhook(request: Request, background: BackgroundTasks):
    secret = request.headers.get("x-telegram-bot-api-secret-token")
    expected = getattr(settings, "WEBHOOK_SECRET", None)
    if expected and secret != expected:
        raise HTTPException(status_code=401, detail="unauthorized")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid json")

    background.add_task(telegram_service.process_update, payload)
    return JSONResponse({"ok": True})


@app.get("/healthz")
def healthz():
    return {"ok": True}
