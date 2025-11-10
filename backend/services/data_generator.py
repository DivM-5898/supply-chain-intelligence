"""
Data Generator Service
Generates synthetic datasets for supplier evaluation, risk profiling, and contract analysis.
"""

import pandas as pd
import numpy as np
from faker import Faker
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict
import random

fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)


class DataGenerator:
    """Generate synthetic supplier and risk data"""
    
    def __init__(self, output_dir: str = "data/raw"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/contracts", exist_ok=True)
        
    def generate_suppliers(self, n_suppliers: int = 100) -> pd.DataFrame:
        """
        Generate synthetic supplier dataset with:
        - Basic information (name, location, industry)
        - Performance metrics (delivery time, quality score, on-time delivery %)
        - Financial metrics (revenue, profit margin, credit score)
        - Operational metrics (capacity, years in business, certifications)
        """
        suppliers = []
        
        industries = [
            "Electronics Manufacturing", "Textiles", "Automotive Parts",
            "Food & Beverage", "Pharmaceuticals", "Chemicals",
            "Machinery", "Construction Materials", "Plastics", "Metals"
        ]
        
        countries = [
            "USA", "China", "India", "Germany", "Japan", "South Korea",
            "Mexico", "Vietnam", "Thailand", "Brazil", "Italy", "UK"
        ]
        
        for i in range(n_suppliers):
            supplier = {
                "supplier_id": f"SUP_{i+1:04d}",
                "name": fake.company(),
                "country": np.random.choice(countries),
                "region": fake.state() if np.random.choice(countries) == "USA" else fake.country(),
                "industry": np.random.choice(industries),
                "years_in_business": np.random.randint(1, 50),
                "employee_count": np.random.randint(50, 10000),
                
                # Performance metrics
                "avg_delivery_time_days": np.random.normal(15, 5),
                "on_time_delivery_rate": np.random.uniform(0.70, 0.99),
                "quality_score": np.random.uniform(0.60, 1.0),
                "defect_rate": np.random.uniform(0.001, 0.05),
                
                # Financial metrics
                "annual_revenue_millions": np.random.uniform(10, 500),
                "profit_margin": np.random.uniform(0.05, 0.25),
                "credit_score": np.random.randint(300, 850),
                "debt_to_equity": np.random.uniform(0.1, 2.0),
                
                # Operational metrics
                "production_capacity_units": np.random.randint(10000, 1000000),
                "utilization_rate": np.random.uniform(0.60, 0.95),
                "certifications": np.random.choice(["ISO9001", "ISO14001", "ISO45001", "None"], p=[0.4, 0.3, 0.2, 0.1]),
                "has_erp_system": np.random.choice([True, False], p=[0.7, 0.3]),
                
                # Cost metrics
                "unit_cost": np.random.uniform(10, 500),
                "min_order_quantity": np.random.randint(100, 10000),
                
                # Risk indicators
                "geopolitical_risk_score": np.random.uniform(0.1, 0.9),
                "esg_score": np.random.uniform(0.3, 1.0),
                "compliance_score": np.random.uniform(0.5, 1.0),
            }
            suppliers.append(supplier)
        
        df = pd.DataFrame(suppliers)
        
        # Ensure delivery time is positive
        df["avg_delivery_time_days"] = df["avg_delivery_time_days"].clip(lower=1)
        
        # Save to CSV
        df.to_csv(f"{self.output_dir}/suppliers.csv", index=False)
        print(f"Generated {n_suppliers} suppliers dataset")
        return df
    
    def generate_risk_data(self, supplier_ids: List[str]) -> pd.DataFrame:
        """
        Generate risk profiling data including:
        - Financial stability indicators
        - Geopolitical risk factors
        - ESG compliance data
        - Historical disruption events
        """
        risk_data = []
        
        risk_factors = [
            "Financial Instability", "Geopolitical Tension", "Natural Disaster",
            "Labor Disputes", "Regulatory Changes", "Supply Chain Disruption",
            "Currency Fluctuation", "Trade Restrictions"
        ]
        
        for supplier_id in supplier_ids:
            # Generate historical risk events
            n_events = np.random.poisson(2)  # Average 2 events per supplier
            
            for _ in range(n_events):
                event_date = fake.date_between(start_date='-2y', end_date='today')
                risk_data.append({
                    "supplier_id": supplier_id,
                    "event_date": event_date.strftime("%Y-%m-%d"),
                    "risk_factor": np.random.choice(risk_factors),
                    "severity": np.random.choice(["Low", "Medium", "High", "Critical"]),
                    "impact_score": np.random.uniform(0.1, 1.0),
                    "resolved": np.random.choice([True, False], p=[0.7, 0.3])
                })
        
        df = pd.DataFrame(risk_data)
        df.to_csv(f"{self.output_dir}/risk_events.csv", index=False)
        print(f"Generated risk events dataset with {len(df)} records")
        return df
    
    def generate_geopolitical_risk(self) -> pd.DataFrame:
        """Generate geopolitical risk scores by country"""
        countries = [
            "USA", "China", "India", "Germany", "Japan", "South Korea",
            "Mexico", "Vietnam", "Thailand", "Brazil", "Italy", "UK",
            "Russia", "Turkey", "Poland", "Czech Republic", "Malaysia"
        ]
        
        geo_risk = []
        for country in countries:
            geo_risk.append({
                "country": country,
                "political_stability": np.random.uniform(0.3, 1.0),
                "trade_freedom": np.random.uniform(0.4, 1.0),
                "regulatory_risk": np.random.uniform(0.2, 0.9),
                "currency_stability": np.random.uniform(0.5, 1.0),
                "overall_risk_score": np.random.uniform(0.2, 0.8),
                "last_updated": datetime.now().strftime("%Y-%m-%d")
            })
        
        df = pd.DataFrame(geo_risk)
        df.to_csv(f"{self.output_dir}/geopolitical_risk.csv", index=False)
        print("Generated geopolitical risk dataset")
        return df
    
    def generate_contract_samples(self, n_contracts: int = 20) -> List[Dict]:
        """
        Generate sample contract documents with various clauses and terms
        """
        contracts = []
        
        contract_templates = [
            {
                "type": "Supply Agreement",
                "template": """
SUPPLY AGREEMENT

This Supply Agreement ("Agreement") is entered into on {date} between {buyer} ("Buyer") 
and {supplier} ("Supplier").

TERM AND DELIVERY:
- The initial term of this Agreement shall be {term} years.
- Supplier shall deliver products within {delivery_days} business days of order confirmation.
- Late deliveries may result in penalties of up to {penalty}% of order value.

PRICING AND PAYMENT:
- Unit price: ${unit_price} per unit.
- Payment terms: Net {payment_days} days.
- Price adjustments may occur quarterly based on market conditions.

QUALITY AND WARRANTIES:
- Supplier warrants that all products meet ISO 9001 standards.
- Defect rate must not exceed {defect_rate}%.
- Buyer has right to reject non-conforming goods.

TERMINATION:
- Either party may terminate with {notice_days} days written notice.
- Immediate termination for material breach.

RISK FACTORS:
- Force majeure clauses apply.
- Supplier responsible for compliance with all applicable laws.
"""
            },
            {
                "type": "Service Contract",
                "template": """
SERVICE CONTRACT

This Service Contract ("Contract") dated {date} is between {buyer} and {supplier}.

SCOPE OF SERVICES:
- Supplier shall provide {service_type} services.
- Service level agreement: {sla}% uptime required.
- Response time: {response_time} hours for critical issues.

COMPENSATION:
- Monthly retainer: ${monthly_fee}
- Additional services billed at ${hourly_rate} per hour.
- Payment due within {payment_days} days of invoice.

LIABILITY:
- Supplier liability limited to ${liability_cap} per incident.
- Indemnification clauses apply.
- Insurance coverage of ${insurance_amount} required.

CONFIDENTIALITY:
- Both parties agree to maintain confidentiality.
- Non-disclosure period: {nda_period} years.
"""
            }
        ]
        
        for i in range(n_contracts):
            template = np.random.choice(contract_templates)
            contract_text = template["template"].format(
                date=fake.date_between(start_date='-1y', end_date='today').strftime("%B %d, %Y"),
                buyer=fake.company(),
                supplier=fake.company(),
                term=np.random.randint(1, 5),
                delivery_days=np.random.randint(7, 30),
                penalty=np.random.randint(5, 20),
                unit_price=np.random.uniform(10, 500),
                payment_days=np.random.choice([30, 45, 60, 90]),
                defect_rate=np.random.uniform(0.001, 0.05),
                notice_days=np.random.choice([30, 60, 90]),
                service_type=np.random.choice(["IT Support", "Logistics", "Consulting", "Maintenance"]),
                sla=np.random.uniform(95, 99.9),
                response_time=np.random.randint(1, 24),
                monthly_fee=np.random.uniform(5000, 50000),
                hourly_rate=np.random.uniform(50, 200),
                liability_cap=np.random.uniform(100000, 1000000),
                insurance_amount=np.random.uniform(1000000, 10000000),
                nda_period=np.random.randint(2, 5)
            )
            
            contract = {
                "contract_id": f"CONTRACT_{i+1:04d}",
                "supplier_id": f"SUP_{np.random.randint(1, 101):04d}",
                "contract_type": template["type"],
                "content": contract_text,
                "created_date": fake.date_between(start_date='-1y', end_date='today').strftime("%Y-%m-%d"),
                "expiry_date": fake.date_between(start_date='today', end_date='+3y').strftime("%Y-%m-%d"),
                "status": np.random.choice(["Active", "Pending", "Expired"], p=[0.7, 0.2, 0.1])
            }
            
            # Save individual contract file
            contract_file = f"{self.output_dir}/contracts/{contract['contract_id']}.txt"
            with open(contract_file, 'w') as f:
                f.write(contract_text)
            
            contracts.append(contract)
        
        # Save contracts metadata
        contracts_df = pd.DataFrame(contracts)
        contracts_df.to_csv(f"{self.output_dir}/contracts_metadata.csv", index=False)
        print(f"Generated {n_contracts} contract samples")
        return contracts
    
    def generate_delivery_history(self, supplier_ids: List[str], n_months: int = 24) -> pd.DataFrame:
        """Generate historical delivery performance data"""
        delivery_history = []
        
        start_date = datetime.now() - timedelta(days=n_months * 30)
        
        for supplier_id in supplier_ids:
            for month in range(n_months):
                order_date = start_date + timedelta(days=month * 30)
                n_orders = np.random.poisson(5)  # Average 5 orders per month
                
                for order in range(n_orders):
                    delivery_history.append({
                        "supplier_id": supplier_id,
                        "order_date": (order_date + timedelta(days=np.random.randint(0, 30))).strftime("%Y-%m-%d"),
                        "order_quantity": np.random.randint(100, 10000),
                        "promised_delivery_date": (order_date + timedelta(days=np.random.randint(7, 30))).strftime("%Y-%m-%d"),
                        "actual_delivery_date": (order_date + timedelta(days=np.random.randint(5, 35))).strftime("%Y-%m-%d"),
                        "on_time": np.random.choice([True, False], p=[0.85, 0.15]),
                        "quality_rating": np.random.uniform(0.7, 1.0),
                        "order_value": np.random.uniform(1000, 100000)
                    })
        
        df = pd.DataFrame(delivery_history)
        df.to_csv(f"{self.output_dir}/delivery_history.csv", index=False)
        print(f"Generated delivery history with {len(df)} records")
        return df
    
    def generate_all(self):
        """Generate all datasets"""
        print("Generating synthetic datasets...")
        
        # Generate suppliers
        suppliers_df = self.generate_suppliers(n_suppliers=100)
        supplier_ids = suppliers_df["supplier_id"].tolist()
        
        # Generate related datasets
        self.generate_risk_data(supplier_ids)
        self.generate_geopolitical_risk()
        self.generate_contract_samples(n_contracts=20)
        self.generate_delivery_history(supplier_ids, n_months=24)
        
        print("\nAll datasets generated successfully!")
        return suppliers_df


if __name__ == "__main__":
    generator = DataGenerator()
    generator.generate_all()

