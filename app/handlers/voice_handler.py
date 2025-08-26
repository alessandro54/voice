import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from app.infra.s3 import S3Storage
from app.adapters.telegram import TelegramAPI

LIMA = ZoneInfo("America/Lima")


class VoiceHandler:
    def __init__(self):
        self.s3 = S3Storage()
        self.tg = TelegramAPI()

    def _prefix(self, user_id: int, tg_unix_date: int) -> tuple[str, str]:
        """
        Returns (date_str, ts_ms_str) where:
        - date_str is YYYY-MM-DD in America/Lima (nice for browsing by local day)
        - ts_ms_str is a millisecond epoch string (stable folder id)
        """
        # Telegram date is seconds since epoch (UTC)
        dt_utc = datetime.fromtimestamp(tg_unix_date, tz=timezone.utc)
        dt_lima = dt_utc.astimezone(LIMA)
        date_str = dt_lima.strftime("%Y-%m-%d")
        ts_ms = int(dt_utc.timestamp() * 1000)
        return date_str, str(ts_ms)

    async def handle(self, message: dict) -> None:
        user = message["from"]
        user_id = user["id"]
        msg_id = message["message_id"]
        v = message["voice"]
        file_id = v["file_id"]
        tg_unix_date = message.get("date", int(
            datetime.now(timezone.utc).timestamp()))

        # Resolve Telegram file_path and download
        file_path = await self.tg.get_file_path(file_id)
        data = await self.tg.download_file(file_path)

        # Decide extension (Telegram voice is usually .oga/.ogg)
        _, ext = os.path.splitext(file_path)
        if not ext:
            ext = ".ogg"

        # Build folder prefix: <date>/<user>/<ts_ms>
        date_str, ts_ms = self._prefix(user_id, tg_unix_date)
        base = f"{date_str}/{user_id}/{ts_ms}"

        # Upload audio
        audio_key = f"{base}/audio{ext}"
        await self.s3.put_bytes(audio_key, data, content_type="audio/ogg")

        # Prepare metadata
        meta = {
            "type": "voice",
            "user": {
                "telegram_id": user_id,
                "username": user.get("username"),
                "first_name": user.get("first_name"),
                "last_name": user.get("last_name"),
                "language_code": user.get("language_code"),
            },
            "telegram": {
                "message_id": msg_id,
                "date_unix": tg_unix_date,            # original UTC seconds
                "file_id": file_id,
                "file_unique_id": v.get("file_unique_id"),
                "duration": v.get("duration"),
                "mime_type": v.get("mime_type"),
                "file_size": v.get("file_size"),
            },
            "audio": {
                "key": audio_key,
                "ext": ext,
            },
            "received_at": datetime.now(timezone.utc).isoformat()
        }

        meta_key = f"{base}/metadata.json"
        await self.s3.put_json(meta_key, meta)

        print(f"[voice] uploaded: s3://{self.s3.bucket}/{audio_key}")
        print(f"[voice] metadata: s3://{self.s3.bucket}/{meta_key}")
