import httpx
from app.core.config import get_settings

class TelegramAPI:
    def __init__(self):
        cfg = get_settings()
        self.token = cfg.TELEGRAM_BOT_TOKEN.get_secret_value()
        self.base = f"https://api.telegram.org/bot{self.token}"
        self.file_base = f"https://api.telegram.org/file/bot{self.token}"

    def api_url(self, path: str) -> str:
        return f"{self.base}/{path}"

    def file_url(self, file_path: str) -> str:
        return f"{self.file_base}/{file_path}"

    async def get_file_path(self, file_id: str) -> str:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(self.api_url("getFile"), params={"file_id": file_id})
            response.raise_for_status()
            return response.json()["result"]["file_path"]

    async def download_file(self, file_path: str) -> bytes:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(self.file_url(file_path))
            response.raise_for_status()
            return response.content

    async def send_message(self, chat_id: int, text: str) -> dict:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(self.api_url("sendMessage"), json={"chat_id": chat_id, "text": text})
            response.raise_for_status()
            return response.json()
