"""
Training Script - Run this to train all models
"""
import sys
import os

# Add backend to Python path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

# Now import and run training
from services.model_trainer import ModelTrainer

if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.train_all()

