import os
from dotenv import load_dotenv
import logging
from google.auth import default

load_dotenv()
logger = logging.getLogger(__name__)


class Settings:
    # Bucket GCS
    BUCKET: str = os.getenv("BUCKET", "crp-dev-dig-ailab-bkt01")
    FOLDER: str = os.getenv("FOLDER", "IMO")

    # Service Account Paths
    SERVICE_ACCOUNT_PATH_DEV: str = os.getenv("SERVICE_ACCOUNT_PATH_DEV", "dev-ai-vertex.json")

    # GenAI Configuration
    GENAI_MODEL: str = os.getenv("GENAI_MODEL", "gemini-2.5-flash")
    GENAI_PROJECT: str = os.getenv("GENAI_PROJECT", "crp-dev-dig-ailab")
    GENAI_LOCATION: str = os.getenv("GENAI_LOCATION", "global")
    GENAI_TEMPERATURE: float = float(os.getenv("GENAI_TEMPERATURE", 1.0))
    GENAI_TOP_P: float = float(os.getenv("GENAI_TOP_P", 0.95))
    GENAI_MAX_OUTPUT_TOKENS: int = int(os.getenv("GENAI_MAX_OUTPUT_TOKENS", 65535))                                

    CREDENTIALS, PROJECT_ID = default(
        scopes=[
            "https://www.googleapis.com/auth/cloud-platform",
            "https://www.googleapis.com/auth/generative-language",
        ]
    )

# Global instance
settings = Settings()
    

