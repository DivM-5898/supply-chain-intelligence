"""
Anomaly Detection Module for Fraud Detection
Implements multiple anomaly detection algorithms for identifying unusual patterns
in supply chain transactions.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from typing import Dict, List, Tuple, Optional
import joblib


class AnomalyDetector:
    """
    Multi-algorithm anomaly detection system for fraud detection.
    Combines Isolation Forest, One-Class SVM, and statistical methods.
    """
    
    def __init__(
        self,
        contamination: float = 0.05,
        n_estimators: int = 100,
        random_state: int = 42
    ):
        """
        Initialize anomaly detector with multiple algorithms.
        
        Args:
            contamination: Expected proportion of anomalies in dataset
            n_estimators: Number of trees for Isolation Forest
            random_state: Random seed for reproducibility
        """
        self.contamination = contamination
        self.random_state = random_state
        
        # Initialize models
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            random_state=random_state,
            n_jobs=-1
        )
        
        self.one_class_svm = OneClassSVM(
            nu=contamination,
            kernel='rbf',
            gamma='auto'
        )
        
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=0.95)  # Retain 95% variance
        
        self.is_fitted = False
        self.feature_names = None
        
    def fit(self, X: pd.DataFrame, use_pca: bool = True) -> 'AnomalyDetector':
        """
        Fit anomaly detection models on training data.
        
        Args:
            X: Training features
            use_pca: Whether to apply PCA for dimensionality reduction
            
        Returns:
            self
        """
        self.feature_names = X.columns.tolist()
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Apply PCA if requested
        if use_pca and X_scaled.shape[1] > 10:
            X_transformed = self.pca.fit_transform(X_scaled)
        else:
            X_transformed = X_scaled
            
        # Fit models
        print("Fitting Isolation Forest...")
        self.isolation_forest.fit(X_transformed)
        
        print("Fitting One-Class SVM...")
        self.one_class_svm.fit(X_transformed)
        
        self.is_fitted = True
        print(f"Anomaly detection models fitted on {len(X)} samples")
        
        return self
    
    def predict(
        self,
        X: pd.DataFrame,
        ensemble: bool = True
    ) -> Dict[str, np.ndarray]:
        """
        Predict anomalies using fitted models.
        
        Args:
            X: Features to predict
            ensemble: Use ensemble of models for final prediction
            
        Returns:
            Dictionary with predictions and scores
        """
        if not self.is_fitted:
            raise ValueError("Models must be fitted before prediction")
            
        # Transform features
        X_scaled = self.scaler.transform(X)
        
        if hasattr(self.pca, 'components_'):
            X_transformed = self.pca.transform(X_scaled)
        else:
            X_transformed = X_scaled
            
        # Get predictions from each model
        if_predictions = self.isolation_forest.predict(X_transformed)
        if_scores = self.isolation_forest.score_samples(X_transformed)
        
        svm_predictions = self.one_class_svm.predict(X_transformed)
        
        # Convert predictions: -1 (anomaly) to 1, 1 (normal) to 0
        if_anomalies = (if_predictions == -1).astype(int)
        svm_anomalies = (svm_predictions == -1).astype(int)
        
        # Statistical anomaly detection (Z-score based)
        stat_anomalies = self._statistical_anomaly_detection(X_scaled)
        
        results = {
            'isolation_forest_predictions': if_anomalies,
            'isolation_forest_scores': if_scores,
            'one_class_svm_predictions': svm_anomalies,
            'statistical_predictions': stat_anomalies
        }
        
        # Ensemble prediction (majority voting)
        if ensemble:
            ensemble_predictions = (
                if_anomalies + svm_anomalies + stat_anomalies
            ) >= 2
            results['ensemble_predictions'] = ensemble_predictions.astype(int)
            results['anomaly_score'] = (
                if_anomalies + svm_anomalies + stat_anomalies
            ) / 3.0
            
        return results
    
    def _statistical_anomaly_detection(
        self,
        X_scaled: np.ndarray,
        threshold: float = 3.0
    ) -> np.ndarray:
        """
        Statistical anomaly detection using Z-scores.
        
        Args:
            X_scaled: Scaled features
            threshold: Z-score threshold for anomaly
            
        Returns:
            Binary array indicating anomalies
        """
        # Calculate Z-scores for each feature
        z_scores = np.abs(X_scaled)
        
        # A sample is anomalous if any feature has |z-score| > threshold
        anomalies = np.any(z_scores > threshold, axis=1)
        
        return anomalies.astype(int)
    
    def get_anomaly_explanation(
        self,
        X: pd.DataFrame,
        sample_idx: int,
        top_n: int = 5
    ) -> Dict[str, any]:
        """
        Explain why a sample was flagged as anomaly.
        
        Args:
            X: Features dataframe
            sample_idx: Index of sample to explain
            top_n: Number of top contributing features
            
        Returns:
            Dictionary with explanation details
        """
        if not self.is_fitted:
            raise ValueError("Models must be fitted before explanation")
            
        sample = X.iloc[sample_idx:sample_idx+1]
        X_scaled = self.scaler.transform(sample)
        
        # Get feature contributions (Z-scores)
        z_scores = np.abs(X_scaled[0])
        
        # Get top contributing features
        top_indices = np.argsort(z_scores)[::-1][:top_n]
        
        explanation = {
            'sample_index': sample_idx,
            'top_anomalous_features': [
                {
                    'feature': self.feature_names[idx],
                    'value': float(sample.iloc[0, idx]),
                    'z_score': float(z_scores[idx])
                }
                for idx in top_indices
            ]
        }
        
        return explanation
    
    def save_model(self, filepath: str):
        """Save trained model to disk."""
        joblib.dump({
            'isolation_forest': self.isolation_forest,
            'one_class_svm': self.one_class_svm,
            'scaler': self.scaler,
            'pca': self.pca,
            'feature_names': self.feature_names,
            'contamination': self.contamination
        }, filepath)
        print(f"Model saved to {filepath}")
    
    @classmethod
    def load_model(cls, filepath: str) -> 'AnomalyDetector':
        """Load trained model from disk."""
        data = joblib.load(filepath)
        
        detector = cls(contamination=data['contamination'])
        detector.isolation_forest = data['isolation_forest']
        detector.one_class_svm = data['one_class_svm']
        detector.scaler = data['scaler']
        detector.pca = data['pca']
        detector.feature_names = data['feature_names']
        detector.is_fitted = True
        
        print(f"Model loaded from {filepath}")
        return detector


class TransactionAnomalyDetector(AnomalyDetector):
    """
    Specialized anomaly detector for transaction data.
    Includes domain-specific feature engineering and rules.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transaction_stats = None
        
    def fit(
        self,
        transactions: pd.DataFrame,
        use_pca: bool = True
    ) -> 'TransactionAnomalyDetector':
        """
        Fit on transaction data with enhanced features.
        
        Args:
            transactions: Transaction dataframe
            use_pca: Whether to apply PCA
            
        Returns:
            self
        """
        # Calculate transaction statistics for rule-based detection
        self.transaction_stats = {
            'amount_mean': transactions['amount'].mean(),
            'amount_std': transactions['amount'].std(),
            'amount_median': transactions['amount'].median(),
            'frequency_mean': transactions.groupby('supplier_id').size().mean()
        }
        
        # Extract features for anomaly detection
        features = self._extract_transaction_features(transactions)
        
        # Fit base anomaly detector
        super().fit(features, use_pca=use_pca)
        
        return self
    
    def predict(
        self,
        transactions: pd.DataFrame,
        ensemble: bool = True
    ) -> Dict[str, np.ndarray]:
        """
        Predict anomalies in transactions.
        
        Args:
            transactions: Transaction dataframe
            ensemble: Use ensemble prediction
            
        Returns:
            Dictionary with predictions and explanations
        """
        # Extract features
        features = self._extract_transaction_features(transactions)
        
        # Get base predictions
        results = super().predict(features, ensemble=ensemble)
        
        # Add rule-based anomaly flags
        results['rule_based_flags'] = self._apply_business_rules(transactions)
        
        return results
    
    def _extract_transaction_features(
        self,
        transactions: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Extract features from transaction data.
        
        Args:
            transactions: Raw transaction data
            
        Returns:
            Feature dataframe
        """
        features = pd.DataFrame()
        
        # Amount-based features
        features['amount'] = transactions['amount']
        features['log_amount'] = np.log1p(transactions['amount'])
        
        # Time-based features
        if 'timestamp' in transactions.columns:
            transactions['timestamp'] = pd.to_datetime(transactions['timestamp'])
            features['hour'] = transactions['timestamp'].dt.hour
            features['day_of_week'] = transactions['timestamp'].dt.dayofweek
            features['is_weekend'] = (features['day_of_week'] >= 5).astype(int)
        
        # Frequency features (if supplier_id available)
        if 'supplier_id' in transactions.columns:
            supplier_counts = transactions.groupby('supplier_id').size()
            features['supplier_transaction_count'] = transactions['supplier_id'].map(supplier_counts)
        
        # Payment method encoding (if available)
        if 'payment_method' in transactions.columns:
            payment_dummies = pd.get_dummies(
                transactions['payment_method'],
                prefix='payment'
            )
            features = pd.concat([features, payment_dummies], axis=1)
        
        return features
    
    def _apply_business_rules(
        self,
        transactions: pd.DataFrame
    ) -> np.ndarray:
        """
        Apply business rule-based anomaly detection.
        
        Args:
            transactions: Transaction dataframe
            
        Returns:
            Binary array indicating rule violations
        """
        flags = np.zeros(len(transactions), dtype=int)
        
        if self.transaction_stats is None:
            return flags
            
        # Rule 1: Unusually large transaction amount
        amount_threshold = (
            self.transaction_stats['amount_mean'] + 
            3 * self.transaction_stats['amount_std']
        )
        flags |= (transactions['amount'] > amount_threshold).values
        
        # Rule 2: Round number amounts (potential fraud indicator)
        if 'amount' in transactions.columns:
            round_amounts = (transactions['amount'] % 1000 == 0).values
            large_amounts = (transactions['amount'] > 10000).values
            flags |= (round_amounts & large_amounts)
        
        # Rule 3: Transactions outside business hours
        if 'timestamp' in transactions.columns:
            transactions['timestamp'] = pd.to_datetime(transactions['timestamp'])
            hour = transactions['timestamp'].dt.hour
            flags |= ((hour < 6) | (hour > 22)).values
        
        return flags
