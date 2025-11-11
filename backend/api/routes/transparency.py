"""
Transparency & Resilience API Routes
Global supply chain visualization and resilience metrics
"""

from fastapi import APIRouter, HTTPException
import sys
import os

backend_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, backend_path)

from utils.data_loader import data_loader

router = APIRouter()


@router.get("/geographic-risk")
async def get_geographic_risk():
    """Get geographic risk distribution"""
    try:
        geo_risk_df = data_loader.load_geopolitical_risk()
        
        return {
            "geographic_risk": geo_risk_df.to_dict('records'),
            "total_countries": len(geo_risk_df)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/supplier-network")
async def get_supplier_network():
    """Get supplier network structure"""
    try:
        suppliers_df = data_loader.load_suppliers()
        
        # Create network structure
        nodes = []
        for _, row in suppliers_df.iterrows():
            nodes.append({
                "id": row['supplier_id'],
                "label": row['name'],
                "country": row['country'],
                "industry": row['industry'],
                "value": row.get('esg_score', 0.5)
            })
        
        return {
            "nodes": nodes,
            "total_nodes": len(nodes)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resilience-metrics")
async def get_resilience_metrics():
    """Get supply chain resilience metrics"""
    try:
        suppliers_df = data_loader.load_suppliers()
        risk_events_df = data_loader.load_risk_events()
        
        # Calculate resilience metrics
        resilience_data = []
        for supplier_id in suppliers_df['supplier_id'].unique():
            supplier_data = suppliers_df[suppliers_df['supplier_id'] == supplier_id].iloc[0]
            supplier_risks = risk_events_df[risk_events_df['supplier_id'] == supplier_id]
            
            resilience_score = (
                supplier_data['esg_score'] * 0.3 +
                supplier_data['compliance_score'] * 0.3 +
                (1 - supplier_data['geopolitical_risk_score']) * 0.2 +
                supplier_data['on_time_delivery_rate'] * 0.2
            )
            
            resilience_data.append({
                "supplier_id": supplier_id,
                "resilience_score": resilience_score,
                "risk_event_count": len(supplier_risks),
                "geographic_risk": supplier_data['geopolitical_risk_score'],
                "esg_score": supplier_data['esg_score']
            })
        
        return {
            "resilience_metrics": resilience_data,
            "total_suppliers": len(resilience_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transparency-scores")
async def get_transparency_scores():
    """Get transparency scores for suppliers"""
    try:
        suppliers_df = data_loader.load_suppliers()
        
        transparency_data = suppliers_df[[
            'supplier_id', 'name', 'country', 'esg_score',
            'compliance_score', 'geopolitical_risk_score'
        ]].copy()
        
        transparency_data['transparency_score'] = (
            transparency_data['esg_score'] * 0.5 +
            transparency_data['compliance_score'] * 0.5
        )
        
        return {
            "transparency_scores": transparency_data.to_dict('records'),
            "total_suppliers": len(transparency_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

