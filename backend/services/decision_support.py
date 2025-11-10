"""
Decision Support Service
TOPSIS and AHP algorithms for multi-criteria decision making
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from scipy.linalg import eig
import warnings
warnings.filterwarnings('ignore')


class TOPSISService:
    """TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)"""
    
    @staticmethod
    def calculate_topsis(df: pd.DataFrame, criteria_weights: Dict[str, float],
                        benefit_criteria: List[str] = None) -> pd.DataFrame:
        """
        Calculate TOPSIS scores for alternatives
        
        Parameters:
        -----------
        df : DataFrame with alternatives as rows, criteria as columns
        criteria_weights : Dictionary of {criterion: weight}
        benefit_criteria : List of criteria that are beneficial (higher is better)
                         If None, all criteria are assumed to be beneficial
        """
        # Extract criteria columns
        criteria_cols = list(criteria_weights.keys())
        alternatives = df.index.tolist() if df.index.name else df.iloc[:, 0].tolist()
        
        # Create decision matrix
        decision_matrix = df[criteria_cols].values
        
        # Normalize decision matrix
        normalized_matrix = decision_matrix / np.sqrt(np.sum(decision_matrix**2, axis=0))
        
        # Apply weights
        weights = np.array([criteria_weights[col] for col in criteria_cols])
        weighted_matrix = normalized_matrix * weights
        
        # Determine ideal and negative ideal solutions
        if benefit_criteria is None:
            benefit_criteria = criteria_cols
        
        ideal_positive = []
        ideal_negative = []
        
        for i, col in enumerate(criteria_cols):
            if col in benefit_criteria:
                ideal_positive.append(np.max(weighted_matrix[:, i]))
                ideal_negative.append(np.min(weighted_matrix[:, i]))
            else:
                ideal_positive.append(np.min(weighted_matrix[:, i]))
                ideal_negative.append(np.max(weighted_matrix[:, i]))
        
        ideal_positive = np.array(ideal_positive)
        ideal_negative = np.array(ideal_negative)
        
        # Calculate distances
        distances_positive = np.sqrt(np.sum((weighted_matrix - ideal_positive)**2, axis=1))
        distances_negative = np.sqrt(np.sum((weighted_matrix - ideal_negative)**2, axis=1))
        
        # Calculate TOPSIS scores
        topsis_scores = distances_negative / (distances_positive + distances_negative)
        
        # Create results DataFrame
        results = pd.DataFrame({
            'alternative': alternatives,
            'topsis_score': topsis_scores,
            'distance_positive': distances_positive,
            'distance_negative': distances_negative
        })
        
        results = results.sort_values('topsis_score', ascending=False)
        results['rank'] = range(1, len(results) + 1)
        
        return results


class AHPService:
    """AHP (Analytic Hierarchy Process)"""
    
    @staticmethod
    def create_pairwise_matrix(criteria: List[str], comparisons: Dict[Tuple[str, str], float]) -> np.ndarray:
        """
        Create pairwise comparison matrix from comparisons dictionary
        
        Parameters:
        -----------
        criteria : List of criteria names
        comparisons : Dictionary of {(criterion1, criterion2): value}
                     where value is the relative importance (1-9 scale)
        """
        n = len(criteria)
        matrix = np.ones((n, n))
        
        # Fill matrix with comparisons
        for (c1, c2), value in comparisons.items():
            i = criteria.index(c1)
            j = criteria.index(c2)
            matrix[i, j] = value
            matrix[j, i] = 1 / value
        
        return matrix
    
    @staticmethod
    def calculate_priority_vector(matrix: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Calculate priority vector and consistency ratio
        
        Returns:
        --------
        priority_vector : Normalized priority vector
        consistency_ratio : CR value (should be < 0.1 for consistency)
        """
        # Calculate eigenvalues and eigenvectors
        eigenvalues, eigenvectors = eig(matrix)
        
        # Get principal eigenvector (largest eigenvalue)
        max_eigenvalue_idx = np.argmax(eigenvalues.real)
        principal_eigenvector = eigenvectors[:, max_eigenvalue_idx].real
        
        # Normalize to get priority vector
        priority_vector = principal_eigenvector / np.sum(principal_eigenvector)
        
        # Calculate consistency ratio
        max_eigenvalue = eigenvalues[max_eigenvalue_idx].real
        n = matrix.shape[0]
        
        # Random Index (RI) values for different matrix sizes
        ri_values = {
            1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12,
            6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49
        }
        
        ci = (max_eigenvalue - n) / (n - 1)
        ri = ri_values.get(n, 1.49)
        cr = ci / ri if ri > 0 else 0
        
        return priority_vector, cr
    
    @staticmethod
    def calculate_ahp_weights(criteria: List[str], 
                             comparisons: Dict[Tuple[str, str], float]) -> Dict[str, float]:
        """
        Calculate AHP weights for criteria
        
        Returns:
        --------
        weights : Dictionary of {criterion: weight}
        consistency_ratio : CR value
        """
        matrix = AHPService.create_pairwise_matrix(criteria, comparisons)
        priority_vector, cr = AHPService.calculate_priority_vector(matrix)
        
        weights = {criteria[i]: float(priority_vector[i]) for i in range(len(criteria))}
        
        return weights, cr
    
    @staticmethod
    def rank_alternatives(df: pd.DataFrame, criteria_weights: Dict[str, float]) -> pd.DataFrame:
        """
        Rank alternatives using AHP weights
        
        Parameters:
        -----------
        df : DataFrame with alternatives as rows, criteria as columns
        criteria_weights : Dictionary of {criterion: weight} from AHP
        """
        criteria_cols = list(criteria_weights.keys())
        alternatives = df.index.tolist() if df.index.name else df.iloc[:, 0].tolist()
        
        # Normalize each criterion column
        normalized_df = df[criteria_cols].copy()
        for col in criteria_cols:
            col_sum = normalized_df[col].sum()
            if col_sum > 0:
                normalized_df[col] = normalized_df[col] / col_sum
        
        # Calculate weighted scores
        scores = np.zeros(len(alternatives))
        for i, col in enumerate(criteria_cols):
            scores += normalized_df[col].values * criteria_weights[col]
        
        # Create results DataFrame
        results = pd.DataFrame({
            'alternative': alternatives,
            'ahp_score': scores
        })
        
        results = results.sort_values('ahp_score', ascending=False)
        results['rank'] = range(1, len(results) + 1)
        
        return results


class DecisionSupportService:
    """Main service for decision support combining TOPSIS and AHP"""
    
    def __init__(self):
        self.topsis = TOPSISService()
        self.ahp = AHPService()
    
    def topsis_ranking(self, supplier_data: pd.DataFrame,
                      criteria_weights: Dict[str, float],
                      benefit_criteria: Optional[List[str]] = None) -> pd.DataFrame:
        """Perform TOPSIS ranking"""
        return self.topsis.calculate_topsis(supplier_data, criteria_weights, benefit_criteria)
    
    def ahp_ranking(self, supplier_data: pd.DataFrame,
                   criteria: List[str],
                   pairwise_comparisons: Dict[Tuple[str, str], float]) -> Tuple[pd.DataFrame, float]:
        """
        Perform AHP ranking
        
        Returns:
        --------
        ranking_df : DataFrame with rankings
        consistency_ratio : CR value
        """
        weights, cr = self.ahp.calculate_ahp_weights(criteria, pairwise_comparisons)
        ranking = self.ahp.rank_alternatives(supplier_data, weights)
        
        return ranking, cr
    
    def compare_methods(self, supplier_data: pd.DataFrame,
                       criteria_weights: Dict[str, float],
                       criteria: List[str],
                       pairwise_comparisons: Dict[Tuple[str, str], float]) -> pd.DataFrame:
        """
        Compare TOPSIS and AHP rankings
        """
        topsis_results = self.topsis_ranking(supplier_data, criteria_weights)
        ahp_results, cr = self.ahp_ranking(supplier_data, criteria, pairwise_comparisons)
        
        comparison = pd.merge(
            topsis_results[['alternative', 'topsis_score', 'rank']],
            ahp_results[['alternative', 'ahp_score', 'rank']],
            on='alternative',
            suffixes=('_topsis', '_ahp')
        )
        
        comparison['rank_difference'] = abs(comparison['rank_topsis'] - comparison['rank_ahp'])
        comparison['avg_rank'] = (comparison['rank_topsis'] + comparison['rank_ahp']) / 2
        
        return comparison.sort_values('avg_rank'), cr


# Global instance
decision_support_service = DecisionSupportService()

