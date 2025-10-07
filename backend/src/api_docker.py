"""
API Server for Transinia
------------------------
This module provides a FastAPI server to expose the Transinia functionality
as a REST API for the frontend to consume.
"""

import uuid
import json
import os
import tempfile
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Try both import styles to support both local and Docker environments
try:
    # Docker imports (direct)
    from src.agents.graph import create_graph
    from src.config.settings import settings, logger
    from src.models.schemas import MeetingState
    from src.repositories.storage_repo import StorageRepository
    print("Using direct imports for Docker environment")
except ImportError:
    # Local dev imports (with backend prefix)
    from backend.src.agents.graph import create_graph
    from backend.src.config.settings import settings, logger
    from backend.src.models.schemas import MeetingState
    from backend.src.repositories.storage_repo import StorageRepository
    print("Using prefixed imports for local environment")

# Create FastAPI app
app = FastAPI(title="Transinia API", 
              description="API for processing meeting transcripts and generating insights",
              version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint for ECS container health checks"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}