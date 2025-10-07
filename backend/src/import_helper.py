# This is a local fix to enable both local and Docker imports
# For Docker, we'll use a different approach

try:
    # Try the direct imports first (for Docker)
    from src.agents.graph import create_graph
    from src.config.settings import settings, logger
    from src.models.schemas import MeetingState
    from src.repositories.storage_repo import StorageRepository
    print("Direct imports successful")
except ImportError:
    # Fall back to backend-prefixed imports (for local dev)
    from backend.src.agents.graph import create_graph
    from backend.src.config.settings import settings, logger
    from backend.src.models.schemas import MeetingState
    from backend.src.repositories.storage_repo import StorageRepository
    print("Backend-prefixed imports successful")