"""
Data Loader Module
Functions to load and cache datasets
"""

import pandas as pd
import os
from typing import Optional, Dict
import json


class DataLoader:
    """Load and manage datasets"""
    
    def __init__(self, data_dir: str = "data/raw"):
        # Resolve absolute path
        backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if not os.path.isabs(data_dir):
            self.data_dir = os.path.join(backend_path, data_dir)
        else:
            self.data_dir = data_dir
        self._cache = {}
    
    def load_suppliers(self, use_cache: bool = True) -> pd.DataFrame:
        """Load supplier dataset"""
        cache_key = "suppliers"
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]
        
        file_path = os.path.join(self.data_dir, "suppliers.csv")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Suppliers dataset not found at {file_path}. Run data generator first.")
        
        df = pd.read_csv(file_path)
        if use_cache:
            self._cache[cache_key] = df
        return df
    
    def load_risk_events(self, use_cache: bool = True) -> pd.DataFrame:
        """Load risk events dataset"""
        cache_key = "risk_events"
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]
        
        file_path = os.path.join(self.data_dir, "risk_events.csv")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Risk events dataset not found at {file_path}")
        
        df = pd.read_csv(file_path)
        if use_cache:
            self._cache[cache_key] = df
        return df
    
    def load_geopolitical_risk(self, use_cache: bool = True) -> pd.DataFrame:
        """Load geopolitical risk dataset"""
        cache_key = "geopolitical_risk"
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]
        
        file_path = os.path.join(self.data_dir, "geopolitical_risk.csv")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Geopolitical risk dataset not found at {file_path}")
        
        df = pd.read_csv(file_path)
        if use_cache:
            self._cache[cache_key] = df
        return df
    
    def load_delivery_history(self, use_cache: bool = True) -> pd.DataFrame:
        """Load delivery history dataset"""
        cache_key = "delivery_history"
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]
        
        file_path = os.path.join(self.data_dir, "delivery_history.csv")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Delivery history dataset not found at {file_path}")
        
        df = pd.read_csv(file_path)
        if use_cache:
            self._cache[cache_key] = df
        return df
    
    def load_contract(self, contract_id: str) -> Optional[str]:
        """Load contract text by ID"""
        file_path = os.path.join(self.data_dir, "contracts", f"{contract_id}.txt")
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def load_contracts_metadata(self, use_cache: bool = True) -> pd.DataFrame:
        """Load contracts metadata"""
        cache_key = "contracts_metadata"
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]
        
        file_path = os.path.join(self.data_dir, "contracts_metadata.csv")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Contracts metadata not found at {file_path}")
        
        df = pd.read_csv(file_path)
        if use_cache:
            self._cache[cache_key] = df
        return df
    
    def clear_cache(self):
        """Clear the data cache"""
        self._cache = {}


# Global instance
data_loader = DataLoader()

