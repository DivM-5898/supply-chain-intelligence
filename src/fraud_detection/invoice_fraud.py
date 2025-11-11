"""
Invoice Fraud Detection Module
Implements classification models and rule-based systems for detecting fraudulent invoices.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import xgboost as xgb
from typing import Dict, List, Tuple, Optional
import joblib
import hashlib


class InvoiceFraudDetector:
    """
    Machine learning-based invoice fraud detection system.
    Detects duplicate invoices, price manipulation, and fake vendors.
    """
    
    def __init__(
        self,
        model_type: str = 'xgboost',
        random_state: int = 42
    ):
        """
        Initialize invoice fraud detector.
        
        Args:
            model_type: Type of model ('xgboost', 'random_forest', 'gradient_boosting')
            random_state: Random seed
        """
        self.random_state = random_state
        self.model_type = model_type
        
        # Initialize model based on type
        if model_type == 'xgboost':
            self.model = xgb.XGBClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                random_state=random_state,
                use_label_encoder=False,
                eval_metric='logloss'
            )
        elif model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                random_state=random_state,
                n_jobs=-1
            )
        elif model_type == 'gradient_boosting':
            self.model = GradientBoostingClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                random_state=random_state
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
            
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.is_fitted = False
        self.feature_names = None
        self.duplicate_detector = DuplicateInvoiceDetector()
        
    def fit(
        self,
        X: pd.DataFrame,
        y: np.ndarray,
        validation_split: float = 0.2
    ) -> Dict[str, float]:
        """
        Train invoice fraud detection model.
        
        Args:
            X: Feature dataframe
            y: Labels (0=legitimate, 1=fraud)
            validation_split: Fraction of data for validation
            
        Returns:
            Dictionary with training metrics
        """
        self.feature_names = X.columns.tolist()
        
        # Encode categorical features
        X_encoded = self._encode_features(X, fit=True)
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X_encoded, y,
            test_size=validation_split,
            random_state=self.random_state,
            stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        # Train model
        print(f"Training {self.model_type} model...")
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_pred = self.model.predict(X_train_scaled)
        val_pred = self.model.predict(X_val_scaled)
        
        train_proba = self.model.predict_proba(X_train_scaled)[:, 1]
        val_proba = self.model.predict_proba(X_val_scaled)[:, 1]
        
        metrics = {
            'train_accuracy': (train_pred == y_train).mean(),
            'val_accuracy': (val_pred == y_val).mean(),
            'train_auc': roc_auc_score(y_train, train_proba),
            'val_auc': roc_auc_score(y_val, val_proba)
        }
        
        self.is_fitted = True
        
        print("\nTraining Complete!")
        print(f"Training Accuracy: {metrics['train_accuracy']:.4f}")
        print(f"Validation Accuracy: {metrics['val_accuracy']:.4f}")
        print(f"Training AUC: {metrics['train_auc']:.4f}")
        print(f"Validation AUC: {metrics['val_auc']:.4f}")
        
        print("\nValidation Set Classification Report:")
        print(classification_report(y_val, val_pred))
        
        return metrics
    
    def predict(
        self,
        X: pd.DataFrame,
        return_proba: bool = True,
        check_duplicates: bool = True
    ) -> Dict[str, np.ndarray]:
        """
        Predict fraud probability for invoices.
        
        Args:
            X: Feature dataframe
            return_proba: Return probability scores
            check_duplicates: Check for duplicate invoices
            
        Returns:
            Dictionary with predictions and scores
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
            
        # Encode and scale features
        X_encoded = self._encode_features(X, fit=False)
        X_scaled = self.scaler.transform(X_encoded)
        
        # Get predictions
        predictions = self.model.predict(X_scaled)
        
        results = {'predictions': predictions}
        
        if return_proba:
            probabilities = self.model.predict_proba(X_scaled)[:, 1]
            results['fraud_probability'] = probabilities
            
        # Check for duplicates
        if check_duplicates and 'invoice_number' in X.columns:
            duplicate_flags = self.duplicate_detector.check_duplicates(X)
            results['duplicate_flags'] = duplicate_flags
            
        return results
    
    def get_feature_importance(self, top_n: int = 10) -> pd.DataFrame:
        """
        Get feature importance scores.
        
        Args:
            top_n: Number of top features to return
            
        Returns:
            DataFrame with feature importance
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
            
        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
            
            importance_df = pd.DataFrame({
                'feature': self.feature_names,
                'importance': importance
            }).sort_values('importance', ascending=False).head(top_n)
            
            return importance_df
        else:
            print("Model does not support feature importance")
            return None
    
    def _encode_features(
        self,
        X: pd.DataFrame,
        fit: bool = False
    ) -> pd.DataFrame:
        """
        Encode categorical features.
        
        Args:
            X: Feature dataframe
            fit: Whether to fit encoders
            
        Returns:
            Encoded dataframe
        """
        X_encoded = X.copy()
        
        categorical_cols = X.select_dtypes(include=['object']).columns
        
        for col in categorical_cols:
            if fit:
                self.label_encoders[col] = LabelEncoder()
                X_encoded[col] = self.label_encoders[col].fit_transform(
                    X[col].astype(str)
                )
            else:
                if col in self.label_encoders:
                    # Handle unseen categories
                    X_encoded[col] = X[col].astype(str).map(
                        lambda x: self.label_encoders[col].transform([x])[0]
                        if x in self.label_encoders[col].classes_
                        else -1
                    )
                    
        return X_encoded
    
    def save_model(self, filepath: str):
        """Save model to disk."""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_names': self.feature_names,
            'model_type': self.model_type
        }, filepath)
        print(f"Model saved to {filepath}")
    
    @classmethod
    def load_model(cls, filepath: str) -> 'InvoiceFraudDetector':
        """Load model from disk."""
        data = joblib.load(filepath)
        
        detector = cls(model_type=data['model_type'])
        detector.model = data['model']
        detector.scaler = data['scaler']
        detector.label_encoders = data['label_encoders']
        detector.feature_names = data['feature_names']
        detector.is_fitted = True
        
        print(f"Model loaded from {filepath}")
        return detector


class DuplicateInvoiceDetector:
    """
    Detector for duplicate and near-duplicate invoices.
    Uses hashing and similarity matching.
    """
    
    def __init__(self):
        self.invoice_hashes = set()
        self.invoice_database = []
        
    def check_duplicates(
        self,
        invoices: pd.DataFrame,
        threshold: float = 0.95
    ) -> np.ndarray:
        """
        Check for duplicate invoices.
        
        Args:
            invoices: Invoice dataframe
            threshold: Similarity threshold for near-duplicates
            
        Returns:
            Binary array indicating duplicates
        """
        flags = np.zeros(len(invoices), dtype=int)
        
        required_cols = ['invoice_number', 'supplier_id', 'amount']
        if not all(col in invoices.columns for col in required_cols):
            return flags
            
        for idx, row in invoices.iterrows():
            # Create hash of invoice
            invoice_hash = self._create_invoice_hash(row)
            
            # Check exact duplicate
            if invoice_hash in self.invoice_hashes:
                flags[idx] = 1
            else:
                # Check near-duplicate
                if self._is_near_duplicate(row, threshold):
                    flags[idx] = 1
                    
        return flags
    
    def register_invoice(self, invoice: pd.Series):
        """Register a legitimate invoice in the database."""
        invoice_hash = self._create_invoice_hash(invoice)
        self.invoice_hashes.add(invoice_hash)
        self.invoice_database.append(invoice.to_dict())
    
    def _create_invoice_hash(self, invoice: pd.Series) -> str:
        """Create hash for invoice."""
        hash_string = f"{invoice['invoice_number']}_{invoice['supplier_id']}_{invoice['amount']}"
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def _is_near_duplicate(
        self,
        invoice: pd.Series,
        threshold: float
    ) -> bool:
        """
        Check if invoice is near-duplicate of any registered invoice.
        
        Args:
            invoice: Invoice to check
            threshold: Similarity threshold
            
        Returns:
            True if near-duplicate found
        """
        # Simple near-duplicate check based on amount and supplier
        for stored_invoice in self.invoice_database[-1000:]:  # Check last 1000
            if stored_invoice['supplier_id'] == invoice['supplier_id']:
                amount_diff = abs(
                    stored_invoice['amount'] - invoice['amount']
                ) / max(stored_invoice['amount'], invoice['amount'])
                
                if amount_diff < (1 - threshold):
                    return True
                    
        return False


def extract_invoice_features(invoices: pd.DataFrame) -> pd.DataFrame:
    """
    Extract features from raw invoice data for fraud detection.
    
    Args:
        invoices: Raw invoice dataframe
        
    Returns:
        Feature dataframe
    """
    features = pd.DataFrame()
    
    # Basic features
    features['amount'] = invoices['amount']
    features['log_amount'] = np.log1p(invoices['amount'])
    
    # Supplier features
    if 'supplier_id' in invoices.columns:
        features['supplier_id'] = invoices['supplier_id']
        
        # Supplier transaction history
        supplier_counts = invoices.groupby('supplier_id').size()
        features['supplier_invoice_count'] = invoices['supplier_id'].map(supplier_counts)
        
        supplier_avg_amount = invoices.groupby('supplier_id')['amount'].mean()
        features['supplier_avg_amount'] = invoices['supplier_id'].map(supplier_avg_amount)
        
        # Amount deviation from supplier average
        features['amount_deviation'] = (
            features['amount'] - features['supplier_avg_amount']
        ) / features['supplier_avg_amount']
    
    # Time-based features
    if 'invoice_date' in invoices.columns:
        invoices['invoice_date'] = pd.to_datetime(invoices['invoice_date'])
        features['month'] = invoices['invoice_date'].dt.month
        features['day_of_month'] = invoices['invoice_date'].dt.day
        features['day_of_week'] = invoices['invoice_date'].dt.dayofweek
        features['is_month_end'] = (invoices['invoice_date'].dt.day >= 28).astype(int)
    
    # Invoice number patterns
    if 'invoice_number' in invoices.columns:
        features['invoice_number_length'] = invoices['invoice_number'].astype(str).str.len()
        features['has_letters'] = invoices['invoice_number'].astype(str).str.contains('[a-zA-Z]').astype(int)
    
    # Payment terms
    if 'payment_terms' in invoices.columns:
        features['payment_terms'] = invoices['payment_terms']
    
    # Line item count
    if 'line_items' in invoices.columns:
        features['line_item_count'] = invoices['line_items']
    
    # Round number check (fraud indicator)
    features['is_round_number'] = (features['amount'] % 100 == 0).astype(int)
    features['is_very_round'] = (features['amount'] % 1000 == 0).astype(int)
    
    return features
