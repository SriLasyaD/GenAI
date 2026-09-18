import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
INDEX_DIR = DATA_DIR / "indices"
SAMPLE_DIR = BASE_DIR / "sample_data"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
INDEX_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)


class AppSettings(BaseModel):
    chunk_size: int = 500
    chunk_overlap: int = 100
    top_k: int = 4
    embedding_model: str = "all-MiniLM-L6-v2"
    llm_provider: str = "groq"
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "groq/compound-mini")
    groq_base_url: str = "https://api.groq.com/openai/v1"


settings = AppSettings()
