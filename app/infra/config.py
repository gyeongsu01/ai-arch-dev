# Config file
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Deployment Toggle (INFRA LAYER)
    DEPLOYMENT_MODE = os.getenv("DEPLOYMENT_MODE", "ONPREM")

    # Vector DB
    CHROMA_HOST = os.getenv("CHROMA_HOST", "chromadb")
    CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
    
    # LLM
    # gemini-2.5-flash-lite
    LLM_MODEL_NAME = os.getenv("LLM_MODEL", "gemini-2.0-flash")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    @classmethod
    def get_infra_context(cls):
        return {
            "mode": cls.DEPLOYMENT_MODE,
            "vector_db": f"{cls.CHROMA_HOST}:{cls.CHROMA_PORT}",
            "llm_model_name": cls.LLM_MODEL_NAME
        }
