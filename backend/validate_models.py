"""
Model Validation Script
Checks if all models exist, verifies integrity, and tests with sample data
"""
import sys
import os
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

# Add backend to path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

from services.supplier_scoring import SupplierScoringService
from utils.data_loader import data_loader
from utils.preprocessing import preprocessor


class ModelValidator:
    """Validate all trained models"""
    
    def __init__(self):
        self.service = SupplierScoringService()
        self.expected_models = [
            'xgboost', 'random_forest', 'gradient_boosting', 
            'svm', 'neural_network', 'adaboost', 'ensemble'
        ]
        self.validation_results = {}
        
    def check_model_files_exist(self):
        """Check if all model files exist"""
        print("\n" + "="*60)
        print("STEP 1: Checking Model Files")
        print("="*60)
        
        model_files = {
            'xgboost': 'xgb_supplier_scoring.pkl',
            'random_forest': 'rf_supplier_scoring.pkl',
            'gradient_boosting': 'gb_supplier_scoring.pkl',
            'svm': 'svm_supplier_scoring.pkl',
            'neural_network': 'nn_supplier_scoring.pkl',
            'adaboost': 'adaboost_supplier_scoring.pkl',
            'ensemble': 'ensemble_supplier_scoring.pkl'
        }
        
        all_exist = True
        for model_name, filename in model_files.items():
            filepath = os.path.join(self.service.models_dir, filename)
            exists = os.path.exists(filepath)
            status = "[OK]" if exists else "[MISSING]"
            print(f"  {status} {model_name}: {filename}")
            
            if not exists:
                all_exist = False
        
        return all_exist
    
    def load_models(self):
        """Load all models"""
        print("\n" + "="*60)
        print("STEP 2: Loading Models")
        print("="*60)
        
        try:
            self.service.load_models()
            print(f"[OK] Successfully loaded {len(self.service.models)} models")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to load models: {e}")
            return False
    
    def test_models_with_sample_data(self):
        """Test each model with sample data"""
        print("\n" + "="*60)
        print("STEP 3: Testing Models with Sample Data")
        print("="*60)
        
        try:
            # Load sample data
            suppliers_df = data_loader.load_suppliers()
            sample_df = suppliers_df.head(10).copy()
            
            # Prepare features
            df_processed, feature_cols = preprocessor.prepare_supplier_features(sample_df, use_advanced_features=False)
            X = df_processed[feature_cols].fillna(0)
            
            print(f"\nUsing {len(X)} sample records with {len(feature_cols)} features")
            print(f"Features: {feature_cols}")
            
            all_passed = True
            
            for model_name in self.expected_models:
                if model_name not in self.service.models:
                    print(f"  [SKIP] {model_name}: Not loaded")
                    all_passed = False
                    continue
                
                try:
                    model = self.service.models[model_name]
                    
                    # Scale if needed
                    X_test = X.copy()
                    if model_name in self.service.scalers:
                        X_test = self.service.scalers[model_name].transform(X_test)
                    
                    # Make prediction
                    predictions = model.predict(X_test)
                    
                    # Validate predictions
                    if len(predictions) != len(X):
                        raise ValueError(f"Expected {len(X)} predictions, got {len(predictions)}")
                    
                    # Check prediction range
                    pred_min, pred_max = predictions.min(), predictions.max()
                    pred_mean = predictions.mean()
                    
                    print(f"  [OK] {model_name}: min={pred_min:.4f}, max={pred_max:.4f}, mean={pred_mean:.4f}")
                    
                    self.validation_results[model_name] = {
                        'status': 'passed',
                        'predictions': len(predictions),
                        'min': float(pred_min),
                        'max': float(pred_max),
                        'mean': float(pred_mean)
                    }
                    
                except Exception as e:
                    print(f"  [FAIL] {model_name}: {str(e)}")
                    self.validation_results[model_name] = {
                        'status': 'failed',
                        'error': str(e)
                    }
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            print(f"[ERROR] Failed to test models: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def check_feature_consistency(self):
        """Check if feature columns are consistent"""
        print("\n" + "="*60)
        print("STEP 4: Checking Feature Consistency")
        print("="*60)
        
        try:
            # Get expected features
            if self.service.feature_columns is None:
                print("[WARNING] Feature columns not loaded")
                return False
            
            print(f"\nExpected {len(self.service.feature_columns)} features:")
            for i, col in enumerate(self.service.feature_columns, 1):
                print(f"  {i}. {col}")
            
            # Test preprocessing
            suppliers_df = data_loader.load_suppliers()
            sample_df = suppliers_df.head(1).copy()
            df_processed, feature_cols = preprocessor.prepare_supplier_features(sample_df, use_advanced_features=False)
            
            print(f"\nPreprocessing generates {len(feature_cols)} features:")
            for i, col in enumerate(feature_cols, 1):
                print(f"  {i}. {col}")
            
            # Compare
            if set(self.service.feature_columns) == set(feature_cols):
                print("\n[OK] Feature columns match!")
                return True
            else:
                missing = set(self.service.feature_columns) - set(feature_cols)
                extra = set(feature_cols) - set(self.service.feature_columns)
                
                if missing:
                    print(f"\n[WARNING] Missing features: {missing}")
                if extra:
                    print(f"[WARNING] Extra features: {extra}")
                
                return False
                
        except Exception as e:
            print(f"[ERROR] Failed to check features: {e}")
            return False
    
    def run_full_validation(self):
        """Run complete validation"""
        print("\n" + "="*80)
        print(" MODEL VALIDATION ".center(80, "="))
        print("="*80)
        
        results = {
            'files_exist': self.check_model_files_exist(),
            'models_loaded': self.load_models(),
            'models_tested': False,
            'features_consistent': False
        }
        
        if results['models_loaded']:
            results['models_tested'] = self.test_models_with_sample_data()
            results['features_consistent'] = self.check_feature_consistency()
        
        # Print summary
        print("\n" + "="*80)
        print(" VALIDATION SUMMARY ".center(80, "="))
        print("="*80)
        
        for check, passed in results.items():
            status = "[PASS]" if passed else "[FAIL]"
            print(f"  {status} {check.replace('_', ' ').title()}")
        
        all_passed = all(results.values())
        
        print("\n" + "="*80)
        if all_passed:
            print(" ALL VALIDATIONS PASSED ".center(80, "="))
        else:
            print(" SOME VALIDATIONS FAILED ".center(80, "="))
        print("="*80)
        
        return all_passed


if __name__ == "__main__":
    validator = ModelValidator()
    success = validator.run_full_validation()
    
    sys.exit(0 if success else 1)

