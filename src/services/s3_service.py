"""
AWS S3 CLOUD STORAGE SERVICE
---------------------------
This file provides direct integration with Amazon S3 cloud storage.
It implements:

1. Secure connection to AWS using credentials from settings
2. Methods to list available transcripts in the source bucket
3. Functions to retrieve transcript text from S3
4. Methods to save meeting minutes to the destination bucket
5. Functions to save action items JSON to the destination bucket
6. Error handling for all S3 operations

This service handles all the low-level details of S3 interactions,
allowing the rest of the application to work with cloud storage without
needing to know AWS-specific implementation details.
"""

import boto3
from botocore.exceptions import ClientError
from src.config.settings import settings, logger

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
        self.bucket_raw = settings.s3_bucket_raw
        self.bucket_processed = settings.s3_bucket_processed

    def list_transcripts(self):
        """List all transcript files in the raw bucket"""
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_raw)
            if 'Contents' in response:
                return [item['Key'] for item in response['Contents']]
            return []
        except ClientError as e:
            logger.error(f"Error listing objects in bucket {self.bucket_raw}: {e}")
            return []

    def get_transcript(self, key):
        """Get the content of a transcript file from S3"""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_raw, Key=key)
            return response['Body'].read().decode('utf-8')
        except ClientError as e:
            logger.error(f"Error getting object {key} from bucket {self.bucket_raw}: {e}")
            return None

    def save_minutes(self, key, content):
        """Save minutes content to S3"""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_processed,
                Key=f"minutes/{key}.md",
                Body=content.encode('utf-8'),
                ContentType='text/markdown'
            )
            return True
        except ClientError as e:
            logger.error(f"Error saving minutes to bucket {self.bucket_processed}: {e}")
            return False

    def save_actions(self, key, content):
        """Save actions JSON to S3"""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_processed,
                Key=f"actions/{key}.json",
                Body=content.encode('utf-8'),
                ContentType='application/json'
            )
            return True
        except ClientError as e:
            logger.error(f"Error saving actions to bucket {self.bucket_processed}: {e}")
            return False
