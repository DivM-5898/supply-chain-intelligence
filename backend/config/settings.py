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
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY", "")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", "AIzaSyCEkfJRwoFvdBKh6RP-gGlil80dxm4CGo8")
    
    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_ENABLED: bool = os.getenv("KAFKA_ENABLED", "false").lower() == "true"
    
    # Redis Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_ENABLED: bool = os.getenv("REDIS_ENABLED", "false").lower() == "true"
    
    # WebSocket Configuration
    WEBSOCKET_ENABLED: bool = True
    
    # Security Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MFA_ENABLED: bool = True
    
    # CORS Configuration
    CORS_ORIGINS: list = [
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ]
    
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

