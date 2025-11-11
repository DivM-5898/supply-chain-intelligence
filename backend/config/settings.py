# Backend Configuration Settings

import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Configuration
    API_TITLE: str = "AI Supplier Selection API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "REST API for AI-powered supplier evaluation and risk management"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Database Configuration
    DATABASE_URL: Optional[str] = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/supplier_db"
    )
    
    # Model Paths
    MODELS_DIR: str = "models/saved_models"
    DATA_DIR: str = "data"
    
    # API Keys (for external services)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", "AIzaSyA8b_9uzdOv7NLxYx4VV88SPHU4pPf65-Y")
    
    # CORS Configuration
    CORS_ORIGINS: list = ["http://localhost:8501", "http://127.0.0.1:8501"]
    
    # Model Configuration
    XGBOOST_PARAMS: dict = {
        "max_depth": 6,
        "learning_rate": 0.1,
        "n_estimators": 100,
        "random_state": 42
    }
    
    # NLP Configuration
    BERT_MODEL_NAME: str = "bert-base-uncased"
    SPACY_MODEL_NAME: str = "en_core_web_sm"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

