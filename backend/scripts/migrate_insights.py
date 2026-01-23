"""
Migration script to move insights data from the raw bucket to the processed bucket
and rename it from 'insights/' to 'meeting_data/'
"""

import os
import sys
import boto3
import json
from botocore.exceptions import ClientError

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config.settings import settings, logger

def migrate_insights():
    """Move insights data from raw bucket to processed bucket"""
    # Initialize S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region
    )
    
    # Get bucket names
    bucket_raw = settings.s3_bucket_raw
    bucket_processed = settings.s3_bucket_processed
    
    # List all objects in the raw bucket with insights/ prefix
    try:
        response = s3_client.list_objects_v2(
            Bucket=bucket_raw,
            Prefix="insights/"
        )
        
        if 'Contents' not in response:
            print(f"No insights/ objects found in {bucket_raw}")
            return
        
        insights_objects = response['Contents']
        print(f"Found {len(insights_objects)} objects with insights/ prefix in {bucket_raw}")
        
        # Process each object
        for obj in insights_objects:
            source_key = obj['Key']
            
            try:
                # Get the object
                obj_response = s3_client.get_object(
                    Bucket=bucket_raw, 
                    Key=source_key
                )
                
                # Create the new key by replacing insights/ with meeting_data/
                target_key = source_key.replace("insights/", "meeting_data/")
                
                # Upload to the processed bucket
                s3_client.put_object(
                    Bucket=bucket_processed,
                    Key=target_key,
                    Body=obj_response['Body'].read(),
                    ContentType=obj_response.get('ContentType', 'application/octet-stream')
                )
                
                print(f"Migrated {source_key} to {bucket_processed}/{target_key}")
                
                # Delete from raw bucket
                s3_client.delete_object(
                    Bucket=bucket_raw,
                    Key=source_key
                )
                
                print(f"Deleted {source_key} from {bucket_raw}")
                
            except ClientError as e:
                print(f"Error processing {source_key}: {str(e)}")
    
    except ClientError as e:
        print(f"Error listing objects: {str(e)}")

if __name__ == "__main__":
    print("Starting migration of insights data...")
    migrate_insights()
    print("Migration completed.")