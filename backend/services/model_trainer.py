"""
Model Trainer Service
Orchestrates training of all ML models
"""

import os
from typing import Dict
import sys
import os
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_path)
from services.supplier_scoring import supplier_scoring_service
from services.risk_prediction import risk_prediction_service
from services.fraud_detection import fraud_detection_service
from services.data_generator import DataGenerator


class ModelTrainer:
    """Service to train all ML models"""
    
    def __init__(self):
        self.training_results = {}
    
    def generate_data(self):
        """Generate synthetic datasets"""
        print("Generating synthetic datasets...")
        generator = DataGenerator()
        generator.generate_all()
        print("Data generation complete!")
    
    def train_all_models(self) -> Dict:
        """Train all ML models"""
        print("\n" + "="*50)
        print("Training Supplier Scoring Models...")
        print("="*50)
        supplier_results = supplier_scoring_service.train_both_models()
        self.training_results['supplier_scoring'] = supplier_results
        
        print("\n" + "="*50)
        print("Training Risk Prediction Models...")
        print("="*50)
        risk_results = risk_prediction_service.train_both_models()
        self.training_results['risk_prediction'] = risk_results
        
        print("\n" + "="*50)
        print("Training Fraud Detection Models...")
        print("="*50)
        fraud_results = fraud_detection_service.train_both_models()
        self.training_results['fraud_detection'] = fraud_results
        
        print("\n" + "="*50)
        print("All models trained successfully!")
        print("="*50)
        
        return self.training_results
    
    def train_all(self):
        """Complete training pipeline: generate data and train models"""
        # Generate data if not exists
        if not os.path.exists("data/raw/suppliers.csv"):
            self.generate_data()
        
        # Train all models
        return self.train_all_models()


if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.train_all()

