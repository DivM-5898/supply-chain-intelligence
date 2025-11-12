"""
Decision Matrix Framework
Manages alternatives, decision matrices, and scenario analysis for MCDA.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class Alternative:
    """Represents a single decision alternative."""
    id: str
    name: str
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Alternative':
        """Create from dictionary."""
        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description', ''),
            metadata=data.get('metadata', {})
        )


class DecisionMatrix:
    """
    Manages a decision matrix with alternatives and criteria values.
    """
    
    def __init__(
        self,
        name: str,
        description: str = "",
        metadata: Optional[Dict] = None
    ):
        """
        Initialize decision matrix.
        
        Args:
            name: Name of the decision scenario
            description: Description of the decision problem
            metadata: Additional metadata
        """
        self.name = name
        self.description = description
        self.metadata = metadata or {}
        self.alternatives: Dict[str, Alternative] = {}
        self.matrix: Optional[np.ndarray] = None
        self.criterion_order: List[str] = []
        self.alternative_order: List[str] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
    def add_alternative(self, alternative: Alternative) -> None:
        """Add an alternative to the decision matrix."""
        if alternative.id in self.alternatives:
            raise ValueError(f"Alternative '{alternative.id}' already exists")
            
        self.alternatives[alternative.id] = alternative
        self.updated_at = datetime.now()
        
    def remove_alternative(self, alternative_id: str) -> None:
        """Remove an alternative from the matrix."""
        if alternative_id not in self.alternatives:
            raise ValueError(f"Alternative '{alternative_id}' not found")
            
        del self.alternatives[alternative_id]
        
        # Remove from matrix if present
        if alternative_id in self.alternative_order:
            idx = self.alternative_order.index(alternative_id)
            self.alternative_order.pop(idx)
            if self.matrix is not None:
                self.matrix = np.delete(self.matrix, idx, axis=0)
                
        self.updated_at = datetime.now()
        
    def set_matrix(
        self,
        matrix: np.ndarray,
        alternative_order: List[str],
        criterion_order: List[str]
    ) -> None:
        """
        Set the decision matrix values.
        
        Args:
            matrix: m x n numpy array (m alternatives, n criteria)
            alternative_order: List of alternative IDs matching matrix rows
            criterion_order: List of criterion IDs matching matrix columns
        """
        # Validate dimensions
        if matrix.shape[0] != len(alternative_order):
            raise ValueError(
                f"Matrix has {matrix.shape[0]} rows but "
                f"{len(alternative_order)} alternatives provided"
            )
            
        if matrix.shape[1] != len(criterion_order):
            raise ValueError(
                f"Matrix has {matrix.shape[1]} columns but "
                f"{len(criterion_order)} criteria provided"
            )
            
        # Validate all alternatives exist
        for alt_id in alternative_order:
            if alt_id not in self.alternatives:
                raise ValueError(f"Alternative '{alt_id}' not found")
                
        self.matrix = matrix.copy()
        self.alternative_order = alternative_order.copy()
        self.criterion_order = criterion_order.copy()
        self.updated_at = datetime.now()
        
    def get_matrix(self) -> Tuple[np.ndarray, List[str], List[str]]:
        """
        Get the decision matrix and orders.
        
        Returns:
            Tuple of (matrix, alternative_order, criterion_order)
        """
        if self.matrix is None:
            raise ValueError("Matrix not set")
            
        return self.matrix.copy(), self.alternative_order.copy(), self.criterion_order.copy()
        
    def update_value(
        self,
        alternative_id: str,
        criterion_id: str,
        value: float
    ) -> None:
        """
        Update a single value in the matrix.
        
        Args:
            alternative_id: ID of alternative
            criterion_id: ID of criterion
            value: New value
        """
        if self.matrix is None:
            raise ValueError("Matrix not set")
            
        if alternative_id not in self.alternative_order:
            raise ValueError(f"Alternative '{alternative_id}' not in matrix")
            
        if criterion_id not in self.criterion_order:
            raise ValueError(f"Criterion '{criterion_id}' not in matrix")
            
        row_idx = self.alternative_order.index(alternative_id)
        col_idx = self.criterion_order.index(criterion_id)
        
        self.matrix[row_idx, col_idx] = value
        self.updated_at = datetime.now()
        
    def get_value(self, alternative_id: str, criterion_id: str) -> float:
        """Get a value from the matrix."""
        if self.matrix is None:
            raise ValueError("Matrix not set")
            
        row_idx = self.alternative_order.index(alternative_id)
        col_idx = self.criterion_order.index(criterion_id)
        
        return float(self.matrix[row_idx, col_idx])
        
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert matrix to pandas DataFrame.
        
        Returns:
            DataFrame with alternatives as rows and criteria as columns
        """
        if self.matrix is None:
            raise ValueError("Matrix not set")
            
        # Get alternative names
        alt_names = [
            self.alternatives[alt_id].name 
            for alt_id in self.alternative_order
        ]
        
        df = pd.DataFrame(
            self.matrix,
            index=alt_names,
            columns=self.criterion_order
        )
        
        return df
        
    @classmethod
    def from_dataframe(
        cls,
        df: pd.DataFrame,
        name: str,
        description: str = "",
        alternative_id_prefix: str = "alt"
    ) -> 'DecisionMatrix':
        """
        Create decision matrix from pandas DataFrame.
        
        Args:
            df: DataFrame with alternatives as rows and criteria as columns
            name: Name for the decision matrix
            description: Description
            alternative_id_prefix: Prefix for generating alternative IDs
            
        Returns:
            DecisionMatrix instance
        """
        matrix_obj = cls(name, description)
        
        # Create alternatives from index
        alternative_order = []
        for idx, alt_name in enumerate(df.index):
            alt_id = f"{alternative_id_prefix}_{idx}"
            alternative = Alternative(
                id=alt_id,
                name=str(alt_name)
            )
            matrix_obj.add_alternative(alternative)
            alternative_order.append(alt_id)
            
        # Set matrix
        criterion_order = list(df.columns)
        matrix_obj.set_matrix(
            df.values,
            alternative_order,
            criterion_order
        )
        
        return matrix_obj
        
    def create_scenario(
        self,
        scenario_name: str,
        modifications: Dict[str, Dict[str, float]]
    ) -> 'DecisionMatrix':
        """
        Create a new scenario by modifying the current matrix.
        
        Args:
            scenario_name: Name for the new scenario
            modifications: Dict mapping alternative_id -> {criterion_id: new_value}
            
        Returns:
            New DecisionMatrix with modifications applied
        """
        if self.matrix is None:
            raise ValueError("Matrix not set")
            
        # Create copy
        new_matrix = DecisionMatrix(
            name=scenario_name,
            description=f"Scenario derived from '{self.name}'",
            metadata={'parent_scenario': self.name}
        )
        
        # Copy alternatives
        for alt_id, alternative in self.alternatives.items():
            new_alt = Alternative(
                id=alternative.id,
                name=alternative.name,
                description=alternative.description,
                metadata=alternative.metadata.copy()
            )
            new_matrix.add_alternative(new_alt)
            
        # Copy and modify matrix
        new_matrix_data = self.matrix.copy()
        
        for alt_id, criterion_changes in modifications.items():
            row_idx = self.alternative_order.index(alt_id)
            for crit_id, new_value in criterion_changes.items():
                col_idx = self.criterion_order.index(crit_id)
                new_matrix_data[row_idx, col_idx] = new_value
                
        new_matrix.set_matrix(
            new_matrix_data,
            self.alternative_order.copy(),
            self.criterion_order.copy()
        )
        
        return new_matrix
        
    def calculate_statistics(self) -> Dict[str, Dict[str, float]]:
        """
        Calculate statistics for each criterion.
        
        Returns:
            Dictionary mapping criterion IDs to statistics
        """
        if self.matrix is None:
            raise ValueError("Matrix not set")
            
        stats = {}
        
        for idx, criterion_id in enumerate(self.criterion_order):
            column = self.matrix[:, idx]
            
            stats[criterion_id] = {
                'min': float(np.min(column)),
                'max': float(np.max(column)),
                'mean': float(np.mean(column)),
                'median': float(np.median(column)),
                'std': float(np.std(column)),
                'range': float(np.ptp(column))
            }
            
        return stats
        
    def get_alternative_profile(self, alternative_id: str) -> Dict[str, float]:
        """
        Get the complete profile (all criterion values) for an alternative.
        
        Args:
            alternative_id: ID of alternative
            
        Returns:
            Dictionary mapping criterion IDs to values
        """
        if self.matrix is None:
            raise ValueError("Matrix not set")
            
        if alternative_id not in self.alternative_order:
            raise ValueError(f"Alternative '{alternative_id}' not in matrix")
            
        row_idx = self.alternative_order.index(alternative_id)
        
        profile = {
            criterion_id: float(self.matrix[row_idx, col_idx])
            for col_idx, criterion_id in enumerate(self.criterion_order)
        }
        
        return profile
        
    def compare_alternatives(
        self,
        alternative_id1: str,
        alternative_id2: str
    ) -> Dict[str, Dict[str, float]]:
        """
        Compare two alternatives across all criteria.
        
        Args:
            alternative_id1: First alternative ID
            alternative_id2: Second alternative ID
            
        Returns:
            Dictionary with comparison details
        """
        profile1 = self.get_alternative_profile(alternative_id1)
        profile2 = self.get_alternative_profile(alternative_id2)
        
        comparison = {}
        
        for criterion_id in self.criterion_order:
            val1 = profile1[criterion_id]
            val2 = profile2[criterion_id]
            
            comparison[criterion_id] = {
                'alternative_1': val1,
                'alternative_2': val2,
                'difference': val1 - val2,
                'ratio': val1 / val2 if val2 != 0 else float('inf')
            }
            
        return comparison
        
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'name': self.name,
            'description': self.description,
            'metadata': self.metadata,
            'alternatives': [alt.to_dict() for alt in self.alternatives.values()],
            'matrix': self.matrix.tolist() if self.matrix is not None else None,
            'alternative_order': self.alternative_order,
            'criterion_order': self.criterion_order,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
    def save_to_file(self, filepath: str) -> None:
        """Save decision matrix to JSON file."""
        data = self.to_dict()
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
            
    @classmethod
    def load_from_file(cls, filepath: str) -> 'DecisionMatrix':
        """Load decision matrix from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        matrix_obj = cls(
            name=data['name'],
            description=data['description'],
            metadata=data.get('metadata', {})
        )
        
        # Load alternatives
        for alt_data in data['alternatives']:
            alternative = Alternative.from_dict(alt_data)
            matrix_obj.add_alternative(alternative)
            
        # Load matrix
        if data['matrix'] is not None:
            matrix_obj.set_matrix(
                np.array(data['matrix']),
                data['alternative_order'],
                data['criterion_order']
            )
            
        return matrix_obj
        
    def __len__(self) -> int:
        """Return number of alternatives."""
        return len(self.alternatives)
        
    def __str__(self) -> str:
        """String representation."""
        return (
            f"DecisionMatrix(name='{self.name}', "
            f"alternatives={len(self.alternatives)}, "
            f"matrix_shape={self.matrix.shape if self.matrix is not None else None})"
        )


class ScenarioManager:
    """
    Manages multiple decision scenarios for what-if analysis.
    """
    
    def __init__(self):
        """Initialize scenario manager."""
        self.scenarios: Dict[str, DecisionMatrix] = {}
        self.base_scenario: Optional[str] = None
        
    def add_scenario(
        self,
        scenario: DecisionMatrix,
        is_base: bool = False
    ) -> None:
        """
        Add a scenario.
        
        Args:
            scenario: DecisionMatrix to add
            is_base: Whether this is the base scenario
        """
        if scenario.name in self.scenarios:
            raise ValueError(f"Scenario '{scenario.name}' already exists")
            
        self.scenarios[scenario.name] = scenario
        
        if is_base or self.base_scenario is None:
            self.base_scenario = scenario.name
            
    def remove_scenario(self, scenario_name: str) -> None:
        """Remove a scenario."""
        if scenario_name not in self.scenarios:
            raise ValueError(f"Scenario '{scenario_name}' not found")
            
        del self.scenarios[scenario_name]
        
        if self.base_scenario == scenario_name:
            self.base_scenario = list(self.scenarios.keys())[0] if self.scenarios else None
            
    def get_scenario(self, scenario_name: str) -> DecisionMatrix:
        """Get a scenario by name."""
        if scenario_name not in self.scenarios:
            raise ValueError(f"Scenario '{scenario_name}' not found")
        return self.scenarios[scenario_name]
        
    def compare_scenarios(
        self,
        scenario_names: List[str],
        alternative_id: str
    ) -> pd.DataFrame:
        """
        Compare an alternative across multiple scenarios.
        
        Args:
            scenario_names: List of scenario names to compare
            alternative_id: ID of alternative to compare
            
        Returns:
            DataFrame with scenarios as rows and criteria as columns
        """
        data = []
        
        for scenario_name in scenario_names:
            scenario = self.get_scenario(scenario_name)
            profile = scenario.get_alternative_profile(alternative_id)
            data.append(profile)
            
        df = pd.DataFrame(data, index=scenario_names)
        
        return df
        
    def list_scenarios(self) -> List[str]:
        """List all scenario names."""
        return list(self.scenarios.keys())
        
    def __len__(self) -> int:
        """Return number of scenarios."""
        return len(self.scenarios)
