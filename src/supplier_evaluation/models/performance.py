"""
Performance Metrics and Evaluation Models
Tracks supplier performance across multiple dimensions.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime, date
from enum import Enum
import numpy as np


class MetricCategory(Enum):
    """Categories of performance metrics."""
    QUALITY = "quality"
    DELIVERY = "delivery"
    COST = "cost"
    COMPLIANCE = "compliance"
    FINANCIAL = "financial"
    RISK = "risk"
    SUSTAINABILITY = "sustainability"
    RESPONSIVENESS = "responsiveness"


@dataclass
class QualityMetrics:
    """Quality performance metrics."""
    defect_rate: float  # Percentage (0-100)
    rejection_rate: float  # Percentage (0-100)
    rework_rate: float  # Percentage (0-100)
    first_pass_yield: float  # Percentage (0-100)
    customer_complaints: int
    quality_incidents: int
    non_conformance_reports: int
    corrective_actions_open: int
    corrective_actions_closed: int
    
    # Certifications compliance
    quality_certifications_valid: int
    quality_audit_score: Optional[float] = None  # 0-100
    
    # Time period
    measurement_start_date: date = field(default_factory=date.today)
    measurement_end_date: date = field(default_factory=date.today)
    
    def calculate_quality_score(self) -> float:
        """
        Calculate composite quality score (0-100).
        Higher is better.
        """
        # Inverse metrics (lower is better)
        defect_score = max(0, 100 - self.defect_rate)
        rejection_score = max(0, 100 - self.rejection_rate)
        rework_score = max(0, 100 - self.rework_rate)
        
        # Direct metric (higher is better)
        yield_score = self.first_pass_yield
        
        # Incident-based scoring (normalize to 0-100)
        incident_penalty = min(50, (self.customer_complaints * 5 + 
                                   self.quality_incidents * 3 + 
                                   self.non_conformance_reports * 2))
        incident_score = max(0, 100 - incident_penalty)
        
        # Corrective action efficiency
        if self.corrective_actions_open + self.corrective_actions_closed > 0:
            ca_efficiency = (self.corrective_actions_closed / 
                           (self.corrective_actions_open + self.corrective_actions_closed)) * 100
        else:
            ca_efficiency = 100
        
        # Audit score (if available)
        audit_score = self.quality_audit_score if self.quality_audit_score else 75
        
        # Weighted average
        weights = {
            'defect': 0.20,
            'rejection': 0.15,
            'rework': 0.10,
            'yield': 0.20,
            'incident': 0.15,
            'ca_efficiency': 0.10,
            'audit': 0.10
        }
        
        composite_score = (
            defect_score * weights['defect'] +
            rejection_score * weights['rejection'] +
            rework_score * weights['rework'] +
            yield_score * weights['yield'] +
            incident_score * weights['incident'] +
            ca_efficiency * weights['ca_efficiency'] +
            audit_score * weights['audit']
        )
        
        return round(composite_score, 2)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'defect_rate': self.defect_rate,
            'rejection_rate': self.rejection_rate,
            'rework_rate': self.rework_rate,
            'first_pass_yield': self.first_pass_yield,
            'customer_complaints': self.customer_complaints,
            'quality_incidents': self.quality_incidents,
            'non_conformance_reports': self.non_conformance_reports,
            'corrective_actions_open': self.corrective_actions_open,
            'corrective_actions_closed': self.corrective_actions_closed,
            'quality_certifications_valid': self.quality_certifications_valid,
            'quality_audit_score': self.quality_audit_score,
            'measurement_start_date': self.measurement_start_date.isoformat(),
            'measurement_end_date': self.measurement_end_date.isoformat(),
            'quality_score': self.calculate_quality_score()
        }


@dataclass
class DeliveryMetrics:
    """Delivery performance metrics."""
    on_time_delivery_rate: float  # Percentage (0-100)
    early_delivery_rate: float  # Percentage (0-100)
    late_delivery_rate: float  # Percentage (0-100)
    average_lead_time_days: float
    lead_time_variance_days: float
    order_fulfillment_rate: float  # Percentage (0-100)
    partial_shipment_rate: float  # Percentage (0-100)
    damage_in_transit_rate: float  # Percentage (0-100)
    documentation_accuracy: float  # Percentage (0-100)
    
    # Counts
    total_deliveries: int
    on_time_deliveries: int
    late_deliveries: int
    
    # Time period
    measurement_start_date: date = field(default_factory=date.today)
    measurement_end_date: date = field(default_factory=date.today)
    
    def calculate_delivery_score(self) -> float:
        """
        Calculate composite delivery score (0-100).
        Higher is better.
        """
        # Main metrics
        otd_score = self.on_time_delivery_rate
        fulfillment_score = self.order_fulfillment_rate
        
        # Penalty for partial shipments and damage
        partial_penalty = self.partial_shipment_rate * 0.5
        damage_penalty = self.damage_in_transit_rate * 2
        reliability_score = max(0, 100 - partial_penalty - damage_penalty)
        
        # Lead time consistency (lower variance is better)
        if self.average_lead_time_days > 0:
            cv = (self.lead_time_variance_days / self.average_lead_time_days) * 100
            consistency_score = max(0, 100 - cv)
        else:
            consistency_score = 100
        
        # Documentation accuracy
        doc_score = self.documentation_accuracy
        
        # Weighted average
        weights = {
            'otd': 0.35,
            'fulfillment': 0.25,
            'reliability': 0.20,
            'consistency': 0.10,
            'documentation': 0.10
        }
        
        composite_score = (
            otd_score * weights['otd'] +
            fulfillment_score * weights['fulfillment'] +
            reliability_score * weights['reliability'] +
            consistency_score * weights['consistency'] +
            doc_score * weights['documentation']
        )
        
        return round(composite_score, 2)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'on_time_delivery_rate': self.on_time_delivery_rate,
            'early_delivery_rate': self.early_delivery_rate,
            'late_delivery_rate': self.late_delivery_rate,
            'average_lead_time_days': self.average_lead_time_days,
            'lead_time_variance_days': self.lead_time_variance_days,
            'order_fulfillment_rate': self.order_fulfillment_rate,
            'partial_shipment_rate': self.partial_shipment_rate,
            'damage_in_transit_rate': self.damage_in_transit_rate,
            'documentation_accuracy': self.documentation_accuracy,
            'total_deliveries': self.total_deliveries,
            'on_time_deliveries': self.on_time_deliveries,
            'late_deliveries': self.late_deliveries,
            'measurement_start_date': self.measurement_start_date.isoformat(),
            'measurement_end_date': self.measurement_end_date.isoformat(),
            'delivery_score': self.calculate_delivery_score()
        }


@dataclass
class CostMetrics:
    """Cost competitiveness metrics."""
    average_unit_cost: float
    cost_variance_percentage: float
    total_cost_of_ownership: float
    price_competitiveness_index: float  # 0-100, compared to market
    payment_discount_utilization: float  # Percentage
    invoice_accuracy_rate: float  # Percentage
    pricing_stability_index: float  # 0-100
    
    # Cost breakdown
    material_cost: float
    transportation_cost: float
    overhead_cost: float
    quality_cost: float  # Cost of poor quality
    
    # Time period
    measurement_start_date: date = field(default_factory=date.today)
    measurement_end_date: date = field(default_factory=date.today)
    
    def calculate_cost_score(self) -> float:
        """
        Calculate composite cost score (0-100).
        Higher is better (more competitive).
        """
        # Price competitiveness (direct metric)
        competitiveness_score = self.price_competitiveness_index
        
        # Cost variance (lower is better)
        variance_score = max(0, 100 - abs(self.cost_variance_percentage))
        
        # Pricing stability
        stability_score = self.pricing_stability_index
        
        # Invoice accuracy
        accuracy_score = self.invoice_accuracy_rate
        
        # Payment discount utilization
        discount_score = self.payment_discount_utilization
        
        # Quality cost impact (lower is better)
        if self.total_cost_of_ownership > 0:
            quality_cost_ratio = (self.quality_cost / self.total_cost_of_ownership) * 100
            quality_impact_score = max(0, 100 - quality_cost_ratio * 2)
        else:
            quality_impact_score = 100
        
        # Weighted average
        weights = {
            'competitiveness': 0.30,
            'variance': 0.15,
            'stability': 0.20,
            'accuracy': 0.15,
            'discount': 0.10,
            'quality_impact': 0.10
        }
        
        composite_score = (
            competitiveness_score * weights['competitiveness'] +
            variance_score * weights['variance'] +
            stability_score * weights['stability'] +
            accuracy_score * weights['accuracy'] +
            discount_score * weights['discount'] +
            quality_impact_score * weights['quality_impact']
        )
        
        return round(composite_score, 2)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'average_unit_cost': self.average_unit_cost,
            'cost_variance_percentage': self.cost_variance_percentage,
            'total_cost_of_ownership': self.total_cost_of_ownership,
            'price_competitiveness_index': self.price_competitiveness_index,
            'payment_discount_utilization': self.payment_discount_utilization,
            'invoice_accuracy_rate': self.invoice_accuracy_rate,
            'pricing_stability_index': self.pricing_stability_index,
            'material_cost': self.material_cost,
            'transportation_cost': self.transportation_cost,
            'overhead_cost': self.overhead_cost,
            'quality_cost': self.quality_cost,
            'measurement_start_date': self.measurement_start_date.isoformat(),
            'measurement_end_date': self.measurement_end_date.isoformat(),
            'cost_score': self.calculate_cost_score()
        }


@dataclass
class ComplianceMetrics:
    """Compliance and regulatory metrics."""
    regulatory_compliance_rate: float  # Percentage (0-100)
    audit_findings_open: int
    audit_findings_closed: int
    certifications_current: int
    certifications_expired: int
    safety_incidents: int
    environmental_violations: int
    labor_violations: int
    data_privacy_breaches: int
    ethical_violations: int
    
    # Compliance areas
    has_iso_9001: bool = False
    has_iso_14001: bool = False
    has_iso_45001: bool = False
    has_social_accountability: bool = False
    
    # Time period
    measurement_start_date: date = field(default_factory=date.today)
    measurement_end_date: date = field(default_factory=date.today)
    
    def calculate_compliance_score(self) -> float:
        """
        Calculate composite compliance score (0-100).
        Higher is better.
        """
        # Base compliance rate
        compliance_rate_score = self.regulatory_compliance_rate
        
        # Audit findings efficiency
        total_findings = self.audit_findings_open + self.audit_findings_closed
        if total_findings > 0:
            findings_efficiency = (self.audit_findings_closed / total_findings) * 100
        else:
            findings_efficiency = 100
        
        # Certification status
        total_certs = self.certifications_current + self.certifications_expired
        if total_certs > 0:
            cert_score = (self.certifications_current / total_certs) * 100
        else:
            cert_score = 50  # Neutral if no certifications
        
        # Violations and incidents (penalties)
        violation_penalty = min(50, (
            self.safety_incidents * 5 +
            self.environmental_violations * 4 +
            self.labor_violations * 4 +
            self.data_privacy_breaches * 6 +
            self.ethical_violations * 5
        ))
        violation_score = max(0, 100 - violation_penalty)
        
        # Certification coverage bonus
        cert_coverage = sum([
            self.has_iso_9001,
            self.has_iso_14001,
            self.has_iso_45001,
            self.has_social_accountability
        ]) / 4 * 100
        
        # Weighted average
        weights = {
            'compliance_rate': 0.30,
            'findings_efficiency': 0.15,
            'cert_status': 0.20,
            'violations': 0.25,
            'cert_coverage': 0.10
        }
        
        composite_score = (
            compliance_rate_score * weights['compliance_rate'] +
            findings_efficiency * weights['findings_efficiency'] +
            cert_score * weights['cert_status'] +
            violation_score * weights['violations'] +
            cert_coverage * weights['cert_coverage']
        )
        
        return round(composite_score, 2)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'regulatory_compliance_rate': self.regulatory_compliance_rate,
            'audit_findings_open': self.audit_findings_open,
            'audit_findings_closed': self.audit_findings_closed,
            'certifications_current': self.certifications_current,
            'certifications_expired': self.certifications_expired,
            'safety_incidents': self.safety_incidents,
            'environmental_violations': self.environmental_violations,
            'labor_violations': self.labor_violations,
            'data_privacy_breaches': self.data_privacy_breaches,
            'ethical_violations': self.ethical_violations,
            'has_iso_9001': self.has_iso_9001,
            'has_iso_14001': self.has_iso_14001,
            'has_iso_45001': self.has_iso_45001,
            'has_social_accountability': self.has_social_accountability,
            'measurement_start_date': self.measurement_start_date.isoformat(),
            'measurement_end_date': self.measurement_end_date.isoformat(),
            'compliance_score': self.calculate_compliance_score()
        }


@dataclass
class FinancialStabilityMetrics:
    """Financial health and stability metrics."""
    credit_score: float  # 0-100 normalized
    debt_to_equity_ratio: float
    current_ratio: float
    quick_ratio: float
    profit_margin_percentage: float
    revenue_growth_rate: float
    payment_delinquency_rate: float  # Percentage
    bankruptcy_risk_score: float  # 0-100, lower is better
    
    # Financial health indicators
    days_payable_outstanding: float
    cash_flow_stability_index: float  # 0-100
    
    # Time period
    measurement_start_date: date = field(default_factory=date.today)
    measurement_end_date: date = field(default_factory=date.today)
    
    def calculate_financial_score(self) -> float:
        """
        Calculate composite financial stability score (0-100).
        Higher is better.
        """
        # Credit score (direct metric)
        credit_score_normalized = self.credit_score
        
        # Liquidity ratios (ideal ranges)
        # Current ratio: 1.5-3.0 is good
        current_ratio_score = min(100, max(0, (self.current_ratio / 2.0) * 100))
        
        # Quick ratio: 1.0-2.0 is good
        quick_ratio_score = min(100, max(0, (self.quick_ratio / 1.5) * 100))
        
        # Debt to equity (lower is better, < 2.0 is good)
        if self.debt_to_equity_ratio <= 2.0:
            debt_score = 100 - (self.debt_to_equity_ratio / 2.0) * 30
        else:
            debt_score = max(0, 70 - (self.debt_to_equity_ratio - 2.0) * 20)
        
        # Profitability
        profit_score = min(100, max(0, self.profit_margin_percentage * 5))
        
        # Growth (normalize to 0-100, cap at 20% growth)
        growth_score = min(100, max(0, (self.revenue_growth_rate + 10) * 5))
        
        # Bankruptcy risk (inverse)
        bankruptcy_score = 100 - self.bankruptcy_risk_score
        
        # Payment behavior (lower delinquency is better)
        payment_score = max(0, 100 - self.payment_delinquency_rate * 2)
        
        # Cash flow stability
        cashflow_score = self.cash_flow_stability_index
        
        # Weighted average
        weights = {
            'credit': 0.20,
            'current_ratio': 0.10,
            'quick_ratio': 0.10,
            'debt': 0.15,
            'profit': 0.10,
            'growth': 0.10,
            'bankruptcy': 0.15,
            'payment': 0.05,
            'cashflow': 0.05
        }
        
        composite_score = (
            credit_score_normalized * weights['credit'] +
            current_ratio_score * weights['current_ratio'] +
            quick_ratio_score * weights['quick_ratio'] +
            debt_score * weights['debt'] +
            profit_score * weights['profit'] +
            growth_score * weights['growth'] +
            bankruptcy_score * weights['bankruptcy'] +
            payment_score * weights['payment'] +
            cashflow_score * weights['cashflow']
        )
        
        return round(composite_score, 2)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'credit_score': self.credit_score,
            'debt_to_equity_ratio': self.debt_to_equity_ratio,
            'current_ratio': self.current_ratio,
            'quick_ratio': self.quick_ratio,
            'profit_margin_percentage': self.profit_margin_percentage,
            'revenue_growth_rate': self.revenue_growth_rate,
            'payment_delinquency_rate': self.payment_delinquency_rate,
            'bankruptcy_risk_score': self.bankruptcy_risk_score,
            'days_payable_outstanding': self.days_payable_outstanding,
            'cash_flow_stability_index': self.cash_flow_stability_index,
            'measurement_start_date': self.measurement_start_date.isoformat(),
            'measurement_end_date': self.measurement_end_date.isoformat(),
            'financial_score': self.calculate_financial_score()
        }


@dataclass
class RiskMetrics:
    """Risk assessment metrics."""
    overall_risk_score: float  # 0-100, lower is better
    geopolitical_risk: float  # 0-100
    operational_risk: float  # 0-100
    financial_risk: float  # 0-100
    reputational_risk: float  # 0-100
    cybersecurity_risk: float  # 0-100
    supply_chain_disruption_risk: float  # 0-100
    
    # Risk indicators
    single_source_dependency: bool
    geographic_concentration: bool
    capacity_constraints: bool
    
    # Historical
    past_supply_disruptions: int
    past_quality_failures: int
    past_delivery_failures: int
    
    # Time period
    measurement_start_date: date = field(default_factory=date.today)
    measurement_end_date: date = field(default_factory=date.today)
    
    def calculate_risk_score(self) -> float:
        """
        Calculate composite risk score (0-100).
        Lower is better (less risky).
        """
        # Average of individual risk components
        risk_components = [
            self.geopolitical_risk,
            self.operational_risk,
            self.financial_risk,
            self.reputational_risk,
            self.cybersecurity_risk,
            self.supply_chain_disruption_risk
        ]
        
        avg_risk = np.mean(risk_components)
        
        # Risk indicator penalties
        indicator_penalty = sum([
            10 if self.single_source_dependency else 0,
            10 if self.geographic_concentration else 0,
            10 if self.capacity_constraints else 0
        ])
        
        # Historical failure penalties
        history_penalty = min(30, (
            self.past_supply_disruptions * 5 +
            self.past_quality_failures * 3 +
            self.past_delivery_failures * 2
        ))
        
        composite_risk = min(100, avg_risk + indicator_penalty + history_penalty)
        
        return round(composite_risk, 2)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'overall_risk_score': self.overall_risk_score,
            'geopolitical_risk': self.geopolitical_risk,
            'operational_risk': self.operational_risk,
            'financial_risk': self.financial_risk,
            'reputational_risk': self.reputational_risk,
            'cybersecurity_risk': self.cybersecurity_risk,
            'supply_chain_disruption_risk': self.supply_chain_disruption_risk,
            'single_source_dependency': self.single_source_dependency,
            'geographic_concentration': self.geographic_concentration,
            'capacity_constraints': self.capacity_constraints,
            'past_supply_disruptions': self.past_supply_disruptions,
            'past_quality_failures': self.past_quality_failures,
            'past_delivery_failures': self.past_delivery_failures,
            'measurement_start_date': self.measurement_start_date.isoformat(),
            'measurement_end_date': self.measurement_end_date.isoformat(),
            'risk_score': self.calculate_risk_score()
        }


@dataclass
class SustainabilityMetrics:
    """Sustainability and ESG metrics."""
    carbon_footprint_score: float  # 0-100, higher is better
    renewable_energy_percentage: float
    waste_reduction_rate: float
    water_conservation_score: float  # 0-100
    recycling_rate: float
    
    # Social responsibility
    fair_labor_practices_score: float  # 0-100
    diversity_inclusion_score: float  # 0-100
    community_engagement_score: float  # 0-100
    
    # Governance
    ethical_sourcing_score: float  # 0-100
    transparency_score: float  # 0-100
    
    # Certifications
    has_environmental_certification: bool
    has_social_certification: bool
    
    # Time period
    measurement_start_date: date = field(default_factory=date.today)
    measurement_end_date: date = field(default_factory=date.today)
    
    def calculate_sustainability_score(self) -> float:
        """
        Calculate composite sustainability score (0-100).
        Higher is better.
        """
        # Environmental metrics
        env_score = (
            self.carbon_footprint_score * 0.30 +
            self.renewable_energy_percentage * 0.25 +
            self.waste_reduction_rate * 0.20 +
            self.water_conservation_score * 0.15 +
            self.recycling_rate * 0.10
        )
        
        # Social metrics
        social_score = (
            self.fair_labor_practices_score * 0.40 +
            self.diversity_inclusion_score * 0.30 +
            self.community_engagement_score * 0.30
        )
        
        # Governance metrics
        governance_score = (
            self.ethical_sourcing_score * 0.60 +
            self.transparency_score * 0.40
        )
        
        # Certification bonus
        cert_bonus = sum([
            5 if self.has_environmental_certification else 0,
            5 if self.has_social_certification else 0
        ])
        
        # Weighted ESG score
        esg_score = (
            env_score * 0.40 +
            social_score * 0.35 +
            governance_score * 0.25
        ) + cert_bonus
        
        return round(min(100, esg_score), 2)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'carbon_footprint_score': self.carbon_footprint_score,
            'renewable_energy_percentage': self.renewable_energy_percentage,
            'waste_reduction_rate': self.waste_reduction_rate,
            'water_conservation_score': self.water_conservation_score,
            'recycling_rate': self.recycling_rate,
            'fair_labor_practices_score': self.fair_labor_practices_score,
            'diversity_inclusion_score': self.diversity_inclusion_score,
            'community_engagement_score': self.community_engagement_score,
            'ethical_sourcing_score': self.ethical_sourcing_score,
            'transparency_score': self.transparency_score,
            'has_environmental_certification': self.has_environmental_certification,
            'has_social_certification': self.has_social_certification,
            'measurement_start_date': self.measurement_start_date.isoformat(),
            'measurement_end_date': self.measurement_end_date.isoformat(),
            'sustainability_score': self.calculate_sustainability_score()
        }


@dataclass
class SupplierPerformance:
    """
    Complete supplier performance profile.
    """
    supplier_id: str
    performance_period_start: date
    performance_period_end: date
    
    quality_metrics: QualityMetrics
    delivery_metrics: DeliveryMetrics
    cost_metrics: CostMetrics
    compliance_metrics: ComplianceMetrics
    financial_metrics: FinancialStabilityMetrics
    risk_metrics: RiskMetrics
    sustainability_metrics: SustainabilityMetrics
    
    created_at: datetime = field(default_factory=datetime.now)
    
    def calculate_overall_score(
        self,
        weights: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Calculate overall supplier performance score (0-100).
        
        Args:
            weights: Custom weights for each category. If None, uses default weights.
            
        Returns:
            Overall performance score
        """
        if weights is None:
            weights = {
                'quality': 0.25,
                'delivery': 0.20,
                'cost': 0.15,
                'compliance': 0.15,
                'financial': 0.10,
                'risk': 0.10,  # Note: risk is inverted (100 - risk_score)
                'sustainability': 0.05
            }
        
        # Normalize weights
        total_weight = sum(weights.values())
        normalized_weights = {k: v / total_weight for k, v in weights.items()}
        
        # Calculate scores
        scores = {
            'quality': self.quality_metrics.calculate_quality_score(),
            'delivery': self.delivery_metrics.calculate_delivery_score(),
            'cost': self.cost_metrics.calculate_cost_score(),
            'compliance': self.compliance_metrics.calculate_compliance_score(),
            'financial': self.financial_metrics.calculate_financial_score(),
            'risk': 100 - self.risk_metrics.calculate_risk_score(),  # Invert risk
            'sustainability': self.sustainability_metrics.calculate_sustainability_score()
        }
        
        # Weighted sum
        overall_score = sum(
            scores[category] * normalized_weights[category]
            for category in scores.keys()
        )
        
        return round(overall_score, 2)
    
    def get_category_scores(self) -> Dict[str, float]:
        """Get individual category scores."""
        return {
            'quality': self.quality_metrics.calculate_quality_score(),
            'delivery': self.delivery_metrics.calculate_delivery_score(),
            'cost': self.cost_metrics.calculate_cost_score(),
            'compliance': self.compliance_metrics.calculate_compliance_score(),
            'financial': self.financial_metrics.calculate_financial_score(),
            'risk': self.risk_metrics.calculate_risk_score(),
            'sustainability': self.sustainability_metrics.calculate_sustainability_score()
        }
    
    def to_dict(self, include_overall_score: bool = True) -> Dict:
        """Convert to dictionary."""
        data = {
            'supplier_id': self.supplier_id,
            'performance_period_start': self.performance_period_start.isoformat(),
            'performance_period_end': self.performance_period_end.isoformat(),
            'quality_metrics': self.quality_metrics.to_dict(),
            'delivery_metrics': self.delivery_metrics.to_dict(),
            'cost_metrics': self.cost_metrics.to_dict(),
            'compliance_metrics': self.compliance_metrics.to_dict(),
            'financial_metrics': self.financial_metrics.to_dict(),
            'risk_metrics': self.risk_metrics.to_dict(),
            'sustainability_metrics': self.sustainability_metrics.to_dict(),
            'created_at': self.created_at.isoformat()
        }
        
        if include_overall_score:
            data['overall_score'] = self.calculate_overall_score()
            data['category_scores'] = self.get_category_scores()
        
        return data
