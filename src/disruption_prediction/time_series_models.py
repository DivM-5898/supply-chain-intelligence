"""
Time Series Forecasting Models for Supply Chain Disruption Prediction
Implements LSTM, ARIMA, and Prophet models for demand forecasting and disruption prediction.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
import warnings
warnings.filterwarnings('ignore')

# Time series models
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
try:
    from prophet import Prophet
except ImportError:
    Prophet = None

# Deep learning
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential, load_model as keras_load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
import joblib


class DisruptionPredictor:
    """
    Ensemble time series predictor for supply chain disruptions.
    Combines multiple forecasting models for robust predictions.
    """
    
    def __init__(self, model_type: str = 'lstm'):
        """
        Initialize disruption predictor.
        
        Args:
            model_type: Type of model ('lstm', 'arima', 'prophet', 'ensemble')
        """
        self.model_type = model_type
        self.model = None
        self.scaler = MinMaxScaler()
        self.is_fitted = False
        self.lookback_window = 30
        
    def fit(
        self,
        data: pd.Series,
        validation_split: float = 0.2,
        **kwargs
    ) -> Dict[str, float]:
        """
        Fit time series model on historical data.
        
        Args:
            data: Time series data
            validation_split: Fraction for validation
            **kwargs: Additional model-specific parameters
            
        Returns:
            Dictionary with training metrics
        """
        if self.model_type == 'lstm':
            return self._fit_lstm(data, validation_split, **kwargs)
        elif self.model_type == 'arima':
            return self._fit_arima(data, **kwargs)
        elif self.model_type == 'prophet':
            return self._fit_prophet(data, **kwargs)
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    def predict(
        self,
        steps_ahead: int = 30,
        X: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Predict future values.
        
        Args:
            steps_ahead: Number of steps to forecast
            X: Input data for prediction (for LSTM)
            
        Returns:
            Array of predictions
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
            
        if self.model_type == 'lstm':
            return self._predict_lstm(steps_ahead, X)
        elif self.model_type == 'arima':
            return self._predict_arima(steps_ahead)
        elif self.model_type == 'prophet':
            return self._predict_prophet(steps_ahead)
    
    def _fit_lstm(
        self,
        data: pd.Series,
        validation_split: float = 0.2,
        epochs: int = 100,
        batch_size: int = 32
    ) -> Dict[str, float]:
        """Fit LSTM model."""
        # Prepare data
        scaled_data = self.scaler.fit_transform(data.values.reshape(-1, 1))
        X, y = self._create_sequences(scaled_data, self.lookback_window)
        
        # Split data
        split_idx = int(len(X) * (1 - validation_split))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        # Build LSTM model
        self.model = Sequential([
            LSTM(128, activation='relu', return_sequences=True, 
                 input_shape=(self.lookback_window, 1)),
            Dropout(0.2),
            LSTM(64, activation='relu', return_sequences=True),
            Dropout(0.2),
            LSTM(32, activation='relu'),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1)
        ])
        
        self.model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        # Callbacks
        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=15,
            restore_best_weights=True
        )
        
        reduce_lr = ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-6
        )
        
        # Train
        print("Training LSTM model...")
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stop, reduce_lr],
            verbose=1
        )
        
        self.is_fitted = True
        
        # Calculate metrics
        train_pred = self.model.predict(X_train)
        val_pred = self.model.predict(X_val)
        
        metrics = {
            'train_mae': mean_absolute_error(y_train, train_pred),
            'val_mae': mean_absolute_error(y_val, val_pred),
            'train_rmse': np.sqrt(mean_squared_error(y_train, train_pred)),
            'val_rmse': np.sqrt(mean_squared_error(y_val, val_pred))
        }
        
        print(f"\nTraining MAE: {metrics['train_mae']:.4f}")
        print(f"Validation MAE: {metrics['val_mae']:.4f}")
        print(f"Validation RMSE: {metrics['val_rmse']:.4f}")
        
        return metrics
    
    def _predict_lstm(
        self,
        steps_ahead: int,
        X: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """Predict using LSTM."""
        if X is None:
            raise ValueError("Input data X required for LSTM prediction")
            
        # Scale input
        if X.shape != (1, self.lookback_window, 1):
            X_scaled = self.scaler.transform(X.reshape(-1, 1))
            X_scaled = X_scaled[-self.lookback_window:].reshape(1, self.lookback_window, 1)
        else:
            X_scaled = X
            
        predictions = []
        current_batch = X_scaled.copy()
        
        # Iterative prediction
        for _ in range(steps_ahead):
            pred = self.model.predict(current_batch, verbose=0)[0]
            predictions.append(pred[0])
            
            # Update batch with prediction
            current_batch = np.append(current_batch[:, 1:, :], [[pred]], axis=1)
        
        # Inverse transform
        predictions = self.scaler.inverse_transform(
            np.array(predictions).reshape(-1, 1)
        ).flatten()
        
        return predictions
    
    def _fit_arima(
        self,
        data: pd.Series,
        order: Tuple[int, int, int] = (5, 1, 2)
    ) -> Dict[str, float]:
        """Fit ARIMA model."""
        print(f"Fitting ARIMA{order} model...")
        
        self.model = ARIMA(data, order=order)
        self.model = self.model.fit()
        
        self.is_fitted = True
        
        # Calculate metrics on in-sample predictions
        predictions = self.model.fittedvalues
        
        metrics = {
            'aic': self.model.aic,
            'bic': self.model.bic,
            'mae': mean_absolute_error(data[1:], predictions[1:]),
            'rmse': np.sqrt(mean_squared_error(data[1:], predictions[1:]))
        }
        
        print(f"AIC: {metrics['aic']:.4f}")
        print(f"BIC: {metrics['bic']:.4f}")
        print(f"MAE: {metrics['mae']:.4f}")
        
        return metrics
    
    def _predict_arima(self, steps_ahead: int) -> np.ndarray:
        """Predict using ARIMA."""
        forecast = self.model.forecast(steps=steps_ahead)
        return forecast.values
    
    def _fit_prophet(self, data: pd.Series, **kwargs) -> Dict[str, float]:
        """Fit Prophet model."""
        if Prophet is None:
            raise ImportError("Prophet not installed. Install with: pip install prophet")
            
        # Prepare data for Prophet
        df = pd.DataFrame({
            'ds': data.index,
            'y': data.values
        })
        
        self.model = Prophet(**kwargs)
        self.model.fit(df)
        
        self.is_fitted = True
        
        return {'status': 'fitted'}
    
    def _predict_prophet(self, steps_ahead: int) -> np.ndarray:
        """Predict using Prophet."""
        future = self.model.make_future_dataframe(periods=steps_ahead)
        forecast = self.model.predict(future)
        
        return forecast['yhat'].values[-steps_ahead:]
    
    def _create_sequences(
        self,
        data: np.ndarray,
        lookback: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for LSTM training."""
        X, y = [], []
        
        for i in range(lookback, len(data)):
            X.append(data[i-lookback:i, 0])
            y.append(data[i, 0])
            
        return np.array(X).reshape(-1, lookback, 1), np.array(y)
    
    def save_model(self, filepath: str):
        """Save model to disk."""
        if self.model_type == 'lstm':
            self.model.save(f"{filepath}_lstm.h5")
            joblib.dump({
                'scaler': self.scaler,
                'lookback_window': self.lookback_window,
                'model_type': self.model_type
            }, f"{filepath}_metadata.pkl")
        else:
            joblib.dump({
                'model': self.model,
                'model_type': self.model_type,
                'scaler': self.scaler
            }, filepath)
        
        print(f"Model saved to {filepath}")
    
    @classmethod
    def load_model(cls, filepath: str) -> 'DisruptionPredictor':
        """Load model from disk."""
        # Try loading metadata first
        try:
            metadata = joblib.load(f"{filepath}_metadata.pkl")
            predictor = cls(model_type=metadata['model_type'])
            predictor.scaler = metadata['scaler']
            predictor.lookback_window = metadata['lookback_window']
            predictor.model = keras_load_model(f"{filepath}_lstm.h5")
            predictor.is_fitted = True
        except:
            data = joblib.load(filepath)
            predictor = cls(model_type=data['model_type'])
            predictor.model = data['model']
            predictor.scaler = data.get('scaler', MinMaxScaler())
            predictor.is_fitted = True
        
        print(f"Model loaded from {filepath}")
        return predictor


class RiskScoreCalculator:
    """
    Calculate risk scores for supply chain disruptions based on multiple factors.
    """
    
    def __init__(self):
        self.risk_factors = {
            'geopolitical': 0.25,
            'financial': 0.20,
            'operational': 0.20,
            'environmental': 0.15,
            'supplier_specific': 0.20
        }
        
    def calculate_risk_score(
        self,
        supplier_data: Dict[str, float]
    ) -> Dict[str, any]:
        """
        Calculate composite risk score for a supplier.
        
        Args:
            supplier_data: Dictionary with risk factor scores (0-1)
            
        Returns:
            Dictionary with risk score and breakdown
        """
        total_score = 0
        factor_scores = {}
        
        for factor, weight in self.risk_factors.items():
            score = supplier_data.get(factor, 0.5)  # Default to medium risk
            weighted_score = score * weight
            total_score += weighted_score
            factor_scores[factor] = {
                'score': score,
                'weight': weight,
                'weighted_score': weighted_score
            }
        
        risk_level = self._classify_risk_level(total_score)
        
        return {
            'total_risk_score': total_score,
            'risk_level': risk_level,
            'factor_breakdown': factor_scores,
            'recommendations': self._generate_recommendations(total_score, factor_scores)
        }
    
    def _classify_risk_level(self, score: float) -> str:
        """Classify risk level based on score."""
        if score < 0.3:
            return 'LOW'
        elif score < 0.6:
            return 'MEDIUM'
        elif score < 0.8:
            return 'HIGH'
        else:
            return 'CRITICAL'
    
    def _generate_recommendations(
        self,
        total_score: float,
        factor_scores: Dict
    ) -> List[str]:
        """Generate risk mitigation recommendations."""
        recommendations = []
        
        # Find highest risk factors
        sorted_factors = sorted(
            factor_scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        for factor, data in sorted_factors[:3]:
            if data['score'] > 0.6:
                recommendations.append(
                    f"High {factor} risk detected. Consider diversifying suppliers."
                )
        
        if total_score > 0.7:
            recommendations.append(
                "Critical overall risk level. Immediate action recommended."
            )
        
        return recommendations
