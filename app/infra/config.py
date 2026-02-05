# Config file
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Deployment Toggle (INFRA LAYER)
    DEPLOYMENT_MODE = os.getenv("DEPLOYMENT_MODE", "ONPREM")

    # Vector DB
    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./chroma_db")
    
    # LLM
    # gemini-2.5-flash-lite
    LLM_MODEL_NAME = os.getenv("LLM_MODEL", "gemini-2.0-flash")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    @classmethod
    def get_infra_context(cls):
        return {
            "mode": cls.DEPLOYMENT_MODE,
            "vector_db": cls.VECTOR_DB_PATH,
            "llm_model_name": cls.LLM_MODEL_NAME
        }
