from app.handlers.text_handler import TextHandler
from app.handlers.voice_handler import VoiceHandler


class TelegramService:
    def __init__(self):
        self.voice_handler = VoiceHandler()
        self.text_handler = TextHandler()

    async def process_update(self, update: dict) -> None:
        msg = update.get("message") or update.get("edited_message")
        if not msg:
            return

        if "voice" in msg:
            await self.voice_handler.handle(msg)
        elif "text" in msg:
            await self.text_handler.handle(msg)
        else:
            print("[tg] unhandled keys:", msg.keys())
