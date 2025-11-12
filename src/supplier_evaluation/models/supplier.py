"""
Supplier Data Models
Comprehensive data structures for supplier information and evaluation.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime, date
from enum import Enum
import json


class SupplierStatus(Enum):
    """Supplier operational status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    UNDER_REVIEW = "under_review"
    BLACKLISTED = "blacklisted"


class SupplierTier(Enum):
    """Supplier tier classification."""
    TIER_1 = "tier_1"  # Direct suppliers
    TIER_2 = "tier_2"  # Sub-suppliers
    TIER_3 = "tier_3"  # Raw material suppliers
    TIER_N = "tier_n"  # Further upstream


class RiskLevel(Enum):
    """Risk level classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CertificationType(Enum):
    """Types of certifications."""
    ISO_9001 = "iso_9001"  # Quality management
    ISO_14001 = "iso_14001"  # Environmental management
    ISO_45001 = "iso_45001"  # Occupational health and safety
    ISO_27001 = "iso_27001"  # Information security
    OHSAS_18001 = "ohsas_18001"  # Health and safety
    SA_8000 = "sa_8000"  # Social accountability
    FAIR_TRADE = "fair_trade"
    ORGANIC = "organic"
    CUSTOM = "custom"


@dataclass
class ContactInformation:
    """Contact details for supplier."""
    primary_contact_name: str
    primary_contact_email: str
    primary_contact_phone: str
    secondary_contact_name: Optional[str] = None
    secondary_contact_email: Optional[str] = None
    secondary_contact_phone: Optional[str] = None
    website: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'primary_contact_name': self.primary_contact_name,
            'primary_contact_email': self.primary_contact_email,
            'primary_contact_phone': self.primary_contact_phone,
            'secondary_contact_name': self.secondary_contact_name,
            'secondary_contact_email': self.secondary_contact_email,
            'secondary_contact_phone': self.secondary_contact_phone,
            'website': self.website
        }


@dataclass
class Address:
    """Physical address information."""
    street: str
    city: str
    state: str
    country: str
    postal_code: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'street': self.street,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'latitude': self.latitude,
            'longitude': self.longitude
        }


@dataclass
class FinancialInformation:
    """Financial details of supplier."""
    annual_revenue: float  # In USD
    credit_rating: Optional[str] = None
    payment_terms_days: int = 30
    currency: str = "USD"
    bank_name: Optional[str] = None
    tax_id: Optional[str] = None
    duns_number: Optional[str] = None  # D&B number
    last_financial_audit_date: Optional[date] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'annual_revenue': self.annual_revenue,
            'credit_rating': self.credit_rating,
            'payment_terms_days': self.payment_terms_days,
            'currency': self.currency,
            'bank_name': self.bank_name,
            'tax_id': self.tax_id,
            'duns_number': self.duns_number,
            'last_financial_audit_date': self.last_financial_audit_date.isoformat() if self.last_financial_audit_date else None
        }


@dataclass
class Certification:
    """Supplier certification information."""
    certification_type: CertificationType
    certification_number: str
    issuing_body: str
    issue_date: date
    expiry_date: date
    is_active: bool = True
    custom_name: Optional[str] = None  # For CUSTOM type
    
    def is_valid(self) -> bool:
        """Check if certification is currently valid."""
        return self.is_active and self.expiry_date >= date.today()
    
    def days_until_expiry(self) -> int:
        """Calculate days until expiry."""
        return (self.expiry_date - date.today()).days
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'certification_type': self.certification_type.value,
            'certification_number': self.certification_number,
            'issuing_body': self.issuing_body,
            'issue_date': self.issue_date.isoformat(),
            'expiry_date': self.expiry_date.isoformat(),
            'is_active': self.is_active,
            'custom_name': self.custom_name
        }


@dataclass
class Supplier:
    """
    Complete supplier information model.
    """
    
    # Basic Information
    supplier_id: str
    name: str
    legal_name: str
    status: SupplierStatus
    tier: SupplierTier
    
    # Contact & Location
    address: Address
    contact_info: ContactInformation
    
    # Business Details
    industry: str
    products_services: List[str]
    manufacturing_capabilities: List[str]
    certifications: List[Certification] = field(default_factory=list)
    
    # Financial
    financial_info: FinancialInformation = None
    
    # Operational
    years_in_business: int = 0
    employee_count: int = 0
    production_capacity: Optional[Dict[str, Any]] = None
    
    # Relationship
    relationship_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    preferred_supplier: bool = False
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_active_certifications(self) -> List[Certification]:
        """Get list of currently valid certifications."""
        return [cert for cert in self.certifications if cert.is_valid()]
    
    def get_relationship_duration_years(self) -> float:
        """Calculate relationship duration in years."""
        if self.relationship_start_date is None:
            return 0.0
        days = (date.today() - self.relationship_start_date).days
        return days / 365.25
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'supplier_id': self.supplier_id,
            'name': self.name,
            'legal_name': self.legal_name,
            'status': self.status.value,
            'tier': self.tier.value,
            'address': self.address.to_dict(),
            'contact_info': self.contact_info.to_dict(),
            'industry': self.industry,
            'products_services': self.products_services,
            'manufacturing_capabilities': self.manufacturing_capabilities,
            'certifications': [cert.to_dict() for cert in self.certifications],
            'financial_info': self.financial_info.to_dict() if self.financial_info else None,
            'years_in_business': self.years_in_business,
            'employee_count': self.employee_count,
            'production_capacity': self.production_capacity,
            'relationship_start_date': self.relationship_start_date.isoformat() if self.relationship_start_date else None,
            'contract_end_date': self.contract_end_date.isoformat() if self.contract_end_date else None,
            'preferred_supplier': self.preferred_supplier,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata
        }
    
    def save_to_file(self, filepath: str) -> None:
        """Save supplier to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
