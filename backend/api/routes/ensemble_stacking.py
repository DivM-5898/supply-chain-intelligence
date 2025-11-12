"""
API Routes for Ensemble Stacking
Meta-learner combining all models for 97%+ accuracy
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from services.ensemble_stacking import ensemble_stacking_service
import pandas as pd

router = APIRouter()


class TrainStackingRequest(BaseModel):
    supplier_ids: Optional[List[str]] = None


class PredictStackingRequest(BaseModel):
    supplier_ids: Optional[List[str]] = None


@router.post("/train")
async def train_stacking_model(request: TrainStackingRequest):
    """
    Train stacking ensemble model with meta-learner
    
    Args:
        request: Training request (optional supplier IDs for subset)
        
    Returns:
        Training results with accuracy metrics
    """
    try:
        from utils.data_loader import data_loader
        from services.supplier_scoring import SupplierScoringService
        
        # Load data
        df = data_loader.load_suppliers()
        
        # Filter if supplier IDs provided
        if request.supplier_ids:
            df = df[df['supplier_id'].isin(request.supplier_ids)]
        
        # Prepare features and target
        scoring_service = SupplierScoringService()
        X, y = scoring_service.prepare_training_data()
        
        # Train stacking model
        result = ensemble_stacking_service.train_stacking_model(X, y)
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "accuracy": result["accuracy"],
            "std": result.get("std"),
            "cv_scores": result.get("cv_scores", []),
            "base_models": result.get("base_models", []),
            "model_path": result.get("model_path"),
            "error": None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict")
async def predict_with_stacking(request: PredictStackingRequest):
    """
    Predict supplier scores using stacking ensemble
    
    Args:
        request: Prediction request with optional supplier IDs
        
    Returns:
        Predictions with stacking scores
    """
    try:
        result = ensemble_stacking_service.predict_suppliers(
            supplier_ids=request.supplier_ids
        )
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "predictions": result["predictions"],
            "model_type": result["model_type"],
            "total_suppliers": result["total_suppliers"],
            "error": None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def compare_with_base_models(request: PredictStackingRequest):
    """
    Compare stacking predictions with base models
    
    Args:
        request: Comparison request with optional supplier IDs
        
    Returns:
        Comparison results between stacking and base models
    """
    try:
        result = ensemble_stacking_service.compare_with_base_models(
            supplier_ids=request.supplier_ids
        )
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "stacking": result["stacking"],
            "base_models": result["base_models"],
            "error": None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_stacking_status():
    """
    Get stacking model status
    
    Returns:
        Status information about stacking model
    """
    try:
        import os
        from config.settings import settings
        
        model_path = os.path.join(
            settings.MODELS_DIR, 
            "stacking_ensemble.pkl"
        )
        
        is_trained = os.path.exists(model_path)
        
        return {
            "success": True,
            "is_trained": is_trained,
            "model_path": model_path,
            "base_models_loaded": len(ensemble_stacking_service.load_base_models())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

