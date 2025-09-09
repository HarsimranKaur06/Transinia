"""
STORAGE AND PERSISTENCE MANAGER
-----------------------------
This file handles all data persistence operations for the application.
It provides methods to:

1. Save meeting minutes as formatted Markdown files locally
2. Save action items as structured JSON files locally
3. Save meeting minutes to AWS S3 cloud storage
4. Save action items to AWS S3 cloud storage
5. Retrieve meeting transcripts from S3
6. List available transcripts in S3 storage

The repository abstracts storage details away from the rest of the application,
providing a consistent interface regardless of where data is stored.
"""

import json
from src.utils.paths import MINUTES_MD, ACTIONS_JSON
from src.config.settings import logger
from src.services.s3_service import S3Service

class StorageRepository:
    """
    Saves outputs locally or to S3.
    """
    def __init__(self):
        self.s3_service = S3Service()
    
    def save_minutes_local(self, text: str) -> str:
        MINUTES_MD.parent.mkdir(parents=True, exist_ok=True)
        MINUTES_MD.write_text(text, encoding="utf-8")
        logger.info(f"Saved minutes: {MINUTES_MD}")
        return str(MINUTES_MD)

    def save_actions_local(self, tasks: list) -> str:
        ACTIONS_JSON.parent.mkdir(parents=True, exist_ok=True)
        ACTIONS_JSON.write_text(json.dumps({"tasks": tasks}, indent=2), encoding="utf-8")
        logger.info(f"Saved actions: {ACTIONS_JSON}")
        return str(ACTIONS_JSON)
    
    def save_minutes_s3(self, key: str, text: str) -> bool:
        """Save minutes to S3"""
        result = self.s3_service.save_minutes(key, text)
        if result:
            logger.info(f"Saved minutes to S3: {key}")
        return result

    def save_actions_s3(self, key: str, tasks: list) -> bool:
        """Save actions to S3"""
        result = self.s3_service.save_actions(key, json.dumps({"tasks": tasks}, indent=2))
        if result:
            logger.info(f"Saved actions to S3: {key}")
        return result
    
    def get_transcript_from_s3(self, key: str) -> str:
        """Get transcript from S3"""
        transcript = self.s3_service.get_transcript(key)
        if transcript:
            logger.info(f"Retrieved transcript from S3: {key}")
        return transcript
    
    def list_s3_transcripts(self) -> list:
        """List all transcripts in S3"""
        return self.s3_service.list_transcripts()
