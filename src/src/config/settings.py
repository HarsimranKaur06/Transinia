import logging
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
logger = logging.getLogger("meeting-bot-local")

@dataclass(frozen=True)
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    # AWS credentials
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    # S3 buckets
    s3_bucket_raw: str = os.getenv("S3_BUCKET_RAW", "meeting-bot-transcripts")
    s3_bucket_processed: str = os.getenv("S3_BUCKET_PROCESSED", "meeting-bot-outputs")

settings = Settings()
