"""
API Request/Response Models
Pydantic models for API validation
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class SupplierEvaluationRequest(BaseModel):
    supplier_ids: Optional[List[str]] = None
    model_type: str = "xgboost"  # xgboost or random_forest


class SupplierEvaluationResponse(BaseModel):
    results: List[Dict[str, Any]]
    model_type: str
    total_suppliers: int


class RiskPredictionRequest(BaseModel):
    supplier_ids: Optional[List[str]] = None


class RiskPredictionResponse(BaseModel):
    results: List[Dict[str, Any]]
    total_suppliers: int


class FraudPredictionRequest(BaseModel):
    supplier_ids: Optional[List[str]] = None
    model_type: str = "random_forest"  # random_forest or gradient_boosting


class FraudPredictionResponse(BaseModel):
    results: List[Dict[str, Any]]
    model_type: str
    total_suppliers: int


class ContractAnalysisRequest(BaseModel):
    contract_text: Optional[str] = None
    contract_id: Optional[str] = None


class ContractAnalysisResponse(BaseModel):
    analysis: Dict[str, Any]
    contract_id: Optional[str] = None


class TOPSISRequest(BaseModel):
    criteria_weights: Dict[str, float]
    benefit_criteria: Optional[List[str]] = None
    supplier_ids: Optional[List[str]] = None


class TOPSISResponse(BaseModel):
    results: List[Dict[str, Any]]
    method: str = "TOPSIS"


class AHPRequest(BaseModel):
    criteria: List[str]
    pairwise_comparisons: Dict[str, Dict[str, float]]
    supplier_ids: Optional[List[str]] = None


class AHPResponse(BaseModel):
    results: List[Dict[str, Any]]
    consistency_ratio: float
    method: str = "AHP"


class ExplainabilityRequest(BaseModel):
    supplier_id: str
    model_type: str = "supplier_scoring"
    explanation_type: str = "lime"  # lime or shap


class ExplainabilityResponse(BaseModel):
    explanation: Dict[str, Any]
    supplier_id: str


class BiasDetectionRequest(BaseModel):
    feature_name: str
    model_type: str = "supplier_scoring"

