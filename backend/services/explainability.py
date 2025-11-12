"""
Explainability Service
SHAP and LIME for model interpretability
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import joblib
import os
import sys

backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_path)

# Try to import SHAP
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    shap = None
    print("Warning: SHAP not available, explainability features will be limited")

# Try to import LIME
try:
    import lime
    from lime import lime_tabular
    LIME_AVAILABLE = True
except ImportError:
    LIME_AVAILABLE = False
    lime = None
    lime_tabular = None
    print("Warning: LIME not available, explainability features will be limited")

from utils.data_loader import data_loader
from utils.preprocessing import preprocessor
from services.supplier_scoring import supplier_scoring_service
from services.risk_prediction import risk_prediction_service
from services.fraud_detection import fraud_detection_service


class ExplainabilityService:
    """Service for model explainability using SHAP and LIME"""
    
    def __init__(self):
        self.shap_explainers = {}
        self.lime_explainers = {}
    
    def get_shap_values_supplier_scoring(self, supplier_ids: List[str],
                                        model_type: str = 'xgboost') -> Dict:
        """Get SHAP values for supplier scoring predictions"""
        if not SHAP_AVAILABLE:
            return {'error': 'SHAP not available'}
        
        # Load model and data
        supplier_scoring_service.load_models()
        model = supplier_scoring_service.models.get(model_type)
        
        if model is None:
            return {'error': f'Model {model_type} not found'}
        
        suppliers_df = data_loader.load_suppliers()
        df, feature_cols = preprocessor.prepare_supplier_features(suppliers_df, use_advanced_features=False)
        
        if supplier_ids:
            df = df[df['supplier_id'].isin(supplier_ids)]
        
        X = df[feature_cols].fillna(0)
        
        # Create SHAP explainer
        explainer_key = f"supplier_scoring_{model_type}"
        if explainer_key not in self.shap_explainers:
            if model_type in ['xgboost', 'random_forest', 'gradient_boosting']:
                self.shap_explainers[explainer_key] = shap.TreeExplainer(model)
            else:
                self.shap_explainers[explainer_key] = shap.KernelExplainer(
                    model.predict, X.sample(min(100, len(X)))
                )
        
        explainer = self.shap_explainers[explainer_key]
        shap_values = explainer.shap_values(X)
        
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        
        return {
            'shap_values': shap_values.tolist(),
            'feature_names': feature_cols,
            'supplier_ids': df['supplier_id'].tolist(),
            'base_value': explainer.expected_value if hasattr(explainer, 'expected_value') else None
        }
    
    def get_lime_explanation(self, supplier_id: str, model_type: str = 'xgboost',
                            explanation_type: str = 'lime') -> Dict:
        """Get LIME explanation for a prediction"""
        if not LIME_AVAILABLE:
            return {'error': 'LIME not available'}
        
        supplier_scoring_service.load_models()
        model = supplier_scoring_service.models.get(model_type)
        
        if model is None:
            return {'error': f'Model {model_type} not found'}
        
        suppliers_df = data_loader.load_suppliers()
        df, feature_cols = preprocessor.prepare_supplier_features(suppliers_df, use_advanced_features=False)
        
        supplier_data = df[df['supplier_id'] == supplier_id]
        if supplier_data.empty:
            return {'error': f'Supplier {supplier_id} not found'}
        
        X = df[feature_cols].fillna(0)
        X_supplier = supplier_data[feature_cols].fillna(0).iloc[0].values
        
        # Create LIME explainer
        explainer = lime_tabular.LimeTabularExplainer(
            X.values,
            feature_names=feature_cols,
            mode='regression'
        )
        
        explanation = explainer.explain_instance(X_supplier, model.predict, num_features=10)
        
        # Return properly structured data
        return {
            'supplier_id': supplier_id,
            'explanation': explanation.as_list(),  # List of (feature, contribution) tuples
            'prediction': float(model.predict(X_supplier.reshape(1, -1))[0])
        }
    
    def explain_prediction(self, supplier_id: str, model_type: str = 'xgboost',
                          explanation_type: str = 'lime') -> Dict:
        """Get explanation for a prediction"""
        if explanation_type == 'lime':
            return self.get_lime_explanation(supplier_id, model_type, explanation_type)
        elif explanation_type == 'shap':
            return self.get_shap_values_supplier_scoring([supplier_id], model_type)
        else:
            return {'error': f'Unknown explanation type: {explanation_type}'}
    
    def detect_bias(self, feature_name: str, model_type: str = 'xgboost') -> Dict:
        """Detect bias in model predictions based on a feature"""
        try:
            # Load model and data
            supplier_scoring_service.load_models()
            model = supplier_scoring_service.models.get(model_type)
            
            if model is None:
                return {'error': f'Model {model_type} not found'}
            
            suppliers_df = data_loader.load_suppliers()
            df, feature_cols = preprocessor.prepare_supplier_features(suppliers_df, use_advanced_features=False)
            
            # Check if feature exists
            if feature_name not in df.columns and feature_name not in feature_cols:
                return {'error': f'Feature {feature_name} not found in data'}
            
            X = df[feature_cols].fillna(0)
            
            # Get predictions
            predictions = model.predict(X)
            
            # Get feature values
            if feature_name in df.columns:
                feature_values = df[feature_name].values
            else:
                feature_values = X[feature_name].values
            
            # Calculate correlation
            from scipy.stats import pearsonr, spearmanr
            
            # Handle categorical features
            if df[feature_name].dtype == 'object' or df[feature_name].dtype.name == 'category':
                # Encode categorical feature
                from sklearn.preprocessing import LabelEncoder
                le = LabelEncoder()
                feature_values_encoded = le.fit_transform(feature_values.astype(str))
                correlation, p_value = spearmanr(feature_values_encoded, predictions)
                
                # Group analysis by category
                bias_df = pd.DataFrame({
                    'category': feature_values,
                    'prediction': predictions
                })
                bias_analysis = bias_df.groupby('category').agg({
                    'prediction': ['mean', 'std', 'count']
                }).reset_index()
                bias_analysis.columns = ['Category', 'Avg_Prediction', 'Std_Prediction', 'Count']
                
                return {
                    'feature': feature_name,
                    'correlation': float(correlation),
                    'p_value': float(p_value),
                    'correlation_type': 'spearman',
                    'bias_analysis': bias_analysis.to_dict('records'),
                    'interpretation': self._interpret_bias(correlation)
                }
            else:
                # Numerical feature
                correlation, p_value = pearsonr(feature_values, predictions)
                
                # Bin analysis
                bins = pd.qcut(feature_values, q=5, duplicates='drop')
                bias_df = pd.DataFrame({
                    'bin': bins,
                    'prediction': predictions
                })
                bias_analysis = bias_df.groupby('bin').agg({
                    'prediction': ['mean', 'std', 'count']
                }).reset_index()
                bias_analysis.columns = ['Range', 'Avg_Prediction', 'Std_Prediction', 'Count']
                bias_analysis['Range'] = bias_analysis['Range'].astype(str)
                
                return {
                    'feature': feature_name,
                    'correlation': float(correlation),
                    'p_value': float(p_value),
                    'correlation_type': 'pearson',
                    'bias_analysis': bias_analysis.to_dict('records'),
                    'interpretation': self._interpret_bias(correlation)
                }
        except Exception as e:
            import traceback
            return {
                'error': str(e),
                'traceback': traceback.format_exc()
            }
    
    def _interpret_bias(self, correlation: float) -> str:
        """Interpret correlation value for bias detection"""
        abs_corr = abs(correlation)
        if abs_corr < 0.1:
            return "Very weak correlation - No significant bias detected"
        elif abs_corr < 0.3:
            return "Weak correlation - Low bias concern"
        elif abs_corr < 0.5:
            return "Moderate correlation - Potential bias detected"
        elif abs_corr < 0.7:
            return "Strong correlation - Significant bias detected"
        else:
            return "Very strong correlation - Critical bias detected"


# Global instance
explainability_service = ExplainabilityService()
