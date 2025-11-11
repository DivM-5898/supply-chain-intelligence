"""
Preprocessing Pipeline
Feature engineering, normalization, and data cleaning utilities
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from typing import List, Tuple, Optional


class Preprocessor:
    """Data preprocessing utilities"""
    
    def __init__(self):
        self.scalers = {}
        self.label_encoders = {}
    
    def prepare_supplier_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Prepare features for supplier scoring model
        Returns: (processed_df, feature_columns)
        """
        df = df.copy()
        
        # Create composite features
        df['performance_score'] = (
            df['on_time_delivery_rate'] * 0.4 +
            df['quality_score'] * 0.4 +
            (1 - df['defect_rate']) * 0.2
        )
        
        df['financial_health'] = (
            (df['credit_score'] / 850) * 0.4 +
            (1 - df['debt_to_equity'].clip(upper=2) / 2) * 0.3 +
            df['profit_margin'] * 0.3
        )
        
        df['operational_maturity'] = (
            (df['years_in_business'] / 50) * 0.3 +
            (df['utilization_rate']) * 0.3 +
            (df['has_erp_system'].astype(int)) * 0.2 +
            (df['certifications'] != 'None').astype(int) * 0.2
        )
        
        # Encode categorical variables
        if 'certifications' in df.columns:
            le = LabelEncoder()
            df['certifications_encoded'] = le.fit_transform(df['certifications'].fillna('None'))
            self.label_encoders['certifications'] = le
        
        # Select features for modeling
        feature_columns = [
            'performance_score',
            'financial_health',
            'operational_maturity',
            'avg_delivery_time_days',
            'on_time_delivery_rate',
            'quality_score',
            'credit_score',
            'profit_margin',
            'years_in_business',
            'utilization_rate',
            'geopolitical_risk_score',
            'esg_score',
            'compliance_score',
            'certifications_encoded'
        ]
        
        # Ensure all columns exist
        available_features = [col for col in feature_columns if col in df.columns]
        
        return df[available_features + ['supplier_id']], available_features
    
    def normalize_features(self, df: pd.DataFrame, feature_columns: List[str], 
                          method: str = 'standard') -> pd.DataFrame:
        """
        Normalize features using StandardScaler or MinMaxScaler
        """
        df = df.copy()
        
        if method == 'standard':
            scaler = StandardScaler()
        else:
            scaler = MinMaxScaler()
        
        df[feature_columns] = scaler.fit_transform(df[feature_columns])
        self.scalers[method] = scaler
        
        return df
    
    def create_risk_features(self, suppliers_df: pd.DataFrame, 
                            risk_events_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create risk features by aggregating risk events
        """
        # Aggregate risk events by supplier
        risk_agg = risk_events_df.groupby('supplier_id').agg({
            'impact_score': ['mean', 'max', 'count'],
            'severity': lambda x: (x == 'Critical').sum()
        }).reset_index()
        
        risk_agg.columns = ['supplier_id', 'avg_impact_score', 'max_impact_score', 
                           'risk_event_count', 'critical_events']
        
        # Merge with suppliers
        result = suppliers_df.merge(risk_agg, on='supplier_id', how='left')
        result['avg_impact_score'] = result['avg_impact_score'].fillna(0)
        result['max_impact_score'] = result['max_impact_score'].fillna(0)
        result['risk_event_count'] = result['risk_event_count'].fillna(0)
        result['critical_events'] = result['critical_events'].fillna(0)
        
        return result
    
    def prepare_fraud_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Prepare features for fraud detection
        """
        df = df.copy()
        
        # Create fraud indicators
        df['suspicious_financial'] = (
            (df['debt_to_equity'] > 1.5).astype(int) +
            (df['credit_score'] < 500).astype(int) +
            (df['profit_margin'] < 0.05).astype(int)
        )
        
        df['suspicious_operational'] = (
            (df['on_time_delivery_rate'] < 0.70).astype(int) +
            (df['defect_rate'] > 0.05).astype(int) +
            (df['quality_score'] < 0.70).astype(int)
        )
        
        fraud_features = [
            'suspicious_financial',
            'suspicious_operational',
            'debt_to_equity',
            'credit_score',
            'profit_margin',
            'on_time_delivery_rate',
            'defect_rate',
            'quality_score',
            'years_in_business',
            'geopolitical_risk_score'
        ]
        
        available_features = [col for col in fraud_features if col in df.columns]
        
        return df[available_features + ['supplier_id']], available_features


# Global instance
preprocessor = Preprocessor()

