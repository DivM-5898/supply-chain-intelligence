"""
Supplier Scoring Service
XGBoost and Random Forest models for supplier evaluation and ranking
"""

import pandas as pd
import numpy as np
from xgboost import XGBClassifier, XGBRegressor
from sklearn.ensemble import (
    RandomForestRegressor, GradientBoostingRegressor, 
    AdaBoostRegressor, VotingRegressor, BaggingRegressor
)
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, classification_report
from sklearn.preprocessing import StandardScaler
import joblib
import os
from typing import Dict, List, Tuple, Optional
import sys
import os
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_path)

from utils.preprocessing import preprocessor

# Import data_loader only when needed to avoid startup errors
def get_data_loader():
    from utils.data_loader import data_loader
    return data_loader


class SupplierScoringService:
    """Service for supplier scoring using multiple ML models"""
    
    def __init__(self, models_dir: str = "models/saved_models"):
        # Resolve absolute path
        backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if not os.path.isabs(models_dir):
            self.models_dir = os.path.join(backend_path, models_dir)
        else:
            self.models_dir = models_dir
        os.makedirs(self.models_dir, exist_ok=True)
        self.models = {}  # Store all models
        self.scalers = {}  # Store scalers for models that need scaling
        self.feature_columns = None
        self.is_trained = False
    
    def prepare_training_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare training data with target labels
        Creates a composite score as target variable
        """
        data_loader = get_data_loader()
        suppliers_df = data_loader.load_suppliers()
        df, feature_cols = preprocessor.prepare_supplier_features(suppliers_df)
        self.feature_columns = feature_cols
        
        # Create target score (composite of performance, financial, operational)
        df['target_score'] = (
            df['performance_score'] * 0.4 +
            df['financial_health'] * 0.35 +
            df['operational_maturity'] * 0.25
        )
        
        # Normalize target to 0-1 range
        df['target_score'] = (df['target_score'] - df['target_score'].min()) / \
                            (df['target_score'].max() - df['target_score'].min())
        
        X = df[feature_cols].fillna(0)
        y = df['target_score']
        
        return X, y
    
    def train_xgboost(self, X: pd.DataFrame, y: pd.Series, 
                     params: Optional[Dict] = None) -> Dict:
        """Train XGBoost model for supplier scoring"""
        if params is None:
            params = {
                'max_depth': 6,
                'learning_rate': 0.1,
                'n_estimators': 100,
                'random_state': 42,
                'objective': 'reg:squarederror'
            }
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        model = XGBRegressor(**params)
        model.fit(X_train, y_train)
        self.models['xgboost'] = model
        
        # Evaluate
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        train_r2 = r2_score(y_train, y_pred_train)
        test_r2 = r2_score(y_test, y_pred_test)
        train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
        test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
        
        # Save model
        model_path = os.path.join(self.models_dir, "xgb_supplier_scoring.pkl")
        joblib.dump(model, model_path)
        
        return {
            'model': 'XGBoost',
            'train_r2': train_r2,
            'test_r2': test_r2,
            'train_rmse': train_rmse,
            'test_rmse': test_rmse,
            'feature_importance': dict(zip(self.feature_columns, 
                                         model.feature_importances_))
        }
    
    def train_random_forest(self, X: pd.DataFrame, y: pd.Series,
                           params: Optional[Dict] = None) -> Dict:
        """Train Random Forest model for supplier scoring"""
        if params is None:
            params = {
                'n_estimators': 100,
                'max_depth': 10,
                'random_state': 42
            }
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        model = RandomForestRegressor(**params)
        model.fit(X_train, y_train)
        self.models['random_forest'] = model
        
        # Evaluate
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        train_r2 = r2_score(y_train, y_pred_train)
        test_r2 = r2_score(y_test, y_pred_test)
        train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
        test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
        
        # Save model
        model_path = os.path.join(self.models_dir, "rf_supplier_scoring.pkl")
        joblib.dump(model, model_path)
        
        return {
            'model': 'Random Forest',
            'train_r2': train_r2,
            'test_r2': test_r2,
            'train_rmse': train_rmse,
            'test_rmse': test_rmse,
            'feature_importance': dict(zip(self.feature_columns,
                                         model.feature_importances_))
        }
    
    def train_gradient_boosting(self, X: pd.DataFrame, y: pd.Series,
                               params: Optional[Dict] = None) -> Dict:
        """Train Gradient Boosting model"""
        if params is None:
            params = {
                'n_estimators': 100,
                'learning_rate': 0.1,
                'max_depth': 5,
                'random_state': 42
            }
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        model = GradientBoostingRegressor(**params)
        model.fit(X_train, y_train)
        self.models['gradient_boosting'] = model
        
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        model_path = os.path.join(self.models_dir, "gb_supplier_scoring.pkl")
        joblib.dump(model, model_path)
        
        return {
            'model': 'Gradient Boosting',
            'train_r2': r2_score(y_train, y_pred_train),
            'test_r2': r2_score(y_test, y_pred_test),
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
            'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
            'feature_importance': dict(zip(self.feature_columns, model.feature_importances_))
        }
    
    def train_svm(self, X: pd.DataFrame, y: pd.Series,
                 params: Optional[Dict] = None) -> Dict:
        """Train Support Vector Machine model"""
        if params is None:
            params = {
                'kernel': 'rbf',
                'C': 1.0,
                'gamma': 'scale'
            }
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features for SVM
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        self.scalers['svm'] = scaler
        
        model = SVR(**params)
        model.fit(X_train_scaled, y_train)
        self.models['svm'] = model
        
        y_pred_train = model.predict(X_train_scaled)
        y_pred_test = model.predict(X_test_scaled)
        
        model_path = os.path.join(self.models_dir, "svm_supplier_scoring.pkl")
        joblib.dump(model, model_path)
        joblib.dump(scaler, os.path.join(self.models_dir, "svm_scaler.pkl"))
        
        return {
            'model': 'SVM',
            'train_r2': r2_score(y_train, y_pred_train),
            'test_r2': r2_score(y_test, y_pred_test),
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
            'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test))
        }
    
    def train_neural_network(self, X: pd.DataFrame, y: pd.Series,
                            params: Optional[Dict] = None) -> Dict:
        """Train Neural Network (MLP) model"""
        if params is None:
            params = {
                'hidden_layer_sizes': (100, 50),
                'activation': 'relu',
                'solver': 'adam',
                'alpha': 0.0001,
                'learning_rate': 'constant',
                'max_iter': 500,
                'random_state': 42
            }
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features for Neural Network
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        self.scalers['neural_network'] = scaler
        
        model = MLPRegressor(**params)
        model.fit(X_train_scaled, y_train)
        self.models['neural_network'] = model
        
        y_pred_train = model.predict(X_train_scaled)
        y_pred_test = model.predict(X_test_scaled)
        
        model_path = os.path.join(self.models_dir, "nn_supplier_scoring.pkl")
        joblib.dump(model, model_path)
        joblib.dump(scaler, os.path.join(self.models_dir, "nn_scaler.pkl"))
        
        return {
            'model': 'Neural Network',
            'train_r2': r2_score(y_train, y_pred_train),
            'test_r2': r2_score(y_test, y_pred_test),
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
            'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test))
        }
    
    def train_adaboost(self, X: pd.DataFrame, y: pd.Series,
                      params: Optional[Dict] = None) -> Dict:
        """Train AdaBoost model"""
        if params is None:
            params = {
                'n_estimators': 100,
                'learning_rate': 1.0,
                'random_state': 42
            }
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        model = AdaBoostRegressor(**params)
        model.fit(X_train, y_train)
        self.models['adaboost'] = model
        
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        model_path = os.path.join(self.models_dir, "adaboost_supplier_scoring.pkl")
        joblib.dump(model, model_path)
        
        return {
            'model': 'AdaBoost',
            'train_r2': r2_score(y_train, y_pred_train),
            'test_r2': r2_score(y_test, y_pred_test),
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
            'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
            'feature_importance': dict(zip(self.feature_columns, model.feature_importances_))
        }
    
    def train_ensemble(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """Train Ensemble Voting model combining multiple models"""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Create ensemble of best models
        ensemble = VotingRegressor([
            ('xgb', XGBRegressor(n_estimators=50, random_state=42)),
            ('rf', RandomForestRegressor(n_estimators=50, random_state=42)),
            ('gb', GradientBoostingRegressor(n_estimators=50, random_state=42))
        ])
        
        ensemble.fit(X_train, y_train)
        self.models['ensemble'] = ensemble
        
        y_pred_train = ensemble.predict(X_train)
        y_pred_test = ensemble.predict(X_test)
        
        model_path = os.path.join(self.models_dir, "ensemble_supplier_scoring.pkl")
        joblib.dump(ensemble, model_path)
        
        return {
            'model': 'Ensemble (Voting)',
            'train_r2': r2_score(y_train, y_pred_train),
            'test_r2': r2_score(y_test, y_pred_test),
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
            'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test))
        }
    
    def train_all_models(self) -> Dict:
        """Train all available models"""
        X, y = self.prepare_training_data()
        
        results = {}
        
        print("Training XGBoost...")
        results['xgboost'] = self.train_xgboost(X, y)
        
        print("Training Random Forest...")
        results['random_forest'] = self.train_random_forest(X, y)
        
        print("Training Gradient Boosting...")
        results['gradient_boosting'] = self.train_gradient_boosting(X, y)
        
        print("Training SVM...")
        results['svm'] = self.train_svm(X, y)
        
        print("Training Neural Network...")
        results['neural_network'] = self.train_neural_network(X, y)
        
        print("Training AdaBoost...")
        results['adaboost'] = self.train_adaboost(X, y)
        
        print("Training Ensemble...")
        results['ensemble'] = self.train_ensemble(X, y)
        
        self.is_trained = True
        
        return results
    
    def train_both_models(self) -> Dict:
        """Train both XGBoost and Random Forest models (for backward compatibility)"""
        return self.train_all_models()
    
    def load_models(self):
        """Load all trained models from disk"""
        model_files = {
            'xgboost': 'xgb_supplier_scoring.pkl',
            'random_forest': 'rf_supplier_scoring.pkl',
            'gradient_boosting': 'gb_supplier_scoring.pkl',
            'svm': 'svm_supplier_scoring.pkl',
            'neural_network': 'nn_supplier_scoring.pkl',
            'adaboost': 'adaboost_supplier_scoring.pkl',
            'ensemble': 'ensemble_supplier_scoring.pkl'
        }
        
        scaler_files = {
            'svm': 'svm_scaler.pkl',
            'neural_network': 'nn_scaler.pkl'
        }
        
        loaded_count = 0
        for model_name, filename in model_files.items():
            model_path = os.path.join(self.models_dir, filename)
            if os.path.exists(model_path):
                try:
                    self.models[model_name] = joblib.load(model_path)
                    loaded_count += 1
                    print(f"Loaded {model_name} model successfully")
                except Exception as e:
                    print(f"Warning: Failed to load {model_name} model: {str(e)}")
        
        for scaler_name, filename in scaler_files.items():
            scaler_path = os.path.join(self.models_dir, filename)
            if os.path.exists(scaler_path):
                try:
                    self.scalers[scaler_name] = joblib.load(scaler_path)
                    print(f"Loaded {scaler_name} scaler successfully")
                except Exception as e:
                    print(f"Warning: Failed to load {scaler_name} scaler: {str(e)}")
        
        # Load feature columns
        try:
            data_loader = get_data_loader()
            suppliers_df = data_loader.load_suppliers()
            _, self.feature_columns = preprocessor.prepare_supplier_features(suppliers_df)
            print(f"Loaded {len(self.feature_columns)} feature columns")
        except Exception as e:
            print(f"Warning: Failed to load feature columns: {str(e)}")
            # Use default feature columns if loading fails
            self.feature_columns = [
                'performance_score', 'financial_health', 'operational_maturity',
                'avg_delivery_time_days', 'on_time_delivery_rate', 'quality_score',
                'credit_score', 'profit_margin', 'years_in_business', 'utilization_rate',
                'geopolitical_risk_score', 'esg_score', 'compliance_score', 'certifications_encoded'
            ]
        
        if loaded_count == 0:
            # Don't raise error, just log warning - allow service to continue
            print(f"Warning: No models found in {self.models_dir}. Please train models first.")
            return
        
        print(f"Successfully loaded {loaded_count} models")
    
    def predict_supplier_score(self, supplier_ids: List[str], 
                              model_type: str = 'xgboost') -> pd.DataFrame:
        """
        Predict supplier scores for given supplier IDs
        Returns DataFrame with supplier_id and predicted scores
        """
        if not self.models:
            self.load_models()
        
        if model_type not in self.models:
            raise ValueError(f"Model {model_type} not available. Available models: {list(self.models.keys())}")
        
        data_loader = get_data_loader()
        suppliers_df = data_loader.load_suppliers()
        df, _ = preprocessor.prepare_supplier_features(suppliers_df)
        
        # Filter to requested suppliers
        if supplier_ids:
            df = df[df['supplier_id'].isin(supplier_ids)]
        
        X = df[self.feature_columns].fillna(0)
        
        # Get model and scale if needed
        model = self.models[model_type]
        if model_type in self.scalers:
            X = self.scalers[model_type].transform(X)
        
        # Predict with selected model
        predictions = model.predict(X)
        
        # Create results DataFrame
        results = pd.DataFrame({
            'supplier_id': df['supplier_id'].values,
            'predicted_score': predictions,
            'model_type': model_type
        })
        
        # Sort by score descending
        results = results.sort_values('predicted_score', ascending=False)
        results['rank'] = range(1, len(results) + 1)
        
        return results
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        try:
            if not self.models:
                # Try to load models, but don't fail if they don't exist
                try:
                    self.load_models()
                except FileNotFoundError:
                    # Models don't exist, return empty list
                    return []
                except Exception as e:
                    # Other error loading models, log and return empty
                    print(f"Warning: Error loading models: {e}")
                    return []
            
            return list(self.models.keys())
        except Exception as e:
            print(f"Error in get_available_models: {e}")
            return []
    
    def compare_models(self, supplier_ids: Optional[List[str]] = None, 
                      model_list: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Compare predictions from multiple models
        Returns DataFrame with all model predictions
        """
        if not self.models:
            self.load_models()
        
        if model_list is None:
            model_list = ['xgboost', 'random_forest', 'gradient_boosting']
        
        # Get predictions from all specified models
        all_results = {}
        for model_type in model_list:
            if model_type in self.models:
                try:
                    results = self.predict_supplier_score(supplier_ids, model_type=model_type)
                    all_results[model_type] = results[['supplier_id', 'predicted_score', 'rank']]
                except Exception as e:
                    print(f"Warning: Could not get predictions from {model_type}: {e}")
        
        if not all_results:
            raise ValueError("No models available for comparison")
        
        # Merge all results
        comparison = all_results[list(all_results.keys())[0]].copy()
        comparison.rename(columns={'predicted_score': f'score_{list(all_results.keys())[0]}',
                                 'rank': f'rank_{list(all_results.keys())[0]}'}, inplace=True)
        
        for model_type in list(all_results.keys())[1:]:
            temp = all_results[model_type].copy()
            temp.rename(columns={'predicted_score': f'score_{model_type}',
                               'rank': f'rank_{model_type}'}, inplace=True)
            comparison = pd.merge(comparison, temp, on='supplier_id', how='outer')
        
        # Calculate average score
        score_cols = [col for col in comparison.columns if col.startswith('score_')]
        comparison['avg_score'] = comparison[score_cols].mean(axis=1)
        
        # Calculate score variance (lower is better - more agreement)
        comparison['score_variance'] = comparison[score_cols].var(axis=1)
        
        return comparison.sort_values('avg_score', ascending=False)


# Global instance - lazy initialization to avoid startup errors
supplier_scoring_service = None

def get_supplier_scoring_service():
    """Get or create supplier scoring service instance"""
    global supplier_scoring_service
    if supplier_scoring_service is None:
        supplier_scoring_service = SupplierScoringService()
    return supplier_scoring_service

# Initialize on import (but handle errors gracefully)
try:
    supplier_scoring_service = SupplierScoringService()
except Exception as e:
    import warnings
    warnings.warn(f"Failed to initialize SupplierScoringService: {e}. Will initialize on first use.")
    supplier_scoring_service = None

