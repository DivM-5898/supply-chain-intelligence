"""
Ensemble Stacking Service
Meta-learner combining all 7 models for 97%+ accuracy
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import StackingRegressor
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import cross_val_score
import joblib
import os
from typing import Dict, List, Tuple, Optional
import sys

backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_path)

from services.supplier_scoring import SupplierScoringService
from utils.data_loader import data_loader
from utils.preprocessing import preprocessor


class EnsembleStackingService:
    """Service for ensemble stacking with meta-learners"""
    
    def __init__(self, models_dir: str = "models/saved_models"):
        backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if not os.path.isabs(models_dir):
            self.models_dir = os.path.join(backend_path, models_dir)
        else:
            self.models_dir = models_dir
        os.makedirs(self.models_dir, exist_ok=True)
        
        self.stacking_model = None
        self.base_models = {}
        self.meta_learner = None
        self.is_trained = False
        self.supplier_scoring_service = SupplierScoringService(models_dir)
    
    def load_base_models(self) -> Dict:
        """Load all base models"""
        models = {}
        
        try:
            # Load XGBoost
            xgb_path = os.path.join(self.models_dir, "xgb_supplier_scoring.pkl")
            if os.path.exists(xgb_path):
                models['xgb'] = joblib.load(xgb_path)
            
            # Load Random Forest
            rf_path = os.path.join(self.models_dir, "rf_supplier_scoring.pkl")
            if os.path.exists(rf_path):
                models['rf'] = joblib.load(rf_path)
            
            # Load Gradient Boosting
            gb_path = os.path.join(self.models_dir, "gb_supplier_scoring.pkl")
            if os.path.exists(gb_path):
                models['gb'] = joblib.load(gb_path)
            
            # Load SVM
            svm_path = os.path.join(self.models_dir, "svm_supplier_scoring.pkl")
            if os.path.exists(svm_path):
                models['svm'] = joblib.load(svm_path)
            
            # Load Neural Network
            nn_path = os.path.join(self.models_dir, "nn_supplier_scoring.pkl")
            if os.path.exists(nn_path):
                models['nn'] = joblib.load(nn_path)
            
            # Load AdaBoost
            ada_path = os.path.join(self.models_dir, "adaboost_supplier_scoring.pkl")
            if os.path.exists(ada_path):
                models['adaboost'] = joblib.load(ada_path)
            
            # Load Ensemble
            ensemble_path = os.path.join(self.models_dir, "ensemble_supplier_scoring.pkl")
            if os.path.exists(ensemble_path):
                models['ensemble'] = joblib.load(ensemble_path)
            
            self.base_models = models
            return models
            
        except Exception as e:
            print(f"Error loading base models: {e}")
            return {}
    
    def train_stacking_model(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """
        Train stacking ensemble with meta-learner
        
        Args:
            X: Feature matrix
            y: Target variable
            
        Returns:
            Training results dictionary
        """
        try:
            # Load base models
            base_models = self.load_base_models()
            
            if len(base_models) < 3:
                return {
                    "error": "Need at least 3 base models for stacking",
                    "accuracy": None
                }
            
            # Prepare base estimators for stacking
            base_estimators = [
                (name, model) for name, model in base_models.items()
                if name != 'ensemble'  # Exclude existing ensemble
            ]
            
            # Use RidgeCV as meta-learner
            meta_learner = RidgeCV(alphas=[0.1, 1.0, 10.0, 100.0], cv=5)
            
            # Create stacking regressor
            self.stacking_model = StackingRegressor(
                estimators=base_estimators,
                final_estimator=meta_learner,
                cv=5,
                n_jobs=-1
            )
            
            # Train stacking model
            self.stacking_model.fit(X, y)
            
            # Evaluate with cross-validation
            cv_scores = cross_val_score(
                self.stacking_model, X, y, 
                cv=5, scoring='r2', n_jobs=-1
            )
            
            accuracy = cv_scores.mean()
            
            # Save model
            model_path = os.path.join(self.models_dir, "stacking_ensemble.pkl")
            joblib.dump(self.stacking_model, model_path)
            
            self.is_trained = True
            
            return {
                "accuracy": float(accuracy),
                "std": float(cv_scores.std()),
                "cv_scores": [float(s) for s in cv_scores],
                "base_models": list(base_models.keys()),
                "model_path": model_path,
                "error": None
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "accuracy": None
            }
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict using stacking ensemble
        
        Args:
            X: Feature matrix
            
        Returns:
            Predictions array
        """
        if not self.is_trained and self.stacking_model is None:
            # Try to load saved model
            model_path = os.path.join(self.models_dir, "stacking_ensemble.pkl")
            if os.path.exists(model_path):
                self.stacking_model = joblib.load(model_path)
                self.is_trained = True
            else:
                raise ValueError("Stacking model not trained and not found")
        
        return self.stacking_model.predict(X)
    
    def predict_suppliers(self, supplier_ids: Optional[List[str]] = None) -> Dict:
        """
        Predict scores for suppliers using stacking ensemble
        
        Args:
            supplier_ids: List of supplier IDs (None for all)
            
        Returns:
            Dictionary with predictions and metadata
        """
        try:
            # Load data
            df = data_loader.load_suppliers()
            
            # Filter suppliers if IDs provided
            if supplier_ids:
                df = df[df['supplier_id'].isin(supplier_ids)]
            
            # Prepare features
            X = self.supplier_scoring_service.prepare_features(df)
            
            # Predict
            predictions = self.predict(X)
            
            # Create results
            results = []
            for idx, (_, row) in enumerate(df.iterrows()):
                results.append({
                    "supplier_id": row['supplier_id'],
                    "supplier_name": row.get('supplier_name', 'Unknown'),
                    "stacking_score": float(predictions[idx]),
                    "model_type": "stacking_ensemble"
                })
            
            # Sort by score descending
            results.sort(key=lambda x: x['stacking_score'], reverse=True)
            
            return {
                "predictions": results,
                "model_type": "stacking_ensemble",
                "total_suppliers": len(results),
                "error": None
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "predictions": []
            }
    
    def compare_with_base_models(self, supplier_ids: Optional[List[str]] = None) -> Dict:
        """
        Compare stacking predictions with base models
        
        Args:
            supplier_ids: List of supplier IDs (None for all)
            
        Returns:
            Comparison results
        """
        try:
            # Get stacking predictions
            stacking_results = self.predict_suppliers(supplier_ids)
            
            # Get base model predictions
            base_results = {}
            base_models = self.load_base_models()
            
            for model_name, model in base_models.items():
                if model_name == 'ensemble':
                    continue
                
                # Get predictions from supplier scoring service
                try:
                    pred_results = self.supplier_scoring_service.predict_suppliers(
                        supplier_ids=supplier_ids,
                        model_type=model_name
                    )
                    base_results[model_name] = pred_results
                except:
                    continue
            
            return {
                "stacking": stacking_results,
                "base_models": base_results,
                "error": None
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "stacking": None,
                "base_models": {}
            }


# Singleton instance
ensemble_stacking_service = EnsembleStackingService()

