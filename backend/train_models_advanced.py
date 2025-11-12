"""
Advanced Model Training Script with Hyperparameter Tuning
Trains all supplier scoring models with optimized parameters and cross-validation
"""
import sys
import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

# Add backend to path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

from services.supplier_scoring import SupplierScoringService
from utils.data_loader import data_loader
from utils.preprocessing import preprocessor


class AdvancedModelTrainer:
    """Advanced training with hyperparameter tuning"""
    
    def __init__(self):
        self.service = SupplierScoringService()
        self.results = {}
        
    def prepare_data(self):
        """Load and prepare training data"""
        print("\n" + "="*80)
        print(" DATA PREPARATION ".center(80, "="))
        print("="*80)
        
        try:
            # Load data
            suppliers_df = data_loader.load_suppliers()
            print(f"[OK] Loaded {len(suppliers_df)} supplier records")
            
            # Prepare features
            df_processed, feature_cols = preprocessor.prepare_supplier_features(suppliers_df, use_advanced_features=False)
            self.service.feature_columns = feature_cols
            
            print(f"[OK] Prepared {len(feature_cols)} features")
            
            # Create target variable (composite score)
            df_processed['target_score'] = (
                df_processed['performance_score'] * 0.4 +
                df_processed['financial_health'] * 0.35 +
                df_processed['operational_maturity'] * 0.25
            )
            
            # Normalize target to 0-1 range
            df_processed['target_score'] = (
                (df_processed['target_score'] - df_processed['target_score'].min()) /
                (df_processed['target_score'].max() - df_processed['target_score'].min())
            )
            
            X = df_processed[feature_cols].fillna(0)
            y = df_processed['target_score']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            print(f"[OK] Training set: {len(X_train)} samples")
            print(f"[OK] Test set: {len(X_test)} samples")
            
            return X_train, X_test, y_train, y_test
            
        except Exception as e:
            print(f"[ERROR] Data preparation failed: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def train_with_tuning(self, model_name, X_train, y_train, X_test, y_test):
        """Train a single model with hyperparameter tuning"""
        print(f"\n{'-'*80}")
        print(f" Training: {model_name.upper()} ".center(80, "-"))
        print(f"{'-'*80}")
        
        try:
            if model_name == 'xgboost':
                from xgboost import XGBRegressor
                
                param_grid = {
                    'n_estimators': [100, 200],
                    'max_depth': [3, 5, 7],
                    'learning_rate': [0.01, 0.1],
                    'subsample': [0.8, 1.0]
                }
                base_model = XGBRegressor(random_state=42, verbosity=0)
                
            elif model_name == 'random_forest':
                from sklearn.ensemble import RandomForestRegressor
                
                param_grid = {
                    'n_estimators': [100, 200],
                    'max_depth': [10, 20, None],
                    'min_samples_split': [2, 5],
                    'min_samples_leaf': [1, 2]
                }
                base_model = RandomForestRegressor(random_state=42)
                
            elif model_name == 'gradient_boosting':
                from sklearn.ensemble import GradientBoostingRegressor
                
                param_grid = {
                    'n_estimators': [100, 200],
                    'max_depth': [3, 5],
                    'learning_rate': [0.01, 0.1],
                    'subsample': [0.8, 1.0]
                }
                base_model = GradientBoostingRegressor(random_state=42)
                
            elif model_name == 'svm':
                from sklearn.svm import SVR
                from sklearn.preprocessing import StandardScaler
                
                # Scale features for SVM
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)
                
                param_grid = {
                    'C': [0.1, 1.0, 10.0],
                    'kernel': ['rbf', 'linear'],
                    'gamma': ['scale', 'auto']
                }
                base_model = SVR()
                
                # Use scaled data
                X_train = X_train_scaled
                X_test = X_test_scaled
                
                # Save scaler
                self.service.scalers['svm'] = scaler
                
            elif model_name == 'neural_network':
                from sklearn.neural_network import MLPRegressor
                from sklearn.preprocessing import StandardScaler
                
                # Scale features
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)
                
                param_grid = {
                    'hidden_layer_sizes': [(50,), (100,), (50, 50)],
                    'activation': ['relu', 'tanh'],
                    'alpha': [0.0001, 0.001],
                    'learning_rate': ['constant', 'adaptive']
                }
                base_model = MLPRegressor(random_state=42, max_iter=1000)
                
                X_train = X_train_scaled
                X_test = X_test_scaled
                self.service.scalers['neural_network'] = scaler
                
            elif model_name == 'adaboost':
                from sklearn.ensemble import AdaBoostRegressor
                
                param_grid = {
                    'n_estimators': [50, 100, 200],
                    'learning_rate': [0.01, 0.1, 1.0]
                }
                base_model = AdaBoostRegressor(random_state=42)
                
            else:
                raise ValueError(f"Unknown model: {model_name}")
            
            # Perform grid search
            print(f"[INFO] Running grid search with {len(param_grid)} parameters...")
            
            grid_search = GridSearchCV(
                base_model,
                param_grid,
                cv=3,
                scoring='r2',
                n_jobs=-1,
                verbose=0
            )
            
            grid_search.fit(X_train, y_train)
            
            best_model = grid_search.best_estimator_
            print(f"[OK] Best parameters: {grid_search.best_params_}")
            
            # Evaluate on test set
            y_pred = best_model.predict(X_test)
            
            r2 = r2_score(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            mae = mean_absolute_error(y_test, y_pred)
            
            # Cross-validation
            cv_scores = cross_val_score(best_model, X_train, y_train, cv=5, scoring='r2')
            cv_mean = cv_scores.mean()
            cv_std = cv_scores.std()
            
            print(f"[METRICS]")
            print(f"  R2 Score:        {r2:.4f}")
            print(f"  RMSE:            {rmse:.4f}")
            print(f"  MAE:             {mae:.4f}")
            print(f"  CV R2 (mean):    {cv_mean:.4f} (+/- {cv_std:.4f})")
            
            # Store model
            self.service.models[model_name] = best_model
            
            # Store results
            self.results[model_name] = {
                'r2': r2,
                'rmse': rmse,
                'mae': mae,
                'cv_mean': cv_mean,
                'cv_std': cv_std,
                'best_params': grid_search.best_params_
            }
            
            return best_model
            
        except Exception as e:
            print(f"[ERROR] Training {model_name} failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def train_ensemble(self, X_train, y_train, X_test, y_test):
        """Train ensemble model using best individual models"""
        print(f"\n{'-'*80}")
        print(f" Training: ENSEMBLE ".center(80, "-"))
        print(f"{'-'*80}")
        
        try:
            from sklearn.ensemble import VotingRegressor
            
            # Use top 3 models based on R2 score
            sorted_models = sorted(
                [(name, metrics['r2']) for name, metrics in self.results.items()],
                key=lambda x: x[1],
                reverse=True
            )[:3]
            
            print(f"[INFO] Using top 3 models:")
            for name, r2 in sorted_models:
                print(f"  - {name}: R2 = {r2:.4f}")
            
            estimators = [(name, self.service.models[name]) for name, _ in sorted_models]
            
            ensemble = VotingRegressor(estimators=estimators)
            ensemble.fit(X_train, y_train)
            
            # Evaluate
            y_pred = ensemble.predict(X_test)
            r2 = r2_score(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            mae = mean_absolute_error(y_test, y_pred)
            
            print(f"[METRICS]")
            print(f"  R2 Score:        {r2:.4f}")
            print(f"  RMSE:            {rmse:.4f}")
            print(f"  MAE:             {mae:.4f}")
            
            self.service.models['ensemble'] = ensemble
            
            self.results['ensemble'] = {
                'r2': r2,
                'rmse': rmse,
                'mae': mae
            }
            
            return ensemble
            
        except Exception as e:
            print(f"[ERROR] Ensemble training failed: {e}")
            return None
    
    def save_models(self):
        """Save all trained models"""
        print("\n" + "="*80)
        print(" SAVING MODELS ".center(80, "="))
        print("="*80)
        
        try:
            import joblib
            os.makedirs(self.service.models_dir, exist_ok=True)
            
            model_files = {
                'xgboost': 'xgb_supplier_scoring.pkl',
                'random_forest': 'rf_supplier_scoring.pkl',
                'gradient_boosting': 'gb_supplier_scoring.pkl',
                'svm': 'svm_supplier_scoring.pkl',
                'neural_network': 'nn_supplier_scoring.pkl',
                'adaboost': 'adaboost_supplier_scoring.pkl',
                'ensemble': 'ensemble_supplier_scoring.pkl'
            }
            
            for model_name, filename in model_files.items():
                if model_name in self.service.models:
                    filepath = os.path.join(self.service.models_dir, filename)
                    joblib.dump(self.service.models[model_name], filepath)
                    print(f"[OK] Saved {model_name} -> {filename}")
            
            # Save scalers
            for scaler_name in ['svm', 'neural_network']:
                if scaler_name in self.service.scalers:
                    filepath = os.path.join(self.service.models_dir, f'{scaler_name}_scaler.pkl')
                    joblib.dump(self.service.scalers[scaler_name], filepath)
                    print(f"[OK] Saved {scaler_name} scaler")
            
            print(f"\n[OK] All models saved to: {self.service.models_dir}")
            
        except Exception as e:
            print(f"[ERROR] Failed to save models: {e}")
    
    def print_summary(self):
        """Print training summary"""
        print("\n" + "="*80)
        print(" TRAINING SUMMARY ".center(80, "="))
        print("="*80)
        
        if not self.results:
            print("[ERROR] No results to display")
            return
        
        # Sort by R2 score
        sorted_results = sorted(
            self.results.items(),
            key=lambda x: x[1].get('r2', 0),
            reverse=True
        )
        
        print(f"\n{'Model':<20} {'R2 Score':<12} {'RMSE':<12} {'MAE':<12}")
        print("-" * 80)
        
        for model_name, metrics in sorted_results:
            r2 = metrics.get('r2', 0)
            rmse = metrics.get('rmse', 0)
            mae = metrics.get('mae', 0)
            status = "[OK]" if r2 > 0.80 else "[WARN]"
            print(f"{status} {model_name:<15} {r2:>10.4f}  {rmse:>10.4f}  {mae:>10.4f}")
        
        best_model = sorted_results[0][0]
        best_r2 = sorted_results[0][1]['r2']
        
        print("\n" + "="*80)
        print(f" BEST MODEL: {best_model.upper()} (R2 = {best_r2:.4f}) ".center(80, "="))
        print("="*80)
    
    def train_all(self):
        """Train all models"""
        print("\n" + "="*80)
        print(" ADVANCED MODEL TRAINING ".center(80, "="))
        print("="*80)
        
        try:
            # Prepare data
            X_train, X_test, y_train, y_test = self.prepare_data()
            
            # Train individual models
            models_to_train = ['xgboost', 'random_forest', 'gradient_boosting', 'svm', 'neural_network', 'adaboost']
            
            for model_name in models_to_train:
                self.train_with_tuning(model_name, X_train, y_train, X_test, y_test)
            
            # Train ensemble
            self.train_ensemble(X_train, y_train, X_test, y_test)
            
            # Save all models
            self.save_models()
            
            # Print summary
            self.print_summary()
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Training failed: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    trainer = AdvancedModelTrainer()
    success = trainer.train_all()
    
    if success:
        print("\n[SUCCESS] All models trained successfully!")
        print("Run 'python validate_models.py' to validate the trained models.")
    else:
        print("\n[FAILED] Training encountered errors.")
    
    sys.exit(0 if success else 1)

