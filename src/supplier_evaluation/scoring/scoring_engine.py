"""
Supplier Scoring Engine
Advanced scoring algorithms and methodologies for supplier evaluation.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class NormalizationMethod(Enum):
    """Methods for normalizing scores."""
    MIN_MAX = "min_max"
    Z_SCORE = "z_score"
    DECIMAL_SCALING = "decimal_scaling"
    VECTOR = "vector"
    MAX_SCALING = "max_scaling"


class AggregationMethod(Enum):
    """Methods for aggregating scores."""
    WEIGHTED_SUM = "weighted_sum"
    WEIGHTED_PRODUCT = "weighted_product"
    GEOMETRIC_MEAN = "geometric_mean"
    HARMONIC_MEAN = "harmonic_mean"


@dataclass
class ScoringCriteria:
    """Definition of a scoring criterion."""
    criterion_id: str
    name: str
    weight: float
    min_value: float = 0.0
    max_value: float = 100.0
    target_value: Optional[float] = None
    is_benefit: bool = True  # True if higher is better, False if lower is better
    threshold_min: Optional[float] = None  # Minimum acceptable value
    threshold_max: Optional[float] = None  # Maximum acceptable value
    
    def normalize_weight(self, total_weight: float) -> float:
        """Normalize weight to sum to 1."""
        return self.weight / total_weight if total_weight > 0 else 0.0


@dataclass
class SupplierScore:
    """Complete supplier score with breakdown."""
    supplier_id: str
    overall_score: float
    category_scores: Dict[str, float]
    weighted_scores: Dict[str, float]
    raw_scores: Dict[str, float]
    rank: Optional[int] = None
    percentile: Optional[float] = None
    tier: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'supplier_id': self.supplier_id,
            'overall_score': self.overall_score,
            'category_scores': self.category_scores,
            'weighted_scores': self.weighted_scores,
            'raw_scores': self.raw_scores,
            'rank': self.rank,
            'percentile': self.percentile,
            'tier': self.tier,
            'timestamp': self.timestamp.isoformat()
        }


class ScoreNormalizer:
    """
    Normalizes scores using various methods.
    """
    
    @staticmethod
    def min_max_normalization(
        values: np.ndarray,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
        target_min: float = 0.0,
        target_max: float = 100.0
    ) -> np.ndarray:
        """
        Min-Max normalization to scale values to target range.
        
        Args:
            values: Array of values to normalize
            min_val: Minimum value for normalization (if None, uses data min)
            max_val: Maximum value for normalization (if None, uses data max)
            target_min: Target minimum value
            target_max: Target maximum value
            
        Returns:
            Normalized array
        """
        values = np.array(values, dtype=float)
        
        if min_val is None:
            min_val = np.min(values)
        if max_val is None:
            max_val = np.max(values)
        
        if max_val == min_val:
            return np.full_like(values, (target_min + target_max) / 2)
        
        normalized = (values - min_val) / (max_val - min_val)
        scaled = normalized * (target_max - target_min) + target_min
        
        return np.clip(scaled, target_min, target_max)
    
    @staticmethod
    def z_score_normalization(
        values: np.ndarray,
        mean: Optional[float] = None,
        std: Optional[float] = None
    ) -> np.ndarray:
        """
        Z-score normalization (standardization).
        
        Args:
            values: Array of values to normalize
            mean: Mean for normalization (if None, uses data mean)
            std: Standard deviation (if None, uses data std)
            
        Returns:
            Normalized array
        """
        values = np.array(values, dtype=float)
        
        if mean is None:
            mean = np.mean(values)
        if std is None:
            std = np.std(values)
        
        if std == 0:
            return np.zeros_like(values)
        
        return (values - mean) / std
    
    @staticmethod
    def decimal_scaling(values: np.ndarray) -> np.ndarray:
        """
        Decimal scaling normalization.
        
        Args:
            values: Array of values to normalize
            
        Returns:
            Normalized array
        """
        values = np.array(values, dtype=float)
        max_abs = np.max(np.abs(values))
        
        if max_abs == 0:
            return values
        
        j = int(np.ceil(np.log10(max_abs)))
        return values / (10 ** j)
    
    @staticmethod
    def vector_normalization(values: np.ndarray) -> np.ndarray:
        """
        Vector (L2) normalization.
        
        Args:
            values: Array of values to normalize
            
        Returns:
            Normalized array
        """
        values = np.array(values, dtype=float)
        norm = np.linalg.norm(values)
        
        if norm == 0:
            return values
        
        return values / norm
    
    @staticmethod
    def max_scaling(
        values: np.ndarray,
        target_max: float = 100.0
    ) -> np.ndarray:
        """
        Scale values by maximum value.
        
        Args:
            values: Array of values to normalize
            target_max: Target maximum value
            
        Returns:
            Normalized array
        """
        values = np.array(values, dtype=float)
        max_val = np.max(values)
        
        if max_val == 0:
            return values
        
        return (values / max_val) * target_max


class ScoringEngine:
    """
    Main scoring engine for supplier evaluation.
    """
    
    def __init__(
        self,
        criteria: List[ScoringCriteria],
        normalization_method: NormalizationMethod = NormalizationMethod.MIN_MAX,
        aggregation_method: AggregationMethod = AggregationMethod.WEIGHTED_SUM
    ):
        """
        Initialize scoring engine.
        
        Args:
            criteria: List of scoring criteria
            normalization_method: Method for normalizing scores
            aggregation_method: Method for aggregating scores
        """
        self.criteria = criteria
        self.normalization_method = normalization_method
        self.aggregation_method = aggregation_method
        self.normalizer = ScoreNormalizer()
        
        # Normalize weights
        total_weight = sum(c.weight for c in criteria)
        for criterion in self.criteria:
            criterion.weight = criterion.normalize_weight(total_weight)
    
    def normalize_scores(
        self,
        scores: Dict[str, float],
        is_benefit: Dict[str, bool]
    ) -> Dict[str, float]:
        """
        Normalize scores based on selected method.
        
        Args:
            scores: Dictionary of criterion_id -> raw score
            is_benefit: Dictionary of criterion_id -> is_benefit flag
            
        Returns:
            Normalized scores
        """
        if not scores:
            return {}
        
        normalized = {}
        
        for criterion_id, score in scores.items():
            # Handle cost criteria (inverse)
            if not is_benefit.get(criterion_id, True):
                score = 100 - score
            
            normalized[criterion_id] = score
        
        return normalized
    
    def aggregate_scores(
        self,
        normalized_scores: Dict[str, float],
        weights: Dict[str, float]
    ) -> float:
        """
        Aggregate normalized scores using selected method.
        
        Args:
            normalized_scores: Dictionary of normalized scores
            weights: Dictionary of weights
            
        Returns:
            Aggregated score
        """
        if not normalized_scores:
            return 0.0
        
        if self.aggregation_method == AggregationMethod.WEIGHTED_SUM:
            return self._weighted_sum(normalized_scores, weights)
        elif self.aggregation_method == AggregationMethod.WEIGHTED_PRODUCT:
            return self._weighted_product(normalized_scores, weights)
        elif self.aggregation_method == AggregationMethod.GEOMETRIC_MEAN:
            return self._geometric_mean(normalized_scores, weights)
        elif self.aggregation_method == AggregationMethod.HARMONIC_MEAN:
            return self._harmonic_mean(normalized_scores, weights)
        else:
            return self._weighted_sum(normalized_scores, weights)
    
    def _weighted_sum(
        self,
        scores: Dict[str, float],
        weights: Dict[str, float]
    ) -> float:
        """Weighted sum aggregation."""
        total = sum(
            scores[cid] * weights.get(cid, 0.0)
            for cid in scores.keys()
        )
        return round(total, 2)
    
    def _weighted_product(
        self,
        scores: Dict[str, float],
        weights: Dict[str, float]
    ) -> float:
        """Weighted product aggregation."""
        product = 1.0
        for cid, score in scores.items():
            weight = weights.get(cid, 0.0)
            if score > 0 and weight > 0:
                product *= (score / 100.0) ** weight
        
        return round(product * 100, 2)
    
    def _geometric_mean(
        self,
        scores: Dict[str, float],
        weights: Dict[str, float]
    ) -> float:
        """Weighted geometric mean."""
        if not scores:
            return 0.0
        
        log_sum = sum(
            weights.get(cid, 0.0) * np.log(max(score, 0.01))
            for cid, score in scores.items()
        )
        
        return round(np.exp(log_sum), 2)
    
    def _harmonic_mean(
        self,
        scores: Dict[str, float],
        weights: Dict[str, float]
    ) -> float:
        """Weighted harmonic mean."""
        if not scores:
            return 0.0
        
        denominator = sum(
            weights.get(cid, 0.0) / max(score, 0.01)
            for cid, score in scores.items()
        )
        
        if denominator == 0:
            return 0.0
        
        return round(1.0 / denominator, 2)
    
    def calculate_supplier_score(
        self,
        supplier_id: str,
        raw_scores: Dict[str, float]
    ) -> SupplierScore:
        """
        Calculate complete supplier score.
        
        Args:
            supplier_id: Supplier identifier
            raw_scores: Dictionary of criterion_id -> raw score value
            
        Returns:
            SupplierScore object
        """
        # Build is_benefit mapping
        is_benefit = {c.criterion_id: c.is_benefit for c in self.criteria}
        
        # Normalize scores
        normalized_scores = self.normalize_scores(raw_scores, is_benefit)
        
        # Build weights mapping
        weights = {c.criterion_id: c.weight for c in self.criteria}
        
        # Calculate weighted scores
        weighted_scores = {
            cid: normalized_scores[cid] * weights.get(cid, 0.0)
            for cid in normalized_scores.keys()
        }
        
        # Aggregate to overall score
        overall_score = self.aggregate_scores(normalized_scores, weights)
        
        return SupplierScore(
            supplier_id=supplier_id,
            overall_score=overall_score,
            category_scores=normalized_scores,
            weighted_scores=weighted_scores,
            raw_scores=raw_scores
        )
    
    def calculate_batch_scores(
        self,
        suppliers_data: Dict[str, Dict[str, float]]
    ) -> List[SupplierScore]:
        """
        Calculate scores for multiple suppliers.
        
        Args:
            suppliers_data: Dictionary of supplier_id -> {criterion_id -> score}
            
        Returns:
            List of SupplierScore objects
        """
        scores = []
        
        for supplier_id, raw_scores in suppliers_data.items():
            score = self.calculate_supplier_score(supplier_id, raw_scores)
            scores.append(score)
        
        # Rank suppliers
        scores.sort(key=lambda x: x.overall_score, reverse=True)
        
        for rank, score in enumerate(scores, 1):
            score.rank = rank
            score.percentile = ((len(scores) - rank + 1) / len(scores)) * 100
            
            # Assign tier
            if score.percentile >= 80:
                score.tier = "A"
            elif score.percentile >= 60:
                score.tier = "B"
            elif score.percentile >= 40:
                score.tier = "C"
            else:
                score.tier = "D"
        
        return scores
    
    def apply_threshold_filtering(
        self,
        scores: List[SupplierScore],
        threshold: float
    ) -> List[SupplierScore]:
        """
        Filter suppliers by minimum score threshold.
        
        Args:
            scores: List of supplier scores
            threshold: Minimum acceptable score
            
        Returns:
            Filtered list of scores
        """
        return [s for s in scores if s.overall_score >= threshold]
    
    def sensitivity_analysis(
        self,
        supplier_id: str,
        raw_scores: Dict[str, float],
        criterion_id: str,
        value_range: Tuple[float, float],
        num_points: int = 10
    ) -> Dict[str, List[float]]:
        """
        Perform sensitivity analysis on a specific criterion.
        
        Args:
            supplier_id: Supplier identifier
            raw_scores: Base raw scores
            criterion_id: Criterion to vary
            value_range: (min, max) range for the criterion
            num_points: Number of points to evaluate
            
        Returns:
            Dictionary with 'values' and 'scores' lists
        """
        values = np.linspace(value_range[0], value_range[1], num_points)
        scores = []
        
        for value in values:
            modified_scores = raw_scores.copy()
            modified_scores[criterion_id] = value
            
            score = self.calculate_supplier_score(supplier_id, modified_scores)
            scores.append(score.overall_score)
        
        return {
            'values': values.tolist(),
            'scores': scores
        }


class TierClassifier:
    """
    Classifies suppliers into performance tiers.
    """
    
    def __init__(
        self,
        tier_thresholds: Optional[Dict[str, float]] = None
    ):
        """
        Initialize tier classifier.
        
        Args:
            tier_thresholds: Dictionary of tier_name -> minimum_score
                            If None, uses default thresholds
        """
        if tier_thresholds is None:
            self.tier_thresholds = {
                'A+': 95.0,
                'A': 85.0,
                'B+': 75.0,
                'B': 65.0,
                'C+': 55.0,
                'C': 45.0,
                'D': 0.0
            }
        else:
            self.tier_thresholds = tier_thresholds
    
    def classify(self, score: float) -> str:
        """
        Classify a score into a tier.
        
        Args:
            score: Overall supplier score
            
        Returns:
            Tier name
        """
        sorted_tiers = sorted(
            self.tier_thresholds.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for tier_name, threshold in sorted_tiers:
            if score >= threshold:
                return tier_name
        
        return sorted_tiers[-1][0]
    
    def classify_batch(
        self,
        scores: List[SupplierScore]
    ) -> Dict[str, List[str]]:
        """
        Classify multiple suppliers.
        
        Args:
            scores: List of supplier scores
            
        Returns:
            Dictionary of tier_name -> [supplier_ids]
        """
        tiers = {tier: [] for tier in self.tier_thresholds.keys()}
        
        for score in scores:
            tier = self.classify(score.overall_score)
            score.tier = tier
            tiers[tier].append(score.supplier_id)
        
        return tiers


class CompositeScoreCalculator:
    """
    Calculates composite scores from multiple sub-scores.
    """
    
    @staticmethod
    def calculate_composite_score(
        sub_scores: Dict[str, float],
        weights: Optional[Dict[str, float]] = None,
        method: str = "weighted_average"
    ) -> float:
        """
        Calculate composite score from sub-scores.
        
        Args:
            sub_scores: Dictionary of category -> score
            weights: Dictionary of category -> weight (if None, uses equal weights)
            method: Aggregation method ('weighted_average', 'min', 'max', 'geometric')
            
        Returns:
            Composite score
        """
        if not sub_scores:
            return 0.0
        
        if weights is None:
            weights = {k: 1.0 / len(sub_scores) for k in sub_scores.keys()}
        
        # Normalize weights
        total_weight = sum(weights.values())
        normalized_weights = {k: v / total_weight for k, v in weights.items()}
        
        if method == "weighted_average":
            return sum(
                sub_scores[k] * normalized_weights.get(k, 0.0)
                for k in sub_scores.keys()
            )
        elif method == "min":
            return min(sub_scores.values())
        elif method == "max":
            return max(sub_scores.values())
        elif method == "geometric":
            product = 1.0
            for k, score in sub_scores.items():
                weight = normalized_weights.get(k, 0.0)
                if score > 0 and weight > 0:
                    product *= score ** weight
            return product
        else:
            return sum(
                sub_scores[k] * normalized_weights.get(k, 0.0)
                for k in sub_scores.keys()
            )
    
    @staticmethod
    def calculate_quality_adjusted_score(
        base_score: float,
        quality_factor: float,
        adjustment_weight: float = 0.3
    ) -> float:
        """
        Adjust score based on quality factor.
        
        Args:
            base_score: Base supplier score
            quality_factor: Quality adjustment factor (0-1)
            adjustment_weight: Weight of quality adjustment
            
        Returns:
            Adjusted score
        """
        adjusted = base_score * (1 - adjustment_weight) + \
                   (base_score * quality_factor * adjustment_weight)
        return round(adjusted, 2)
    
    @staticmethod
    def calculate_risk_adjusted_score(
        base_score: float,
        risk_score: float,
        risk_weight: float = 0.2
    ) -> float:
        """
        Adjust score based on risk.
        
        Args:
            base_score: Base supplier score
            risk_score: Risk score (0-100, higher = more risky)
            risk_weight: Weight of risk adjustment
            
        Returns:
            Risk-adjusted score
        """
        risk_penalty = (risk_score / 100.0) * risk_weight
        adjusted = base_score * (1 - risk_penalty)
        return round(adjusted, 2)
