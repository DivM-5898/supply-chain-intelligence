"""
Preprocessing Pipeline
Feature engineering, normalization, and data cleaning utilities
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from typing import List, Tuple, Optional
from utils.advanced_feature_engineering import advanced_feature_engineer


class Preprocessor:
    """Data preprocessing utilities"""
    
    def __init__(self):
        self.scalers = {}
        self.label_encoders = {}
    
    def prepare_supplier_features(self, df: pd.DataFrame, 
                                  use_advanced_features: bool = False) -> Tuple[pd.DataFrame, List[str]]:
        """
        Prepare features for supplier scoring model with advanced feature engineering
        Returns: (processed_df, feature_columns)
        """
        df = df.copy()
        
        # Add default values for missing columns
        if 'has_erp_system' not in df.columns:
            df['has_erp_system'] = False
        if 'certifications' not in df.columns:
            df['certifications'] = 'None'
        if 'on_time_delivery_rate' not in df.columns:
            df['on_time_delivery_rate'] = 0.8
        if 'quality_score' not in df.columns:
            df['quality_score'] = 0.8
        if 'defect_rate' not in df.columns:
            df['defect_rate'] = 0.05
        if 'credit_score' not in df.columns:
            df['credit_score'] = 650
        if 'debt_to_equity' not in df.columns:
            df['debt_to_equity'] = 0.5
        if 'profit_margin' not in df.columns:
            df['profit_margin'] = 0.1
        if 'years_in_business' not in df.columns:
            df['years_in_business'] = 10
        if 'utilization_rate' not in df.columns:
            df['utilization_rate'] = 0.75
        if 'avg_delivery_time_days' not in df.columns:
            df['avg_delivery_time_days'] = 7
        if 'geopolitical_risk_score' not in df.columns:
            df['geopolitical_risk_score'] = 0.5
        if 'esg_score' not in df.columns:
            df['esg_score'] = 0.7
        if 'compliance_score' not in df.columns:
            df['compliance_score'] = 0.8
        
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
        
        # Apply advanced feature engineering
        if use_advanced_features:
            try:
                # Statistical features
                df = advanced_feature_engineer.create_zscore_features(df)
                df = advanced_feature_engineer.create_ratio_features(df)
                df = advanced_feature_engineer.create_logarithmic_features(df)
                
                # Domain-specific features
                df = advanced_feature_engineer.create_supplier_reliability_index(df)
                df = advanced_feature_engineer.create_financial_health_score(df)
                df = advanced_feature_engineer.create_contract_compliance_rate(df)
                df = advanced_feature_engineer.create_supplier_diversification_index(df)
            except Exception as e:
                import warnings
                warnings.warn(f"Advanced feature engineering failed: {str(e)}. Using basic features only.")
        
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
        
        # Add advanced features if available
        if use_advanced_features:
            advanced_cols = [
                'supplier_reliability_index',
                'financial_health_score',
                'contract_compliance_rate',
                'supplier_diversification_index'
            ]
            feature_columns.extend([col for col in advanced_cols if col in df.columns])
        
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

