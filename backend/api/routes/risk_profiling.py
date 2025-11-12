"""
Risk Profiling API Routes
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, List
import sys
import os
import pandas as pd

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


@router.post("/upload-and-analyze")
async def upload_and_analyze_risk(file: UploadFile = File(...)):
    """Upload CSV/Excel file and analyze risks and anomalies"""
    try:
        # Validate file type
        if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload CSV or Excel file.")
        
        # Read file
        if file.filename.endswith('.csv'):
            suppliers_df = pd.read_csv(file.file)
        else:
            import io
            file.file.seek(0)  # Reset file pointer
            file_content = file.file.read()
            suppliers_df = pd.read_excel(io.BytesIO(file_content))
        
        # Validate supplier_id column
        if 'supplier_id' not in suppliers_df.columns:
            raise HTTPException(status_code=400, detail="CSV must contain 'supplier_id' column")
        
        # Ensure models are loaded
        if not risk_prediction_service.logistic_model:
            risk_prediction_service.load_models()
        if not risk_prediction_service.anomaly_detector:
            risk_prediction_service.load_models()
        
        supplier_ids = suppliers_df['supplier_id'].tolist()
        
        # Predict risks using uploaded data
        risk_results_df = risk_prediction_service.predict_risk(supplier_ids, suppliers_df=suppliers_df)
        
        # Detect anomalies with uploaded data
        anomaly_results_df = risk_prediction_service.detect_anomalies(supplier_ids, suppliers_df=suppliers_df)
        
        return {
            "results": suppliers_df.to_dict('records'),
            "risk_results": risk_results_df.to_dict('records'),
            "anomaly_results": anomaly_results_df.to_dict('records'),
            "total_suppliers": len(suppliers_df),
            "anomalies_detected": int(anomaly_results_df['is_anomaly'].sum())
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=f"Error processing uploaded data: {error_detail}")


@router.get("/data-sources")
async def get_data_sources():
    """Get information about data sources used for risk profiling"""
    try:
        # Load actual data to show what sources are available
        from utils.data_loader import data_loader
        
        suppliers_df = data_loader.load_suppliers()
        risk_events_df = data_loader.load_risk_events()
        
        # Extract actual data sources from loaded data
        data_sources = []
        
        # Financial Data
        if 'credit_score' in suppliers_df.columns or 'profit_margin' in suppliers_df.columns:
            data_sources.append({
                "source": "Financial Data",
                "description": f"Credit scores, profit margins, debt-to-equity ratios from {len(suppliers_df)} suppliers",
                "type": "Internal",
                "record_count": len(suppliers_df)
            })
        
        # Delivery History
        if 'on_time_delivery_rate' in suppliers_df.columns or 'avg_delivery_time_days' in suppliers_df.columns:
            data_sources.append({
                "source": "Delivery History",
                "description": f"On-time delivery rates, delivery times, quality scores from {len(suppliers_df)} suppliers",
                "type": "Internal",
                "record_count": len(suppliers_df)
            })
        
        # Geopolitical Risk
        try:
            geo_risk_df = data_loader.load_geopolitical_risk()
            data_sources.append({
                "source": "Geopolitical Risk",
                "description": f"Country-level risk scores, political stability from {len(geo_risk_df)} countries",
                "type": "External",
                "record_count": len(geo_risk_df)
            })
        except:
            pass
        
        # Risk Events
        if not risk_events_df.empty:
            data_sources.append({
                "source": "Risk Events",
                "description": f"Historical risk events, disruptions, compliance issues: {len(risk_events_df)} events",
                "type": "Internal",
                "record_count": len(risk_events_df)
            })
        
        # ESG Scores
        if 'esg_score' in suppliers_df.columns:
            data_sources.append({
                "source": "ESG Scores",
                "description": f"Environmental, Social, Governance scores from {len(suppliers_df)} suppliers",
                "type": "External",
                "record_count": len(suppliers_df)
            })
        
        return {
            "data_sources": data_sources,
            "total_suppliers": len(suppliers_df),
            "total_risk_events": len(risk_events_df) if not risk_events_df.empty else 0
        }
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"Error loading data sources: {str(e)}\n{traceback.format_exc()}")

