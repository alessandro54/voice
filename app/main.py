from fastapi import Request, BackgroundTasks
from fastapi.responses import JSONResponse
from app.services import telegram_bot_service

from fastapi import FastAPI
from app.core.config import Settings

settings = Settings()
app = FastAPI()

telegram_service = telegram_bot_service.TelegramBotService()


@app.post(f"/telegram/{settings.TELEGRAM_BOT_TOKEN.get_secret_value()}")
async def webhook(request: Request, background: BackgroundTasks):
    payload = await request.json()
    background.add_task(telegram_service.process_update, payload)
    return JSONResponse({"ok": True})


@app.get("/healthz")
def healthz():
    return {"ok": True}
