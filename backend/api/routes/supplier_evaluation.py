"""
Supplier Evaluation API Routes
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
import sys
import os

# Add parent directory to path
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, backend_path)

from services.supplier_scoring import supplier_scoring_service
from api.models import SupplierEvaluationRequest, SupplierEvaluationResponse

router = APIRouter()


@router.post("/evaluate", response_model=SupplierEvaluationResponse)
async def evaluate_suppliers(request: SupplierEvaluationRequest):
    """Evaluate suppliers using ML models"""
    try:
        # Ensure models are loaded
        if not supplier_scoring_service.models:
            supplier_scoring_service.load_models()
        
        # Validate model type
        available_models = supplier_scoring_service.get_available_models()
        if request.model_type not in available_models:
            raise HTTPException(
                status_code=400, 
                detail=f"Model {request.model_type} not available. Available models: {available_models}"
            )
        
        results_df = supplier_scoring_service.predict_supplier_score(
            request.supplier_ids,
            request.model_type
        )
        
        if results_df.empty:
            raise HTTPException(status_code=404, detail="No suppliers found matching the criteria")
        
        results = results_df.to_dict('records')
        
        return SupplierEvaluationResponse(
            results=results,
            model_type=request.model_type,
            total_suppliers=len(results)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Required data file not found: {str(e)}")
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


@router.get("/compare-models")
async def compare_models(supplier_ids: Optional[str] = None, models: Optional[str] = None):
    """Compare multiple models"""
    try:
        ids_list = supplier_ids.split(',') if supplier_ids else None
        model_list = models.split(',') if models else None
        comparison_df = supplier_scoring_service.compare_models(ids_list, model_list)
        
        return {
            "results": comparison_df.to_dict('records'),
            "total_suppliers": len(comparison_df),
            "models_compared": model_list or ['xgboost', 'random_forest', 'gradient_boosting']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/available-models")
async def get_available_models():
    """Get list of available models"""
    try:
        available_models = supplier_scoring_service.get_available_models()
        return {
            "available_models": available_models,
            "total_models": len(available_models)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feature-importance/{model_type}")
async def get_feature_importance(model_type: str):
    """Get feature importance for a model"""
    try:
        if supplier_scoring_service.models.get(model_type) is None:
            supplier_scoring_service.load_models()
        
        model = supplier_scoring_service.models.get(model_type)
        if model is None:
            raise HTTPException(status_code=404, detail=f"Model {model_type} not found")
        
        # Check if model has feature_importances_ attribute
        if not hasattr(model, 'feature_importances_'):
            # Return a helpful message instead of error
            return {
                "model_type": model_type,
                "message": f"Feature importance is not available for {model_type} model type. Use tree-based models (XGBoost, Random Forest, Gradient Boosting, AdaBoost, Ensemble) for feature importance.",
                "available_models_with_importance": ['xgboost', 'random_forest', 'gradient_boosting', 'adaboost', 'ensemble'],
                "feature_importance": {}
            }
        
        importance = model.feature_importances_
        feature_importance = dict(zip(supplier_scoring_service.feature_columns, importance.tolist()))
        
        return {
            "model_type": model_type,
            "feature_importance": feature_importance
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)
