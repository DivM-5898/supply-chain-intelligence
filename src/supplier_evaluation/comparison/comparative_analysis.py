"""
Comparative Analysis Tools
Provides tools for comparing suppliers, ranking, and gap analysis.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ComparisonMethod(Enum):
    """Methods for supplier comparison."""
    ABSOLUTE = "absolute"
    RELATIVE = "relative"
    PERCENTILE = "percentile"
    Z_SCORE = "z_score"


class RankingMethod(Enum):
    """Methods for ranking suppliers."""
    SIMPLE = "simple"  # Direct score ranking
    BORDA = "borda"  # Borda count
    CONDORCET = "condorcet"  # Pairwise comparison
    PARETO = "pareto"  # Pareto efficiency


@dataclass
class SupplierComparison:
    """Results of supplier comparison."""
    supplier_1_id: str
    supplier_2_id: str
    comparison_metrics: Dict[str, Dict[str, float]]
    overall_difference: float
    winner: Optional[str]
    confidence_score: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'supplier_1_id': self.supplier_1_id,
            'supplier_2_id': self.supplier_2_id,
            'comparison_metrics': self.comparison_metrics,
            'overall_difference': self.overall_difference,
            'winner': self.winner,
            'confidence_score': self.confidence_score,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class GapAnalysis:
    """Gap analysis between supplier and benchmark."""
    supplier_id: str
    benchmark_name: str
    gaps: Dict[str, float]
    critical_gaps: List[str]
    improvement_priority: List[Tuple[str, float]]
    overall_gap_score: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'supplier_id': self.supplier_id,
            'benchmark_name': self.benchmark_name,
            'gaps': self.gaps,
            'critical_gaps': self.critical_gaps,
            'improvement_priority': self.improvement_priority,
            'overall_gap_score': self.overall_gap_score,
            'timestamp': self.timestamp.isoformat()
        }


class SupplierComparator:
    """
    Compares suppliers across multiple dimensions.
    """
    
    def __init__(self, comparison_method: ComparisonMethod = ComparisonMethod.ABSOLUTE):
        """
        Initialize comparator.
        
        Args:
            comparison_method: Method for comparison
        """
        self.comparison_method = comparison_method
    
    def compare_two_suppliers(
        self,
        supplier_1_id: str,
        supplier_1_scores: Dict[str, float],
        supplier_2_id: str,
        supplier_2_scores: Dict[str, float],
        weights: Optional[Dict[str, float]] = None
    ) -> SupplierComparison:
        """
        Compare two suppliers.
        
        Args:
            supplier_1_id: First supplier ID
            supplier_1_scores: First supplier's scores
            supplier_2_id: Second supplier ID
            supplier_2_scores: Second supplier's scores
            weights: Optional weights for metrics
            
        Returns:
            SupplierComparison object
        """
        # Get common metrics
        common_metrics = set(supplier_1_scores.keys()) & set(supplier_2_scores.keys())
        
        if not common_metrics:
            raise ValueError("No common metrics found between suppliers")
        
        comparison_metrics = {}
        differences = []
        
        for metric in common_metrics:
            score_1 = supplier_1_scores[metric]
            score_2 = supplier_2_scores[metric]
            
            if self.comparison_method == ComparisonMethod.ABSOLUTE:
                diff = score_1 - score_2
            elif self.comparison_method == ComparisonMethod.RELATIVE:
                diff = ((score_1 - score_2) / max(score_2, 0.01)) * 100
            elif self.comparison_method == ComparisonMethod.PERCENTILE:
                # Assume scores are already percentile-based
                diff = score_1 - score_2
            else:
                diff = score_1 - score_2
            
            comparison_metrics[metric] = {
                'supplier_1': score_1,
                'supplier_2': score_2,
                'difference': diff,
                'percentage_diff': ((score_1 - score_2) / max(score_2, 0.01)) * 100
            }
            
            weight = weights.get(metric, 1.0) if weights else 1.0
            differences.append(diff * weight)
        
        # Calculate overall difference
        overall_diff = np.mean(differences)
        
        # Determine winner
        if abs(overall_diff) < 1.0:  # Threshold for tie
            winner = None
            confidence = 0.5
        elif overall_diff > 0:
            winner = supplier_1_id
            confidence = min(0.5 + abs(overall_diff) / 100, 1.0)
        else:
            winner = supplier_2_id
            confidence = min(0.5 + abs(overall_diff) / 100, 1.0)
        
        return SupplierComparison(
            supplier_1_id=supplier_1_id,
            supplier_2_id=supplier_2_id,
            comparison_metrics=comparison_metrics,
            overall_difference=round(overall_diff, 2),
            winner=winner,
            confidence_score=round(confidence, 2)
        )
    
    def compare_multiple_suppliers(
        self,
        suppliers_data: Dict[str, Dict[str, float]],
        reference_supplier_id: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Compare multiple suppliers.
        
        Args:
            suppliers_data: Dictionary of supplier_id -> {metric -> score}
            reference_supplier_id: Optional reference supplier for comparison
            
        Returns:
            DataFrame with comparison results
        """
        # Create DataFrame from suppliers data
        df = pd.DataFrame(suppliers_data).T
        
        if reference_supplier_id and reference_supplier_id in suppliers_data:
            # Calculate differences from reference
            ref_scores = suppliers_data[reference_supplier_id]
            
            for metric in df.columns:
                df[f'{metric}_diff'] = df[metric] - ref_scores.get(metric, 0)
                df[f'{metric}_pct_diff'] = ((df[metric] - ref_scores.get(metric, 0)) / 
                                            max(ref_scores.get(metric, 0.01), 0.01)) * 100
        
        return df
    
    def create_comparison_matrix(
        self,
        suppliers_data: Dict[str, Dict[str, float]],
        metric: str
    ) -> pd.DataFrame:
        """
        Create pairwise comparison matrix for a specific metric.
        
        Args:
            suppliers_data: Dictionary of supplier_id -> {metric -> score}
            metric: Metric to compare
            
        Returns:
            DataFrame with pairwise comparisons
        """
        supplier_ids = list(suppliers_data.keys())
        n = len(supplier_ids)
        
        matrix = np.zeros((n, n))
        
        for i, supplier_i in enumerate(supplier_ids):
            for j, supplier_j in enumerate(supplier_ids):
                if i == j:
                    matrix[i, j] = 0
                else:
                    score_i = suppliers_data[supplier_i].get(metric, 0)
                    score_j = suppliers_data[supplier_j].get(metric, 0)
                    matrix[i, j] = score_i - score_j
        
        return pd.DataFrame(matrix, index=supplier_ids, columns=supplier_ids)


class SupplierRanker:
    """
    Ranks suppliers using various methods.
    """
    
    def __init__(self, ranking_method: RankingMethod = RankingMethod.SIMPLE):
        """
        Initialize ranker.
        
        Args:
            ranking_method: Method for ranking
        """
        self.ranking_method = ranking_method
    
    def rank_suppliers(
        self,
        suppliers_scores: Dict[str, float]
    ) -> List[Tuple[str, float, int]]:
        """
        Rank suppliers based on overall scores.
        
        Args:
            suppliers_scores: Dictionary of supplier_id -> overall_score
            
        Returns:
            List of (supplier_id, score, rank) tuples, sorted by rank
        """
        # Sort by score descending
        sorted_suppliers = sorted(
            suppliers_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Assign ranks (handle ties)
        ranked = []
        prev_score = None
        prev_rank = 0
        
        for idx, (supplier_id, score) in enumerate(sorted_suppliers, 1):
            if score == prev_score:
                rank = prev_rank
            else:
                rank = idx
                prev_rank = rank
            
            ranked.append((supplier_id, score, rank))
            prev_score = score
        
        return ranked
    
    def borda_count_ranking(
        self,
        suppliers_criteria_scores: Dict[str, Dict[str, float]]
    ) -> List[Tuple[str, int, int]]:
        """
        Rank suppliers using Borda count method.
        
        Args:
            suppliers_criteria_scores: Dictionary of supplier_id -> {criterion -> score}
            
        Returns:
            List of (supplier_id, borda_count, rank) tuples
        """
        supplier_ids = list(suppliers_criteria_scores.keys())
        criteria = list(next(iter(suppliers_criteria_scores.values())).keys())
        
        borda_counts = {sid: 0 for sid in supplier_ids}
        
        # For each criterion, rank suppliers and assign Borda points
        for criterion in criteria:
            # Get scores for this criterion
            criterion_scores = {
                sid: scores.get(criterion, 0)
                for sid, scores in suppliers_criteria_scores.items()
            }
            
            # Rank for this criterion
            ranked = self.rank_suppliers(criterion_scores)
            n = len(ranked)
            
            # Assign Borda points (n-rank)
            for supplier_id, _, rank in ranked:
                borda_counts[supplier_id] += (n - rank)
        
        # Final ranking based on Borda counts
        sorted_borda = sorted(
            borda_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        ranked = []
        for idx, (supplier_id, count) in enumerate(sorted_borda, 1):
            ranked.append((supplier_id, count, idx))
        
        return ranked
    
    def pareto_frontier(
        self,
        suppliers_data: Dict[str, List[float]],
        maximize_all: bool = True
    ) -> List[str]:
        """
        Find Pareto-efficient suppliers.
        
        Args:
            suppliers_data: Dictionary of supplier_id -> [metric_values]
            maximize_all: If True, all metrics are maximized. If False, minimized.
            
        Returns:
            List of Pareto-efficient supplier IDs
        """
        supplier_ids = list(suppliers_data.keys())
        scores_array = np.array([suppliers_data[sid] for sid in supplier_ids])
        
        if not maximize_all:
            scores_array = -scores_array
        
        pareto_efficient = []
        
        for i, scores_i in enumerate(scores_array):
            is_dominated = False
            
            for j, scores_j in enumerate(scores_array):
                if i != j:
                    # Check if j dominates i
                    if np.all(scores_j >= scores_i) and np.any(scores_j > scores_i):
                        is_dominated = True
                        break
            
            if not is_dominated:
                pareto_efficient.append(supplier_ids[i])
        
        return pareto_efficient
    
    def create_ranking_dataframe(
        self,
        suppliers_criteria_scores: Dict[str, Dict[str, float]],
        overall_scores: Dict[str, float]
    ) -> pd.DataFrame:
        """
        Create comprehensive ranking DataFrame.
        
        Args:
            suppliers_criteria_scores: Dictionary of supplier_id -> {criterion -> score}
            overall_scores: Dictionary of supplier_id -> overall_score
            
        Returns:
            DataFrame with rankings and scores
        """
        # Simple ranking
        simple_ranks = self.rank_suppliers(overall_scores)
        
        # Borda count ranking
        borda_ranks = self.borda_count_ranking(suppliers_criteria_scores)
        
        # Create DataFrame
        data = []
        
        for supplier_id in suppliers_criteria_scores.keys():
            # Find ranks
            simple_rank = next((r for sid, s, r in simple_ranks if sid == supplier_id), None)
            borda_count = next((c for sid, c, r in borda_ranks if sid == supplier_id), 0)
            borda_rank = next((r for sid, c, r in borda_ranks if sid == supplier_id), None)
            
            row = {
                'supplier_id': supplier_id,
                'overall_score': overall_scores[supplier_id],
                'simple_rank': simple_rank,
                'borda_count': borda_count,
                'borda_rank': borda_rank,
                **suppliers_criteria_scores[supplier_id]
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        df = df.sort_values('simple_rank')
        
        return df


class GapAnalyzer:
    """
    Performs gap analysis between suppliers and benchmarks.
    """
    
    def __init__(self, critical_gap_threshold: float = 15.0):
        """
        Initialize gap analyzer.
        
        Args:
            critical_gap_threshold: Threshold for identifying critical gaps
        """
        self.critical_gap_threshold = critical_gap_threshold
    
    def analyze_gap(
        self,
        supplier_id: str,
        supplier_scores: Dict[str, float],
        benchmark_scores: Dict[str, float],
        benchmark_name: str = "Industry Average"
    ) -> GapAnalysis:
        """
        Analyze gaps between supplier and benchmark.
        
        Args:
            supplier_id: Supplier identifier
            supplier_scores: Supplier's scores
            benchmark_scores: Benchmark scores
            benchmark_name: Name of benchmark
            
        Returns:
            GapAnalysis object
        """
        common_metrics = set(supplier_scores.keys()) & set(benchmark_scores.keys())
        
        gaps = {}
        critical_gaps = []
        
        for metric in common_metrics:
            gap = benchmark_scores[metric] - supplier_scores[metric]
            gaps[metric] = round(gap, 2)
            
            if abs(gap) >= self.critical_gap_threshold:
                critical_gaps.append(metric)
        
        # Calculate improvement priority (largest gaps first)
        improvement_priority = sorted(
            [(metric, gap) for metric, gap in gaps.items()],
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        # Overall gap score (average absolute gap)
        overall_gap = np.mean([abs(g) for g in gaps.values()]) if gaps else 0.0
        
        return GapAnalysis(
            supplier_id=supplier_id,
            benchmark_name=benchmark_name,
            gaps=gaps,
            critical_gaps=critical_gaps,
            improvement_priority=improvement_priority,
            overall_gap_score=round(overall_gap, 2)
        )
    
    def benchmark_against_best(
        self,
        target_supplier_id: str,
        suppliers_data: Dict[str, Dict[str, float]]
    ) -> GapAnalysis:
        """
        Benchmark supplier against best performers.
        
        Args:
            target_supplier_id: Target supplier to analyze
            suppliers_data: Dictionary of all suppliers' data
            
        Returns:
            GapAnalysis object
        """
        if target_supplier_id not in suppliers_data:
            raise ValueError(f"Supplier {target_supplier_id} not found")
        
        target_scores = suppliers_data[target_supplier_id]
        
        # Find best score for each metric
        best_scores = {}
        metrics = target_scores.keys()
        
        for metric in metrics:
            best_score = max(
                scores.get(metric, 0)
                for scores in suppliers_data.values()
            )
            best_scores[metric] = best_score
        
        return self.analyze_gap(
            supplier_id=target_supplier_id,
            supplier_scores=target_scores,
            benchmark_scores=best_scores,
            benchmark_name="Best in Class"
        )
    
    def create_gap_matrix(
        self,
        suppliers_data: Dict[str, Dict[str, float]],
        benchmark_scores: Dict[str, float]
    ) -> pd.DataFrame:
        """
        Create gap matrix for multiple suppliers.
        
        Args:
            suppliers_data: Dictionary of supplier_id -> {metric -> score}
            benchmark_scores: Benchmark scores
            
        Returns:
            DataFrame with gap analysis
        """
        data = []
        
        for supplier_id, scores in suppliers_data.items():
            row = {'supplier_id': supplier_id}
            
            for metric in scores.keys():
                if metric in benchmark_scores:
                    gap = benchmark_scores[metric] - scores[metric]
                    row[f'{metric}_gap'] = round(gap, 2)
                    row[f'{metric}_score'] = scores[metric]
            
            data.append(row)
        
        return pd.DataFrame(data)


class PerformanceTrendAnalyzer:
    """
    Analyzes performance trends over time.
    """
    
    @staticmethod
    def calculate_trend(
        time_series_scores: List[Tuple[datetime, float]]
    ) -> Dict[str, Any]:
        """
        Calculate trend from time series data.
        
        Args:
            time_series_scores: List of (timestamp, score) tuples
            
        Returns:
            Dictionary with trend metrics
        """
        if len(time_series_scores) < 2:
            return {
                'trend': 'insufficient_data',
                'slope': 0.0,
                'direction': 'stable',
                'volatility': 0.0
            }
        
        # Sort by time
        sorted_data = sorted(time_series_scores, key=lambda x: x[0])
        
        # Extract scores
        scores = np.array([s for t, s in sorted_data])
        
        # Calculate simple linear trend
        x = np.arange(len(scores))
        coefficients = np.polyfit(x, scores, 1)
        slope = coefficients[0]
        
        # Determine direction
        if abs(slope) < 0.1:
            direction = 'stable'
        elif slope > 0:
            direction = 'improving'
        else:
            direction = 'declining'
        
        # Calculate volatility (standard deviation)
        volatility = np.std(scores)
        
        # Calculate percentage change
        pct_change = ((scores[-1] - scores[0]) / scores[0] * 100) if scores[0] != 0 else 0
        
        return {
            'trend': direction,
            'slope': round(float(slope), 4),
            'direction': direction,
            'volatility': round(float(volatility), 2),
            'percent_change': round(float(pct_change), 2),
            'start_score': round(float(scores[0]), 2),
            'end_score': round(float(scores[-1]), 2)
        }
    
    @staticmethod
    def forecast_next_score(
        time_series_scores: List[Tuple[datetime, float]],
        periods_ahead: int = 1
    ) -> List[float]:
        """
        Simple linear forecast of future scores.
        
        Args:
            time_series_scores: List of (timestamp, score) tuples
            periods_ahead: Number of periods to forecast
            
        Returns:
            List of forecasted scores
        """
        if len(time_series_scores) < 2:
            # Return last score if insufficient data
            if time_series_scores:
                return [time_series_scores[-1][1]] * periods_ahead
            return [0.0] * periods_ahead
        
        # Sort by time
        sorted_data = sorted(time_series_scores, key=lambda x: x[0])
        scores = np.array([s for t, s in sorted_data])
        
        # Fit linear model
        x = np.arange(len(scores))
        coefficients = np.polyfit(x, scores, 1)
        
        # Forecast
        forecast_x = np.arange(len(scores), len(scores) + periods_ahead)
        forecasted = np.polyval(coefficients, forecast_x)
        
        # Clip to reasonable range [0, 100]
        forecasted = np.clip(forecasted, 0, 100)
        
        return forecasted.tolist()
