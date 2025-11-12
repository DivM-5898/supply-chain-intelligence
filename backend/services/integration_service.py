"""
Integration Service
Connects all modules: MCDA, Supplier Evaluation, Risk Profiling, Fraud Detection, etc.
"""

import sys
import os
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from datetime import datetime, date

# Add src directory to path
backend_path = os.path.dirname(os.path.dirname(__file__))
src_path = os.path.join(os.path.dirname(backend_path), 'src')
sys.path.insert(0, src_path)
sys.path.insert(0, backend_path)

# Import MCDA modules
from mcda.algorithms.ahp import AHP
from mcda.algorithms.topsis import TOPSIS
from mcda.algorithms.electre import ELECTRE
from mcda.criteria.criteria_manager import CriteriaManager, Criterion, create_supply_chain_criteria
from mcda.scenarios.decision_matrix import DecisionMatrix, Alternative, ScenarioManager

# Import Supplier Evaluation modules
from supplier_evaluation.models.supplier import Supplier, SupplierStatus, SupplierTier
from supplier_evaluation.models.performance import (
    QualityMetrics, DeliveryMetrics, CostMetrics, ComplianceMetrics,
    FinancialStabilityMetrics, RiskMetrics, SustainabilityMetrics,
    SupplierPerformance
)
from supplier_evaluation.scoring.scoring_engine import (
    ScoringEngine, ScoringCriteria, ScoreNormalizer, TierClassifier,
    CompositeScoreCalculator, NormalizationMethod, AggregationMethod
)
from supplier_evaluation.comparison.comparative_analysis import (
    SupplierComparator, SupplierRanker, GapAnalyzer, PerformanceTrendAnalyzer,
    ComparisonMethod, RankingMethod
)


class SupplyChainIntegrationService:
    """
    Unified integration service that connects all supply chain intelligence modules.
    """
    
    def __init__(self):
        """Initialize the integration service."""
        self.criteria_manager = CriteriaManager()
        self.scenario_manager = ScenarioManager()
        
        # Initialize MCDA algorithms
        self.ahp = AHP()
        self.topsis = TOPSIS()
        self.electre = ELECTRE()
        
        # Initialize scoring and comparison tools
        self.tier_classifier = TierClassifier()
        self.comparator = SupplierComparator()
        self.ranker = SupplierRanker()
        self.gap_analyzer = GapAnalyzer()
        
        # Cache for performance data
        self.performance_cache: Dict[str, SupplierPerformance] = {}
        self.suppliers_cache: Dict[str, Supplier] = {}
    
    def evaluate_supplier_comprehensive(
        self,
        supplier_id: str,
        quality_metrics: Dict,
        delivery_metrics: Dict,
        cost_metrics: Dict,
        compliance_metrics: Dict,
        financial_metrics: Dict,
        risk_metrics: Dict,
        sustainability_metrics: Dict,
        performance_period_start: date,
        performance_period_end: date,
        custom_weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive supplier evaluation using all metric categories.
        
        Args:
            supplier_id: Supplier identifier
            quality_metrics: Quality metrics dictionary
            delivery_metrics: Delivery metrics dictionary
            cost_metrics: Cost metrics dictionary
            compliance_metrics: Compliance metrics dictionary
            financial_metrics: Financial metrics dictionary
            risk_metrics: Risk metrics dictionary
            sustainability_metrics: Sustainability metrics dictionary
            performance_period_start: Start date of evaluation period
            performance_period_end: End date of evaluation period
            custom_weights: Optional custom weights for categories
            
        Returns:
            Comprehensive evaluation results
        """
        # Create metric objects
        quality = QualityMetrics(**quality_metrics)
        delivery = DeliveryMetrics(**delivery_metrics)
        cost = CostMetrics(**cost_metrics)
        compliance = ComplianceMetrics(**compliance_metrics)
        financial = FinancialStabilityMetrics(**financial_metrics)
        risk = RiskMetrics(**risk_metrics)
        sustainability = SustainabilityMetrics(**sustainability_metrics)
        
        # Create performance profile
        performance = SupplierPerformance(
            supplier_id=supplier_id,
            performance_period_start=performance_period_start,
            performance_period_end=performance_period_end,
            quality_metrics=quality,
            delivery_metrics=delivery,
            cost_metrics=cost,
            compliance_metrics=compliance,
            financial_metrics=financial,
            risk_metrics=risk,
            sustainability_metrics=sustainability
        )
        
        # Cache performance data
        self.performance_cache[supplier_id] = performance
        
        # Calculate scores
        overall_score = performance.calculate_overall_score(custom_weights)
        category_scores = performance.get_category_scores()
        
        # Classify tier
        tier = self.tier_classifier.classify(overall_score)
        
        return {
            'supplier_id': supplier_id,
            'overall_score': overall_score,
            'tier': tier,
            'category_scores': category_scores,
            'evaluation_period': {
                'start': performance_period_start.isoformat(),
                'end': performance_period_end.isoformat()
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def mcda_supplier_selection(
        self,
        suppliers_data: Dict[str, Dict[str, float]],
        criteria: List[Dict[str, Any]],
        method: str = 'topsis',
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Perform multi-criteria decision analysis for supplier selection.
        
        Args:
            suppliers_data: Dictionary of supplier_id -> {criterion -> value}
            criteria: List of criterion definitions
            method: MCDA method ('topsis', 'ahp', 'electre')
            weights: Optional criterion weights
            
        Returns:
            MCDA analysis results with rankings
        """
        # Create criteria
        criteria_list = []
        for crit_def in criteria:
            criterion = Criterion(
                criterion_id=crit_def['id'],
                name=crit_def['name'],
                weight=weights.get(crit_def['id'], crit_def.get('weight', 1.0)) if weights else crit_def.get('weight', 1.0),
                criterion_type=crit_def.get('type', 'benefit'),
                scale_type=crit_def.get('scale', 'ratio')
            )
            criteria_list.append(criterion)
        
        self.criteria_manager.add_criteria(criteria_list)
        
        # Create decision matrix
        alternatives = []
        for supplier_id in suppliers_data.keys():
            alt = Alternative(
                id=supplier_id,
                name=supplier_id,
                description=f"Supplier {supplier_id}"
            )
            alternatives.append(alt)
        
        # Build matrix
        criterion_ids = [c.criterion_id for c in criteria_list]
        matrix_data = np.array([
            [suppliers_data[sid].get(cid, 0) for cid in criterion_ids]
            for sid in suppliers_data.keys()
        ])
        
        # Apply selected MCDA method
        if method.lower() == 'topsis':
            results = self.topsis.rank(
                matrix_data,
                [c.weight for c in criteria_list],
                [c.criterion_type == 'benefit' for c in criteria_list]
            )
            
            rankings = []
            for idx, (supplier_id, alt) in enumerate(zip(suppliers_data.keys(), alternatives)):
                rankings.append({
                    'supplier_id': supplier_id,
                    'score': float(results['closeness_coefficient'][idx]),
                    'rank': int(results['ranking'][idx])
                })
            
            return {
                'method': 'TOPSIS',
                'rankings': sorted(rankings, key=lambda x: x['rank']),
                'criteria_weights': {c.criterion_id: c.weight for c in criteria_list}
            }
        
        elif method.lower() == 'ahp':
            # For AHP, need pairwise comparisons - generate from weights
            pairwise = self.ahp.create_pairwise_matrix_from_weights(
                [c.weight for c in criteria_list]
            )
            
            results = self.ahp.calculate_priority_vector(pairwise)
            criterion_weights = results['priority_vector']
            
            # Evaluate alternatives
            ahp_results = self.ahp.evaluate_alternatives(
                matrix_data,
                criterion_weights,
                [c.criterion_type == 'benefit' for c in criteria_list]
            )
            
            rankings = []
            for idx, supplier_id in enumerate(suppliers_data.keys()):
                rankings.append({
                    'supplier_id': supplier_id,
                    'score': float(ahp_results['scores'][idx]),
                    'rank': int(ahp_results['ranking'][idx])
                })
            
            return {
                'method': 'AHP',
                'rankings': sorted(rankings, key=lambda x: x['rank']),
                'consistency_ratio': float(results['consistency_ratio']),
                'criteria_weights': {c.criterion_id: float(w) for c, w in zip(criteria_list, criterion_weights)}
            }
        
        elif method.lower() == 'electre':
            results = self.electre.rank(
                matrix_data,
                [c.weight for c in criteria_list],
                [c.criterion_type == 'benefit' for c in criteria_list]
            )
            
            rankings = []
            for idx, supplier_id in enumerate(suppliers_data.keys()):
                rankings.append({
                    'supplier_id': supplier_id,
                    'dominance_score': float(results['net_dominance'][idx]),
                    'rank': int(results['ranking'][idx]),
                    'is_in_kernel': bool(results['kernel'][idx])
                })
            
            return {
                'method': 'ELECTRE',
                'rankings': sorted(rankings, key=lambda x: x['rank']),
                'criteria_weights': {c.criterion_id: c.weight for c in criteria_list},
                'kernel_suppliers': [r['supplier_id'] for r in rankings if r['is_in_kernel']]
            }
        
        else:
            raise ValueError(f"Unknown MCDA method: {method}")
    
    def compare_suppliers(
        self,
        supplier_1_id: str,
        supplier_2_id: str,
        comparison_method: str = 'absolute'
    ) -> Dict[str, Any]:
        """
        Compare two suppliers across all dimensions.
        
        Args:
            supplier_1_id: First supplier ID
            supplier_2_id: Second supplier ID
            comparison_method: Comparison method ('absolute', 'relative', 'percentile')
            
        Returns:
            Detailed comparison results
        """
        # Get performance data from cache
        perf1 = self.performance_cache.get(supplier_1_id)
        perf2 = self.performance_cache.get(supplier_2_id)
        
        if not perf1 or not perf2:
            raise ValueError(f"Performance data not found for one or both suppliers. Please evaluate them first.")
        
        # Get category scores
        scores1 = perf1.get_category_scores()
        scores2 = perf2.get_category_scores()
        
        # Set comparison method
        method_map = {
            'absolute': ComparisonMethod.ABSOLUTE,
            'relative': ComparisonMethod.RELATIVE,
            'percentile': ComparisonMethod.PERCENTILE
        }
        self.comparator.comparison_method = method_map.get(comparison_method, ComparisonMethod.ABSOLUTE)
        
        # Perform comparison
        comparison = self.comparator.compare_two_suppliers(
            supplier_1_id, scores1,
            supplier_2_id, scores2
        )
        
        return comparison.to_dict()
    
    def rank_suppliers(
        self,
        supplier_ids: List[str],
        ranking_method: str = 'simple'
    ) -> Dict[str, Any]:
        """
        Rank multiple suppliers.
        
        Args:
            supplier_ids: List of supplier IDs to rank
            ranking_method: Ranking method ('simple', 'borda', 'pareto')
            
        Returns:
            Ranking results
        """
        # Get overall scores for all suppliers
        overall_scores = {}
        criteria_scores = {}
        
        for supplier_id in supplier_ids:
            perf = self.performance_cache.get(supplier_id)
            if not perf:
                raise ValueError(f"Performance data not found for supplier {supplier_id}")
            
            overall_scores[supplier_id] = perf.calculate_overall_score()
            criteria_scores[supplier_id] = perf.get_category_scores()
        
        # Apply ranking method
        if ranking_method == 'simple':
            self.ranker.ranking_method = RankingMethod.SIMPLE
            ranked = self.ranker.rank_suppliers(overall_scores)
            
            return {
                'method': 'simple',
                'rankings': [
                    {'supplier_id': sid, 'score': score, 'rank': rank}
                    for sid, score, rank in ranked
                ]
            }
        
        elif ranking_method == 'borda':
            self.ranker.ranking_method = RankingMethod.BORDA
            ranked = self.ranker.borda_count_ranking(criteria_scores)
            
            return {
                'method': 'borda',
                'rankings': [
                    {'supplier_id': sid, 'borda_count': count, 'rank': rank}
                    for sid, count, rank in ranked
                ]
            }
        
        elif ranking_method == 'pareto':
            # Convert to list format for Pareto analysis
            suppliers_data = {
                sid: list(criteria_scores[sid].values())
                for sid in supplier_ids
            }
            
            pareto_efficient = self.ranker.pareto_frontier(suppliers_data)
            
            return {
                'method': 'pareto',
                'pareto_efficient_suppliers': pareto_efficient,
                'total_suppliers': len(supplier_ids),
                'efficiency_rate': len(pareto_efficient) / len(supplier_ids) * 100
            }
        
        else:
            raise ValueError(f"Unknown ranking method: {ranking_method}")
    
    def gap_analysis(
        self,
        supplier_id: str,
        benchmark_type: str = 'best_in_class',
        benchmark_scores: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Perform gap analysis for a supplier.
        
        Args:
            supplier_id: Supplier to analyze
            benchmark_type: Type of benchmark ('best_in_class', 'industry_average', 'custom')
            benchmark_scores: Custom benchmark scores (required if benchmark_type='custom')
            
        Returns:
            Gap analysis results
        """
        perf = self.performance_cache.get(supplier_id)
        if not perf:
            raise ValueError(f"Performance data not found for supplier {supplier_id}")
        
        supplier_scores = perf.get_category_scores()
        
        if benchmark_type == 'best_in_class':
            # Find best scores from all cached suppliers
            all_scores = {
                sid: self.performance_cache[sid].get_category_scores()
                for sid in self.performance_cache.keys()
            }
            
            gap = self.gap_analyzer.benchmark_against_best(supplier_id, all_scores)
        
        elif benchmark_type == 'custom':
            if not benchmark_scores:
                raise ValueError("benchmark_scores required for custom benchmark")
            
            gap = self.gap_analyzer.analyze_gap(
                supplier_id,
                supplier_scores,
                benchmark_scores,
                benchmark_name="Custom Benchmark"
            )
        
        else:
            # Industry average - use median of all suppliers
            all_scores = {}
            for category in supplier_scores.keys():
                category_values = [
                    self.performance_cache[sid].get_category_scores()[category]
                    for sid in self.performance_cache.keys()
                ]
                all_scores[category] = float(np.median(category_values))
            
            gap = self.gap_analyzer.analyze_gap(
                supplier_id,
                supplier_scores,
                all_scores,
                benchmark_name="Industry Average"
            )
        
        return gap.to_dict()
    
    def integrated_decision_support(
        self,
        suppliers_data: Dict[str, Dict],
        criteria_definition: List[Dict],
        mcda_method: str = 'topsis',
        include_gap_analysis: bool = True,
        include_comparison: bool = True
    ) -> Dict[str, Any]:
        """
        Complete integrated decision support combining evaluation, MCDA, comparison, and gap analysis.
        
        Args:
            suppliers_data: Complete supplier data with all metrics
            criteria_definition: Criteria definition for MCDA
            mcda_method: MCDA method to use
            include_gap_analysis: Include gap analysis
            include_comparison: Include pairwise comparisons
            
        Returns:
            Comprehensive decision support results
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'suppliers_analyzed': len(suppliers_data),
            'mcda_method': mcda_method
        }
        
        # 1. Evaluate all suppliers
        evaluations = {}
        for supplier_id, data in suppliers_data.items():
            eval_result = self.evaluate_supplier_comprehensive(
                supplier_id=supplier_id,
                **data
            )
            evaluations[supplier_id] = eval_result
        
        results['evaluations'] = evaluations
        
        # 2. MCDA Ranking
        mcda_data = {
            sid: eval_data['category_scores']
            for sid, eval_data in evaluations.items()
        }
        
        mcda_results = self.mcda_supplier_selection(
            mcda_data,
            criteria_definition,
            method=mcda_method
        )
        
        results['mcda_rankings'] = mcda_results
        
        # 3. Simple ranking
        ranking_results = self.rank_suppliers(
            list(suppliers_data.keys()),
            ranking_method='simple'
        )
        
        results['simple_rankings'] = ranking_results
        
        # 4. Gap analysis (if requested)
        if include_gap_analysis:
            gap_results = {}
            for supplier_id in suppliers_data.keys():
                try:
                    gap = self.gap_analysis(supplier_id, benchmark_type='best_in_class')
                    gap_results[supplier_id] = gap
                except Exception as e:
                    gap_results[supplier_id] = {'error': str(e)}
            
            results['gap_analysis'] = gap_results
        
        # 5. Top recommendation
        top_supplier_id = mcda_results['rankings'][0]['supplier_id']
        results['recommendation'] = {
            'top_supplier': top_supplier_id,
            'overall_score': evaluations[top_supplier_id]['overall_score'],
            'tier': evaluations[top_supplier_id]['tier'],
            'mcda_rank': 1
        }
        
        return results


# Singleton instance
_integration_service = None

def get_integration_service() -> SupplyChainIntegrationService:
    """Get or create the integration service singleton."""
    global _integration_service
    if _integration_service is None:
        _integration_service = SupplyChainIntegrationService()
    return _integration_service
