"""
APPLICATION CONFIGURATION MANAGER
-------------------------------
This file manages all external configuration for the application.
It provides:

1. Loading of environment variables from .env file
2. Configuration of the logging system with appropriate formatting
3. A central Settings class that contains:
   - OpenAI API credentials for AI services
   - AWS access credentials for S3 storage
   - S3 bucket names for raw transcripts and processed outputs
   - Other configurable application parameters

This centralized configuration makes the application more maintainable
and allows for configuration changes without code modifications.
"""

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
