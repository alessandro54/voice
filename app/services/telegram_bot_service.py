from app.core.config import get_settings

class TelegramBotService:

    def __init__(self) -> None:
        config = get_settings()
        self.token = config.TELEGRAM_BOT_TOKEN


    async def process_update(self, update: dict) -> None:
        """Called from webhook. Just print for now."""
        message = update.get("message")
        if not message:
            return

        chat_id = message.get("chat", {}).get("id")
        from_id = message.get("from", {}).get("id")

        if "text" in message:
            print(f"[Telegram] Text from {from_id} in chat {chat_id}: {message['text']}")

        elif "voice" in message:
            voice = message["voice"]
            print(f"[Telegram] Voice msg from {from_id} in chat {chat_id}: {voice}")

        else:
            print(f"[Telegram] Other message type: {message}")


    def _api(self, path: str) -> str:
        return f"https://api.telegram.org/bot{self.token}/{path}"

    def _file_url(self, file_path: str) -> str:
        return f"https://api.telegram.org/file/bot{self.token}/{file_path}"
