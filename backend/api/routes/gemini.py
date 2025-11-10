"""
Gemini AI API Routes
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict
from pydantic import BaseModel
import sys
import os

backend_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, backend_path)

from services.gemini_service import gemini_service
from services.supplier_scoring import supplier_scoring_service
from services.risk_prediction import risk_prediction_service
from utils.data_loader import data_loader


router = APIRouter()


class ContractAnalysisRequest(BaseModel):
    contract_text: str


class SupplierRecommendationRequest(BaseModel):
    supplier_id: str
    context: Optional[str] = ""


class RiskAnalysisRequest(BaseModel):
    supplier_id: str


class ReportRequest(BaseModel):
    supplier_ids: List[str]
    report_type: Optional[str] = "comprehensive"


class QueryRequest(BaseModel):
    query: str
    context_data: Optional[Dict] = None


@router.post("/analyze-contract")
async def analyze_contract_with_gemini(request: ContractAnalysisRequest):
    """Analyze contract using Gemini AI"""
    try:
        result = gemini_service.analyze_contract_with_gemini(request.contract_text)
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', 'Analysis failed'))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/supplier-recommendations")
async def get_supplier_recommendations(request: SupplierRecommendationRequest):
    """Get AI-powered supplier recommendations"""
    try:
        suppliers_df = data_loader.load_suppliers()
        supplier_data = suppliers_df[suppliers_df['supplier_id'] == request.supplier_id]
        
        if supplier_data.empty:
            raise HTTPException(status_code=404, detail=f"Supplier {request.supplier_id} not found")
        
        supplier_dict = supplier_data.iloc[0].to_dict()
        result = gemini_service.get_supplier_recommendations(supplier_dict, request.context)
        
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', 'Analysis failed'))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-risk")
async def analyze_risk_with_gemini(request: RiskAnalysisRequest):
    """Analyze supplier risk using Gemini AI"""
    try:
        # Get risk prediction data
        risk_results = risk_prediction_service.predict_risk([request.supplier_id])
        risk_data = risk_results.iloc[0].to_dict() if not risk_results.empty else {}
        
        result = gemini_service.analyze_risk_with_gemini(request.supplier_id, risk_data)
        
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', 'Analysis failed'))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-report")
async def generate_supplier_report(request: ReportRequest):
    """Generate comprehensive supplier report using Gemini"""
    try:
        result = gemini_service.generate_supplier_report(
            request.supplier_ids,
            request.report_type
        )
        
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', 'Report generation failed'))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query")
async def answer_query(request: QueryRequest):
    """Answer natural language questions about suppliers"""
    try:
        result = gemini_service.answer_natural_language_query(
            request.query,
            request.context_data
        )
        
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', 'Query failed'))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def gemini_health_check():
    """Check if Gemini service is available"""
    try:
        test_response = gemini_service.model.generate_content("Say 'OK' if you can read this.")
        return {
            "status": "healthy",
            "model": gemini_service.model_name,
            "response": test_response.text[:50]
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

