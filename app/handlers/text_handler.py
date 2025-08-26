# app/services/handlers/text_handler.py
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from app.infra.s3 import S3Storage
from app.adapters.telegram import TelegramAPI

LIMA = ZoneInfo("America/Lima")

class TextHandler:
    def __init__(self):
        self.s3 = S3Storage()
        self.tg = TelegramAPI()

    def _prefix(self, user_id: int, tg_unix_date: int) -> tuple[str, str]:
        """
        Returns (date_str, ts_ms_str):
          - date_str -> YYYY-MM-DD in America/Lima (readable per local day)
          - ts_ms_str -> UTC epoch milliseconds (stable folder id)
        """
        dt_utc = datetime.fromtimestamp(tg_unix_date, tz=timezone.utc)
        dt_lima = dt_utc.astimezone(LIMA)
        date_str = dt_lima.strftime("%Y-%m-%d")
        ts_ms = int(dt_utc.timestamp() * 1000)
        return date_str, str(ts_ms)

    async def handle(self, message: dict) -> None:
        user  = message["from"]
        chat  = message["chat"]
        text  = message.get("text", "")
        msg_id = message["message_id"]
        tg_unix_date = message.get("date", int(datetime.now(timezone.utc).timestamp()))

        user_id = user["id"]
        chat_id = chat["id"]

        # Folder prefix: <date>/<user>/<ts_ms>
        date_str, ts_ms = self._prefix(user_id, tg_unix_date)
        base = f"{date_str}/{user_id}/{ts_ms}"

        # Build metadata (no audio here)
        meta = {
            "type": "text",
            "user": {
                "telegram_id": user_id,
                "username": user.get("username"),
                "first_name": user.get("first_name"),
                "last_name": user.get("last_name"),
                "language_code": user.get("language_code"),
            },
            "telegram": {
                "chat_id": chat_id,
                "message_id": msg_id,
                "date_unix": tg_unix_date,
            },
            "text": text,
            "received_at": datetime.now(timezone.utc).isoformat(),
        }

        # Save metadata.json next to where audios would go
        meta_key = f"{base}/metadata.json"
        await self.s3.put_json(meta_key, meta)

        # Optional: acknowledge in chat (comment out if not needed)
        try:
            await self.tg.send_message(chat_id, "✅ Recibido")
        except Exception:
            # Don't fail the handler if Telegram reply fails
            pass

        print(f"[text] saved s3://{self.s3.bucket}/{meta_key} :: {text[:80]!r}")
