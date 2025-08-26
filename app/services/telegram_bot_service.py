import os, httpx
from datetime import datetime, timezone
from app.core.config import get_settings
from app.infra.s3 import S3Storage

class TelegramBotService:

    def __init__(self) -> None:
        config = get_settings()
        self._token = config.TELEGRAM_BOT_TOKEN.get_secret_value()
        self._s3 = S3Storage()

    def _api(self, path: str) -> str:
        return f"https://api.telegram.org/bot{self._token}/{path}"

    def _file_url(self, file_path: str) -> str:
        return f"https://api.telegram.org/file/bot{self._token}/{file_path}"

    @staticmethod
    def _ymd() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _audio_key(self, user_id: int, file_id: str, ext: str) -> str:
        return f"telegram/{self._ymd()}/{user_id}/audios/{file_id}{ext}"

    async def process_update(self, update: dict) -> None:
        msg = update.get("message") or update.get("edited_message")
        if not msg or "voice" not in msg:
            return
        await self._handle_voice(msg)


    async def _handle_voice(self, msg: dict) -> None:
        from_id = msg.get("from", {}).get("id")
        voice = msg.get("voice", {})
        file_id = voice.get("file_id")

        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.get(self._api("getFile"), params={"file_id": file_id})
            r.raise_for_status()
            file_path = r.json()["result"]["file_path"]

        async with httpx.AsyncClient(timeout=60) as c:
            r2 = await c.get(self._file_url(file_path))
            r2.raise_for_status()
            data = r2.content

        _, ext = os.path.splitext(file_path)
        if not ext: ext = ".ogg"
        key = self._audio_key(from_id, file_id, ext)
        url = await self._s3.put_bytes(key, data, content_type="audio/ogg")

        print(f"[tg] voice uploaded to s3://{self._s3.bucket}/{key}")
        print(f"[tg] accessible at {url}")
