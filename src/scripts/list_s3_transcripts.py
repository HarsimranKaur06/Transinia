"""
List all available transcripts in S3
"""

from src.repositories.storage_repo import StorageRepository

def main():
    storage_repo = StorageRepository()
    transcripts = storage_repo.list_s3_transcripts()
    
    print(f"Found {len(transcripts)} transcripts in S3:")
    for key in transcripts:
        print(f"- {key}")

if __name__ == "__main__":
    main()
