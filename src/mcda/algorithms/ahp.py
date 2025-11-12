"""
Analytic Hierarchy Process (AHP) Algorithm
Complete implementation for multi-criteria decision analysis.

AHP is a structured technique for organizing and analyzing complex decisions based on
mathematics and psychology. Developed by Thomas L. Saaty in the 1970s.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class AHPResult:
    """Results from AHP analysis."""
    weights: np.ndarray
    consistency_ratio: float
    consistency_index: float
    is_consistent: bool
    principal_eigenvalue: float
    alternatives_scores: Optional[Dict[str, float]] = None
    ranking: Optional[List[Tuple[str, float]]] = None


class AHP:
    """
    Analytic Hierarchy Process (AHP) implementation.
    
    AHP helps decision-makers make choices when multiple criteria must be considered.
    It uses pairwise comparisons to determine relative importance.
    """
    
    # Random Consistency Index (RI) values for different matrix sizes
    RANDOM_CONSISTENCY_INDEX = {
        1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
        6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49,
        11: 1.51, 12: 1.48, 13: 1.56, 14: 1.57, 15: 1.59
    }
    
    CONSISTENCY_THRESHOLD = 0.10  # Standard threshold for acceptable consistency
    
    def __init__(self):
        """Initialize AHP calculator."""
        self.pairwise_matrix = None
        self.criteria_weights = None
        self.cr = None
        
    def create_pairwise_matrix(
        self,
        comparisons: Dict[Tuple[int, int], float]
    ) -> np.ndarray:
        """
        Create pairwise comparison matrix from comparison values.
        
        Args:
            comparisons: Dictionary with (i, j) tuples as keys and comparison values
                        Values should be on Saaty's 1-9 scale:
                        1: Equal importance
                        3: Moderate importance
                        5: Strong importance
                        7: Very strong importance
                        9: Extreme importance
                        2, 4, 6, 8: Intermediate values
                        
        Returns:
            Pairwise comparison matrix
        """
        # Determine matrix size from comparisons
        max_index = max(max(i, j) for i, j in comparisons.keys())
        n = max_index + 1
        
        # Initialize matrix with ones on diagonal
        matrix = np.ones((n, n))
        
        # Fill matrix with comparison values
        for (i, j), value in comparisons.items():
            if value <= 0:
                raise ValueError(f"Comparison value must be positive, got {value}")
            matrix[i, j] = value
            matrix[j, i] = 1.0 / value  # Reciprocal for symmetric entry
            
        self.pairwise_matrix = matrix
        return matrix
    
    def create_pairwise_matrix_from_full(
        self,
        matrix: np.ndarray
    ) -> np.ndarray:
        """
        Validate and use a pre-constructed pairwise comparison matrix.
        
        Args:
            matrix: Square pairwise comparison matrix
            
        Returns:
            Validated pairwise comparison matrix
        """
        if matrix.shape[0] != matrix.shape[1]:
            raise ValueError("Matrix must be square")
            
        # Validate reciprocal property
        n = matrix.shape[0]
        for i in range(n):
            for j in range(n):
                if i != j:
                    expected_reciprocal = 1.0 / matrix[i, j]
                    if not np.isclose(matrix[j, i], expected_reciprocal, rtol=1e-5):
                        raise ValueError(
                            f"Matrix does not satisfy reciprocal property at ({i},{j})"
                        )
                        
        self.pairwise_matrix = matrix
        return matrix
    
    def calculate_weights(
        self,
        matrix: Optional[np.ndarray] = None,
        method: str = 'eigenvalue'
    ) -> np.ndarray:
        """
        Calculate criteria weights from pairwise comparison matrix.
        
        Args:
            matrix: Pairwise comparison matrix (uses stored matrix if None)
            method: Method to use ('eigenvalue', 'geometric_mean', 'normalized_column')
                   - eigenvalue: Principal eigenvector method (most accurate)
                   - geometric_mean: Geometric mean of rows
                   - normalized_column: Column sum normalization
                   
        Returns:
            Weight vector (sums to 1)
        """
        if matrix is None:
            if self.pairwise_matrix is None:
                raise ValueError("No pairwise matrix available")
            matrix = self.pairwise_matrix
            
        if method == 'eigenvalue':
            weights = self._eigenvalue_method(matrix)
        elif method == 'geometric_mean':
            weights = self._geometric_mean_method(matrix)
        elif method == 'normalized_column':
            weights = self._normalized_column_method(matrix)
        else:
            raise ValueError(f"Unknown method: {method}")
            
        self.criteria_weights = weights
        return weights
    
    def _eigenvalue_method(self, matrix: np.ndarray) -> np.ndarray:
        """
        Calculate weights using principal eigenvector method.
        This is the most accurate method recommended by Saaty.
        """
        # Calculate eigenvalues and eigenvectors
        eigenvalues, eigenvectors = np.linalg.eig(matrix)
        
        # Find principal eigenvalue (largest real eigenvalue)
        max_eigenvalue_idx = np.argmax(eigenvalues.real)
        principal_eigenvector = eigenvectors[:, max_eigenvalue_idx].real
        
        # Normalize to sum to 1
        weights = principal_eigenvector / principal_eigenvector.sum()
        
        return weights
    
    def _geometric_mean_method(self, matrix: np.ndarray) -> np.ndarray:
        """
        Calculate weights using geometric mean of rows.
        Simpler approximation method.
        """
        n = matrix.shape[0]
        geometric_means = np.zeros(n)
        
        for i in range(n):
            # Calculate geometric mean of row i
            row_product = np.prod(matrix[i, :])
            geometric_means[i] = row_product ** (1.0 / n)
            
        # Normalize to sum to 1
        weights = geometric_means / geometric_means.sum()
        
        return weights
    
    def _normalized_column_method(self, matrix: np.ndarray) -> np.ndarray:
        """
        Calculate weights using normalized column averages.
        Simple approximation method.
        """
        # Normalize each column
        column_sums = matrix.sum(axis=0)
        normalized_matrix = matrix / column_sums
        
        # Average across rows
        weights = normalized_matrix.mean(axis=1)
        
        return weights
    
    def calculate_consistency_ratio(
        self,
        matrix: Optional[np.ndarray] = None,
        weights: Optional[np.ndarray] = None
    ) -> Tuple[float, float, float]:
        """
        Calculate consistency ratio (CR) to check for logical consistency.
        
        CR < 0.10 indicates acceptable consistency
        CR >= 0.10 indicates inconsistency; reconsideration recommended
        
        Args:
            matrix: Pairwise comparison matrix
            weights: Weight vector
            
        Returns:
            Tuple of (consistency_ratio, consistency_index, principal_eigenvalue)
        """
        if matrix is None:
            matrix = self.pairwise_matrix
        if weights is None:
            weights = self.criteria_weights
            
        if matrix is None or weights is None:
            raise ValueError("Matrix and weights are required")
            
        n = matrix.shape[0]
        
        # Calculate principal eigenvalue (λ_max)
        weighted_sum = matrix @ weights
        lambda_max = np.mean(weighted_sum / weights)
        
        # Calculate Consistency Index (CI)
        ci = (lambda_max - n) / (n - 1) if n > 1 else 0
        
        # Get Random Consistency Index (RI)
        ri = self.RANDOM_CONSISTENCY_INDEX.get(n, 1.49)
        
        # Calculate Consistency Ratio (CR)
        cr = ci / ri if ri > 0 else 0
        
        self.cr = cr
        
        return cr, ci, lambda_max
    
    def evaluate_alternatives(
        self,
        alternative_matrices: Dict[str, np.ndarray],
        criteria_weights: Optional[np.ndarray] = None
    ) -> Dict[str, float]:
        """
        Evaluate alternatives across multiple criteria.
        
        Args:
            alternative_matrices: Dictionary mapping criterion names to pairwise
                                 comparison matrices of alternatives under that criterion
            criteria_weights: Weights of criteria (uses stored weights if None)
            
        Returns:
            Dictionary mapping alternative names to final scores
        """
        if criteria_weights is None:
            if self.criteria_weights is None:
                raise ValueError("Criteria weights not calculated")
            criteria_weights = self.criteria_weights
            
        # Get number of alternatives from first matrix
        first_matrix = next(iter(alternative_matrices.values()))
        n_alternatives = first_matrix.shape[0]
        
        # Initialize scores
        alternative_scores = np.zeros(n_alternatives)
        
        # Calculate scores for each criterion
        for criterion_idx, (criterion_name, alt_matrix) in enumerate(alternative_matrices.items()):
            # Calculate alternative weights for this criterion
            alt_weights = self.calculate_weights(alt_matrix)
            
            # Add weighted contribution to total score
            alternative_scores += criteria_weights[criterion_idx] * alt_weights
            
        return alternative_scores
    
    def run_ahp(
        self,
        criteria_matrix: np.ndarray,
        alternative_matrices: Optional[Dict[str, np.ndarray]] = None,
        alternative_names: Optional[List[str]] = None
    ) -> AHPResult:
        """
        Run complete AHP analysis.
        
        Args:
            criteria_matrix: Pairwise comparison matrix for criteria
            alternative_matrices: Optional dict of alternative comparison matrices
            alternative_names: Names of alternatives
            
        Returns:
            AHPResult with complete analysis
        """
        # Calculate criteria weights
        weights = self.calculate_weights(criteria_matrix)
        
        # Calculate consistency
        cr, ci, lambda_max = self.calculate_consistency_ratio(criteria_matrix, weights)
        is_consistent = cr < self.CONSISTENCY_THRESHOLD
        
        # Evaluate alternatives if provided
        alternatives_scores = None
        ranking = None
        
        if alternative_matrices is not None:
            alternatives_scores = self.evaluate_alternatives(
                alternative_matrices,
                weights
            )
            
            # Create ranking
            if alternative_names is not None:
                ranking = sorted(
                    zip(alternative_names, alternatives_scores),
                    key=lambda x: x[1],
                    reverse=True
                )
        
        return AHPResult(
            weights=weights,
            consistency_ratio=cr,
            consistency_index=ci,
            is_consistent=is_consistent,
            principal_eigenvalue=lambda_max,
            alternatives_scores=alternatives_scores,
            ranking=ranking
        )
    
    def sensitivity_analysis(
        self,
        criteria_matrix: np.ndarray,
        criterion_index: int,
        variation_range: Tuple[float, float] = (0.5, 2.0),
        n_steps: int = 20
    ) -> Dict[str, np.ndarray]:
        """
        Perform sensitivity analysis by varying one criterion's importance.
        
        Args:
            criteria_matrix: Original pairwise comparison matrix
            criterion_index: Index of criterion to vary
            variation_range: Range of variation factors (min, max)
            n_steps: Number of steps in variation
            
        Returns:
            Dictionary with variation factors and corresponding weight vectors
        """
        factors = np.linspace(variation_range[0], variation_range[1], n_steps)
        weight_history = []
        
        for factor in factors:
            # Create modified matrix
            modified_matrix = criteria_matrix.copy()
            modified_matrix[criterion_index, :] *= factor
            modified_matrix[:, criterion_index] /= factor
            modified_matrix[criterion_index, criterion_index] = 1.0
            
            # Calculate weights
            weights = self.calculate_weights(modified_matrix)
            weight_history.append(weights)
            
        return {
            'factors': factors,
            'weights': np.array(weight_history)
        }


def create_comparison_from_scores(
    scores: List[float],
    scale_type: str = 'ratio'
) -> np.ndarray:
    """
    Create pairwise comparison matrix from direct scores/ratings.
    
    Args:
        scores: List of scores for each criterion/alternative
        scale_type: 'ratio' for direct ratios, 'saaty' to map to 1-9 scale
        
    Returns:
        Pairwise comparison matrix
    """
    scores = np.array(scores)
    n = len(scores)
    matrix = np.ones((n, n))
    
    for i in range(n):
        for j in range(n):
            if i != j:
                if scale_type == 'ratio':
                    matrix[i, j] = scores[i] / scores[j]
                elif scale_type == 'saaty':
                    ratio = scores[i] / scores[j]
                    # Map ratio to Saaty scale
                    if ratio >= 9:
                        matrix[i, j] = 9
                    elif ratio >= 7:
                        matrix[i, j] = 7
                    elif ratio >= 5:
                        matrix[i, j] = 5
                    elif ratio >= 3:
                        matrix[i, j] = 3
                    elif ratio >= 1:
                        matrix[i, j] = 1
                    else:
                        matrix[i, j] = 1 / create_comparison_from_scores(
                            [scores[j]], 'saaty'
                        )[0, 0]
                        
    return matrix
