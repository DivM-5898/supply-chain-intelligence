"""
Compliance Framework Module
Core data models and framework for ethics and compliance management.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from datetime import datetime, date
from enum import Enum
import json


class ComplianceCategory(Enum):
    """Compliance categories."""
    LABOR_STANDARDS = "labor_standards"
    ENVIRONMENTAL = "environmental"
    ANTI_CORRUPTION = "anti_corruption"
    DATA_PRIVACY = "data_privacy"
    PRODUCT_SAFETY = "product_safety"
    TRADE_COMPLIANCE = "trade_compliance"
    ETHICAL_SOURCING = "ethical_sourcing"


class RiskLevel(Enum):
    """Risk severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ComplianceStatus(Enum):
    """Compliance status."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNDER_REVIEW = "under_review"
    NOT_ASSESSED = "not_assessed"


class ViolationType(Enum):
    """Types of compliance violations."""
    CHILD_LABOR = "child_labor"
    FORCED_LABOR = "forced_labor"
    UNSAFE_CONDITIONS = "unsafe_conditions"
    WAGE_VIOLATIONS = "wage_violations"
    ENVIRONMENTAL_DAMAGE = "environmental_damage"
    CORRUPTION = "corruption"
    DATA_BREACH = "data_breach"
    PRODUCT_DEFECT = "product_defect"
    CONFLICT_MINERALS = "conflict_minerals"
    SANCTIONS_VIOLATION = "sanctions_violation"


@dataclass
class ComplianceRequirement:
    """Individual compliance requirement."""
    id: str
    name: str
    category: ComplianceCategory
    description: str
    regulation: str  # e.g., "GDPR Article 5"
    mandatory: bool
    risk_level: RiskLevel
    verification_method: str
    evidence_required: List[str]
    frequency: str  # e.g., "annual", "quarterly"
    applicable_regions: List[str] = field(default_factory=list)
    industry_specific: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category.value,
            'description': self.description,
            'regulation': self.regulation,
            'mandatory': self.mandatory,
            'risk_level': self.risk_level.value,
            'verification_method': self.verification_method,
            'evidence_required': self.evidence_required,
            'frequency': self.frequency,
            'applicable_regions': self.applicable_regions,
            'industry_specific': self.industry_specific
        }


@dataclass
class ComplianceViolation:
    """Compliance violation record."""
    id: str
    supplier_id: str
    violation_type: ViolationType
    category: ComplianceCategory
    severity: RiskLevel
    description: str
    detected_date: datetime
    reported_by: str
    status: str  # "open", "under_investigation", "resolved", "closed"
    evidence: List[str] = field(default_factory=list)
    corrective_action: Optional[str] = None
    resolution_date: Optional[datetime] = None
    notes: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'violation_type': self.violation_type.value,
            'category': self.category.value,
            'severity': self.severity.value,
            'description': self.description,
            'detected_date': self.detected_date.isoformat(),
            'reported_by': self.reported_by,
            'status': self.status,
            'evidence': self.evidence,
            'corrective_action': self.corrective_action,
            'resolution_date': self.resolution_date.isoformat() if self.resolution_date else None,
            'notes': self.notes
        }


@dataclass
class Certification:
    """Supplier certification."""
    id: str
    supplier_id: str
    cert_type: str  # e.g., "ISO 14001", "SA8000"
    cert_number: str
    issuing_body: str
    issue_date: date
    expiry_date: date
    scope: str
    status: str  # "valid", "expired", "suspended", "revoked"
    document_url: Optional[str] = None
    verified: bool = False
    verification_date: Optional[date] = None
    
    def is_valid(self) -> bool:
        """Check if certification is currently valid."""
        today = date.today()
        return (
            self.status == "valid" and
            self.issue_date <= today < self.expiry_date
        )
    
    def days_until_expiry(self) -> int:
        """Days until certification expires."""
        return (self.expiry_date - date.today()).days
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'cert_type': self.cert_type,
            'cert_number': self.cert_number,
            'issuing_body': self.issuing_body,
            'issue_date': self.issue_date.isoformat(),
            'expiry_date': self.expiry_date.isoformat(),
            'scope': self.scope,
            'status': self.status,
            'document_url': self.document_url,
            'verified': self.verified,
            'verification_date': self.verification_date.isoformat() if self.verification_date else None,
            'is_valid': self.is_valid(),
            'days_until_expiry': self.days_until_expiry()
        }


@dataclass
class AuditRecord:
    """Compliance audit record."""
    id: str
    supplier_id: str
    audit_type: str  # "full", "focused", "follow-up"
    category: ComplianceCategory
    scheduled_date: date
    completed_date: Optional[date] = None
    auditor: str = ""
    status: str = "scheduled"  # "scheduled", "in_progress", "completed", "cancelled"
    findings: List[Dict] = field(default_factory=list)
    overall_score: Optional[float] = None
    recommendations: List[str] = field(default_factory=list)
    corrective_actions: List[Dict] = field(default_factory=list)
    next_audit_date: Optional[date] = None
    report_url: Optional[str] = None
    
    def add_finding(
        self,
        finding_type: str,
        severity: RiskLevel,
        description: str,
        evidence: List[str] = None
    ):
        """Add audit finding."""
        finding = {
            'type': finding_type,
            'severity': severity.value,
            'description': description,
            'evidence': evidence or [],
            'timestamp': datetime.now().isoformat()
        }
        self.findings.append(finding)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'audit_type': self.audit_type,
            'category': self.category.value,
            'scheduled_date': self.scheduled_date.isoformat(),
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'auditor': self.auditor,
            'status': self.status,
            'findings': self.findings,
            'overall_score': self.overall_score,
            'recommendations': self.recommendations,
            'corrective_actions': self.corrective_actions,
            'next_audit_date': self.next_audit_date.isoformat() if self.next_audit_date else None,
            'report_url': self.report_url
        }


@dataclass
class SupplierCompliance:
    """Supplier compliance profile."""
    supplier_id: str
    company_name: str
    country: str
    industry: str
    risk_tier: int  # 1 (highest risk) to 4 (lowest risk)
    overall_status: ComplianceStatus
    last_assessment_date: Optional[date] = None
    next_assessment_date: Optional[date] = None
    
    # Compliance scores by category (0-100)
    labor_score: Optional[float] = None
    environmental_score: Optional[float] = None
    anti_corruption_score: Optional[float] = None
    data_privacy_score: Optional[float] = None
    product_safety_score: Optional[float] = None
    trade_compliance_score: Optional[float] = None
    ethical_sourcing_score: Optional[float] = None
    
    # Additional tracking
    violations: List[str] = field(default_factory=list)  # Violation IDs
    certifications: List[str] = field(default_factory=list)  # Certification IDs
    audits: List[str] = field(default_factory=list)  # Audit IDs
    corrective_actions_open: int = 0
    corrective_actions_closed: int = 0
    
    def calculate_overall_score(self) -> float:
        """Calculate weighted overall compliance score."""
        scores = []
        weights = {
            'labor': (self.labor_score, 0.25),
            'environmental': (self.environmental_score, 0.20),
            'anti_corruption': (self.anti_corruption_score, 0.15),
            'data_privacy': (self.data_privacy_score, 0.15),
            'product_safety': (self.product_safety_score, 0.10),
            'trade': (self.trade_compliance_score, 0.10),
            'ethical': (self.ethical_sourcing_score, 0.05)
        }
        
        total_weight = 0
        weighted_sum = 0
        
        for category, (score, weight) in weights.items():
            if score is not None:
                weighted_sum += score * weight
                total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def get_compliance_gaps(self) -> List[str]:
        """Identify compliance gaps (scores below 70)."""
        gaps = []
        threshold = 70.0
        
        categories = {
            'Labor Standards': self.labor_score,
            'Environmental': self.environmental_score,
            'Anti-Corruption': self.anti_corruption_score,
            'Data Privacy': self.data_privacy_score,
            'Product Safety': self.product_safety_score,
            'Trade Compliance': self.trade_compliance_score,
            'Ethical Sourcing': self.ethical_sourcing_score
        }
        
        for name, score in categories.items():
            if score is not None and score < threshold:
                gaps.append(f"{name}: {score:.1f}%")
        
        return gaps
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'supplier_id': self.supplier_id,
            'company_name': self.company_name,
            'country': self.country,
            'industry': self.industry,
            'risk_tier': self.risk_tier,
            'overall_status': self.overall_status.value,
            'overall_score': self.calculate_overall_score(),
            'last_assessment_date': self.last_assessment_date.isoformat() if self.last_assessment_date else None,
            'next_assessment_date': self.next_assessment_date.isoformat() if self.next_assessment_date else None,
            'category_scores': {
                'labor': self.labor_score,
                'environmental': self.environmental_score,
                'anti_corruption': self.anti_corruption_score,
                'data_privacy': self.data_privacy_score,
                'product_safety': self.product_safety_score,
                'trade_compliance': self.trade_compliance_score,
                'ethical_sourcing': self.ethical_sourcing_score
            },
            'violations_count': len(self.violations),
            'certifications_count': len(self.certifications),
            'audits_count': len(self.audits),
            'corrective_actions_open': self.corrective_actions_open,
            'corrective_actions_closed': self.corrective_actions_closed,
            'compliance_gaps': self.get_compliance_gaps()
        }


class ComplianceFramework:
    """
    Main compliance framework managing requirements, violations, and assessments.
    """
    
    def __init__(self):
        self.requirements: Dict[str, ComplianceRequirement] = {}
        self.violations: Dict[str, ComplianceViolation] = {}
        self.certifications: Dict[str, Certification] = {}
        self.audits: Dict[str, AuditRecord] = {}
        self.suppliers: Dict[str, SupplierCompliance] = {}
        
        # Initialize with standard requirements
        self._load_standard_requirements()
    
    def _load_standard_requirements(self):
        """Load standard compliance requirements."""
        # This would typically load from a database or config file
        standard_requirements = [
            ComplianceRequirement(
                id="REQ_LABOR_001",
                name="Minimum Wage Compliance",
                category=ComplianceCategory.LABOR_STANDARDS,
                description="Ensure all workers receive at least minimum wage",
                regulation="ILO Convention 131",
                mandatory=True,
                risk_level=RiskLevel.HIGH,
                verification_method="Payroll audit",
                evidence_required=["Payroll records", "Employment contracts"],
                frequency="quarterly",
                applicable_regions=["Global"]
            ),
            ComplianceRequirement(
                id="REQ_ENV_001",
                name="Carbon Emissions Reporting",
                category=ComplianceCategory.ENVIRONMENTAL,
                description="Report greenhouse gas emissions",
                regulation="ISO 14064",
                mandatory=False,
                risk_level=RiskLevel.MEDIUM,
                verification_method="Third-party verification",
                evidence_required=["Emissions data", "Calculation methodology"],
                frequency="annual",
                applicable_regions=["EU", "US", "UK"]
            ),
            ComplianceRequirement(
                id="REQ_PRIV_001",
                name="GDPR Data Protection",
                category=ComplianceCategory.DATA_PRIVACY,
                description="Implement GDPR-compliant data handling",
                regulation="GDPR Article 5",
                mandatory=True,
                risk_level=RiskLevel.CRITICAL,
                verification_method="Audit and documentation review",
                evidence_required=["Privacy policy", "Data processing agreements", "Security measures"],
                frequency="annual",
                applicable_regions=["EU", "EEA"]
            )
        ]
        
        for req in standard_requirements:
            self.requirements[req.id] = req
    
    def add_requirement(self, requirement: ComplianceRequirement):
        """Add a compliance requirement."""
        self.requirements[requirement.id] = requirement
    
    def get_requirements_by_category(
        self,
        category: ComplianceCategory
    ) -> List[ComplianceRequirement]:
        """Get all requirements for a category."""
        return [
            req for req in self.requirements.values()
            if req.category == category
        ]
    
    def get_mandatory_requirements(self) -> List[ComplianceRequirement]:
        """Get all mandatory requirements."""
        return [
            req for req in self.requirements.values()
            if req.mandatory
        ]
    
    def register_supplier(self, supplier: SupplierCompliance):
        """Register supplier compliance profile."""
        self.suppliers[supplier.supplier_id] = supplier
    
    def record_violation(self, violation: ComplianceViolation):
        """Record a compliance violation."""
        self.violations[violation.id] = violation
        
        # Update supplier record
        if violation.supplier_id in self.suppliers:
            self.suppliers[violation.supplier_id].violations.append(violation.id)
    
    def get_supplier_violations(
        self,
        supplier_id: str,
        status: Optional[str] = None,
        severity: Optional[RiskLevel] = None
    ) -> List[ComplianceViolation]:
        """Get violations for a supplier with optional filters."""
        violations = [
            v for v in self.violations.values()
            if v.supplier_id == supplier_id
        ]
        
        if status:
            violations = [v for v in violations if v.status == status]
        
        if severity:
            violations = [v for v in violations if v.severity == severity]
        
        return violations
    
    def add_certification(self, certification: Certification):
        """Add supplier certification."""
        self.certifications[certification.id] = certification
        
        # Update supplier record
        if certification.supplier_id in self.suppliers:
            self.suppliers[certification.supplier_id].certifications.append(certification.id)
    
    def get_expiring_certifications(self, days: int = 90) -> List[Certification]:
        """Get certifications expiring within specified days."""
        return [
            cert for cert in self.certifications.values()
            if cert.is_valid() and 0 <= cert.days_until_expiry() <= days
        ]
    
    def schedule_audit(self, audit: AuditRecord):
        """Schedule a compliance audit."""
        self.audits[audit.id] = audit
        
        # Update supplier record
        if audit.supplier_id in self.suppliers:
            self.suppliers[audit.supplier_id].audits.append(audit.id)
    
    def get_compliance_summary(self) -> Dict:
        """Get overall compliance summary statistics."""
        total_suppliers = len(self.suppliers)
        total_violations = len(self.violations)
        open_violations = sum(
            1 for v in self.violations.values()
            if v.status in ["open", "under_investigation"]
        )
        
        compliant_suppliers = sum(
            1 for s in self.suppliers.values()
            if s.overall_status == ComplianceStatus.COMPLIANT
        )
        
        avg_score = sum(
            s.calculate_overall_score()
            for s in self.suppliers.values()
        ) / total_suppliers if total_suppliers > 0 else 0
        
        return {
            'total_suppliers': total_suppliers,
            'compliant_suppliers': compliant_suppliers,
            'compliance_rate': (compliant_suppliers / total_suppliers * 100) if total_suppliers > 0 else 0,
            'total_violations': total_violations,
            'open_violations': open_violations,
            'average_compliance_score': avg_score,
            'total_audits': len(self.audits),
            'total_certifications': len(self.certifications),
            'expiring_certifications': len(self.get_expiring_certifications())
        }
