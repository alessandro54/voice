import asyncio, boto3, json
from app.core.config import get_settings

class S3Storage:
    def __init__(self):
        cfg = get_settings()
        self.bucket = cfg.S3_BUCKET
        self.endpoint = cfg.S3_ENDPOINT
        self.region = cfg.S3_REGION
        self.client = boto3.client(
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=cfg.S3_ACCESS_KEY.get_secret_value(),
            aws_secret_access_key=cfg.S3_SECRET_KEY.get_secret_value(),
            region_name=self.region,
        )

    async def put_bytes(self, key: str, data: bytes, content_type="application/octet-stream") -> str:
        await asyncio.to_thread(
            self.client.put_object,
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType=content_type
        )
        if self.endpoint:  # MinIO (dev)
            return f"{self.endpoint.rstrip('/')}/{self.bucket}/{key}"
        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{key}"

    async def put_json(self, key: str, obj: dict) -> str:
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        return await self.put_bytes(key, data, content_type="application/json")

    def url_for(self, key: str) -> str:
        if self.endpoint:
            return f"{self.endpoint.rstrip('/')}/{self.bucket}/{key}"
        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{key}"
