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

import os
import boto3
from botocore.exceptions import ClientError
from backend.src.config.settings import settings, logger

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
            logger.info(f"Listing all transcripts in bucket: {self.bucket_raw}")
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_raw)
            if 'Contents' in response:
                # Filter for only transcript files (typically .txt files)
                transcript_files = []
                for item in response['Contents']:
                    key = item['Key']
                    # Only include files that are likely transcripts (.txt, .md, .docx)
                    if key.lower().endswith(('.txt', '.md', '.docx')):
                        transcript_files.append(key)
                        logger.info(f"Found transcript: {key}")
                logger.info(f"Total transcripts found: {len(transcript_files)}")
                return transcript_files
            logger.warning(f"No contents found in bucket: {self.bucket_raw}")
            return []
        except ClientError as e:
            logger.error(f"Error listing objects in bucket {self.bucket_raw}: {e}")
            return []
    
    def list_processed_files(self, prefix=None):
        """List all files in the processed bucket, optionally with a prefix"""
        try:
            params = {'Bucket': self.bucket_processed}
            if prefix:
                params['Prefix'] = prefix
                
            response = self.s3_client.list_objects_v2(**params)
            if 'Contents' in response:
                return [item['Key'] for item in response['Contents']]
            return []
        except ClientError as e:
            logger.error(f"Error listing objects in bucket {self.bucket_processed}: {e}")
            return []

    def get_transcript_by_uuid(self, uuid):
        """Get a transcript by its UUID, trying different key formats"""
        logger.info(f"Searching for transcript with UUID: {uuid}")
        
        # Based on the provided example format: UUID_transcript.txt
        exact_key = f"{uuid}_transcript.txt"
        logger.info(f"Trying exact format match: {exact_key}")
        
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_raw, Key=exact_key)
            transcript = response['Body'].read().decode('utf-8')
            logger.info(f"Successfully retrieved transcript with exact format: {exact_key}")
            return transcript, exact_key
        except ClientError as e:
            logger.info(f"Could not retrieve transcript with exact format: {exact_key}, error: {e}")
        
        # Try with transcripts/ prefix
        prefixed_key = f"transcripts/{uuid}_transcript.txt"
        logger.info(f"Trying with transcripts/ prefix: {prefixed_key}")
        
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_raw, Key=prefixed_key)
            transcript = response['Body'].read().decode('utf-8')
            logger.info(f"Successfully retrieved transcript with prefixed key: {prefixed_key}")
            return transcript, prefixed_key
        except ClientError as e:
            logger.info(f"Could not retrieve transcript with prefixed key: {prefixed_key}, error: {e}")
        
        # List all transcripts and find one with this UUID
        all_transcripts = self.list_transcripts()
        logger.info(f"Found {len(all_transcripts)} total transcripts to search through")
        
        # Check if any transcript contains this UUID
        matching_transcripts = [t for t in all_transcripts if uuid in t]
        logger.info(f"Found {len(matching_transcripts)} transcripts containing UUID {uuid}: {matching_transcripts}")
        
        if matching_transcripts:
            matching_key = matching_transcripts[0]
            logger.info(f"Attempting to retrieve transcript with matching key: {matching_key}")
            try:
                response = self.s3_client.get_object(Bucket=self.bucket_raw, Key=matching_key)
                transcript = response['Body'].read().decode('utf-8')
                logger.info(f"Successfully retrieved transcript by UUID match: {matching_key}")
                return transcript, matching_key
            except ClientError as e:
                logger.info(f"Could not retrieve matching transcript: {matching_key}, error: {e}")
        
        logger.error(f"No transcript found with UUID: {uuid} after trying all patterns")
        return None, None

    def get_transcript(self, key):
        """Get the content of a transcript file from S3"""
        try:
            # Log the original key we're trying to retrieve
            logger.info(f"Original transcript key: {key}")
            
            # Check if the key looks like a UUID
            import re
            uuid_pattern = r'^([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$'
            uuid_match = re.match(uuid_pattern, key)
            
            if uuid_match:
                # This is a pure UUID, so use our specialized UUID search method
                logger.info(f"Key is a pure UUID: {key}, using specialized search")
                transcript, found_key = self.get_transcript_by_uuid(key)
                if transcript:
                    return transcript
                logger.error(f"Could not find transcript with UUID: {key}")
                return None
            
            # Extract UUID if it's part of a longer key
            uuid_in_string = r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'
            uuid_in_key = re.search(uuid_in_string, key)
            
            if uuid_in_key:
                # Try the specialized UUID search first
                uuid = uuid_in_key.group(1)
                logger.info(f"Found UUID {uuid} in key {key}, trying specialized search first")
                transcript, found_key = self.get_transcript_by_uuid(uuid)
                if transcript:
                    return transcript
                # If that fails, continue with regular key processing
            
            # Now try with the exact key provided
            logger.info(f"Trying exact key: {key}")
            try:
                response = self.s3_client.get_object(Bucket=self.bucket_raw, Key=key)
                transcript = response['Body'].read().decode('utf-8')
                logger.info(f"Successfully retrieved transcript with exact key: {key}")
                return transcript
            except ClientError as e:
                logger.info(f"Could not find transcript with exact key: {key}, error: {e}")
            
            # Check for and fix duplicate "transcripts/" prefix
            if key.startswith("transcripts/transcripts/"):
                fixed_key = key.replace("transcripts/transcripts/", "transcripts/")
                logger.info(f"Trying with fixed duplicate prefix: {fixed_key}")
                try:
                    response = self.s3_client.get_object(Bucket=self.bucket_raw, Key=fixed_key)
                    transcript = response['Body'].read().decode('utf-8')
                    logger.info(f"Successfully retrieved transcript with fixed key: {fixed_key}")
                    return transcript
                except ClientError as e:
                    logger.info(f"Could not find transcript with fixed key: {fixed_key}, error: {e}")
            
            # If the key doesn't start with "transcripts/", try adding it
            if not key.startswith("transcripts/"):
                prefixed_key = f"transcripts/{key}"
                logger.info(f"Trying with added 'transcripts/' prefix: {prefixed_key}")
                try:
                    response = self.s3_client.get_object(Bucket=self.bucket_raw, Key=prefixed_key)
                    transcript = response['Body'].read().decode('utf-8')
                    logger.info(f"Successfully retrieved transcript with prefixed key: {prefixed_key}")
                    return transcript
                except ClientError as e:
                    logger.info(f"Could not find transcript with prefixed key: {prefixed_key}, error: {e}")
            
            # If all attempts fail in raw bucket, try the processed bucket as last resort
            logger.info(f"Trying processed bucket with original key: {key}")
            try:
                response = self.s3_client.get_object(Bucket=self.bucket_processed, Key=key)
                transcript = response['Body'].read().decode('utf-8')
                logger.info(f"Successfully retrieved transcript from processed bucket: {key}")
                return transcript
            except ClientError as e:
                logger.error(f"Could not find transcript in processed bucket: {key}, error: {e}")
                
            # If we get here, all attempts failed
            logger.error(f"All attempts to retrieve transcript failed for key: {key}")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error retrieving transcript: {str(e)}")
            return None
        except ClientError as e:
            logger.error(f"Error getting transcript {key} from bucket {self.bucket_raw}: {e}")
            # If we couldn't find it in the raw bucket, let's try the processed bucket as a fallback
            try:
                logger.info(f"Attempting to get transcript from processed bucket: {self.bucket_processed}, key: {key}")
                response = self.s3_client.get_object(Bucket=self.bucket_processed, Key=key)
                transcript = response['Body'].read().decode('utf-8')
                logger.info(f"Successfully retrieved transcript from processed bucket: {key}")
                return transcript
            except ClientError as e2:
                logger.error(f"Transcript {key} not found in processed bucket either: {e2}")
                
                # One more attempt - try removing "transcripts/" if it was added above
                if key.startswith("transcripts/"):
                    try:
                        simple_key = key.replace("transcripts/", "")
                        logger.info(f"Final attempt - removing 'transcripts/' prefix. Trying raw bucket with key: {simple_key}")
                        response = self.s3_client.get_object(Bucket=self.bucket_raw, Key=simple_key)
                        transcript = response['Body'].read().decode('utf-8')
                        logger.info(f"Successfully retrieved transcript using simple key: {simple_key}")
                        return transcript
                    except ClientError as e3:
                        logger.error(f"Final attempt failed for simple key {simple_key}: {e3}")
                
                logger.error(f"Transcript {key} not found in either bucket")
                return None

    def save_minutes(self, key, content):
        """Save minutes content to S3"""
        try:
            # Extract just the ID part, removing path prefixes and extensions
            clean_key = key
            
            # Remove "minutes/" prefix if present
            if clean_key.startswith("minutes/"):
                clean_key = clean_key[8:]
                
            # Remove ".md" extension if present
            if clean_key.endswith(".md"):
                clean_key = clean_key[:-3]
                
            self.s3_client.put_object(
                Bucket=self.bucket_processed,
                Key=f"minutes/{clean_key}.md",
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
            # Extract just the ID part, removing path prefixes and extensions
            clean_key = key
            
            # Remove "actions/" prefix if present
            if clean_key.startswith("actions/"):
                clean_key = clean_key[8:]
                
            # Remove ".json" extension if present
            if clean_key.endswith(".json"):
                clean_key = clean_key[:-5]
                
            self.s3_client.put_object(
                Bucket=self.bucket_processed,
                Key=f"actions/{clean_key}.json",
                Body=content.encode('utf-8'),
                ContentType='application/json'
            )
            return True
        except ClientError as e:
            logger.error(f"Error saving actions to bucket {self.bucket_processed}: {e}")
            return False
    
    def save_file(self, key, content):
        """Save arbitrary file content to S3"""
        try:
            # Default bucket (raw) is for transcripts
            bucket_name = self.bucket_raw
            
            # Check if this is a transcript file
            is_transcript = key.startswith("transcripts/") or key.lower().endswith(('.txt', '.md', '.docx'))
            
            # For all processed data, use the processed bucket
            if key.startswith("meeting_data/") or key.startswith("minutes/") or key.startswith("actions/") or not is_transcript:
                bucket_name = self.bucket_processed
                
                # For meeting data specifically, clean the key to avoid double folders/extensions
                if key.startswith("meeting_data/"):
                    clean_key = key
                    
                    # Extract the filename only
                    filename = os.path.basename(clean_key)
                    
                    # Remove the extension if it's duplicated
                    if filename.endswith(".json.json"):
                        filename = filename[:-5]  # Remove one ".json"
                    
                    # Reconstruct the key with clean filename
                    key = f"meeting_data/{filename}"
            
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=content
            )
            return True
        except ClientError as e:
            logger.error(f"Error saving file to bucket {bucket_name}: {e}")
            return False
    
    def get_file(self, key):
        """Get the content of any file from S3"""
        try:
            # First try the processed bucket
            try:
                response = self.s3_client.get_object(Bucket=self.bucket_processed, Key=key)
                return response['Body'].read().decode('utf-8')
            except ClientError:
                # If not found, try the raw bucket
                response = self.s3_client.get_object(Bucket=self.bucket_raw, Key=key)
                return response['Body'].read().decode('utf-8')
        except ClientError as e:
            logger.error(f"Error getting file {key}: {e}")
            return None
    
    def get_object(self, key):
        """Get an S3 object and return it (backward compatibility)"""
        return self.get_file(key)
        
    def get_object_metadata(self, key):
        """Get metadata for an S3 object"""
        try:
            # First try the raw bucket
            try:
                response = self.s3_client.head_object(Bucket=self.bucket_raw, Key=key)
                return response
            except ClientError:
                # If not found, try the processed bucket
                response = self.s3_client.head_object(Bucket=self.bucket_processed, Key=key)
                return response
        except ClientError as e:
            logger.error(f"Error getting metadata for {key}: {e}")
            return None
    
    def list_objects_with_prefix(self, prefix):
        """List all objects in S3 with a specific prefix"""
        try:
            # First try the processed bucket
            processed_objects = []
            raw_objects = []
            
            # Get objects from processed bucket
            try:
                response = self.s3_client.list_objects_v2(
                    Bucket=self.bucket_processed,
                    Prefix=prefix
                )
                if 'Contents' in response:
                    processed_objects = [item['Key'] for item in response['Contents']]
            except ClientError as e:
                logger.error(f"Error listing objects in bucket {self.bucket_processed}: {e}")
            
            # Get objects from raw bucket
            try:
                response = self.s3_client.list_objects_v2(
                    Bucket=self.bucket_raw,
                    Prefix=prefix
                )
                if 'Contents' in response:
                    raw_objects = [item['Key'] for item in response['Contents']]
            except ClientError as e:
                logger.error(f"Error listing objects in bucket {self.bucket_raw}: {e}")
            
            # Combine the results
            return processed_objects + raw_objects
            
        except Exception as e:
            logger.error(f"Error listing objects with prefix {prefix}: {e}")
            return []
    
    def get_object(self, key):
        """Get an object from S3"""
        return self.get_file(key)
    
    def save_object(self, key, content):
        """Save an object to S3 (backward compatibility)"""
        return self.save_file(key, content)
    def save_object(self, key, content):
        """Save an object to S3"""
        return self.save_file(key, content)
