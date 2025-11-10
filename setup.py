"""
Setup Script
Run this to initialize the project: generate data and train models
"""

import os
import sys

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

def main():
    print("="*60)
    print("AI Supplier Selection Dashboard - Setup")
    print("="*60)
    
    # Change to backend directory
    os.chdir(backend_path)
    
    print("\n1. Generating synthetic datasets...")
    from services.data_generator import DataGenerator
    generator = DataGenerator()
    generator.generate_all()
    
    print("\n2. Training ML models...")
    from services.model_trainer import ModelTrainer
    trainer = ModelTrainer()
    trainer.train_all_models()
    
    print("\n" + "="*60)
    print("Setup complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Start backend: cd backend && uvicorn main:app --reload")
    print("2. Start frontend: cd frontend && streamlit run main.py")
    print("="*60)

if __name__ == "__main__":
    main()

