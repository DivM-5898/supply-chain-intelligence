"""
Fraud Detection Service
Classification models for detecting potential fraud patterns
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.preprocessing import StandardScaler
import joblib
import os
from typing import Dict, List, Tuple, Optional
import sys
import os
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_path)
from utils.data_loader import data_loader
from utils.preprocessing import preprocessor


class FraudDetectionService:
    """Service for detecting potential fraud in supplier data"""
    
    def __init__(self, models_dir: str = "models/saved_models"):
        # Resolve absolute path
        backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if not os.path.isabs(models_dir):
            self.models_dir = os.path.join(backend_path, models_dir)
        else:
            self.models_dir = models_dir
        os.makedirs(self.models_dir, exist_ok=True)
        self.rf_model = None
        self.gb_model = None
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.is_trained = False
    
    def prepare_training_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare training data for fraud detection
        Creates fraud labels based on suspicious patterns
        """
        suppliers_df = data_loader.load_suppliers()
        df, _ = preprocessor.prepare_fraud_features(suppliers_df)
        self.feature_columns = df.columns.tolist()
        self.feature_columns.remove('supplier_id')
        
        # Create fraud labels based on multiple suspicious indicators
        # Fraud if: suspicious_financial >= 2 OR suspicious_operational >= 2
        df['is_fraud'] = (
            (df['suspicious_financial'] >= 2) |
            (df['suspicious_operational'] >= 2) |
            ((df['credit_score'] < 400) & (df['profit_margin'] < 0.02)) |
            ((df['on_time_delivery_rate'] < 0.60) & (df['defect_rate'] > 0.10))
        ).astype(int)
        
        X = df[self.feature_columns].fillna(0)
        y = df['is_fraud']
        
        return X, y
    
    def train_random_forest(self, X: pd.DataFrame, y: pd.Series,
                           params: Optional[Dict] = None) -> Dict:
        """Train Random Forest for fraud detection"""
        if params is None:
            params = {
                'n_estimators': 100,
                'max_depth': 10,
                'random_state': 42,
                'class_weight': 'balanced'
            }
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.rf_model = RandomForestClassifier(**params)
        self.rf_model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred_train = self.rf_model.predict(X_train_scaled)
        y_pred_test = self.rf_model.predict(X_test_scaled)
        y_pred_proba_test = self.rf_model.predict_proba(X_test_scaled)[:, 1]
        
        train_report = classification_report(y_train, y_pred_train, output_dict=True)
        test_report = classification_report(y_test, y_pred_test, output_dict=True)
        auc_score = roc_auc_score(y_test, y_pred_proba_test)
        
        # Save model
        model_path = os.path.join(self.models_dir, "rf_fraud_detection.pkl")
        joblib.dump(self.rf_model, model_path)
        scaler_path = os.path.join(self.models_dir, "fraud_scaler.pkl")
        joblib.dump(self.scaler, scaler_path)
        
        self.is_trained = True
        
        return {
            'model': 'Random Forest',
            'train_accuracy': train_report['accuracy'],
            'test_accuracy': test_report['accuracy'],
            'test_auc': auc_score,
            'classification_report': test_report,
            'feature_importance': dict(zip(self.feature_columns,
                                         self.rf_model.feature_importances_))
        }
    
    def train_gradient_boosting(self, X: pd.DataFrame, y: pd.Series,
                               params: Optional[Dict] = None) -> Dict:
        """Train Gradient Boosting for fraud detection"""
        if params is None:
            params = {
                'n_estimators': 100,
                'learning_rate': 0.1,
                'max_depth': 5,
                'random_state': 42
            }
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.gb_model = GradientBoostingClassifier(**params)
        self.gb_model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred_train = self.gb_model.predict(X_train_scaled)
        y_pred_test = self.gb_model.predict(X_test_scaled)
        y_pred_proba_test = self.gb_model.predict_proba(X_test_scaled)[:, 1]
        
        train_report = classification_report(y_train, y_pred_train, output_dict=True)
        test_report = classification_report(y_test, y_pred_test, output_dict=True)
        auc_score = roc_auc_score(y_test, y_pred_proba_test)
        
        # Save model
        model_path = os.path.join(self.models_dir, "gb_fraud_detection.pkl")
        joblib.dump(self.gb_model, model_path)
        
        self.is_trained = True
        
        return {
            'model': 'Gradient Boosting',
            'train_accuracy': train_report['accuracy'],
            'test_accuracy': test_report['accuracy'],
            'test_auc': auc_score,
            'classification_report': test_report,
            'feature_importance': dict(zip(self.feature_columns,
                                         self.gb_model.feature_importances_))
        }
    
    def train_both_models(self) -> Dict:
        """Train both Random Forest and Gradient Boosting models"""
        X, y = self.prepare_training_data()
        
        rf_results = self.train_random_forest(X, y)
        gb_results = self.train_gradient_boosting(X, y)
        
        return {
            'random_forest': rf_results,
            'gradient_boosting': gb_results
        }
    
    def load_models(self):
        """Load trained models from disk"""
        rf_path = os.path.join(self.models_dir, "rf_fraud_detection.pkl")
        gb_path = os.path.join(self.models_dir, "gb_fraud_detection.pkl")
        scaler_path = os.path.join(self.models_dir, "fraud_scaler.pkl")
        
        if os.path.exists(rf_path):
            self.rf_model = joblib.load(rf_path)
        if os.path.exists(gb_path):
            self.gb_model = joblib.load(gb_path)
        if os.path.exists(scaler_path):
            self.scaler = joblib.load(scaler_path)
        
        # Load feature columns
        suppliers_df = data_loader.load_suppliers()
        df, _ = preprocessor.prepare_fraud_features(suppliers_df)
        self.feature_columns = [col for col in df.columns if col != 'supplier_id']
    
    def predict_fraud(self, supplier_ids: List[str],
                     model_type: str = 'random_forest') -> pd.DataFrame:
        """
        Predict fraud probability for suppliers
        """
        if not self.rf_model and not self.gb_model:
            self.load_models()
        
        suppliers_df = data_loader.load_suppliers()
        df, _ = preprocessor.prepare_fraud_features(suppliers_df)
        
        if supplier_ids:
            df = df[df['supplier_id'].isin(supplier_ids)]
        
        X = df[self.feature_columns].fillna(0)
        X_scaled = self.scaler.transform(X)
        
        # Predict with selected model
        if model_type == 'random_forest' and self.rf_model:
            fraud_proba = self.rf_model.predict_proba(X_scaled)[:, 1]
            fraud_pred = self.rf_model.predict(X_scaled)
        elif model_type == 'gradient_boosting' and self.gb_model:
            fraud_proba = self.gb_model.predict_proba(X_scaled)[:, 1]
            fraud_pred = self.gb_model.predict(X_scaled)
        else:
            raise ValueError(f"Model {model_type} not available")
        
        # Calculate fraud risk with proper handling of edge cases
        fraud_risk = []
        for prob in fraud_proba:
            if pd.isna(prob) or np.isnan(prob):
                fraud_risk.append('Unknown')
            elif prob < 0.3:
                fraud_risk.append('Low')
            elif prob < 0.7:
                fraud_risk.append('Medium')
            else:
                fraud_risk.append('High')
        
        results = pd.DataFrame({
            'supplier_id': df['supplier_id'].values,
            'fraud_probability': fraud_proba,
            'is_fraud': fraud_pred.tolist(),  # Convert numpy array to list for JSON serialization
            'fraud_risk': fraud_risk  # Use calculated risk levels
        })
        
        return results.sort_values('fraud_probability', ascending=False)
    
    def compare_models(self, supplier_ids: Optional[List[str]] = None) -> pd.DataFrame:
        """Compare fraud predictions from both models"""
        if not self.rf_model or not self.gb_model:
            self.load_models()
        
        rf_results = self.predict_fraud(supplier_ids, model_type='random_forest')
        gb_results = self.predict_fraud(supplier_ids, model_type='gradient_boosting')
        
        comparison = pd.merge(
            rf_results[['supplier_id', 'fraud_probability', 'is_fraud']],
            gb_results[['supplier_id', 'fraud_probability', 'is_fraud']],
            on='supplier_id',
            suffixes=('_rf', '_gb')
        )
        
        comparison['avg_fraud_probability'] = (
            comparison['fraud_probability_rf'] + comparison['fraud_probability_gb']
        ) / 2
        comparison['agreement'] = (
            comparison['is_fraud_rf'] == comparison['is_fraud_gb']
        )
        
        return comparison.sort_values('avg_fraud_probability', ascending=False)


# Global instance
fraud_detection_service = FraudDetectionService()

