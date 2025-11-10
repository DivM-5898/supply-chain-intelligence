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
        df, feature_cols = preprocessor.prepare_supplier_features(suppliers_df)
        
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
    
    def get_lime_explanation(self, supplier_id: str, model_type: str = 'supplier_scoring',
                            explanation_type: str = 'lime') -> Dict:
        """Get LIME explanation for a prediction"""
        if not LIME_AVAILABLE:
            return {'error': 'LIME not available'}
        
        supplier_scoring_service.load_models()
        model = supplier_scoring_service.models.get(model_type)
        
        if model is None:
            return {'error': f'Model {model_type} not found'}
        
        suppliers_df = data_loader.load_suppliers()
        df, feature_cols = preprocessor.prepare_supplier_features(suppliers_df)
        
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
        
        return {
            'explanation': explanation.as_list(),
            'prediction': float(model.predict(X_supplier.reshape(1, -1))[0]),
            'supplier_id': supplier_id
        }
    
    def explain_prediction(self, supplier_id: str, model_type: str = 'supplier_scoring',
                          explanation_type: str = 'lime') -> Dict:
        """Get explanation for a prediction"""
        if explanation_type == 'lime':
            return self.get_lime_explanation(supplier_id, model_type, explanation_type)
        elif explanation_type == 'shap':
            return self.get_shap_values_supplier_scoring([supplier_id], model_type)
        else:
            return {'error': f'Unknown explanation type: {explanation_type}'}


# Global instance
explainability_service = ExplainabilityService()
