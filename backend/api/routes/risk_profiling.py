"""
Risk Profiling API Routes
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
import sys
import os

backend_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, backend_path)

from services.risk_prediction import risk_prediction_service
from api.models import RiskPredictionRequest, RiskPredictionResponse

router = APIRouter()


@router.post("/predict", response_model=RiskPredictionResponse)
async def predict_risk(request: RiskPredictionRequest):
    """Predict risk for suppliers"""
    try:
        # Ensure models are loaded
        if not risk_prediction_service.logistic_model:
            risk_prediction_service.load_models()
        
        results_df = risk_prediction_service.predict_risk(request.supplier_ids)
        
        if results_df.empty:
            raise HTTPException(status_code=404, detail="No suppliers found matching the criteria")
        
        return RiskPredictionResponse(
            results=results_df.to_dict('records'),
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


@router.post("/anomalies")
async def detect_anomalies(request: RiskPredictionRequest):
    """Detect anomalous suppliers"""
    try:
        # Ensure models are loaded
        if not risk_prediction_service.anomaly_detector:
            risk_prediction_service.load_models()
        
        results_df = risk_prediction_service.detect_anomalies(request.supplier_ids)
        
        if results_df.empty:
            raise HTTPException(status_code=404, detail="No suppliers found matching the criteria")
        
        return {
            "results": results_df.to_dict('records'),
            "total_suppliers": len(results_df),
            "anomalies_detected": int(results_df['is_anomaly'].sum())
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Required data file not found: {str(e)}")
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


@router.get("/data-sources")
async def get_data_sources():
    """Get information about data sources used for risk profiling"""
    return {
        "data_sources": [
            {
                "source": "Financial Data",
                "description": "Credit scores, profit margins, debt-to-equity ratios",
                "type": "Internal"
            },
            {
                "source": "Delivery History",
                "description": "On-time delivery rates, delivery times, quality scores",
                "type": "Internal"
            },
            {
                "source": "Geopolitical Risk",
                "description": "Country-level risk scores, political stability, trade freedom",
                "type": "External"
            },
            {
                "source": "Risk Events",
                "description": "Historical risk events, disruptions, compliance issues",
                "type": "Internal"
            },
            {
                "source": "ESG Scores",
                "description": "Environmental, Social, and Governance compliance scores",
                "type": "External"
            }
        ]
    }

