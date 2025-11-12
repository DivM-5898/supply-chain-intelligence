"""
ELECTRE (ELimination Et Choix Traduisant la REalité) Algorithm
Complete implementation for multi-criteria decision analysis.

ELECTRE is an outranking method that builds pairwise comparison of alternatives
based on concordance and discordance indices.
Developed by Bernard Roy in 1965.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum


class CriterionType(Enum):
    """Type of criterion."""
    BENEFIT = "benefit"  # Higher values are preferred
    COST = "cost"  # Lower values are preferred


@dataclass
class ELECTREResult:
    """Results from ELECTRE analysis."""
    concordance_matrix: np.ndarray
    discordance_matrix: np.ndarray
    outranking_matrix: np.ndarray
    kernel: Set[int]  # Non-dominated alternatives
    dominated: Set[int]  # Dominated alternatives
    ranking: List[int]  # Preference ordering
    concordance_threshold: float
    discordance_threshold: float


class ELECTRE:
    """
    ELECTRE (ELimination Et Choix Traduisant la REalité) implementation.
    
    ELECTRE is based on outranking relations: alternative A outranks B if
    A is at least as good as B on a majority of criteria (concordance) and
    not significantly worse on any criterion (discordance).
    """
    
    def __init__(self):
        """Initialize ELECTRE calculator."""
        self.decision_matrix = None
        self.weights = None
        self.criterion_types = None
        
    def normalize_matrix(
        self,
        decision_matrix: np.ndarray,
        criterion_types: List[CriterionType]
    ) -> np.ndarray:
        """
        Normalize decision matrix based on criterion types.
        
        Args:
            decision_matrix: m x n matrix (m alternatives, n criteria)
            criterion_types: List indicating benefit or cost for each criterion
            
        Returns:
            Normalized matrix where higher is always better
        """
        normalized = decision_matrix.copy().astype(float)
        
        for j, ctype in enumerate(criterion_types):
            column = normalized[:, j]
            col_max = column.max()
            col_min = column.min()
            
            if col_max == col_min:
                # All values are the same, set to 1
                normalized[:, j] = 1.0
            elif ctype == CriterionType.COST:
                # For cost criteria, invert: normalized = (max - value) / (max - min)
                normalized[:, j] = (col_max - column) / (col_max - col_min)
            else:  # BENEFIT
                # For benefit criteria: normalized = (value - min) / (max - min)
                normalized[:, j] = (column - col_min) / (col_max - col_min)
                
        return normalized
    
    def calculate_concordance_matrix(
        self,
        decision_matrix: np.ndarray,
        weights: np.ndarray,
        criterion_types: List[CriterionType]
    ) -> np.ndarray:
        """
        Calculate concordance matrix.
        
        Concordance c(a,b) measures the strength of support for "a outranks b".
        It's the sum of weights of criteria where a is at least as good as b.
        
        Args:
            decision_matrix: Decision matrix
            weights: Criterion weights (must sum to 1)
            criterion_types: Criterion types
            
        Returns:
            Concordance matrix where c[i,j] is concordance of i over j
        """
        m, n = decision_matrix.shape  # m alternatives, n criteria
        
        if not np.isclose(weights.sum(), 1.0, rtol=1e-5):
            raise ValueError(f"Weights must sum to 1, got {weights.sum()}")
            
        # Normalize matrix
        normalized = self.normalize_matrix(decision_matrix, criterion_types)
        
        # Initialize concordance matrix
        concordance = np.zeros((m, m))
        
        # Calculate concordance for each pair of alternatives
        for i in range(m):
            for j in range(m):
                if i == j:
                    continue
                    
                # Sum weights where alternative i is at least as good as j
                concordance_sum = 0.0
                for k in range(n):
                    if normalized[i, k] >= normalized[j, k]:
                        concordance_sum += weights[k]
                        
                concordance[i, j] = concordance_sum
                
        return concordance
    
    def calculate_discordance_matrix(
        self,
        decision_matrix: np.ndarray,
        criterion_types: List[CriterionType]
    ) -> np.ndarray:
        """
        Calculate discordance matrix.
        
        Discordance d(a,b) measures the strength of opposition to "a outranks b".
        It's based on the maximum difference where b is better than a.
        
        Args:
            decision_matrix: Decision matrix
            criterion_types: Criterion types
            
        Returns:
            Discordance matrix where d[i,j] is discordance of i over j
        """
        m, n = decision_matrix.shape
        
        # Normalize matrix
        normalized = self.normalize_matrix(decision_matrix, criterion_types)
        
        # Calculate range for each criterion
        ranges = np.zeros(n)
        for j in range(n):
            ranges[j] = normalized[:, j].max() - normalized[:, j].min()
            if ranges[j] == 0:
                ranges[j] = 1.0  # Avoid division by zero
        
        # Initialize discordance matrix
        discordance = np.zeros((m, m))
        
        # Calculate discordance for each pair
        for i in range(m):
            for j in range(m):
                if i == j:
                    continue
                    
                # Find maximum disadvantage of i compared to j
                max_disadvantage = 0.0
                for k in range(n):
                    if normalized[j, k] > normalized[i, k]:
                        disadvantage = (normalized[j, k] - normalized[i, k]) / ranges[k]
                        max_disadvantage = max(max_disadvantage, disadvantage)
                        
                discordance[i, j] = max_disadvantage
                
        return discordance
    
    def calculate_outranking_matrix(
        self,
        concordance_matrix: np.ndarray,
        discordance_matrix: np.ndarray,
        concordance_threshold: float,
        discordance_threshold: float
    ) -> np.ndarray:
        """
        Calculate outranking matrix based on thresholds.
        
        Alternative i outranks j if:
        1. Concordance c(i,j) >= concordance_threshold
        2. Discordance d(i,j) <= discordance_threshold
        
        Args:
            concordance_matrix: Concordance matrix
            discordance_matrix: Discordance matrix
            concordance_threshold: Minimum concordance level (typically 0.6-0.8)
            discordance_threshold: Maximum discordance level (typically 0.2-0.4)
            
        Returns:
            Binary outranking matrix where 1 means i outranks j
        """
        m = concordance_matrix.shape[0]
        outranking = np.zeros((m, m), dtype=int)
        
        for i in range(m):
            for j in range(m):
                if i != j:
                    if (concordance_matrix[i, j] >= concordance_threshold and
                        discordance_matrix[i, j] <= discordance_threshold):
                        outranking[i, j] = 1
                        
        return outranking
    
    def find_kernel(
        self,
        outranking_matrix: np.ndarray
    ) -> Tuple[Set[int], Set[int]]:
        """
        Find the kernel (non-dominated alternatives).
        
        The kernel consists of alternatives that:
        1. Are not outranked by any other alternative
        2. Outrank all alternatives outside the kernel
        
        Args:
            outranking_matrix: Binary outranking matrix
            
        Returns:
            Tuple of (kernel_set, dominated_set)
        """
        m = outranking_matrix.shape[0]
        
        # Find which alternatives are outranked
        is_outranked = np.any(outranking_matrix == 1, axis=0)
        
        # Non-dominated alternatives (not outranked by anyone)
        kernel = set(np.where(~is_outranked)[0].tolist())
        
        # Dominated alternatives
        dominated = set(np.where(is_outranked)[0].tolist())
        
        return kernel, dominated
    
    def create_ranking(
        self,
        outranking_matrix: np.ndarray
    ) -> List[int]:
        """
        Create a complete ranking of alternatives.
        
        Uses iterative kernel extraction: alternatives in higher tiers
        are preferred to those in lower tiers.
        
        Args:
            outranking_matrix: Binary outranking matrix
            
        Returns:
            List of alternative indices in order of preference
        """
        m = outranking_matrix.shape[0]
        remaining = set(range(m))
        ranking = []
        
        current_matrix = outranking_matrix.copy()
        
        while remaining:
            # Find kernel of current matrix
            is_outranked = np.zeros(m, dtype=bool)
            for i in remaining:
                for j in remaining:
                    if i != j and current_matrix[j, i] == 1:
                        is_outranked[i] = True
                        break
                        
            # Current kernel (non-dominated among remaining)
            current_kernel = [i for i in remaining if not is_outranked[i]]
            
            if not current_kernel:
                # No clear kernel, add remaining in arbitrary order
                ranking.extend(sorted(remaining))
                break
                
            # Add kernel to ranking
            ranking.extend(sorted(current_kernel))
            
            # Remove kernel from remaining
            for idx in current_kernel:
                remaining.remove(idx)
                
        return ranking
    
    def calculate_net_dominance_score(
        self,
        outranking_matrix: np.ndarray
    ) -> np.ndarray:
        """
        Calculate net dominance score for each alternative.
        
        Net dominance = (number outranked - number outranked by)
        
        Args:
            outranking_matrix: Binary outranking matrix
            
        Returns:
            Array of net dominance scores
        """
        # Count how many each alternative outranks
        outranks_count = outranking_matrix.sum(axis=1)
        
        # Count how many outrank each alternative
        outranked_by_count = outranking_matrix.sum(axis=0)
        
        # Net dominance
        net_dominance = outranks_count - outranked_by_count
        
        return net_dominance
    
    def run_electre(
        self,
        decision_matrix: np.ndarray,
        weights: np.ndarray,
        criterion_types: List[CriterionType],
        concordance_threshold: Optional[float] = None,
        discordance_threshold: Optional[float] = None
    ) -> ELECTREResult:
        """
        Run complete ELECTRE analysis.
        
        Args:
            decision_matrix: m x n matrix (m alternatives, n criteria)
            weights: Criterion weights (must sum to 1)
            criterion_types: List indicating benefit or cost for each criterion
            concordance_threshold: Minimum concordance (default: 0.75)
            discordance_threshold: Maximum discordance (default: 0.25)
            
        Returns:
            ELECTREResult with complete analysis
        """
        # Set default thresholds
        if concordance_threshold is None:
            concordance_threshold = 0.75
        if discordance_threshold is None:
            discordance_threshold = 0.25
            
        # Store inputs
        self.decision_matrix = decision_matrix
        self.weights = weights
        self.criterion_types = criterion_types
        
        # Step 1: Calculate concordance matrix
        concordance_matrix = self.calculate_concordance_matrix(
            decision_matrix,
            weights,
            criterion_types
        )
        
        # Step 2: Calculate discordance matrix
        discordance_matrix = self.calculate_discordance_matrix(
            decision_matrix,
            criterion_types
        )
        
        # Step 3: Calculate outranking matrix
        outranking_matrix = self.calculate_outranking_matrix(
            concordance_matrix,
            discordance_matrix,
            concordance_threshold,
            discordance_threshold
        )
        
        # Step 4: Find kernel (non-dominated alternatives)
        kernel, dominated = self.find_kernel(outranking_matrix)
        
        # Step 5: Create ranking
        ranking = self.create_ranking(outranking_matrix)
        
        return ELECTREResult(
            concordance_matrix=concordance_matrix,
            discordance_matrix=discordance_matrix,
            outranking_matrix=outranking_matrix,
            kernel=kernel,
            dominated=dominated,
            ranking=ranking,
            concordance_threshold=concordance_threshold,
            discordance_threshold=discordance_threshold
        )
    
    def sensitivity_analysis_thresholds(
        self,
        decision_matrix: np.ndarray,
        weights: np.ndarray,
        criterion_types: List[CriterionType],
        concordance_range: Tuple[float, float] = (0.5, 0.9),
        discordance_range: Tuple[float, float] = (0.1, 0.5),
        n_steps: int = 10
    ) -> Dict[str, any]:
        """
        Perform sensitivity analysis by varying thresholds.
        
        Args:
            decision_matrix: Decision matrix
            weights: Criterion weights
            criterion_types: Criterion types
            concordance_range: Range of concordance thresholds to test
            discordance_range: Range of discordance thresholds to test
            n_steps: Number of steps for each threshold
            
        Returns:
            Dictionary with threshold combinations and corresponding results
        """
        concordance_values = np.linspace(
            concordance_range[0],
            concordance_range[1],
            n_steps
        )
        discordance_values = np.linspace(
            discordance_range[0],
            discordance_range[1],
            n_steps
        )
        
        # Pre-calculate concordance and discordance matrices
        concordance_matrix = self.calculate_concordance_matrix(
            decision_matrix,
            weights,
            criterion_types
        )
        discordance_matrix = self.calculate_discordance_matrix(
            decision_matrix,
            criterion_types
        )
        
        results = {
            'concordance_thresholds': [],
            'discordance_thresholds': [],
            'kernel_sizes': [],
            'rankings': []
        }
        
        for c_thresh in concordance_values:
            for d_thresh in discordance_values:
                # Calculate outranking with these thresholds
                outranking = self.calculate_outranking_matrix(
                    concordance_matrix,
                    discordance_matrix,
                    c_thresh,
                    d_thresh
                )
                
                # Find kernel
                kernel, _ = self.find_kernel(outranking)
                
                # Create ranking
                ranking = self.create_ranking(outranking)
                
                results['concordance_thresholds'].append(c_thresh)
                results['discordance_thresholds'].append(d_thresh)
                results['kernel_sizes'].append(len(kernel))
                results['rankings'].append(ranking)
                
        return results
    
    def compare_alternatives(
        self,
        result: ELECTREResult,
        alternative_names: Optional[List[str]] = None
    ) -> Dict[str, any]:
        """
        Generate detailed comparison of alternatives.
        
        Args:
            result: ELECTRE result
            alternative_names: Optional names for alternatives
            
        Returns:
            Dictionary with comparison details
        """
        m = result.concordance_matrix.shape[0]
        
        if alternative_names is None:
            alternative_names = [f"Alternative {i+1}" for i in range(m)]
            
        # Calculate net dominance scores
        net_dominance = self.calculate_net_dominance_score(result.outranking_matrix)
        
        comparison = {
            'ranking': [],
            'kernel_alternatives': [],
            'dominated_alternatives': [],
            'pairwise_outranking': {}
        }
        
        # Build ranking details
        for rank, idx in enumerate(result.ranking, 1):
            comparison['ranking'].append({
                'rank': rank,
                'name': alternative_names[idx],
                'index': idx,
                'net_dominance': int(net_dominance[idx]),
                'in_kernel': idx in result.kernel
            })
            
        # Kernel alternatives
        comparison['kernel_alternatives'] = [
            alternative_names[idx] for idx in sorted(result.kernel)
        ]
        
        # Dominated alternatives
        comparison['dominated_alternatives'] = [
            alternative_names[idx] for idx in sorted(result.dominated)
        ]
        
        # Pairwise outranking relationships
        for i in range(m):
            for j in range(m):
                if i != j and result.outranking_matrix[i, j] == 1:
                    key = f"{alternative_names[i]} > {alternative_names[j]}"
                    comparison['pairwise_outranking'][key] = {
                        'concordance': float(result.concordance_matrix[i, j]),
                        'discordance': float(result.discordance_matrix[i, j])
                    }
                    
        return comparison


def calculate_threshold_from_data(
    concordance_matrix: np.ndarray,
    percentile: float = 75.0
) -> float:
    """
    Calculate concordance threshold based on data distribution.
    
    Args:
        concordance_matrix: Concordance matrix
        percentile: Percentile to use (default: 75th percentile)
        
    Returns:
        Suggested concordance threshold
    """
    # Get upper triangle (excluding diagonal)
    m = concordance_matrix.shape[0]
    values = []
    for i in range(m):
        for j in range(m):
            if i != j:
                values.append(concordance_matrix[i, j])
                
    return np.percentile(values, percentile)
