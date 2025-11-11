"""
Decision Support API Routes
TOPSIS and AHP endpoints
"""

from fastapi import APIRouter, HTTPException
import sys
import os
import pandas as pd

backend_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, backend_path)

from services.decision_support import decision_support_service
from utils.data_loader import data_loader
from utils.preprocessing import preprocessor
from api.models import TOPSISRequest, TOPSISResponse, AHPRequest, AHPResponse

router = APIRouter()


@router.post("/topsis", response_model=TOPSISResponse)
async def topsis_ranking(request: TOPSISRequest):
    """Perform TOPSIS ranking"""
    try:
        # Load supplier data
        suppliers_df = data_loader.load_suppliers()
        
        if request.supplier_ids:
            suppliers_df = suppliers_df[suppliers_df['supplier_id'].isin(request.supplier_ids)]
        
        # Prepare data for TOPSIS
        # Select relevant criteria columns
        criteria_cols = list(request.criteria_weights.keys())
        
        # Create decision matrix
        decision_df = suppliers_df.set_index('supplier_id')[criteria_cols]
        
        # Normalize if needed (TOPSIS handles normalization internally)
        results_df = decision_support_service.topsis_ranking(
            decision_df,
            request.criteria_weights,
            request.benefit_criteria
        )
        
        return TOPSISResponse(
            results=results_df.to_dict('records'),
            method="TOPSIS"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ahp", response_model=AHPResponse)
async def ahp_ranking(request: AHPRequest):
    """Perform AHP ranking"""
    try:
        # Convert pairwise comparisons to tuple format
        pairwise_tuples = {}
        for c1, comparisons in request.pairwise_comparisons.items():
            for c2, value in comparisons.items():
                pairwise_tuples[(c1, c2)] = value
        
        # Load supplier data
        suppliers_df = data_loader.load_suppliers()
        
        if request.supplier_ids:
            suppliers_df = suppliers_df[suppliers_df['supplier_id'].isin(request.supplier_ids)]
        
        # Prepare decision matrix
        decision_df = suppliers_df.set_index('supplier_id')[request.criteria]
        
        # Perform AHP ranking
        results_df, cr = decision_support_service.ahp_ranking(
            decision_df,
            request.criteria,
            pairwise_tuples
        )
        
        return AHPResponse(
            results=results_df.to_dict('records'),
            consistency_ratio=cr,
            method="AHP"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def compare_methods(request: TOPSISRequest):
    """Compare TOPSIS and AHP rankings"""
    try:
        # This would need both TOPSIS and AHP inputs
        # Simplified version - would need proper request model
        return {"message": "Comparison endpoint - requires both TOPSIS and AHP inputs"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

