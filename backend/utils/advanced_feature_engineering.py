"""
Advanced Feature Engineering Module
Implements temporal, statistical, and domain-specific features
with comprehensive feature selection techniques
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Optional, Dict
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.feature_selection import (
    RFE, SelectFromModel, mutual_info_regression, mutual_info_classif
)
from sklearn.linear_model import LassoCV, RidgeCV
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from scipy import stats
from scipy.stats import zscore
import warnings
warnings.filterwarnings('ignore')

try:
    from statsmodels.tsa.seasonal import seasonal_decompose
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    warnings.warn("statsmodels not available. Seasonal decomposition features will be skipped.")

try:
    from boruta.boruta_py import BorutaPy
    BORUTA_AVAILABLE = True
except ImportError:
    try:
        from boruta import BorutaPy
        BORUTA_AVAILABLE = True
    except ImportError:
        BORUTA_AVAILABLE = False
        warnings.warn("boruta not available. Boruta feature selection will be skipped.")

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    warnings.warn("shap not available. SHAP-based feature selection will be skipped.")


class AdvancedFeatureEngineer:
    """Advanced feature engineering with temporal, statistical, and domain-specific features"""
    
    def __init__(self):
        self.scalers = {}
        self.poly_transformers = {}
        self.feature_stats = {}
        self.is_fitted = False
    
    # ==================== TEMPORAL FEATURES ====================
    
    def create_rolling_statistics(self, df: pd.DataFrame, 
                                  date_col: Optional[str] = None,
                                  value_cols: Optional[List[str]] = None,
                                  windows: List[int] = [7, 14, 30, 60, 90]) -> pd.DataFrame:
        """
        Create rolling statistics for all metrics
        
        Args:
            df: DataFrame with time series data
            date_col: Column name for dates (if None, assumes index is datetime)
            value_cols: Columns to compute rolling stats for (if None, uses numeric columns)
            windows: List of window sizes in days
        
        Returns:
            DataFrame with rolling statistics features
        """
        df = df.copy()
        
        if date_col:
            df = df.set_index(date_col)
        
        if value_cols is None:
            value_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            value_cols = [col for col in value_cols if col not in ['supplier_id']]
        
        for col in value_cols:
            if col not in df.columns:
                continue
            
            for window in windows:
                # Rolling mean
                df[f'{col}_rolling_mean_{window}d'] = df[col].rolling(window=window, min_periods=1).mean()
                
                # Rolling std
                df[f'{col}_rolling_std_{window}d'] = df[col].rolling(window=window, min_periods=1).std().fillna(0)
                
                # Rolling min/max
                df[f'{col}_rolling_min_{window}d'] = df[col].rolling(window=window, min_periods=1).min()
                df[f'{col}_rolling_max_{window}d'] = df[col].rolling(window=window, min_periods=1).max()
                
                # Rolling median
                df[f'{col}_rolling_median_{window}d'] = df[col].rolling(window=window, min_periods=1).median()
        
        return df.reset_index() if date_col else df
    
    def create_lag_features(self, df: pd.DataFrame,
                           value_cols: Optional[List[str]] = None,
                           lags: List[int] = [1, 2, 3, 6, 12]) -> pd.DataFrame:
        """
        Create lag features for trend analysis
        
        Args:
            df: DataFrame with time series data
            value_cols: Columns to create lags for
            lags: List of lag periods
        
        Returns:
            DataFrame with lag features
        """
        df = df.copy()
        
        if value_cols is None:
            value_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            value_cols = [col for col in value_cols if col not in ['supplier_id']]
        
        for col in value_cols:
            if col not in df.columns:
                continue
            
            for lag in lags:
                df[f'{col}_lag_{lag}'] = df[col].shift(lag).fillna(method='bfill')
        
        return df
    
    def create_seasonal_decomposition_features(self, df: pd.DataFrame,
                                               date_col: Optional[str] = None,
                                               value_cols: Optional[List[str]] = None,
                                               period: int = 12) -> pd.DataFrame:
        """
        Create seasonal decomposition features (trend, seasonal, residual)
        
        Args:
            df: DataFrame with time series data
            date_col: Column name for dates
            value_cols: Columns to decompose
            period: Seasonal period
        
        Returns:
            DataFrame with decomposition features
        """
        if not STATSMODELS_AVAILABLE:
            return df
        
        df = df.copy()
        
        if date_col:
            df = df.set_index(date_col)
        
        if value_cols is None:
            value_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            value_cols = [col for col in value_cols if col not in ['supplier_id']]
        
        for col in value_cols:
            if col not in df.columns or len(df) < period * 2:
                continue
            
            try:
                series = df[col].dropna()
                if len(series) < period * 2:
                    continue
                
                decomposition = seasonal_decompose(series, model='additive', period=period)
                
                df[f'{col}_trend'] = decomposition.trend.fillna(method='bfill').fillna(method='ffill')
                df[f'{col}_seasonal'] = decomposition.seasonal.fillna(0)
                df[f'{col}_residual'] = decomposition.resid.fillna(0)
            except Exception as e:
                warnings.warn(f"Could not decompose {col}: {str(e)}")
                continue
        
        return df.reset_index() if date_col else df
    
    def create_rate_of_change_features(self, df: pd.DataFrame,
                                      value_cols: Optional[List[str]] = None,
                                      periods: List[int] = [1, 3, 6, 12]) -> pd.DataFrame:
        """
        Create rate of change features (velocity, acceleration)
        
        Args:
            df: DataFrame with time series data
            value_cols: Columns to compute rate of change for
            periods: Periods for rate of change calculation
        
        Returns:
            DataFrame with rate of change features
        """
        df = df.copy()
        
        if value_cols is None:
            value_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            value_cols = [col for col in value_cols if col not in ['supplier_id']]
        
        for col in value_cols:
            if col not in df.columns:
                continue
            
            for period in periods:
                # Velocity (rate of change)
                df[f'{col}_velocity_{period}'] = df[col].pct_change(period).fillna(0)
                
                # Acceleration (rate of change of velocity)
                df[f'{col}_acceleration_{period}'] = df[f'{col}_velocity_{period}'].diff().fillna(0)
        
        return df
    
    def create_cyclical_encoding(self, df: pd.DataFrame,
                                 date_col: Optional[str] = None,
                                 include_hour: bool = False) -> pd.DataFrame:
        """
        Create time-based cyclical encoding (sin/cos transformations)
        
        Args:
            df: DataFrame with datetime column
            date_col: Column name for dates
            include_hour: Whether to include hour encoding
        
        Returns:
            DataFrame with cyclical features
        """
        df = df.copy()
        
        if date_col:
            dates = pd.to_datetime(df[date_col])
        else:
            dates = pd.to_datetime(df.index)
        
        # Day of week (0=Monday, 6=Sunday)
        df['day_of_week_sin'] = np.sin(2 * np.pi * dates.dt.dayofweek / 7)
        df['day_of_week_cos'] = np.cos(2 * np.pi * dates.dt.dayofweek / 7)
        
        # Day of month
        df['day_of_month_sin'] = np.sin(2 * np.pi * dates.dt.day / 31)
        df['day_of_month_cos'] = np.cos(2 * np.pi * dates.dt.day / 31)
        
        # Month
        df['month_sin'] = np.sin(2 * np.pi * dates.dt.month / 12)
        df['month_cos'] = np.cos(2 * np.pi * dates.dt.month / 12)
        
        # Quarter
        df['quarter_sin'] = np.sin(2 * np.pi * dates.dt.quarter / 4)
        df['quarter_cos'] = np.cos(2 * np.pi * dates.dt.quarter / 4)
        
        if include_hour:
            df['hour_sin'] = np.sin(2 * np.pi * dates.dt.hour / 24)
            df['hour_cos'] = np.cos(2 * np.pi * dates.dt.hour / 24)
        
        return df
    
    # ==================== STATISTICAL FEATURES ====================
    
    def create_zscore_features(self, df: pd.DataFrame,
                               value_cols: Optional[List[str]] = None,
                               outlier_cap: float = 3.0) -> pd.DataFrame:
        """
        Create Z-score normalized features with outlier capping
        
        Args:
            df: DataFrame with numeric columns
            value_cols: Columns to normalize
            outlier_cap: Z-score threshold for capping outliers
        
        Returns:
            DataFrame with Z-score features
        """
        df = df.copy()
        
        if value_cols is None:
            value_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            value_cols = [col for col in value_cols if col not in ['supplier_id']]
        
        for col in value_cols:
            if col not in df.columns:
                continue
            
            z_scores = zscore(df[col].fillna(df[col].median()))
            df[f'{col}_zscore'] = z_scores
            
            # Cap outliers
            df[f'{col}_zscore_capped'] = np.clip(z_scores, -outlier_cap, outlier_cap)
        
        return df
    
    def create_polynomial_features(self, df: pd.DataFrame,
                                   value_cols: Optional[List[str]] = None,
                                   degrees: List[int] = [2, 3],
                                   interaction_only: bool = False) -> pd.DataFrame:
        """
        Create polynomial features (2nd and 3rd degree interactions)
        
        Args:
            df: DataFrame with numeric columns
            value_cols: Columns to create polynomial features for
            degrees: List of polynomial degrees
            interaction_only: Whether to include only interaction terms
        
        Returns:
            DataFrame with polynomial features
        """
        df = df.copy()
        
        if value_cols is None:
            value_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            value_cols = [col for col in value_cols if col not in ['supplier_id']][:10]  # Limit to avoid explosion
        
        if len(value_cols) == 0:
            return df
        
        for degree in degrees:
            if degree < 2:
                continue
            
            poly = PolynomialFeatures(degree=degree, interaction_only=interaction_only, include_bias=False)
            
            # Select columns that exist
            available_cols = [col for col in value_cols if col in df.columns]
            if len(available_cols) == 0:
                continue
            
            X_poly = poly.fit_transform(df[available_cols].fillna(0))
            
            # Create feature names
            feature_names = poly.get_feature_names_out(available_cols)
            
            # Add polynomial features to dataframe
            for i, name in enumerate(feature_names):
                if name not in df.columns:  # Avoid duplicates
                    df[f'poly_{degree}_{name}'] = X_poly[:, i]
        
        return df
    
    def create_ratio_features(self, df: pd.DataFrame,
                             ratio_pairs: Optional[List[Tuple[str, str]]] = None) -> pd.DataFrame:
        """
        Create ratio features (e.g., delivery_rate/quality_score, cost/performance)
        
        Args:
            df: DataFrame with numeric columns
            ratio_pairs: List of (numerator, denominator) pairs
        
        Returns:
            DataFrame with ratio features
        """
        df = df.copy()
        
        if ratio_pairs is None:
            # Default ratio pairs based on common supplier metrics
            ratio_pairs = [
                ('on_time_delivery_rate', 'quality_score'),
                ('performance_score', 'cost'),
                ('credit_score', 'debt_to_equity'),
                ('profit_margin', 'utilization_rate'),
                ('esg_score', 'compliance_score')
            ]
        
        for num_col, den_col in ratio_pairs:
            if num_col in df.columns and den_col in df.columns:
                # Avoid division by zero
                denominator = df[den_col].replace(0, np.nan)
                df[f'{num_col}_div_{den_col}'] = df[num_col] / denominator
                df[f'{num_col}_div_{den_col}'] = df[f'{num_col}_div_{den_col}'].fillna(0)
        
        return df
    
    def create_logarithmic_features(self, df: pd.DataFrame,
                                    value_cols: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Create logarithmic and exponential transformations
        
        Args:
            df: DataFrame with numeric columns
            value_cols: Columns to transform
        
        Returns:
            DataFrame with log/exp features
        """
        df = df.copy()
        
        if value_cols is None:
            value_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            value_cols = [col for col in value_cols if col not in ['supplier_id']]
        
        for col in value_cols:
            if col not in df.columns:
                continue
            
            # Only apply to positive values
            positive_values = df[col] > 0
            
            # Log transformation (log1p to handle zeros)
            df[f'{col}_log'] = np.log1p(df[col].clip(lower=0))
            
            # Exponential transformation
            df[f'{col}_exp'] = np.exp(df[col].clip(upper=10))  # Cap to avoid overflow
        
        return df
    
    def create_binned_features(self, df: pd.DataFrame,
                               value_cols: Optional[List[str]] = None,
                               n_bins: int = 5,
                               method: str = 'quantile') -> pd.DataFrame:
        """
        Create binned features with optimal discretization
        
        Args:
            df: DataFrame with numeric columns
            value_cols: Columns to bin
            n_bins: Number of bins
            method: Binning method ('quantile', 'uniform', 'kmeans')
        
        Returns:
            DataFrame with binned features
        """
        df = df.copy()
        
        if value_cols is None:
            value_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            value_cols = [col for col in value_cols if col not in ['supplier_id']]
        
        for col in value_cols:
            if col not in df.columns:
                continue
            
            if method == 'quantile':
                df[f'{col}_binned'] = pd.qcut(df[col].fillna(df[col].median()), 
                                              q=n_bins, duplicates='drop', labels=False)
            elif method == 'uniform':
                df[f'{col}_binned'] = pd.cut(df[col].fillna(df[col].median()), 
                                            bins=n_bins, labels=False)
            else:
                # K-means binning
                from sklearn.cluster import KMeans
                kmeans = KMeans(n_clusters=n_bins, random_state=42, n_init=10)
                values = df[col].fillna(df[col].median()).values.reshape(-1, 1)
                df[f'{col}_binned'] = kmeans.fit_predict(values)
        
        return df
    
    # ==================== DOMAIN-SPECIFIC FEATURES ====================
    
    def create_supplier_reliability_index(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create supplier reliability index (composite metric)
        
        Args:
            df: DataFrame with supplier metrics
        
        Returns:
            DataFrame with reliability index
        """
        df = df.copy()
        
        # Components of reliability
        components = {}
        
        if 'on_time_delivery_rate' in df.columns:
            components['delivery'] = df['on_time_delivery_rate']
        
        if 'quality_score' in df.columns:
            components['quality'] = df['quality_score']
        
        if 'defect_rate' in df.columns:
            components['defect'] = 1 - df['defect_rate'].clip(0, 1)
        
        if 'compliance_score' in df.columns:
            components['compliance'] = df['compliance_score']
        
        if len(components) > 0:
            # Weighted average
            weights = np.array([0.3, 0.3, 0.2, 0.2][:len(components)])
            weights = weights / weights.sum()
            
            reliability = sum(components[list(components.keys())[i]] * weights[i] 
                            for i in range(len(components)))
            df['supplier_reliability_index'] = reliability.fillna(0)
        else:
            df['supplier_reliability_index'] = 0.5
        
        return df
    
    def create_financial_health_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create financial health score (Altman Z-score adaptation)
        
        Args:
            df: DataFrame with financial metrics
        
        Returns:
            DataFrame with financial health score
        """
        df = df.copy()
        
        # Altman Z-score components (adapted for supplier context)
        score = 0
        
        if 'credit_score' in df.columns:
            score += (df['credit_score'] / 850) * 1.2
        
        if 'profit_margin' in df.columns:
            score += df['profit_margin'].clip(0, 1) * 1.4
        
        if 'debt_to_equity' in df.columns:
            score += (1 - df['debt_to_equity'].clip(0, 2) / 2) * 3.3
        
        if 'utilization_rate' in df.columns:
            score += df['utilization_rate'] * 0.6
        
        if 'years_in_business' in df.columns:
            score += (df['years_in_business'] / 50).clip(0, 1) * 0.999
        
        df['financial_health_score'] = score.fillna(0)
        
        return df
    
    def create_geographic_risk_encoding(self, df: pd.DataFrame,
                                        geo_col: str = 'location') -> pd.DataFrame:
        """
        Create geographic risk encoding (multi-hot encoding with weights)
        
        Args:
            df: DataFrame with geographic information
            geo_col: Column name for geographic location
        
        Returns:
            DataFrame with geographic risk features
        """
        df = df.copy()
        
        if geo_col not in df.columns:
            return df
        
        # Risk weights by region (example - should be customized)
        risk_weights = {
            'high_risk': 0.8,
            'medium_risk': 0.5,
            'low_risk': 0.2
        }
        
        # Create risk score based on location
        if 'geopolitical_risk_score' in df.columns:
            df['geo_risk_encoded'] = df['geopolitical_risk_score']
        else:
            # Simple encoding based on location
            df['geo_risk_encoded'] = df[geo_col].apply(
                lambda x: risk_weights.get(str(x).lower(), 0.5)
            )
        
        return df
    
    def create_contract_compliance_rate(self, df: pd.DataFrame,
                                       time_window: int = 90) -> pd.DataFrame:
        """
        Create contract compliance rate over time
        
        Args:
            df: DataFrame with compliance data
            time_window: Time window in days
        
        Returns:
            DataFrame with compliance rate
        """
        df = df.copy()
        
        if 'compliance_score' in df.columns:
            df['contract_compliance_rate'] = df['compliance_score']
        else:
            # Estimate from other metrics
            compliance_components = []
            
            if 'on_time_delivery_rate' in df.columns:
                compliance_components.append(df['on_time_delivery_rate'])
            
            if 'quality_score' in df.columns:
                compliance_components.append(df['quality_score'])
            
            if len(compliance_components) > 0:
                df['contract_compliance_rate'] = pd.concat(compliance_components, axis=1).mean(axis=1)
            else:
                df['contract_compliance_rate'] = 0.5
        
        return df
    
    def create_supplier_diversification_index(self, df: pd.DataFrame,
                                             group_col: str = 'category') -> pd.DataFrame:
        """
        Create supplier diversification index
        
        Args:
            df: DataFrame with supplier data
            group_col: Column to group by for diversification
        
        Returns:
            DataFrame with diversification index
        """
        df = df.copy()
        
        if group_col in df.columns:
            # Calculate Herfindahl-Hirschman Index (HHI) for diversification
            category_counts = df.groupby(group_col).size()
            total = len(df)
            
            if total > 0:
                hhi = ((category_counts / total) ** 2).sum()
                # Convert to diversification index (1 - HHI, normalized)
                diversification = 1 - hhi
                df['supplier_diversification_index'] = diversification
            else:
                df['supplier_diversification_index'] = 0
        else:
            df['supplier_diversification_index'] = 0.5
        
        return df
    
    # ==================== FEATURE SELECTION TECHNIQUES ====================
    
    def recursive_feature_elimination(self, X: pd.DataFrame, y: pd.Series,
                                     estimator=None, n_features: Optional[int] = None,
                                     cv: int = 5) -> Tuple[List[str], pd.DataFrame]:
        """
        Recursive Feature Elimination (RFE) with cross-validation
        
        Args:
            X: Feature matrix
            y: Target variable
            estimator: Base estimator (default: RandomForest)
            n_features: Number of features to select
            cv: Cross-validation folds
        
        Returns:
            (selected_features, X_selected)
        """
        if estimator is None:
            if y.dtype == 'object' or y.nunique() < 10:
                estimator = RandomForestClassifier(n_estimators=100, random_state=42)
            else:
                estimator = RandomForestRegressor(n_estimators=100, random_state=42)
        
        if n_features is None:
            n_features = min(20, X.shape[1] // 2)
        
        rfe = RFE(estimator=estimator, n_features_to_select=n_features)
        rfe.fit(X.fillna(0), y)
        
        selected_features = X.columns[rfe.support_].tolist()
        X_selected = X[selected_features]
        
        return selected_features, X_selected
    
    def boruta_feature_selection(self, X: pd.DataFrame, y: pd.Series,
                                estimator=None, max_iter: int = 100) -> Tuple[List[str], pd.DataFrame]:
        """
        Boruta Algorithm for all-relevant feature selection
        
        Args:
            X: Feature matrix
            y: Target variable
            estimator: Base estimator
            max_iter: Maximum iterations
        
        Returns:
            (selected_features, X_selected)
        """
        if not BORUTA_AVAILABLE:
            warnings.warn("Boruta not available. Skipping Boruta feature selection.")
            return X.columns.tolist(), X
        
        if estimator is None:
            if y.dtype == 'object' or y.nunique() < 10:
                estimator = RandomForestClassifier(n_estimators=100, random_state=42)
            else:
                estimator = RandomForestRegressor(n_estimators=100, random_state=42)
        
        boruta = BorutaPy(estimator=estimator, n_estimators='auto', verbose=0, max_iter=max_iter)
        boruta.fit(X.fillna(0).values, y.values)
        
        selected_features = X.columns[boruta.support_].tolist()
        X_selected = X[selected_features]
        
        return selected_features, X_selected
    
    def shap_feature_selection(self, X: pd.DataFrame, y: pd.Series,
                              estimator=None, top_k: int = 20) -> Tuple[List[str], pd.DataFrame]:
        """
        SHAP-based feature selection for model-agnostic importance
        
        Args:
            X: Feature matrix
            y: Target variable
            estimator: Base estimator
            top_k: Number of top features to select
        
        Returns:
            (selected_features, X_selected)
        """
        if not SHAP_AVAILABLE:
            warnings.warn("SHAP not available. Skipping SHAP feature selection.")
            return X.columns.tolist(), X
        
        if estimator is None:
            if y.dtype == 'object' or y.nunique() < 10:
                estimator = RandomForestClassifier(n_estimators=100, random_state=42)
            else:
                estimator = RandomForestRegressor(n_estimators=100, random_state=42)
        
        estimator.fit(X.fillna(0), y)
        
        # Calculate SHAP values
        explainer = shap.TreeExplainer(estimator)
        shap_values = explainer.shap_values(X.fillna(0))
        
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        
        # Calculate mean absolute SHAP values
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': np.abs(shap_values).mean(axis=0)
        }).sort_values('importance', ascending=False)
        
        selected_features = feature_importance.head(top_k)['feature'].tolist()
        X_selected = X[selected_features]
        
        return selected_features, X_selected
    
    def mutual_information_selection(self, X: pd.DataFrame, y: pd.Series,
                                    top_k: int = 20) -> Tuple[List[str], pd.DataFrame]:
        """
        Mutual Information for non-linear relationships
        
        Args:
            X: Feature matrix
            y: Target variable
            top_k: Number of top features to select
        
        Returns:
            (selected_features, X_selected)
        """
        if y.dtype == 'object' or y.nunique() < 10:
            mi_scores = mutual_info_classif(X.fillna(0), y, random_state=42)
        else:
            mi_scores = mutual_info_regression(X.fillna(0), y, random_state=42)
        
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': mi_scores
        }).sort_values('importance', ascending=False)
        
        selected_features = feature_importance.head(top_k)['feature'].tolist()
        X_selected = X[selected_features]
        
        return selected_features, X_selected
    
    def l1_l2_regularization_selection(self, X: pd.DataFrame, y: pd.Series,
                                      method: str = 'l1', alpha: float = 0.1) -> Tuple[List[str], pd.DataFrame]:
        """
        L1/L2 regularization for automatic feature selection
        
        Args:
            X: Feature matrix
            y: Target variable
            method: 'l1' or 'l2'
            alpha: Regularization strength
        
        Returns:
            (selected_features, X_selected)
        """
        if method == 'l1':
            model = LassoCV(alphas=[alpha], cv=5, random_state=42)
        else:
            model = RidgeCV(alphas=[alpha], cv=5)
        
        model.fit(X.fillna(0), y)
        
        if method == 'l1':
            # L1 selects features with non-zero coefficients
            selected_features = X.columns[model.coef_ != 0].tolist()
        else:
            # L2 ranks by coefficient magnitude
            feature_importance = pd.DataFrame({
                'feature': X.columns,
                'importance': np.abs(model.coef_)
            }).sort_values('importance', ascending=False)
            selected_features = feature_importance.head(min(20, len(X.columns)))['feature'].tolist()
        
        X_selected = X[selected_features] if selected_features else X
        
        return selected_features, X_selected
    
    def genetic_algorithm_selection(self, X: pd.DataFrame, y: pd.Series,
                                   n_features: int = 20, n_generations: int = 10,
                                   population_size: int = 50) -> Tuple[List[str], pd.DataFrame]:
        """
        Genetic Algorithm for optimal feature subset selection
        
        Args:
            X: Feature matrix
            y: Target variable
            n_features: Target number of features
            n_generations: Number of generations
            population_size: Population size
        
        Returns:
            (selected_features, X_selected)
        """
        from sklearn.model_selection import cross_val_score
        
        if y.dtype == 'object' or y.nunique() < 10:
            estimator = RandomForestClassifier(n_estimators=50, random_state=42)
            scoring = 'accuracy'
        else:
            estimator = RandomForestRegressor(n_estimators=50, random_state=42)
            scoring = 'neg_mean_squared_error'
        
        # Simple genetic algorithm implementation
        n_features_total = X.shape[1]
        n_features = min(n_features, n_features_total)
        
        # Initialize population
        population = []
        for _ in range(population_size):
            features = np.random.choice(n_features_total, size=n_features, replace=False)
            population.append(features)
        
        # Evolution
        for generation in range(n_generations):
            # Evaluate fitness
            fitness_scores = []
            for individual in population:
                X_subset = X.iloc[:, individual].fillna(0)
                try:
                    scores = cross_val_score(estimator, X_subset, y, cv=3, scoring=scoring)
                    fitness = scores.mean()
                except:
                    fitness = -1e10
                fitness_scores.append(fitness)
            
            # Select top performers
            top_indices = np.argsort(fitness_scores)[-population_size//2:]
            new_population = [population[i] for i in top_indices]
            
            # Crossover and mutation
            while len(new_population) < population_size:
                parent1, parent2 = np.random.choice(len(new_population), size=2, replace=False)
                child = np.unique(np.concatenate([
                    new_population[parent1][:n_features//2],
                    new_population[parent2][n_features//2:]
                ]))
                
                # Mutation
                if np.random.random() < 0.1:
                    child = np.random.choice(n_features_total, size=min(len(child), n_features), replace=False)
                
                new_population.append(child)
            
            population = new_population
        
        # Select best individual
        best_individual = population[np.argmax(fitness_scores)]
        selected_features = X.columns[best_individual].tolist()
        X_selected = X[selected_features]
        
        return selected_features, X_selected
    
    # ==================== COMPREHENSIVE PIPELINE ====================
    
    def create_all_features(self, df: pd.DataFrame,
                           date_col: Optional[str] = None,
                           include_temporal: bool = True,
                           include_statistical: bool = True,
                           include_domain: bool = True) -> pd.DataFrame:
        """
        Create all advanced features in one pipeline
        
        Args:
            df: Input DataFrame
            date_col: Date column for temporal features
            include_temporal: Whether to include temporal features
            include_statistical: Whether to include statistical features
            include_domain: Whether to include domain-specific features
        
        Returns:
            DataFrame with all engineered features
        """
        df = df.copy()
        
        if include_temporal:
            # Rolling statistics
            df = self.create_rolling_statistics(df, date_col=date_col)
            
            # Lag features
            df = self.create_lag_features(df)
            
            # Rate of change
            df = self.create_rate_of_change_features(df)
            
            # Cyclical encoding
            if date_col:
                df = self.create_cyclical_encoding(df, date_col=date_col)
        
        if include_statistical:
            # Z-score normalization
            df = self.create_zscore_features(df)
            
            # Ratio features
            df = self.create_ratio_features(df)
            
            # Logarithmic features
            df = self.create_logarithmic_features(df)
        
        if include_domain:
            # Domain-specific features
            df = self.create_supplier_reliability_index(df)
            df = self.create_financial_health_score(df)
            df = self.create_contract_compliance_rate(df)
            df = self.create_supplier_diversification_index(df)
        
        return df


# Global instance
advanced_feature_engineer = AdvancedFeatureEngineer()

