"""
Criteria Management System for Multi-Criteria Decision Analysis
Handles definition, weighting, validation, and normalization of decision criteria.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json


class CriterionType(Enum):
    """Type of criterion."""
    BENEFIT = "benefit"  # Maximization criterion
    COST = "cost"  # Minimization criterion


class CriterionScale(Enum):
    """Scale type of criterion."""
    RATIO = "ratio"  # Ratio scale (e.g., price, weight)
    INTERVAL = "interval"  # Interval scale (e.g., temperature)
    ORDINAL = "ordinal"  # Ordinal scale (e.g., ratings)
    NOMINAL = "nominal"  # Nominal scale (e.g., categories)


@dataclass
class Criterion:
    """
    Represents a single decision criterion.
    """
    id: str
    name: str
    description: str
    type: CriterionType
    scale: CriterionScale
    weight: float = 0.0
    unit: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    ideal_value: Optional[float] = None
    threshold: Optional[float] = None  # Indifference threshold
    veto_threshold: Optional[float] = None  # Veto threshold for ELECTRE
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate criterion after initialization."""
        if self.weight < 0:
            raise ValueError(f"Weight must be non-negative, got {self.weight}")
            
        if self.min_value is not None and self.max_value is not None:
            if self.min_value >= self.max_value:
                raise ValueError(
                    f"min_value ({self.min_value}) must be less than "
                    f"max_value ({self.max_value})"
                )
                
    def normalize_value(
        self,
        value: float,
        method: str = 'minmax'
    ) -> float:
        """
        Normalize a value for this criterion.
        
        Args:
            value: Value to normalize
            method: Normalization method ('minmax', 'standardize')
            
        Returns:
            Normalized value
        """
        if method == 'minmax':
            if self.min_value is None or self.max_value is None:
                raise ValueError("Min and max values required for minmax normalization")
                
            if self.max_value == self.min_value:
                return 0.5
                
            normalized = (value - self.min_value) / (self.max_value - self.min_value)
            
            # Invert for cost criteria
            if self.type == CriterionType.COST:
                normalized = 1.0 - normalized
                
            return np.clip(normalized, 0.0, 1.0)
            
        elif method == 'standardize':
            # Would need mean and std for standardization
            raise NotImplementedError("Standardization requires mean and std")
            
        else:
            raise ValueError(f"Unknown normalization method: {method}")
            
    def to_dict(self) -> Dict:
        """Convert criterion to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type.value,
            'scale': self.scale.value,
            'weight': self.weight,
            'unit': self.unit,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'ideal_value': self.ideal_value,
            'threshold': self.threshold,
            'veto_threshold': self.veto_threshold,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Criterion':
        """Create criterion from dictionary."""
        return cls(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            type=CriterionType(data['type']),
            scale=CriterionScale(data['scale']),
            weight=data.get('weight', 0.0),
            unit=data.get('unit'),
            min_value=data.get('min_value'),
            max_value=data.get('max_value'),
            ideal_value=data.get('ideal_value'),
            threshold=data.get('threshold'),
            veto_threshold=data.get('veto_threshold'),
            metadata=data.get('metadata', {})
        )


class CriteriaManager:
    """
    Manages a collection of criteria for decision analysis.
    """
    
    def __init__(self):
        """Initialize criteria manager."""
        self.criteria: Dict[str, Criterion] = {}
        self._weights_normalized = False
        
    def add_criterion(
        self,
        criterion: Criterion,
        auto_normalize_weights: bool = True
    ) -> None:
        """
        Add a criterion to the manager.
        
        Args:
            criterion: Criterion to add
            auto_normalize_weights: Automatically normalize weights after adding
        """
        if criterion.id in self.criteria:
            raise ValueError(f"Criterion with id '{criterion.id}' already exists")
            
        self.criteria[criterion.id] = criterion
        self._weights_normalized = False
        
        if auto_normalize_weights:
            self.normalize_weights()
            
    def remove_criterion(self, criterion_id: str) -> None:
        """Remove a criterion by ID."""
        if criterion_id not in self.criteria:
            raise ValueError(f"Criterion with id '{criterion_id}' not found")
            
        del self.criteria[criterion_id]
        self._weights_normalized = False
        
    def get_criterion(self, criterion_id: str) -> Criterion:
        """Get a criterion by ID."""
        if criterion_id not in self.criteria:
            raise ValueError(f"Criterion with id '{criterion_id}' not found")
        return self.criteria[criterion_id]
        
    def update_weight(
        self,
        criterion_id: str,
        weight: float,
        auto_normalize: bool = True
    ) -> None:
        """
        Update weight for a criterion.
        
        Args:
            criterion_id: ID of criterion to update
            weight: New weight value
            auto_normalize: Automatically normalize all weights
        """
        criterion = self.get_criterion(criterion_id)
        
        if weight < 0:
            raise ValueError(f"Weight must be non-negative, got {weight}")
            
        criterion.weight = weight
        self._weights_normalized = False
        
        if auto_normalize:
            self.normalize_weights()
            
    def update_weights(
        self,
        weights: Dict[str, float],
        auto_normalize: bool = True
    ) -> None:
        """
        Update weights for multiple criteria.
        
        Args:
            weights: Dictionary mapping criterion IDs to weights
            auto_normalize: Automatically normalize all weights
        """
        for criterion_id, weight in weights.items():
            criterion = self.get_criterion(criterion_id)
            if weight < 0:
                raise ValueError(f"Weight must be non-negative for '{criterion_id}'")
            criterion.weight = weight
            
        self._weights_normalized = False
        
        if auto_normalize:
            self.normalize_weights()
            
    def normalize_weights(self) -> None:
        """Normalize all weights to sum to 1."""
        if not self.criteria:
            return
            
        total_weight = sum(c.weight for c in self.criteria.values())
        
        if total_weight == 0:
            # Equal weights if all are zero
            equal_weight = 1.0 / len(self.criteria)
            for criterion in self.criteria.values():
                criterion.weight = equal_weight
        else:
            # Normalize to sum to 1
            for criterion in self.criteria.values():
                criterion.weight = criterion.weight / total_weight
                
        self._weights_normalized = True
        
    def get_weights_array(self, criterion_order: Optional[List[str]] = None) -> np.ndarray:
        """
        Get weights as numpy array.
        
        Args:
            criterion_order: Optional list of criterion IDs defining order
            
        Returns:
            Array of weights
        """
        if not self._weights_normalized:
            self.normalize_weights()
            
        if criterion_order is None:
            criterion_order = list(self.criteria.keys())
            
        weights = np.array([
            self.criteria[cid].weight for cid in criterion_order
        ])
        
        return weights
        
    def get_types_list(self, criterion_order: Optional[List[str]] = None) -> List[CriterionType]:
        """
        Get criterion types as list.
        
        Args:
            criterion_order: Optional list of criterion IDs defining order
            
        Returns:
            List of criterion types
        """
        if criterion_order is None:
            criterion_order = list(self.criteria.keys())
            
        return [self.criteria[cid].type for cid in criterion_order]
        
    def validate_decision_matrix(
        self,
        matrix: np.ndarray,
        criterion_order: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Validate a decision matrix against criteria definitions.
        
        Args:
            matrix: Decision matrix (alternatives x criteria)
            criterion_order: Order of criteria in matrix columns
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check dimensions
        if matrix.shape[1] != len(criterion_order):
            errors.append(
                f"Matrix has {matrix.shape[1]} columns but "
                f"{len(criterion_order)} criteria specified"
            )
            return False, errors
            
        # Check each criterion
        for col_idx, criterion_id in enumerate(criterion_order):
            if criterion_id not in self.criteria:
                errors.append(f"Unknown criterion: {criterion_id}")
                continue
                
            criterion = self.criteria[criterion_id]
            column_values = matrix[:, col_idx]
            
            # Check for invalid values
            if np.any(np.isnan(column_values)):
                errors.append(f"NaN values in criterion '{criterion.name}'")
                
            if np.any(np.isinf(column_values)):
                errors.append(f"Inf values in criterion '{criterion.name}'")
                
            # Check bounds if defined
            if criterion.min_value is not None:
                if np.any(column_values < criterion.min_value):
                    errors.append(
                        f"Values below min for criterion '{criterion.name}' "
                        f"(min: {criterion.min_value})"
                    )
                    
            if criterion.max_value is not None:
                if np.any(column_values > criterion.max_value):
                    errors.append(
                        f"Values above max for criterion '{criterion.name}' "
                        f"(max: {criterion.max_value})"
                    )
                    
        is_valid = len(errors) == 0
        return is_valid, errors
        
    def create_summary(self) -> Dict:
        """Create summary of all criteria."""
        if not self._weights_normalized:
            self.normalize_weights()
            
        return {
            'total_criteria': len(self.criteria),
            'benefit_criteria': sum(
                1 for c in self.criteria.values() 
                if c.type == CriterionType.BENEFIT
            ),
            'cost_criteria': sum(
                1 for c in self.criteria.values() 
                if c.type == CriterionType.COST
            ),
            'weights_normalized': self._weights_normalized,
            'criteria': [c.to_dict() for c in self.criteria.values()]
        }
        
    def save_to_file(self, filepath: str) -> None:
        """Save criteria definitions to JSON file."""
        summary = self.create_summary()
        
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
            
    @classmethod
    def load_from_file(cls, filepath: str) -> 'CriteriaManager':
        """Load criteria definitions from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        manager = cls()
        
        for criterion_data in data['criteria']:
            criterion = Criterion.from_dict(criterion_data)
            manager.add_criterion(criterion, auto_normalize_weights=False)
            
        if data.get('weights_normalized', False):
            manager._weights_normalized = True
        else:
            manager.normalize_weights()
            
        return manager
        
    def calculate_weights_from_ranks(
        self,
        ranks: Dict[str, int],
        method: str = 'rank_sum'
    ) -> None:
        """
        Calculate weights from criterion rankings.
        
        Args:
            ranks: Dictionary mapping criterion IDs to ranks (1 = most important)
            method: Method to use ('rank_sum', 'rank_reciprocal', 'rank_exponent')
        """
        n = len(self.criteria)
        
        for criterion_id in self.criteria:
            if criterion_id not in ranks:
                raise ValueError(f"Missing rank for criterion '{criterion_id}'")
                
            rank = ranks[criterion_id]
            
            if rank < 1 or rank > n:
                raise ValueError(f"Invalid rank {rank} for '{criterion_id}' (must be 1-{n})")
                
        # Calculate weights based on method
        for criterion_id, rank in ranks.items():
            if method == 'rank_sum':
                # Rank sum method: w_i = (n - r_i + 1) / sum
                weight = (n - rank + 1)
                
            elif method == 'rank_reciprocal':
                # Rank reciprocal: w_i = 1/r_i / sum
                weight = 1.0 / rank
                
            elif method == 'rank_exponent':
                # Rank exponent: w_i = (n - r_i + 1)^2 / sum
                weight = (n - rank + 1) ** 2
                
            else:
                raise ValueError(f"Unknown ranking method: {method}")
                
            self.criteria[criterion_id].weight = weight
            
        # Normalize weights
        self.normalize_weights()
        
    def __len__(self) -> int:
        """Return number of criteria."""
        return len(self.criteria)
        
    def __contains__(self, criterion_id: str) -> bool:
        """Check if criterion exists."""
        return criterion_id in self.criteria
        
    def __iter__(self):
        """Iterate over criteria."""
        return iter(self.criteria.values())


def create_supply_chain_criteria() -> CriteriaManager:
    """
    Create pre-defined criteria for supply chain decision making.
    
    Returns:
        CriteriaManager with common supply chain criteria
    """
    manager = CriteriaManager()
    
    # Cost criterion
    manager.add_criterion(Criterion(
        id='cost',
        name='Total Cost',
        description='Total cost including unit price, shipping, and handling',
        type=CriterionType.COST,
        scale=CriterionScale.RATIO,
        weight=0.30,
        unit='USD',
        min_value=0.0
    ), auto_normalize_weights=False)
    
    # Quality criterion
    manager.add_criterion(Criterion(
        id='quality',
        name='Product Quality',
        description='Quality score based on defect rate and specifications',
        type=CriterionType.BENEFIT,
        scale=CriterionScale.RATIO,
        weight=0.25,
        min_value=0.0,
        max_value=100.0
    ), auto_normalize_weights=False)
    
    # Delivery time
    manager.add_criterion(Criterion(
        id='delivery_time',
        name='Delivery Time',
        description='Lead time from order to delivery',
        type=CriterionType.COST,
        scale=CriterionScale.RATIO,
        weight=0.20,
        unit='days',
        min_value=0.0
    ), auto_normalize_weights=False)
    
    # Reliability
    manager.add_criterion(Criterion(
        id='reliability',
        name='Supplier Reliability',
        description='On-time delivery rate and order fulfillment accuracy',
        type=CriterionType.BENEFIT,
        scale=CriterionScale.RATIO,
        weight=0.15,
        min_value=0.0,
        max_value=100.0
    ), auto_normalize_weights=False)
    
    # Flexibility
    manager.add_criterion(Criterion(
        id='flexibility',
        name='Flexibility',
        description='Ability to accommodate changes in order volume and specifications',
        type=CriterionType.BENEFIT,
        scale=CriterionScale.ORDINAL,
        weight=0.10,
        min_value=1.0,
        max_value=5.0
    ), auto_normalize_weights=False)
    
    manager.normalize_weights()
    
    return manager
