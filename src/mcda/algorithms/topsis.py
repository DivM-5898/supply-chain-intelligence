"""
TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution) Algorithm
Complete implementation for multi-criteria decision analysis.

TOPSIS is a method that chooses alternatives closest to the ideal solution
and farthest from the negative-ideal solution.
Developed by Hwang and Yoon in 1981.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class CriteriaType(Enum):
    """Type of criterion."""
    BENEFIT = "benefit"  # Higher is better (e.g., quality, profit)
    COST = "cost"  # Lower is better (e.g., price, risk)


@dataclass
class TOPSISResult:
    """Results from TOPSIS analysis."""
    scores: np.ndarray  # Closeness coefficients for each alternative
    ranking: List[Tuple[int, float]]  # (alternative_index, score) sorted
    ideal_solution: np.ndarray
    negative_ideal_solution: np.ndarray
    distances_to_ideal: np.ndarray
    distances_to_negative_ideal: np.ndarray
    normalized_matrix: np.ndarray
    weighted_matrix: np.ndarray


class TOPSIS:
    """
    TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution).
    
    The basic principle is that the chosen alternative should have the shortest
    geometric distance from the positive ideal solution (PIS) and the longest
    geometric distance from the negative ideal solution (NIS).
    """
    
    def __init__(self):
        """Initialize TOPSIS calculator."""
        self.decision_matrix = None
        self.weights = None
        self.criteria_types = None
        
    def normalize_matrix(
        self,
        decision_matrix: np.ndarray,
        method: str = 'vector'
    ) -> np.ndarray:
        """
        Normalize the decision matrix.
        
        Args:
            decision_matrix: m x n matrix (m alternatives, n criteria)
            method: Normalization method ('vector', 'minmax', 'sum')
                   - vector: Vector normalization (most common for TOPSIS)
                   - minmax: Min-max normalization
                   - sum: Sum normalization
                   
        Returns:
            Normalized matrix
        """
        if method == 'vector':
            # Vector normalization: r_ij = x_ij / sqrt(sum(x_ij^2))
            squared_sums = np.sqrt(np.sum(decision_matrix ** 2, axis=0))
            normalized = decision_matrix / squared_sums
            
        elif method == 'minmax':
            # Min-max normalization
            min_vals = decision_matrix.min(axis=0)
            max_vals = decision_matrix.max(axis=0)
            range_vals = max_vals - min_vals
            # Handle cases where range is zero
            range_vals[range_vals == 0] = 1
            normalized = (decision_matrix - min_vals) / range_vals
            
        elif method == 'sum':
            # Sum normalization
            col_sums = decision_matrix.sum(axis=0)
            # Handle zero sums
            col_sums[col_sums == 0] = 1
            normalized = decision_matrix / col_sums
            
        else:
            raise ValueError(f"Unknown normalization method: {method}")
            
        return normalized
    
    def apply_weights(
        self,
        normalized_matrix: np.ndarray,
        weights: np.ndarray
    ) -> np.ndarray:
        """
        Apply criteria weights to normalized matrix.
        
        Args:
            normalized_matrix: Normalized decision matrix
            weights: Weight vector (should sum to 1)
            
        Returns:
            Weighted normalized matrix
        """
        if not np.isclose(weights.sum(), 1.0, rtol=1e-5):
            raise ValueError(f"Weights must sum to 1, got {weights.sum()}")
            
        if len(weights) != normalized_matrix.shape[1]:
            raise ValueError(
                f"Weight vector length ({len(weights)}) must match "
                f"number of criteria ({normalized_matrix.shape[1]})"
            )
            
        # Multiply each column by corresponding weight
        weighted_matrix = normalized_matrix * weights
        
        return weighted_matrix
    
    def identify_ideal_solutions(
        self,
        weighted_matrix: np.ndarray,
        criteria_types: List[CriteriaType]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Identify positive ideal solution (PIS) and negative ideal solution (NIS).
        
        Args:
            weighted_matrix: Weighted normalized matrix
            criteria_types: List indicating if each criterion is benefit or cost
            
        Returns:
            Tuple of (positive_ideal_solution, negative_ideal_solution)
        """
        n_criteria = weighted_matrix.shape[1]
        
        if len(criteria_types) != n_criteria:
            raise ValueError(
                f"Number of criteria types ({len(criteria_types)}) must match "
                f"number of criteria ({n_criteria})"
            )
            
        positive_ideal = np.zeros(n_criteria)
        negative_ideal = np.zeros(n_criteria)
        
        for j in range(n_criteria):
            if criteria_types[j] == CriteriaType.BENEFIT:
                # For benefit criteria: max is ideal, min is negative ideal
                positive_ideal[j] = weighted_matrix[:, j].max()
                negative_ideal[j] = weighted_matrix[:, j].min()
            else:  # COST
                # For cost criteria: min is ideal, max is negative ideal
                positive_ideal[j] = weighted_matrix[:, j].min()
                negative_ideal[j] = weighted_matrix[:, j].max()
                
        return positive_ideal, negative_ideal
    
    def calculate_distances(
        self,
        weighted_matrix: np.ndarray,
        ideal_solution: np.ndarray,
        distance_metric: str = 'euclidean'
    ) -> np.ndarray:
        """
        Calculate distances from each alternative to ideal solution.
        
        Args:
            weighted_matrix: Weighted normalized matrix
            ideal_solution: Ideal solution vector
            distance_metric: Distance metric ('euclidean', 'manhattan', 'chebyshev')
            
        Returns:
            Array of distances for each alternative
        """
        if distance_metric == 'euclidean':
            # Euclidean distance (most common in TOPSIS)
            distances = np.sqrt(np.sum((weighted_matrix - ideal_solution) ** 2, axis=1))
            
        elif distance_metric == 'manhattan':
            # Manhattan distance
            distances = np.sum(np.abs(weighted_matrix - ideal_solution), axis=1)
            
        elif distance_metric == 'chebyshev':
            # Chebyshev distance (maximum difference)
            distances = np.max(np.abs(weighted_matrix - ideal_solution), axis=1)
            
        else:
            raise ValueError(f"Unknown distance metric: {distance_metric}")
            
        return distances
    
    def calculate_closeness_coefficients(
        self,
        distances_to_positive: np.ndarray,
        distances_to_negative: np.ndarray
    ) -> np.ndarray:
        """
        Calculate closeness coefficients (relative closeness to ideal solution).
        
        Closeness coefficient: CC_i = d_i- / (d_i+ + d_i-)
        where d_i+ is distance to positive ideal and d_i- is distance to negative ideal
        
        Args:
            distances_to_positive: Distances to positive ideal solution
            distances_to_negative: Distances to negative ideal solution
            
        Returns:
            Closeness coefficients (values between 0 and 1, higher is better)
        """
        # Handle cases where both distances are zero
        total_distances = distances_to_positive + distances_to_negative
        total_distances[total_distances == 0] = 1
        
        closeness = distances_to_negative / total_distances
        
        return closeness
    
    def run_topsis(
        self,
        decision_matrix: np.ndarray,
        weights: np.ndarray,
        criteria_types: List[CriteriaType],
        normalization_method: str = 'vector',
        distance_metric: str = 'euclidean'
    ) -> TOPSISResult:
        """
        Run complete TOPSIS analysis.
        
        Args:
            decision_matrix: m x n matrix (m alternatives, n criteria)
            weights: Weight vector for criteria (must sum to 1)
            criteria_types: List indicating benefit or cost for each criterion
            normalization_method: Method for normalization
            distance_metric: Metric for distance calculation
            
        Returns:
            TOPSISResult with complete analysis
        """
        # Store inputs
        self.decision_matrix = decision_matrix
        self.weights = weights
        self.criteria_types = criteria_types
        
        # Step 1: Normalize decision matrix
        normalized_matrix = self.normalize_matrix(
            decision_matrix,
            method=normalization_method
        )
        
        # Step 2: Apply weights
        weighted_matrix = self.apply_weights(normalized_matrix, weights)
        
        # Step 3: Identify ideal solutions
        positive_ideal, negative_ideal = self.identify_ideal_solutions(
            weighted_matrix,
            criteria_types
        )
        
        # Step 4: Calculate distances
        distances_to_positive = self.calculate_distances(
            weighted_matrix,
            positive_ideal,
            distance_metric=distance_metric
        )
        
        distances_to_negative = self.calculate_distances(
            weighted_matrix,
            negative_ideal,
            distance_metric=distance_metric
        )
        
        # Step 5: Calculate closeness coefficients
        closeness_coefficients = self.calculate_closeness_coefficients(
            distances_to_positive,
            distances_to_negative
        )
        
        # Step 6: Create ranking
        ranking = sorted(
            enumerate(closeness_coefficients),
            key=lambda x: x[1],
            reverse=True
        )
        
        return TOPSISResult(
            scores=closeness_coefficients,
            ranking=ranking,
            ideal_solution=positive_ideal,
            negative_ideal_solution=negative_ideal,
            distances_to_ideal=distances_to_positive,
            distances_to_negative_ideal=distances_to_negative,
            normalized_matrix=normalized_matrix,
            weighted_matrix=weighted_matrix
        )
    
    def sensitivity_analysis_weights(
        self,
        decision_matrix: np.ndarray,
        base_weights: np.ndarray,
        criteria_types: List[CriteriaType],
        criterion_index: int,
        weight_range: Tuple[float, float] = (0.0, 1.0),
        n_steps: int = 20
    ) -> Dict[str, np.ndarray]:
        """
        Perform sensitivity analysis by varying one criterion's weight.
        
        Args:
            decision_matrix: Decision matrix
            base_weights: Original weight vector
            criteria_types: Criterion types
            criterion_index: Index of criterion to vary
            weight_range: Range of weights to test
            n_steps: Number of steps
            
        Returns:
            Dictionary with weight values and corresponding rankings
        """
        weight_values = np.linspace(weight_range[0], weight_range[1], n_steps)
        rankings_history = []
        scores_history = []
        
        for weight in weight_values:
            # Create modified weights
            modified_weights = base_weights.copy()
            
            # Adjust other weights proportionally
            remaining_weight = 1.0 - weight
            other_indices = [i for i in range(len(base_weights)) if i != criterion_index]
            
            if remaining_weight > 0 and len(other_indices) > 0:
                # Distribute remaining weight proportionally
                other_weights_sum = base_weights[other_indices].sum()
                if other_weights_sum > 0:
                    for i in other_indices:
                        modified_weights[i] = (base_weights[i] / other_weights_sum) * remaining_weight
                        
            modified_weights[criterion_index] = weight
            
            # Run TOPSIS with modified weights
            result = self.run_topsis(
                decision_matrix,
                modified_weights,
                criteria_types
            )
            
            rankings_history.append([r[0] for r in result.ranking])
            scores_history.append(result.scores)
            
        return {
            'weight_values': weight_values,
            'rankings': rankings_history,
            'scores': np.array(scores_history)
        }
    
    def compare_alternatives(
        self,
        result: TOPSISResult,
        alternative_names: Optional[List[str]] = None
    ) -> Dict[str, any]:
        """
        Generate detailed comparison of alternatives.
        
        Args:
            result: TOPSIS result
            alternative_names: Optional names for alternatives
            
        Returns:
            Dictionary with comparison details
        """
        n_alternatives = len(result.scores)
        
        if alternative_names is None:
            alternative_names = [f"Alternative {i+1}" for i in range(n_alternatives)]
            
        comparison = {
            'rankings': [],
            'best_alternative': None,
            'worst_alternative': None,
            'score_differences': []
        }
        
        # Build detailed ranking
        for rank, (idx, score) in enumerate(result.ranking, 1):
            comparison['rankings'].append({
                'rank': rank,
                'name': alternative_names[idx],
                'index': idx,
                'score': float(score),
                'distance_to_ideal': float(result.distances_to_ideal[idx]),
                'distance_to_negative_ideal': float(result.distances_to_negative_ideal[idx])
            })
            
        # Best and worst
        best_idx = result.ranking[0][0]
        worst_idx = result.ranking[-1][0]
        
        comparison['best_alternative'] = {
            'name': alternative_names[best_idx],
            'index': best_idx,
            'score': float(result.scores[best_idx])
        }
        
        comparison['worst_alternative'] = {
            'name': alternative_names[worst_idx],
            'index': worst_idx,
            'score': float(result.scores[worst_idx])
        }
        
        # Calculate score differences
        sorted_scores = sorted(result.scores, reverse=True)
        comparison['score_differences'] = [
            float(sorted_scores[i] - sorted_scores[i+1])
            for i in range(len(sorted_scores) - 1)
        ]
        
        return comparison


def create_decision_matrix_from_dataframe(
    df,
    alternative_column: str,
    criteria_columns: List[str]
) -> Tuple[np.ndarray, List[str]]:
    """
    Create decision matrix from pandas DataFrame.
    
    Args:
        df: DataFrame with alternatives and criteria
        alternative_column: Column name containing alternative names
        criteria_columns: List of column names for criteria
        
    Returns:
        Tuple of (decision_matrix, alternative_names)
    """
    import pandas as pd
    
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
        
    alternative_names = df[alternative_column].tolist()
    decision_matrix = df[criteria_columns].values
    
    return decision_matrix, alternative_names
