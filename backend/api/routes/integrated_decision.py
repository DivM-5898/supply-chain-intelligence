"""
Integrated Decision Support API Routes
Unified endpoints that connect MCDA, Supplier Evaluation, and Analysis
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import date
import sys
import os

backend_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, backend_path)

from services.integration_service import get_integration_service

router = APIRouter()


# Request/Response Models
class MetricsData(BaseModel):
    """Base metrics data"""
    measurement_start_date: date
    measurement_end_date: date


class QualityMetricsRequest(MetricsData):
    defect_rate: float
    rejection_rate: float
    rework_rate: float
    first_pass_yield: float
    customer_complaints: int
    quality_incidents: int
    non_conformance_reports: int
    corrective_actions_open: int
    corrective_actions_closed: int
    quality_certifications_valid: int
    quality_audit_score: Optional[float] = None


class DeliveryMetricsRequest(MetricsData):
    on_time_delivery_rate: float
    early_delivery_rate: float
    late_delivery_rate: float
    average_lead_time_days: float
    lead_time_variance_days: float
    order_fulfillment_rate: float
    partial_shipment_rate: float
    damage_in_transit_rate: float
    documentation_accuracy: float
    total_deliveries: int
    on_time_deliveries: int
    late_deliveries: int


class CostMetricsRequest(MetricsData):
    average_unit_cost: float
    cost_variance_percentage: float
    total_cost_of_ownership: float
    price_competitiveness_index: float
    payment_discount_utilization: float
    invoice_accuracy_rate: float
    pricing_stability_index: float
    material_cost: float
    transportation_cost: float
    overhead_cost: float
    quality_cost: float


class ComplianceMetricsRequest(MetricsData):
    regulatory_compliance_rate: float
    audit_findings_open: int
    audit_findings_closed: int
    certifications_current: int
    certifications_expired: int
    safety_incidents: int
    environmental_violations: int
    labor_violations: int
    data_privacy_breaches: int
    ethical_violations: int
    has_iso_9001: bool = False
    has_iso_14001: bool = False
    has_iso_45001: bool = False
    has_social_accountability: bool = False


class FinancialMetricsRequest(MetricsData):
    credit_score: float
    debt_to_equity_ratio: float
    current_ratio: float
    quick_ratio: float
    profit_margin_percentage: float
    revenue_growth_rate: float
    payment_delinquency_rate: float
    bankruptcy_risk_score: float
    days_payable_outstanding: float
    cash_flow_stability_index: float


class RiskMetricsRequest(MetricsData):
    overall_risk_score: float
    geopolitical_risk: float
    operational_risk: float
    financial_risk: float
    reputational_risk: float
    cybersecurity_risk: float
    supply_chain_disruption_risk: float
    single_source_dependency: bool
    geographic_concentration: bool
    capacity_constraints: bool
    past_supply_disruptions: int
    past_quality_failures: int
    past_delivery_failures: int


class SustainabilityMetricsRequest(MetricsData):
    carbon_footprint_score: float
    renewable_energy_percentage: float
    waste_reduction_rate: float
    water_conservation_score: float
    recycling_rate: float
    fair_labor_practices_score: float
    diversity_inclusion_score: float
    community_engagement_score: float
    ethical_sourcing_score: float
    transparency_score: float
    has_environmental_certification: bool
    has_social_certification: bool


class SupplierEvaluationRequest(BaseModel):
    """Complete supplier evaluation request"""
    supplier_id: str
    quality_metrics: QualityMetricsRequest
    delivery_metrics: DeliveryMetricsRequest
    cost_metrics: CostMetricsRequest
    compliance_metrics: ComplianceMetricsRequest
    financial_metrics: FinancialMetricsRequest
    risk_metrics: RiskMetricsRequest
    sustainability_metrics: SustainabilityMetricsRequest
    performance_period_start: date
    performance_period_end: date
    custom_weights: Optional[Dict[str, float]] = None


class CriterionDefinition(BaseModel):
    """MCDA criterion definition"""
    id: str
    name: str
    weight: float = 1.0
    type: str = "benefit"  # "benefit" or "cost"
    scale: str = "ratio"


class MCDARequest(BaseModel):
    """MCDA ranking request"""
    suppliers_data: Dict[str, Dict[str, float]]
    criteria: List[CriterionDefinition]
    method: str = Field(default="topsis", pattern="^(topsis|ahp|electre)$")
    weights: Optional[Dict[str, float]] = None


class ComparisonRequest(BaseModel):
    """Supplier comparison request"""
    supplier_1_id: str
    supplier_2_id: str
    comparison_method: str = Field(default="absolute", pattern="^(absolute|relative|percentile)$")


class RankingRequest(BaseModel):
    """Supplier ranking request"""
    supplier_ids: List[str]
    ranking_method: str = Field(default="simple", pattern="^(simple|borda|pareto)$")


class GapAnalysisRequest(BaseModel):
    """Gap analysis request"""
    supplier_id: str
    benchmark_type: str = Field(default="best_in_class", pattern="^(best_in_class|industry_average|custom)$")
    benchmark_scores: Optional[Dict[str, float]] = None


class IntegratedDecisionRequest(BaseModel):
    """Comprehensive integrated decision support request"""
    suppliers: List[SupplierEvaluationRequest]
    criteria: List[CriterionDefinition]
    mcda_method: str = Field(default="topsis", pattern="^(topsis|ahp|electre)$")
    include_gap_analysis: bool = True
    include_comparison: bool = True


# API Endpoints

@router.post("/evaluate-supplier")
async def evaluate_supplier(request: SupplierEvaluationRequest):
    """
    Comprehensive supplier evaluation across all 7 metric categories.
    Returns overall score, tier classification, and category breakdowns.
    """
    try:
        integration_service = get_integration_service()
        
        result = integration_service.evaluate_supplier_comprehensive(
            supplier_id=request.supplier_id,
            quality_metrics=request.quality_metrics.dict(),
            delivery_metrics=request.delivery_metrics.dict(),
            cost_metrics=request.cost_metrics.dict(),
            compliance_metrics=request.compliance_metrics.dict(),
            financial_metrics=request.financial_metrics.dict(),
            risk_metrics=request.risk_metrics.dict(),
            sustainability_metrics=request.sustainability_metrics.dict(),
            performance_period_start=request.performance_period_start,
            performance_period_end=request.performance_period_end,
            custom_weights=request.custom_weights
        )
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mcda-ranking")
async def mcda_ranking(request: MCDARequest):
    """
    Perform Multi-Criteria Decision Analysis using TOPSIS, AHP, or ELECTRE.
    Returns ranked suppliers with scores.
    """
    try:
        integration_service = get_integration_service()
        
        result = integration_service.mcda_supplier_selection(
            suppliers_data=request.suppliers_data,
            criteria=[c.dict() for c in request.criteria],
            method=request.method,
            weights=request.weights
        )
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare-suppliers")
async def compare_suppliers(request: ComparisonRequest):
    """
    Compare two suppliers across all performance dimensions.
    Returns detailed comparison metrics and winner identification.
    """
    try:
        integration_service = get_integration_service()
        
        result = integration_service.compare_suppliers(
            supplier_1_id=request.supplier_1_id,
            supplier_2_id=request.supplier_2_id,
            comparison_method=request.comparison_method
        )
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rank-suppliers")
async def rank_suppliers(request: RankingRequest):
    """
    Rank multiple suppliers using simple, Borda count, or Pareto methods.
    Returns ranked list with scores and efficiency metrics.
    """
    try:
        integration_service = get_integration_service()
        
        result = integration_service.rank_suppliers(
            supplier_ids=request.supplier_ids,
            ranking_method=request.ranking_method
        )
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gap-analysis")
async def gap_analysis(request: GapAnalysisRequest):
    """
    Perform gap analysis against benchmarks (best-in-class, industry average, or custom).
    Returns identified gaps, critical gaps, and improvement priorities.
    """
    try:
        integration_service = get_integration_service()
        
        result = integration_service.gap_analysis(
            supplier_id=request.supplier_id,
            benchmark_type=request.benchmark_type,
            benchmark_scores=request.benchmark_scores
        )
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/integrated-decision-support")
async def integrated_decision_support(request: IntegratedDecisionRequest):
    """
    Comprehensive integrated decision support combining:
    - Full supplier evaluation (all 7 metric categories)
    - MCDA ranking (TOPSIS/AHP/ELECTRE)
    - Supplier comparison
    - Gap analysis
    - Top recommendation
    
    This is the main endpoint for complete supplier selection analysis.
    """
    try:
        integration_service = get_integration_service()
        
        # Prepare suppliers data
        suppliers_data = {}
        for supplier_req in request.suppliers:
            suppliers_data[supplier_req.supplier_id] = {
                'quality_metrics': supplier_req.quality_metrics.dict(),
                'delivery_metrics': supplier_req.delivery_metrics.dict(),
                'cost_metrics': supplier_req.cost_metrics.dict(),
                'compliance_metrics': supplier_req.compliance_metrics.dict(),
                'financial_metrics': supplier_req.financial_metrics.dict(),
                'risk_metrics': supplier_req.risk_metrics.dict(),
                'sustainability_metrics': supplier_req.sustainability_metrics.dict(),
                'performance_period_start': supplier_req.performance_period_start,
                'performance_period_end': supplier_req.performance_period_end,
                'custom_weights': supplier_req.custom_weights
            }
        
        # Run integrated analysis
        result = integration_service.integrated_decision_support(
            suppliers_data=suppliers_data,
            criteria_definition=[c.dict() for c in request.criteria],
            mcda_method=request.mcda_method,
            include_gap_analysis=request.include_gap_analysis,
            include_comparison=request.include_comparison
        )
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        )


@router.get("/health")
async def integration_health_check():
    """Health check for integrated services"""
    try:
        integration_service = get_integration_service()
        
        return {
            "success": True,
            "status": "healthy",
            "modules": {
                "mcda": "available",
                "supplier_evaluation": "available",
                "comparison": "available",
                "gap_analysis": "available"
            },
            "algorithms": {
                "topsis": "ready",
                "ahp": "ready",
                "electre": "ready"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
