"""
Fraud Prediction API Routes
"""

from fastapi import APIRouter, HTTPException
import sys
import os

backend_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, backend_path)

from services.fraud_detection import fraud_detection_service
from api.models import FraudPredictionRequest, FraudPredictionResponse

router = APIRouter()


@router.post("/predict", response_model=FraudPredictionResponse)
async def predict_fraud(request: FraudPredictionRequest):
    """Predict fraud probability for suppliers"""
    try:
        # Ensure models are loaded
        if not fraud_detection_service.rf_model and not fraud_detection_service.gb_model:
            fraud_detection_service.load_models()
        
        # Validate model type
        if request.model_type not in ['random_forest', 'gradient_boosting']:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid model type. Use 'random_forest' or 'gradient_boosting'"
            )
        
        results_df = fraud_detection_service.predict_fraud(
            request.supplier_ids,
            request.model_type
        )
        
        if results_df.empty:
            raise HTTPException(status_code=404, detail="No suppliers found matching the criteria")
        
        return FraudPredictionResponse(
            results=results_df.to_dict('records'),
            model_type=request.model_type,
            total_suppliers=len(results_df)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Required data file not found: {str(e)}")
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


@router.post("/compare-models")
async def compare_fraud_models(request: FraudPredictionRequest):
    """Compare Random Forest and Gradient Boosting predictions"""
    try:
        comparison_df = fraud_detection_service.compare_models(request.supplier_ids)
        
        return {
            "results": comparison_df.to_dict('records'),
            "total_suppliers": len(comparison_df),
            "agreement_rate": comparison_df['agreement'].mean()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model-performance/{model_type}")
async def get_model_performance(model_type: str):
    """Get model performance metrics"""
    try:
        if model_type == "random_forest":
            if fraud_detection_service.rf_model is None:
                fraud_detection_service.load_models()
            # Return training metrics if available
            return {
                "model_type": model_type,
                "status": "Model loaded successfully"
            }
        elif model_type == "gradient_boosting":
            if fraud_detection_service.gb_model is None:
                fraud_detection_service.load_models()
            return {
                "model_type": model_type,
                "status": "Model loaded successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid model type")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

