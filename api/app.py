"""
FastAPI Application for Fraud & Disruption Prediction
Provides REST API endpoints for real-time predictions.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import numpy as np
import pandas as pd
from datetime import datetime
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.fraud_detection.anomaly_detection import TransactionAnomalyDetector
from src.fraud_detection.invoice_fraud import InvoiceFraudDetector, extract_invoice_features
from src.disruption_prediction.time_series_models import DisruptionPredictor, RiskScoreCalculator

# Initialize FastAPI app
app = FastAPI(
    title="Supply Chain Fraud & Disruption Prediction API",
    description="AI-powered fraud detection and disruption prediction for supply chains",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instances (in production, load from disk)
fraud_detector = None
anomaly_detector = None
disruption_predictor = None
risk_calculator = RiskScoreCalculator()

# Request/Response Models
class TransactionData(BaseModel):
    """Transaction data for fraud detection."""
    transaction_id: str
    supplier_id: str
    amount: float
    timestamp: Optional[str] = None
    payment_method: Optional[str] = None
    
class TransactionBatch(BaseModel):
    """Batch of transactions."""
    transactions: List[TransactionData]

class InvoiceData(BaseModel):
    """Invoice data for fraud detection."""
    invoice_number: str
    supplier_id: str
    amount: float
    invoice_date: Optional[str] = None
    payment_terms: Optional[str] = None
    line_items: Optional[int] = None
    
class InvoiceBatch(BaseModel):
    """Batch of invoices."""
    invoices: List[InvoiceData]

class TimeSeriesData(BaseModel):
    """Time series data for disruption prediction."""
    values: List[float]
    timestamps: Optional[List[str]] = None
    
class DisruptionPredictionRequest(BaseModel):
    """Request for disruption prediction."""
    supplier_id: str
    historical_data: TimeSeriesData
    steps_ahead: int = Field(default=30, ge=1, le=365)
    
class RiskScoreRequest(BaseModel):
    """Request for risk score calculation."""
    supplier_id: str
    geopolitical: float = Field(default=0.5, ge=0.0, le=1.0)
    financial: float = Field(default=0.5, ge=0.0, le=1.0)
    operational: float = Field(default=0.5, ge=0.0, le=1.0)
    environmental: float = Field(default=0.5, ge=0.0, le=1.0)
    supplier_specific: float = Field(default=0.5, ge=0.0, le=1.0)

# Health check
@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Fraud & Disruption Prediction API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "models_loaded": {
            "fraud_detector": fraud_detector is not None,
            "anomaly_detector": anomaly_detector is not None,
            "disruption_predictor": disruption_predictor is not None
        },
        "timestamp": datetime.now().isoformat()
    }

# Fraud Detection Endpoints
@app.post("/api/v1/fraud/detect/transaction")
async def detect_transaction_fraud(data: TransactionBatch):
    """
    Detect fraud in transactions using anomaly detection.
    
    Returns:
        Dict with fraud predictions and scores for each transaction
    """
    try:
        # Convert to DataFrame
        df = pd.DataFrame([t.dict() for t in data.transactions])
        
        # Initialize detector if not loaded
        global anomaly_detector
        if anomaly_detector is None:
            anomaly_detector = TransactionAnomalyDetector()
            # In production, load pre-trained model
            # anomaly_detector = TransactionAnomalyDetector.load_model("path/to/model")
        
        # For demo purposes, if not fitted, return mock predictions
        if not anomaly_detector.is_fitted:
            return {
                "status": "success",
                "message": "Model not fitted. Please train the model first.",
                "predictions": [
                    {
                        "transaction_id": t.transaction_id,
                        "is_fraud": False,
                        "fraud_score": 0.0,
                        "confidence": 0.0
                    }
                    for t in data.transactions
                ]
            }
        
        # Make predictions
        results = anomaly_detector.predict(df, ensemble=True)
        
        predictions = [
            {
                "transaction_id": data.transactions[i].transaction_id,
                "is_fraud": bool(results['ensemble_predictions'][i]),
                "fraud_score": float(results['anomaly_score'][i]),
                "isolation_forest_score": float(results['isolation_forest_scores'][i]),
                "rule_based_flag": bool(results['rule_based_flags'][i])
            }
            for i in range(len(data.transactions))
        ]
        
        return {
            "status": "success",
            "count": len(predictions),
            "fraud_detected": sum(p['is_fraud'] for p in predictions),
            "predictions": predictions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/fraud/detect/invoice")
async def detect_invoice_fraud(data: InvoiceBatch):
    """
    Detect fraud in invoices using classification models.
    
    Returns:
        Dict with fraud predictions and probabilities
    """
    try:
        # Convert to DataFrame
        df = pd.DataFrame([inv.dict() for inv in data.invoices])
        
        # Extract features
        features = extract_invoice_features(df)
        
        # Initialize detector if not loaded
        global fraud_detector
        if fraud_detector is None:
            fraud_detector = InvoiceFraudDetector(model_type='xgboost')
            # In production, load pre-trained model
            # fraud_detector = InvoiceFraudDetector.load_model("path/to/model")
        
        # For demo purposes, if not fitted, return mock predictions
        if not fraud_detector.is_fitted:
            return {
                "status": "success",
                "message": "Model not fitted. Please train the model first.",
                "predictions": [
                    {
                        "invoice_number": inv.invoice_number,
                        "is_fraud": False,
                        "fraud_probability": 0.0,
                        "is_duplicate": False
                    }
                    for inv in data.invoices
                ]
            }
        
        # Make predictions
        results = fraud_detector.predict(features, return_proba=True, check_duplicates=True)
        
        predictions = [
            {
                "invoice_number": data.invoices[i].invoice_number,
                "supplier_id": data.invoices[i].supplier_id,
                "amount": data.invoices[i].amount,
                "is_fraud": bool(results['predictions'][i]),
                "fraud_probability": float(results['fraud_probability'][i]),
                "is_duplicate": bool(results['duplicate_flags'][i]),
                "risk_level": "HIGH" if results['fraud_probability'][i] > 0.7 
                             else "MEDIUM" if results['fraud_probability'][i] > 0.4 
                             else "LOW"
            }
            for i in range(len(data.invoices))
        ]
        
        return {
            "status": "success",
            "count": len(predictions),
            "fraud_detected": sum(p['is_fraud'] for p in predictions),
            "high_risk_count": sum(p['risk_level'] == 'HIGH' for p in predictions),
            "predictions": predictions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Disruption Prediction Endpoints
@app.post("/api/v1/disruption/predict")
async def predict_disruption(request: DisruptionPredictionRequest):
    """
    Predict supply chain disruptions using time series forecasting.
    
    Returns:
        Forecast for specified number of steps ahead
    """
    try:
        # Initialize predictor if not loaded
        global disruption_predictor
        if disruption_predictor is None:
            disruption_predictor = DisruptionPredictor(model_type='lstm')
            # In production, load pre-trained model
            # disruption_predictor = DisruptionPredictor.load_model("path/to/model")
        
        # For demo purposes, if not fitted, return mock predictions
        if not disruption_predictor.is_fitted:
            # Generate mock forecast
            last_value = request.historical_data.values[-1]
            forecast = [last_value * (1 + np.random.uniform(-0.1, 0.1)) 
                       for _ in range(request.steps_ahead)]
            
            return {
                "status": "success",
                "message": "Model not fitted. Returning mock predictions.",
                "supplier_id": request.supplier_id,
                "forecast_horizon": request.steps_ahead,
                "forecast": forecast,
                "confidence_interval": {
                    "lower": [v * 0.9 for v in forecast],
                    "upper": [v * 1.1 for v in forecast]
                }
            }
        
        # Convert to time series
        ts_data = pd.Series(request.historical_data.values)
        
        # Make prediction
        X = np.array(request.historical_data.values)
        forecast = disruption_predictor.predict(
            steps_ahead=request.steps_ahead,
            X=X
        )
        
        return {
            "status": "success",
            "supplier_id": request.supplier_id,
            "forecast_horizon": request.steps_ahead,
            "forecast": forecast.tolist(),
            "mean_forecast": float(np.mean(forecast)),
            "trend": "increasing" if forecast[-1] > forecast[0] else "decreasing"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/disruption/risk-score")
async def calculate_risk_score(request: RiskScoreRequest):
    """
    Calculate composite risk score for a supplier.
    
    Returns:
        Risk score breakdown and recommendations
    """
    try:
        supplier_data = {
            'geopolitical': request.geopolitical,
            'financial': request.financial,
            'operational': request.operational,
            'environmental': request.environmental,
            'supplier_specific': request.supplier_specific
        }
        
        result = risk_calculator.calculate_risk_score(supplier_data)
        result['supplier_id'] = request.supplier_id
        result['timestamp'] = datetime.now().isoformat()
        
        return {
            "status": "success",
            **result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/disruption/risk-score/{supplier_id}")
async def get_supplier_risk_score(supplier_id: str):
    """
    Get cached risk score for a supplier.
    
    In production, this would query a database for the latest risk score.
    """
    # Mock response
    return {
        "status": "success",
        "supplier_id": supplier_id,
        "total_risk_score": 0.45,
        "risk_level": "MEDIUM",
        "last_updated": datetime.now().isoformat(),
        "factor_breakdown": {
            "geopolitical": {"score": 0.4, "weight": 0.25},
            "financial": {"score": 0.5, "weight": 0.20},
            "operational": {"score": 0.3, "weight": 0.20},
            "environmental": {"score": 0.6, "weight": 0.15},
            "supplier_specific": {"score": 0.4, "weight": 0.20}
        }
    }

# Model Management Endpoints
@app.post("/api/v1/models/train/fraud")
async def train_fraud_model(background_tasks: BackgroundTasks):
    """
    Trigger fraud detection model training.
    
    In production, this would queue a training job.
    """
    return {
        "status": "success",
        "message": "Training job queued",
        "job_id": "fraud_train_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    }

@app.post("/api/v1/models/train/disruption")
async def train_disruption_model(background_tasks: BackgroundTasks):
    """
    Trigger disruption prediction model training.
    
    In production, this would queue a training job.
    """
    return {
        "status": "success",
        "message": "Training job queued",
        "job_id": "disruption_train_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
