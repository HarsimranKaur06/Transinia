"""
MAIN APPLICATION ENTRY POINT
---------------------------
This file serves as the main entry point for the Transinia application.
It provides:

1. Command-line interface for processing meeting transcripts
2. Functions to load transcripts from local files or S3 storage
3. Pipeline execution to analyze transcripts and extract information
4. Output handling to save results locally or to S3

Usage:
1. For local transcripts: python -m src.app
2. For S3 stored transcripts: python -m src.app --source s3 --s3-key your_transcript.txt
3. To list available S3 transcripts: python -m src.app --list-s3
"""

import sys
import argparse
from src.config.settings import logger
from src.utils.paths import TRANSCRIPT_TXT
from src.models.schemas import MeetingState
from src.agents.graph import build_app
from src.repositories.storage_repo import StorageRepository

def _load_local_transcript() -> str:
    if not TRANSCRIPT_TXT.exists():
        TRANSCRIPT_TXT.parent.mkdir(parents=True, exist_ok=True)
        TRANSCRIPT_TXT.write_text(
            "Attendees: Alex, Priya, Jordan\n"
            "Agenda: onboarding flow, pricing update, Q3 launch\n"
            "- We agreed to simplify the signup from 5 steps to 3.\n"
            "- Pricing change: Starter $19, Pro $49. Priya to update website copy.\n"
            "- Q3 launch date holds: Sept 15. Jordan owns risk register.\n"
            "- Security gap: missing 2FA on admin dashboard. Alex to file ticket; due next Friday.\n",
            encoding="utf-8"
        )
    return TRANSCRIPT_TXT.read_text(encoding="utf-8")

def run_local_text():
    logger.info("Running pipeline with local transcript text...")
    transcript = _load_local_transcript()
    state = MeetingState(source="local_text", transcript=transcript)
    _run_pipeline_and_save(state, "local")

def run_s3_text(key: str):
    logger.info(f"Running pipeline with S3 transcript: {key}")
    repo = StorageRepository()
    transcript = repo.get_transcript_from_s3(key)
    if not transcript:
        logger.error(f"Failed to retrieve transcript from S3: {key}")
        return
    
    state = MeetingState(source="s3", transcript=transcript)
    _run_pipeline_and_save(state, "s3", key)

def list_s3_transcripts():
    repo = StorageRepository()
    transcripts = repo.list_s3_transcripts()
    if not transcripts:
        logger.info("No transcripts found in S3 bucket")
        return
    
    logger.info("Available transcripts in S3:")
    for i, key in enumerate(transcripts, 1):
        logger.info(f"{i}. {key}")

def _run_pipeline_and_save(state: MeetingState, storage_type: str, s3_key: str = ""):
    app = build_app()
    repo = StorageRepository()
    final = app.invoke(state.model_dump(), config={"configurable": {"thread_id": "demo-run"}})

    minutes_md = final.get("minutes_md", "")
    tasks = final.get("tasks", [])
    
    if storage_type == "local":
        repo.save_minutes_local(minutes_md)
        repo.save_actions_local(tasks)
        logger.info("All done. Check the outputs/ folder.")
    elif storage_type == "s3":
        output_key = s3_key.replace(".txt", "").replace(".json", "")
        repo.save_minutes_s3(output_key, minutes_md)
        repo.save_actions_s3(output_key, tasks)
        logger.info(f"All done. Files saved to S3 with key prefix: {output_key}")

def main():
    parser = argparse.ArgumentParser(description="Meeting Bot Processing")
    parser.add_argument("--source", choices=["local", "s3"], default="local", 
                        help="Source of transcript (local file or S3)")
    parser.add_argument("--s3-key", help="S3 key of the transcript file")
    parser.add_argument("--list-s3", action="store_true", help="List available transcripts in S3")
    
    args = parser.parse_args()
    
    if args.list_s3:
        list_s3_transcripts()
        return
    
    if args.source == "s3":
        if not args.s3_key:
            logger.error("S3 key is required when source is s3")
            parser.print_help()
            return
        run_s3_text(args.s3_key)
    else:
        run_local_text()

if __name__ == "__main__":
    main()
