"""
Compliance Assessor Module
Comprehensive system for assessing supplier compliance across all categories.
"""

from typing import Dict, List, Optional
from datetime import date, datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.ethics_compliance.models.compliance_framework import (
    ComplianceCategory,
    ComplianceStatus,
    RiskLevel,
    SupplierCompliance
)


class ComplianceAssessor:
    """
    Main assessor for evaluating supplier compliance across all categories.
    """
    
    def __init__(self):
        self.assessment_weights = {
            ComplianceCategory.LABOR_STANDARDS: 0.25,
            ComplianceCategory.ENVIRONMENTAL: 0.20,
            ComplianceCategory.ANTI_CORRUPTION: 0.15,
            ComplianceCategory.DATA_PRIVACY: 0.15,
            ComplianceCategory.PRODUCT_SAFETY: 0.10,
            ComplianceCategory.TRADE_COMPLIANCE: 0.10,
            ComplianceCategory.ETHICAL_SOURCING: 0.05
        }
    
    def assess_supplier(
        self,
        supplier_id: str,
        company_name: str,
        country: str,
        industry: str,
        assessment_data: Dict,
        assessment_type: str = 'full'
    ) -> SupplierCompliance:
        """
        Conduct comprehensive supplier compliance assessment.
        
        Args:
            supplier_id: Unique supplier identifier
            company_name: Supplier company name
            country: Country of operation
            industry: Industry sector
            assessment_data: Dict with category-specific assessment data
            assessment_type: 'full', 'focused', or 'follow-up'
            
        Returns:
            SupplierCompliance object with scores and status
        """
        # Initialize supplier compliance profile
        supplier = SupplierCompliance(
            supplier_id=supplier_id,
            company_name=company_name,
            country=country,
            industry=industry,
            risk_tier=self._calculate_risk_tier(country, industry),
            overall_status=ComplianceStatus.UNDER_REVIEW,
            last_assessment_date=date.today()
        )
        
        # Assess each category
        if assessment_type in ['full', 'focused']:
            supplier.labor_score = self._assess_labor_standards(
                assessment_data.get('labor', {})
            )
            supplier.environmental_score = self._assess_environmental(
                assessment_data.get('environmental', {})
            )
            supplier.anti_corruption_score = self._assess_anti_corruption(
                assessment_data.get('anti_corruption', {})
            )
            supplier.data_privacy_score = self._assess_data_privacy(
                assessment_data.get('data_privacy', {})
            )
            supplier.product_safety_score = self._assess_product_safety(
                assessment_data.get('product_safety', {})
            )
            supplier.trade_compliance_score = self._assess_trade_compliance(
                assessment_data.get('trade_compliance', {})
            )
            supplier.ethical_sourcing_score = self._assess_ethical_sourcing(
                assessment_data.get('ethical_sourcing', {})
            )
        
        # Calculate overall status
        overall_score = supplier.calculate_overall_score()
        supplier.overall_status = self._determine_status(overall_score)
        
        # Set next assessment date
        supplier.next_assessment_date = self._schedule_next_assessment(
            supplier.overall_status,
            supplier.risk_tier
        )
        
        return supplier
    
    def _calculate_risk_tier(self, country: str, industry: str) -> int:
        """
        Calculate supplier risk tier (1-4, where 1 is highest risk).
        
        Args:
            country: Country of operation
            industry: Industry sector
            
        Returns:
            Risk tier (1-4)
        """
        # High-risk countries (simplified example)
        high_risk_countries = ['CN', 'BD', 'MM', 'VN', 'IN']
        
        # High-risk industries
        high_risk_industries = [
            'textile', 'mining', 'electronics', 
            'agriculture', 'construction'
        ]
        
        risk_score = 0
        
        if country.upper() in high_risk_countries:
            risk_score += 2
        
        if any(ind in industry.lower() for ind in high_risk_industries):
            risk_score += 2
        
        # Convert to tier (1-4)
        if risk_score >= 4:
            return 1  # Highest risk
        elif risk_score >= 3:
            return 2
        elif risk_score >= 2:
            return 3
        else:
            return 4  # Lowest risk
    
    def _assess_labor_standards(self, data: Dict) -> float:
        """
        Assess labor standards compliance.
        
        Criteria:
        - Fair wages (20 points)
        - Working hours (15 points)
        - No child labor (25 points)
        - No forced labor (25 points)
        - Health & safety (15 points)
        """
        score = 0.0
        max_score = 100.0
        
        # Fair wages
        if data.get('minimum_wage_compliance', False):
            score += 20
        
        # Working hours
        max_hours = data.get('max_weekly_hours', 80)
        if max_hours <= 48:
            score += 15
        elif max_hours <= 60:
            score += 10
        
        # Child labor
        if data.get('no_child_labor_verified', False):
            score += 25
        
        # Forced labor
        if data.get('no_forced_labor_verified', False):
            score += 25
        
        # Health & safety
        if data.get('safety_standards_met', False):
            score += 15
        
        return min(score, max_score)
    
    def _assess_environmental(self, data: Dict) -> float:
        """
        Assess environmental compliance.
        
        Criteria:
        - Carbon emissions management (25 points)
        - Waste management (20 points)
        - Water usage (20 points)
        - Environmental certifications (20 points)
        - Pollution control (15 points)
        """
        score = 0.0
        
        if data.get('carbon_reporting', False):
            score += 15
        if data.get('carbon_reduction_plan', False):
            score += 10
        
        if data.get('waste_management_system', False):
            score += 20
        
        if data.get('water_efficiency_program', False):
            score += 20
        
        # Certifications
        env_certs = data.get('certifications', [])
        if any(cert in ['ISO 14001', 'EMAS'] for cert in env_certs):
            score += 20
        
        if data.get('pollution_controls', False):
            score += 15
        
        return min(score, 100.0)
    
    def _assess_anti_corruption(self, data: Dict) -> float:
        """
        Assess anti-corruption compliance.
        
        Criteria:
        - Anti-bribery policy (30 points)
        - Gifts & entertainment policy (20 points)
        - Conflicts of interest management (20 points)
        - Whistleblower mechanism (20 points)
        - Training programs (10 points)
        """
        score = 0.0
        
        if data.get('anti_bribery_policy', False):
            score += 30
        
        if data.get('gifts_policy', False):
            score += 20
        
        if data.get('conflict_of_interest_policy', False):
            score += 20
        
        if data.get('whistleblower_hotline', False):
            score += 20
        
        if data.get('ethics_training_provided', False):
            score += 10
        
        return min(score, 100.0)
    
    def _assess_data_privacy(self, data: Dict) -> float:
        """
        Assess data privacy compliance.
        
        Criteria:
        - GDPR/Privacy law compliance (30 points)
        - Data security measures (25 points)
        - Privacy policy (20 points)
        - Data breach procedures (15 points)
        - Training (10 points)
        """
        score = 0.0
        
        if data.get('gdpr_compliant', False):
            score += 30
        
        security_measures = data.get('security_measures', [])
        if len(security_measures) >= 3:
            score += 25
        elif len(security_measures) >= 2:
            score += 15
        
        if data.get('privacy_policy_published', False):
            score += 20
        
        if data.get('breach_response_plan', False):
            score += 15
        
        if data.get('privacy_training', False):
            score += 10
        
        return min(score, 100.0)
    
    def _assess_product_safety(self, data: Dict) -> float:
        """
        Assess product safety compliance.
        
        Criteria:
        - Quality standards (30 points)
        - Testing procedures (25 points)
        - Certifications (25 points)
        - Recall procedures (20 points)
        """
        score = 0.0
        
        if data.get('quality_management_system', False):
            score += 30
        
        if data.get('testing_protocols', False):
            score += 25
        
        safety_certs = data.get('certifications', [])
        if len(safety_certs) > 0:
            score += 25
        
        if data.get('recall_procedures', False):
            score += 20
        
        return min(score, 100.0)
    
    def _assess_trade_compliance(self, data: Dict) -> float:
        """
        Assess trade compliance.
        
        Criteria:
        - Import/export licenses (25 points)
        - Sanctions screening (30 points)
        - Country of origin documentation (25 points)
        - Trade agreement compliance (20 points)
        """
        score = 0.0
        
        if data.get('import_export_licenses', False):
            score += 25
        
        if data.get('sanctions_screening_process', False):
            score += 30
        
        if data.get('country_of_origin_documented', False):
            score += 25
        
        if data.get('trade_agreement_compliance', False):
            score += 20
        
        return min(score, 100.0)
    
    def _assess_ethical_sourcing(self, data: Dict) -> float:
        """
        Assess ethical sourcing compliance.
        
        Criteria:
        - Conflict minerals verification (40 points)
        - Supply chain transparency (30 points)
        - Supplier code of conduct (30 points)
        """
        score = 0.0
        
        if data.get('conflict_minerals_policy', False):
            score += 20
        if data.get('conflict_minerals_audit', False):
            score += 20
        
        if data.get('supply_chain_mapping', False):
            score += 30
        
        if data.get('supplier_code_of_conduct', False):
            score += 30
        
        return min(score, 100.0)
    
    def _determine_status(self, overall_score: float) -> ComplianceStatus:
        """Determine compliance status based on overall score."""
        if overall_score >= 85:
            return ComplianceStatus.COMPLIANT
        elif overall_score >= 70:
            return ComplianceStatus.PARTIALLY_COMPLIANT
        else:
            return ComplianceStatus.NON_COMPLIANT
    
    def _schedule_next_assessment(
        self,
        status: ComplianceStatus,
        risk_tier: int
    ) -> date:
        """Schedule next assessment based on status and risk."""
        from datetime import timedelta
        
        # Base intervals (in days)
        if status == ComplianceStatus.NON_COMPLIANT:
            days = 90  # Quarterly for non-compliant
        elif status == ComplianceStatus.PARTIALLY_COMPLIANT:
            days = 180  # Semi-annually
        else:
            days = 365  # Annually for compliant
        
        # Adjust for risk tier
        if risk_tier == 1:
            days = int(days * 0.5)  # More frequent for high risk
        elif risk_tier == 2:
            days = int(days * 0.75)
        
        return date.today() + timedelta(days=days)
    
    def generate_assessment_report(
        self,
        supplier: SupplierCompliance
    ) -> Dict:
        """Generate comprehensive assessment report."""
        return {
            'supplier_id': supplier.supplier_id,
            'company_name': supplier.company_name,
            'assessment_date': supplier.last_assessment_date.isoformat(),
            'overall_status': supplier.overall_status.value,
            'overall_score': supplier.calculate_overall_score(),
            'risk_tier': supplier.risk_tier,
            'category_scores': {
                'labor_standards': supplier.labor_score,
                'environmental': supplier.environmental_score,
                'anti_corruption': supplier.anti_corruption_score,
                'data_privacy': supplier.data_privacy_score,
                'product_safety': supplier.product_safety_score,
                'trade_compliance': supplier.trade_compliance_score,
                'ethical_sourcing': supplier.ethical_sourcing_score
            },
            'compliance_gaps': supplier.get_compliance_gaps(),
            'next_assessment_date': supplier.next_assessment_date.isoformat(),
            'recommendations': self._generate_recommendations(supplier)
        }
    
    def _generate_recommendations(
        self,
        supplier: SupplierCompliance
    ) -> List[str]:
        """Generate recommendations based on assessment."""
        recommendations = []
        
        # Check each category
        if supplier.labor_score and supplier.labor_score < 70:
            recommendations.append(
                "Improve labor standards: Focus on wage compliance and working conditions"
            )
        
        if supplier.environmental_score and supplier.environmental_score < 70:
            recommendations.append(
                "Enhance environmental practices: Implement carbon reduction and waste management"
            )
        
        if supplier.anti_corruption_score and supplier.anti_corruption_score < 70:
            recommendations.append(
                "Strengthen anti-corruption controls: Implement comprehensive ethics policies"
            )
        
        if supplier.data_privacy_score and supplier.data_privacy_score < 70:
            recommendations.append(
                "Upgrade data privacy compliance: Ensure GDPR/privacy law alignment"
            )
        
        # Risk-based recommendations
        if supplier.risk_tier == 1:
            recommendations.append(
                "High-risk supplier: Increase monitoring frequency and conduct surprise audits"
            )
        
        # Overall status
        if supplier.overall_status == ComplianceStatus.NON_COMPLIANT:
            recommendations.append(
                "Critical action required: Develop immediate corrective action plan"
            )
        
        return recommendations
