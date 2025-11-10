"""
Risk Prediction Service
Logistic Regression and Anomaly Detection for supplier risk prediction
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import IsolationForest
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


class RiskPredictionService:
    """Service for predicting supplier risks and disruptions"""
    
    def __init__(self, models_dir: str = "models/saved_models"):
        # Resolve absolute path
        backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if not os.path.isabs(models_dir):
            self.models_dir = os.path.join(backend_path, models_dir)
        else:
            self.models_dir = models_dir
        os.makedirs(self.models_dir, exist_ok=True)
        self.logistic_model = None
        self.anomaly_detector = None
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.is_trained = False
    
    def prepare_training_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare training data for risk prediction
        Creates binary labels based on risk events
        """
        suppliers_df = data_loader.load_suppliers()
        risk_events_df = data_loader.load_risk_events()
        
        # Merge risk events with suppliers
        df = preprocessor.create_risk_features(suppliers_df, risk_events_df)
        df, feature_cols = preprocessor.prepare_supplier_features(df)
        self.feature_columns = feature_cols
        
        # Create binary target: 1 if high risk (critical events > 0 or avg impact > 0.5)
        # Ensure we have both classes by using top 30% as high risk
        if 'critical_events' in df.columns and 'avg_impact_score' in df.columns:
            df['is_high_risk'] = (
                (df['critical_events'] > 0) |
                (df['avg_impact_score'] > df['avg_impact_score'].quantile(0.7))
            ).astype(int)
        else:
            # Fallback: use top 30% of risk scores
            risk_scores = df.get('geopolitical_risk_score', pd.Series([0.5]*len(df)))
            df['is_high_risk'] = (risk_scores > risk_scores.quantile(0.7)).astype(int)
        
        # Fill missing risk features
        risk_features = ['avg_impact_score', 'max_impact_score', 'risk_event_count', 'critical_events']
        for feat in risk_features:
            if feat in df.columns:
                df[feat] = df[feat].fillna(0)
                if feat not in feature_cols:
                    feature_cols.append(feat)
        
        X = df[feature_cols].fillna(0)
        y = df['is_high_risk']
        
        self.feature_columns = feature_cols
        
        return X, y
    
    def train_logistic_regression(self, X: pd.DataFrame, y: pd.Series,
                                 params: Optional[Dict] = None) -> Dict:
        """Train Logistic Regression model for risk prediction"""
        if params is None:
            params = {
                'max_iter': 1000,
                'random_state': 42,
                'solver': 'lbfgs'
            }
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.logistic_model = LogisticRegression(**params)
        self.logistic_model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred_train = self.logistic_model.predict(X_train_scaled)
        y_pred_test = self.logistic_model.predict(X_test_scaled)
        y_pred_proba_test = self.logistic_model.predict_proba(X_test_scaled)[:, 1]
        
        train_report = classification_report(y_train, y_pred_train, output_dict=True)
        test_report = classification_report(y_test, y_pred_test, output_dict=True)
        auc_score = roc_auc_score(y_test, y_pred_proba_test)
        
        # Save model
        model_path = os.path.join(self.models_dir, "logistic_risk_prediction.pkl")
        joblib.dump(self.logistic_model, model_path)
        scaler_path = os.path.join(self.models_dir, "risk_scaler.pkl")
        joblib.dump(self.scaler, scaler_path)
        
        self.is_trained = True
        
        return {
            'model': 'Logistic Regression',
            'train_accuracy': train_report['accuracy'],
            'test_accuracy': test_report['accuracy'],
            'test_auc': auc_score,
            'classification_report': test_report,
            'feature_coefficients': dict(zip(self.feature_columns,
                                           self.logistic_model.coef_[0]))
        }
    
    def train_anomaly_detector(self, X: pd.DataFrame,
                              contamination: float = 0.1) -> Dict:
        """Train Isolation Forest for anomaly detection"""
        # Use all data for anomaly detection (unsupervised)
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.anomaly_detector = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.anomaly_detector.fit(X_scaled)
        
        # Predict anomalies
        anomalies = self.anomaly_detector.predict(X_scaled)
        anomaly_scores = self.anomaly_detector.score_samples(X_scaled)
        
        # Save model
        model_path = os.path.join(self.models_dir, "isolation_forest.pkl")
        joblib.dump(self.anomaly_detector, model_path)
        
        return {
            'model': 'Isolation Forest',
            'n_anomalies': (anomalies == -1).sum(),
            'anomaly_rate': (anomalies == -1).mean(),
            'avg_anomaly_score': anomaly_scores.mean()
        }
    
    def train_both_models(self) -> Dict:
        """Train both Logistic Regression and Anomaly Detection models"""
        X, y = self.prepare_training_data()
        
        lr_results = self.train_logistic_regression(X, y)
        anomaly_results = self.train_anomaly_detector(X)
        
        return {
            'logistic_regression': lr_results,
            'anomaly_detection': anomaly_results
        }
    
    def load_models(self):
        """Load trained models from disk"""
        lr_path = os.path.join(self.models_dir, "logistic_risk_prediction.pkl")
        anomaly_path = os.path.join(self.models_dir, "isolation_forest.pkl")
        scaler_path = os.path.join(self.models_dir, "risk_scaler.pkl")
        
        if os.path.exists(lr_path):
            self.logistic_model = joblib.load(lr_path)
        if os.path.exists(anomaly_path):
            self.anomaly_detector = joblib.load(anomaly_path)
        if os.path.exists(scaler_path):
            self.scaler = joblib.load(scaler_path)
        
        # Load feature columns
        suppliers_df = data_loader.load_suppliers()
        _, self.feature_columns = preprocessor.prepare_supplier_features(suppliers_df)
    
    def predict_risk(self, supplier_ids: List[str]) -> pd.DataFrame:
        """
        Predict risk probability for suppliers
        Returns DataFrame with risk predictions
        """
        if not self.logistic_model:
            self.load_models()
        
        suppliers_df = data_loader.load_suppliers()
        risk_events_df = data_loader.load_risk_events()
        
        df = preprocessor.create_risk_features(suppliers_df, risk_events_df)
        df, _ = preprocessor.prepare_supplier_features(df)
        
        # Filter to requested suppliers
        if supplier_ids:
            df = df[df['supplier_id'].isin(supplier_ids)]
        
        X = df[self.feature_columns].fillna(0)
        X_scaled = self.scaler.transform(X)
        
        # Predict risk probability
        risk_proba = self.logistic_model.predict_proba(X_scaled)[:, 1]
        risk_pred = self.logistic_model.predict(X_scaled)
        
        results = pd.DataFrame({
            'supplier_id': df['supplier_id'].values,
            'risk_probability': risk_proba,
            'is_high_risk': risk_pred,
            'risk_level': pd.cut(risk_proba, 
                               bins=[0, 0.3, 0.7, 1.0],
                               labels=['Low', 'Medium', 'High'])
        })
        
        return results.sort_values('risk_probability', ascending=False)
    
    def detect_anomalies(self, supplier_ids: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Detect anomalous suppliers using Isolation Forest
        """
        if not self.anomaly_detector:
            self.load_models()
        
        suppliers_df = data_loader.load_suppliers()
        df, _ = preprocessor.prepare_supplier_features(suppliers_df)
        
        if supplier_ids:
            df = df[df['supplier_id'].isin(supplier_ids)]
        
        X = df[self.feature_columns].fillna(0)
        X_scaled = self.scaler.transform(X)
        
        # Detect anomalies
        anomalies = self.anomaly_detector.predict(X_scaled)
        anomaly_scores = self.anomaly_detector.score_samples(X_scaled)
        
        results = pd.DataFrame({
            'supplier_id': df['supplier_id'].values,
            'is_anomaly': (anomalies == -1),
            'anomaly_score': anomaly_scores,
            'severity': pd.cut(-anomaly_scores,
                              bins=[-np.inf, -0.5, -0.3, np.inf],
                              labels=['High', 'Medium', 'Low'])
        })
        
        return results.sort_values('anomaly_score')


# Global instance
risk_prediction_service = RiskPredictionService()

