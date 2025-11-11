"""
NLP Contract Analyzer API Routes
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
import sys
import os

backend_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, backend_path)

from services.contract_analyzer import contract_analyzer_service
from api.models import ContractAnalysisRequest, ContractAnalysisResponse

router = APIRouter()


@router.post("/analyze", response_model=ContractAnalysisResponse)
async def analyze_contract(request: ContractAnalysisRequest):
    """Analyze contract text or by contract ID"""
    try:
        if request.contract_id:
            analysis = contract_analyzer_service.analyze_contract_by_id(request.contract_id)
        elif request.contract_text:
            analysis = contract_analyzer_service.analyze_contract(request.contract_text)
        else:
            raise HTTPException(status_code=400, detail="Either contract_text or contract_id required")
        
        if 'error' in analysis:
            raise HTTPException(status_code=404, detail=analysis['error'])
        
        return ContractAnalysisResponse(
            analysis=analysis,
            contract_id=request.contract_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_and_analyze(file: UploadFile = File(...)):
    """Upload contract file and analyze"""
    try:
        content = await file.read()
        contract_text = content.decode('utf-8')
        
        analysis = contract_analyzer_service.analyze_contract(contract_text)
        
        return ContractAnalysisResponse(
            analysis=analysis,
            contract_id=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contracts")
async def list_contracts():
    """List available contracts"""
    try:
        from utils.data_loader import data_loader
        contracts_df = data_loader.load_contracts_metadata()
        
        return {
            "contracts": contracts_df.to_dict('records'),
            "total": len(contracts_df)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

