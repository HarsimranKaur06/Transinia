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
   - DynamoDB table names for persistent storage
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
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "dev")
    
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    # AWS credentials
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    
    # S3 buckets with environment prefix
    _s3_bucket_raw_base: str = os.getenv("S3_BUCKET_RAW_BASE", "transcripts")
    _s3_bucket_processed_base: str = os.getenv("S3_BUCKET_PROCESSED_BASE", "outputs")
    
    # DynamoDB settings with environment prefix
    use_dynamodb: bool = os.getenv("USE_DYNAMODB", "false").lower() in ("true", "1", "yes")
    _dynamodb_table_meetings_base: str = os.getenv("DYNAMODB_TABLE_MEETINGS_BASE", "meetings")
    _dynamodb_table_actions_base: str = os.getenv("DYNAMODB_TABLE_ACTIONS_BASE", "actions")
    
    # Dynamic properties that include environment prefix
    @property
    def s3_bucket_raw(self) -> str:
        return f"transinia-{self.environment}-{self._s3_bucket_raw_base}"
        
    @property
    def s3_bucket_processed(self) -> str:
        return f"transinia-{self.environment}-{self._s3_bucket_processed_base}"
        
    @property
    def dynamodb_table_meetings(self) -> str:
        return f"transinia-{self.environment}-{self._dynamodb_table_meetings_base}"
        
    @property
    def dynamodb_table_actions(self) -> str:
        return f"transinia-{self.environment}-{self._dynamodb_table_actions_base}"
    
    # Legacy setting for backward compatibility
    @property
    def dynamodb_table_name(self) -> str:
        return self.dynamodb_table_meetings

settings = Settings()
