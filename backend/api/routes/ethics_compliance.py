"""
Ethics & Compliance API Routes
SHAP/LIME explainability and bias detection
"""

from fastapi import APIRouter, HTTPException
import sys
import os

backend_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, backend_path)

from services.explainability import explainability_service
from api.models import ExplainabilityRequest, ExplainabilityResponse, BiasDetectionRequest

router = APIRouter()


@router.post("/explain", response_model=ExplainabilityResponse)
async def explain_prediction(request: ExplainabilityRequest):
    """Get explanation for a supplier prediction"""
    try:
        if request.explanation_type == "lime":
            explanation = explainability_service.get_lime_explanation(
                request.supplier_id,
                request.model_type
            )
        elif request.explanation_type == "shap":
            # For SHAP, get values for single supplier
            explanation = explainability_service.get_shap_values_supplier_scoring(
                [request.supplier_id]
            )
            # Extract single supplier's explanation
            idx = explanation['supplier_ids'].index(request.supplier_id)
            explanation = {
                'supplier_id': request.supplier_id,
                'shap_values': explanation['shap_values'][idx],
                'feature_names': explanation['feature_names']
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid explanation type")
        
        return ExplainabilityResponse(
            explanation=explanation,
            supplier_id=request.supplier_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/shap-values")
async def get_shap_values(supplier_ids: list, model_type: str = "supplier_scoring"):
    """Get SHAP values for multiple suppliers"""
    try:
        if model_type == "supplier_scoring":
            shap_data = explainability_service.get_shap_values_supplier_scoring(supplier_ids)
        elif model_type == "risk_prediction":
            shap_data = explainability_service.get_shap_values_risk_prediction(supplier_ids)
        else:
            raise HTTPException(status_code=400, detail="Invalid model type")
        
        return shap_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bias-detection")
async def detect_bias(request: BiasDetectionRequest):
    """Detect bias in model predictions"""
    try:
        bias_analysis = explainability_service.detect_bias(request.feature_name, request.model_type)
        
        return bias_analysis
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


@router.get("/esg-scores")
async def get_esg_scores():
    """Get ESG compliance scores for suppliers"""
    try:
        from utils.data_loader import data_loader
        suppliers_df = data_loader.load_suppliers()
        
        esg_data = suppliers_df[['supplier_id', 'esg_score', 'compliance_score']].to_dict('records')
        
        return {
            "esg_scores": esg_data,
            "total_suppliers": len(esg_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

