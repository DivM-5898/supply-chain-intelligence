# AI Supplier Selection & Risk Management Platform
## Comprehensive Technical Methodology Guide

---

## Table of Contents

1. [System Architecture Overview](#1-system-architecture-overview)
2. [Data Pipeline & Feature Engineering](#2-data-pipeline--feature-engineering)
3. [Supplier Evaluation & Scoring](#3-supplier-evaluation--scoring)
4. [Risk Profiling & Prediction](#4-risk-profiling--prediction)
5. [Fraud Detection](#5-fraud-detection)
6. [Multi-Criteria Decision Analysis](#6-multi-criteria-decision-analysis)
7. [Explainable AI & Ethics](#7-explainable-ai--ethics)
8. [Natural Language Processing](#8-natural-language-processing)
9. [Transparency & Supply Chain Visualization](#9-transparency--supply-chain-visualization)
10. [Model Training & Deployment](#10-model-training--deployment)

---

## 1. System Architecture Overview

### 1.1 Technology Stack

**Backend:**
- **FastAPI**: High-performance async web framework for RESTful API
- **Python 3.10+**: Core programming language
- **Uvicorn**: ASGI server for production deployment

**Machine Learning:**
- **scikit-learn**: Classical ML algorithms
- **XGBoost**: Gradient boosting framework
- **SHAP**: Model explainability
- **LIME**: Local interpretable model-agnostic explanations

**Data Processing:**
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **SciPy**: Scientific computing and statistics

**NLP:**
- **spaCy**: Industrial-strength NLP
- **Transformers (Hugging Face)**: Pre-trained language models

**Frontend:**
- **Vanilla JavaScript**: No framework overhead
- **Plotly.js**: Interactive visualizations
- **Bootstrap 5**: Responsive UI components

### 1.2 Architecture Pattern

```
┌─────────────────┐
│   Frontend      │ ← User Interface (JavaScript SPA)
│   (Port 8080)   │
└────────┬────────┘
         │ HTTP/JSON
         ↓
┌─────────────────┐
│   FastAPI       │ ← REST API Layer
│   Backend       │
│   (Port 8000)   │
└────────┬────────┘
         │
    ┌────┴────┬────────────┬──────────┐
    ↓         ↓            ↓          ↓
┌────────┐ ┌─────┐  ┌──────────┐ ┌─────────┐
│ ML     │ │ NLP │  │ Decision │ │ Data    │
│ Models │ │ Svc │  │ Support  │ │ Loader  │
└────────┘ └─────┘  └──────────┘ └─────────┘
                                       ↓
                                  ┌─────────┐
                                  │ CSV Data│
                                  └─────────┘
```

---

## 2. Data Pipeline & Feature Engineering

### 2.1 Data Schema

**Supplier Master Data:**
```python
{
    'supplier_id': str,              # Unique identifier
    'name': str,                     # Supplier name
    'country': str,                  # Geographic location
    'region': str,                   # Continental region
    'industry': str,                 # Industry sector
    'years_in_business': int,        # Company age
    'employee_count': int,           # Workforce size
    'annual_revenue_millions': float,# Financial scale
    'credit_score': int,             # Creditworthiness (300-850)
    'debt_to_equity': float,         # Financial leverage
    'profit_margin': float,          # Profitability (0-1)
    'on_time_delivery_rate': float,  # Delivery performance (0-1)
    'quality_score': float,          # Quality metrics (0-1)
    'defect_rate': float,            # Quality issues (0-1)
    'utilization_rate': float,       # Capacity utilization (0-1)
    'geopolitical_risk_score': float,# Country risk (0-1)
    'esg_score': float,              # ESG compliance (0-1)
    'compliance_score': float,       # Regulatory compliance (0-1)
    'certifications': str            # ISO/Industry certifications
}
```

### 2.2 Feature Engineering Pipeline

**Step 1: Composite Feature Creation**

```python
# Performance Score (40% delivery + 40% quality + 20% defect reduction)
performance_score = (
    on_time_delivery_rate * 0.4 +
    quality_score * 0.4 +
    (1 - defect_rate) * 0.2
)

# Financial Health (40% credit + 30% leverage + 30% profitability)
financial_health = (
    (credit_score / 850) * 0.4 +
    (1 - min(debt_to_equity, 2) / 2) * 0.3 +
    profit_margin * 0.3
)

# Operational Maturity (30% experience + 30% capacity + 20% ERP + 20% certs)
operational_maturity = (
    (years_in_business / 50) * 0.3 +
    utilization_rate * 0.3 +
    has_erp_system * 0.2 +
    has_certifications * 0.2
)
```

**Methodology:**
- **Weighted Aggregation**: Combines related metrics with domain-expert weights
- **Normalization**: Scales features to [0,1] range for comparability
- **Dimensionality Reduction**: Reduces 20+ raw features to 14 engineered features

### 2.3 Advanced Feature Engineering

**Statistical Features:**
```python
# Z-score normalization for outlier detection
z_score = (value - mean) / std_dev

# Ratio features for relative performance
efficiency_ratio = revenue / employee_count
risk_adjusted_return = profit_margin / (1 + geopolitical_risk_score)
```

**Domain-Specific Indices:**
```python
# Supplier Reliability Index
reliability_index = (
    on_time_delivery_rate * 0.35 +
    quality_score * 0.35 +
    (1 - defect_rate) * 0.30
)

# Financial Health Score (Altman Z-Score inspired)
financial_health_score = (
    working_capital_ratio * 1.2 +
    retained_earnings_ratio * 1.4 +
    ebit_ratio * 3.3 +
    equity_ratio * 0.6 +
    revenue_ratio * 1.0
)
```

---

## 3. Supplier Evaluation & Scoring

### 3.1 Machine Learning Models

#### 3.1.1 XGBoost (eXtreme Gradient Boosting)

**Algorithm Overview:**
XGBoost is an ensemble learning method that builds decision trees sequentially, where each tree corrects the errors of previous trees.

**Mathematical Formulation:**
```
ŷᵢ = Σ(fₖ(xᵢ))  where fₖ ∈ F (functional space of regression trees)

Objective Function:
L(φ) = Σᵢ l(ŷᵢ, yᵢ) + Σₖ Ω(fₖ)

where:
- l = loss function (MSE for regression)
- Ω = regularization term (complexity penalty)
- Ω(f) = γT + ½λ||w||²
```

**Implementation:**
```python
model = XGBRegressor(
    max_depth=6,           # Tree depth (prevents overfitting)
    learning_rate=0.1,     # Step size shrinkage (0.01-0.3)
    n_estimators=100,      # Number of boosting rounds
    objective='reg:squarederror',  # Loss function
    subsample=0.8,         # Stochastic sampling
    colsample_bytree=0.8,  # Feature sampling
    random_state=42
)
```

**Why XGBoost for Supplier Scoring?**
1. **Handles Non-linearity**: Captures complex relationships (e.g., quality vs cost tradeoffs)
2. **Built-in Regularization**: Prevents overfitting on limited supplier data
3. **Feature Importance**: Identifies key drivers of supplier performance
4. **Missing Value Handling**: Robust to incomplete supplier data

**Real-World Application:**
- **Training Data**: Historical supplier performance (target = composite score)
- **Prediction**: Ranks new/existing suppliers on 0-1 scale
- **Use Case**: Pre-qualify suppliers before RFP process

#### 3.1.2 Random Forest

**Algorithm Overview:**
Ensemble of decision trees trained on bootstrapped samples with random feature selection.

**Key Concepts:**
```
Bagging (Bootstrap Aggregating):
- Sample n data points with replacement
- Train tree on each bootstrap sample
- Average predictions: ŷ = (1/B) Σ treeᵢ(x)

Random Subspace Method:
- At each split, randomly select √p features (p = total features)
- Choose best split from random subset
- Reduces correlation between trees
```

**Implementation:**
```python
model = RandomForestRegressor(
    n_estimators=100,      # Number of trees
    max_depth=10,          # Maximum tree depth
    min_samples_split=5,   # Minimum samples to split
    min_samples_leaf=2,    # Minimum samples per leaf
    max_features='sqrt',   # √p features per split
    random_state=42
)
```

**Advantages:**
- **Variance Reduction**: Multiple trees reduce prediction variance
- **Outlier Robustness**: Aggregation smooths outlier effects
- **Interpretability**: Feature importance via Gini impurity

#### 3.1.3 Gradient Boosting Machines

**Algorithm Overview:**
Sequential ensemble where each model fits the residual errors of the previous model.

**Mathematical Foundation:**
```
Stage m:
1. Compute pseudo-residuals:
   rᵢₘ = -[∂L(yᵢ, F(xᵢ))/∂F(xᵢ)]|F=Fₘ₋₁

2. Fit regression tree hₘ(x) to residuals

3. Update model:
   Fₘ(x) = Fₘ₋₁(x) + ν·hₘ(x)
   where ν = learning rate
```

**Implementation:**
```python
model = GradientBoostingRegressor(
    n_estimators=100,
    learning_rate=0.1,     # Shrinkage parameter
    max_depth=5,
    subsample=0.8,         # Stochastic gradient boosting
    loss='squared_error',
    random_state=42
)
```

#### 3.1.4 Support Vector Regression (SVR)

**Algorithm Overview:**
Finds optimal hyperplane that best fits data within epsilon-insensitive tube.

**Mathematical Formulation:**
```
Primal Problem:
min ½||w||² + C·Σᵢ(ξᵢ + ξᵢ*)

subject to:
yᵢ - (w·xᵢ + b) ≤ ε + ξᵢ
(w·xᵢ + b) - yᵢ ≤ ε + ξᵢ*
ξᵢ, ξᵢ* ≥ 0

Kernel Trick (RBF):
K(x, x') = exp(-γ||x - x'||²)
```

**Implementation:**
```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = SVR(
    kernel='rbf',          # Radial basis function
    C=1.0,                 # Regularization parameter
    epsilon=0.1,           # Epsilon-tube width
    gamma='scale'          # RBF kernel coefficient
)
```

**Use Case**: When you need smooth, continuous predictions with outlier robustness.

#### 3.1.5 Neural Network (MLPRegressor)

**Architecture:**
Multi-layer perceptron with feedforward architecture.

**Network Structure:**
```
Input Layer (14 neurons) → 
Hidden Layer 1 (100 neurons, ReLU) → 
Hidden Layer 2 (50 neurons, ReLU) → 
Output Layer (1 neuron)
```

**Implementation:**
```python
model = MLPRegressor(
    hidden_layer_sizes=(100, 50),  # Two hidden layers
    activation='relu',              # ReLU activation
    solver='adam',                  # Adaptive moment estimation
    alpha=0.0001,                   # L2 regularization
    learning_rate='adaptive',       # Learning rate schedule
    max_iter=500,
    random_state=42
)
```

**Forward Propagation:**
```
z₁ = W₁·x + b₁
a₁ = ReLU(z₁) = max(0, z₁)
z₂ = W₂·a₁ + b₂
a₂ = ReLU(z₂)
ŷ = W₃·a₂ + b₃
```

**Backpropagation:**
```
Adam Optimizer:
mₜ = β₁·mₜ₋₁ + (1-β₁)·∇L
vₜ = β₂·vₜ₋₁ + (1-β₂)·(∇L)²
m̂ₜ = mₜ/(1-β₁ᵗ)
v̂ₜ = vₜ/(1-β₂ᵗ)
θₜ = θₜ₋₁ - α·m̂ₜ/(√v̂ₜ + ε)
```

### 3.2 Ensemble Methods

#### 3.2.1 Voting Regressor

**Concept**: Combines predictions from multiple models through averaging.

**Implementation:**
```python
ensemble = VotingRegressor([
    ('xgb', XGBRegressor(n_estimators=50)),
    ('rf', RandomForestRegressor(n_estimators=50)),
    ('gb', GradientBoostingRegressor(n_estimators=50))
])
```

**Prediction:**
```
ŷ_ensemble = (ŷ_xgb + ŷ_rf + ŷ_gb) / 3
```

**Advantages:**
- Reduces model-specific biases
- Improves prediction stability
- Often achieves better generalization

### 3.3 Model Evaluation Metrics

**R² Score (Coefficient of Determination):**
```
R² = 1 - (Σ(yᵢ - ŷᵢ)²) / (Σ(yᵢ - ȳ)²)

Interpretation:
- R² = 1: Perfect predictions
- R² = 0: Model no better than mean
- R² < 0: Model worse than mean
```

**Root Mean Squared Error (RMSE):**
```
RMSE = √[(1/n)·Σ(yᵢ - ŷᵢ)²]

Lower is better; same units as target variable
```

**Feature Importance Analysis:**
```python
# XGBoost Feature Importance (Gain)
importance = model.feature_importances_

# Interpretation:
# - Higher values = more important for predictions
# - Identifies key drivers of supplier performance
```

---

## 4. Risk Profiling & Prediction

### 4.1 Risk Classification

**Objective**: Binary classification to identify high-risk suppliers.

#### 4.1.1 Logistic Regression

**Algorithm Overview:**
Linear model for binary classification using logistic (sigmoid) function.

**Mathematical Formulation:**
```
Logistic Function:
σ(z) = 1 / (1 + e^(-z))

where z = β₀ + β₁x₁ + β₂x₂ + ... + βₚxₚ

Probability:
P(y=1|x) = σ(β·x)

Log-Odds (Logit):
log[P/(1-P)] = β·x

Maximum Likelihood Estimation:
L(β) = Πᵢ P(yᵢ|xᵢ)^yᵢ · (1-P(yᵢ|xᵢ))^(1-yᵢ)
```

**Implementation:**
```python
model = LogisticRegression(
    penalty='l2',          # Ridge regularization
    C=1.0,                 # Inverse regularization strength
    solver='lbfgs',        # Limited-memory BFGS
    max_iter=1000,
    class_weight='balanced'  # Handle class imbalance
)
```

**Risk Threshold Determination:**
```python
# Optimize threshold using ROC curve
fpr, tpr, thresholds = roc_curve(y_true, y_pred_proba)
optimal_idx = np.argmax(tpr - fpr)
optimal_threshold = thresholds[optimal_idx]
```

#### 4.1.2 Risk Scoring System

**Composite Risk Score:**
```python
risk_score = (
    geopolitical_risk_score * 0.30 +
    financial_risk_indicator * 0.25 +
    operational_risk_indicator * 0.20 +
    compliance_risk_indicator * 0.15 +
    reputational_risk_indicator * 0.10
)

# Risk Classification
if risk_score > 0.7:
    risk_level = 'HIGH'
elif risk_score > 0.4:
    risk_level = 'MEDIUM'
else:
    risk_level = 'LOW'
```

### 4.2 Time Series Risk Prediction

**Approach**: Predict future risk events using historical patterns.

**Feature Engineering for Time Series:**
```python
# Lagged features
risk_events['lag_1_month'] = risk_events['impact_score'].shift(1)
risk_events['lag_3_month'] = risk_events['impact_score'].shift(3)

# Rolling statistics
risk_events['rolling_mean_6m'] = risk_events['impact_score'].rolling(6).mean()
risk_events['rolling_std_6m'] = risk_events['impact_score'].rolling(6).std()

# Trend features
risk_events['trend'] = risk_events['impact_score'].diff()
risk_events['acceleration'] = risk_events['trend'].diff()
```

---

## 5. Fraud Detection

### 5.1 Anomaly Detection Algorithms

#### 5.1.1 Isolation Forest

**Algorithm Overview:**
Identifies anomalies by isolating observations through random partitioning.

**Key Concept:**
```
Anomalies are:
1. Few in number (minority)
2. Different in feature values
3. Easier to isolate (require fewer splits)

Anomaly Score:
s(x, n) = 2^(-E[h(x)] / c(n))

where:
- h(x) = path length to isolate x
- c(n) = average path length for n samples
- s ∈ [0, 1], s → 1 indicates anomaly
```

**Implementation:**
```python
model = IsolationForest(
    n_estimators=100,      # Number of trees
    max_samples='auto',    # Subsample size
    contamination=0.1,     # Expected fraud rate (10%)
    random_state=42,
    n_jobs=-1
)

# Training (unsupervised)
model.fit(X)

# Prediction
anomaly_scores = model.decision_function(X)
predictions = model.predict(X)  # -1 = anomaly, 1 = normal
```

**Fraud Indicators:**
```python
# Financial anomalies
financial_anomaly = (
    (debt_to_equity > 2.0) +
    (credit_score < 500) +
    (profit_margin < 0.05)
)

# Operational anomalies
operational_anomaly = (
    (on_time_delivery_rate < 0.70) +
    (defect_rate > 0.05) +
    (quality_score < 0.70)
)

# Fraud suspicion score
fraud_score = (financial_anomaly + operational_anomaly) / 6
```

#### 5.1.2 One-Class SVM

**Algorithm Overview:**
Learns decision boundary around normal data to identify outliers.

**Mathematical Formulation:**
```
Objective:
min ½||w||² - ρ + (1/νn)·Σᵢξᵢ

subject to:
w·φ(xᵢ) ≥ ρ - ξᵢ
ξᵢ ≥ 0

Decision Function:
f(x) = sign(w·φ(x) - ρ)
```

**Implementation:**
```python
model = OneClassSVM(
    kernel='rbf',
    gamma='auto',
    nu=0.1  # Upper bound on fraction of outliers
)
```

#### 5.1.3 Local Outlier Factor (LOF)

**Algorithm Overview:**
Identifies outliers based on local density deviation.

**Key Metrics:**
```
Local Reachability Density (LRD):
LRD(x) = 1 / (Σ reachability_distance(x, neighbor) / k)

Local Outlier Factor:
LOF(x) = (Σ LRD(neighbor) / LRD(x)) / k

Interpretation:
- LOF ≈ 1: Similar density to neighbors (normal)
- LOF >> 1: Much lower density (outlier)
```

### 5.2 Supervised Fraud Detection

**Approach**: Train classifier on labeled fraud cases.

**Feature Engineering for Fraud:**
```python
features = {
    # Velocity features
    'transaction_velocity': count_per_month,
    'order_value_spike': (current_value - avg_value) / std_value,
    
    # Consistency features
    'address_changes': count_address_changes_90d,
    'contact_changes': count_contact_changes_90d,
    
    # Behavior features
    'unusual_order_patterns': deviation_from_typical_pattern,
    'geographic_inconsistency': distance_from_usual_location
}
```

**Model Selection:**
- **Random Forest**: High accuracy, handles imbalance well
- **Gradient Boosting**: Best for fraud patterns
- **Neural Networks**: For complex, evolving fraud schemes

---

## 6. Multi-Criteria Decision Analysis (MCDA)

### 6.1 TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)

**Algorithm Overview:**
Ranks alternatives based on distance from ideal best and worst solutions.

**Step-by-Step Methodology:**

**Step 1: Create Decision Matrix**
```
        Cost  Quality  Delivery  Risk   ESG
Sup_A   [100,   0.8,    0.9,    0.3,   0.7]
Sup_B   [120,   0.9,    0.8,    0.2,   0.8]
Sup_C   [90,    0.7,    0.85,   0.4,   0.6]
```

**Step 2: Normalize Decision Matrix**
```
Normalized value:
rᵢⱼ = xᵢⱼ / √(Σᵢ xᵢⱼ²)

Example:
r₁₁ = 100 / √(100² + 120² + 90²) = 0.5547
```

**Step 3: Apply Weights**
```
Weighted matrix:
vᵢⱼ = wⱼ · rᵢⱼ

where wⱼ = weight for criterion j
```

**Step 4: Determine Ideal Solutions**
```
For benefit criteria (higher is better):
A⁺ⱼ = max(vᵢⱼ)  # Ideal best
A⁻ⱼ = min(vᵢⱼ)  # Ideal worst

For cost criteria (lower is better):
A⁺ⱼ = min(vᵢⱼ)  # Ideal best
A⁻ⱼ = max(vᵢⱼ)  # Ideal worst
```

**Step 5: Calculate Distances**
```
Euclidean Distance from Ideal Best:
D⁺ᵢ = √[Σⱼ(vᵢⱼ - A⁺ⱼ)²]

Distance from Ideal Worst:
D⁻ᵢ = √[Σⱼ(vᵢⱼ - A⁻ⱼ)²]
```

**Step 6: Calculate TOPSIS Score**
```
Relative Closeness:
Cᵢ = D⁻ᵢ / (D⁺ᵢ + D⁻ᵢ)

where Cᵢ ∈ [0, 1]

Higher Cᵢ → Better alternative
```

**Implementation:**
```python
def calculate_topsis(df, criteria_weights, benefit_criteria):
    # Step 2: Normalize
    normalized = df / np.sqrt((df**2).sum(axis=0))
    
    # Step 3: Apply weights
    weighted = normalized * criteria_weights
    
    # Step 4: Ideal solutions
    ideal_best = weighted.max(axis=0)  # For benefit criteria
    ideal_worst = weighted.min(axis=0)
    
    # Step 5: Distances
    dist_best = np.sqrt(((weighted - ideal_best)**2).sum(axis=1))
    dist_worst = np.sqrt(((weighted - ideal_worst)**2).sum(axis=1))
    
    # Step 6: TOPSIS score
    scores = dist_worst / (dist_best + dist_worst)
    
    return scores
```

**Real-World Application:**
```python
# Criteria weights (must sum to 1)
weights = {
    'unit_cost': 0.30,
    'quality_score': 0.25,
    'on_time_delivery_rate': 0.20,
    'geopolitical_risk_score': 0.15,
    'esg_score': 0.10
}

# Benefit criteria (higher is better)
benefit_criteria = ['quality_score', 'on_time_delivery_rate', 'esg_score']

# Run TOPSIS
rankings = calculate_topsis(suppliers_df, weights, benefit_criteria)
```

### 6.2 AHP (Analytic Hierarchy Process)

**Algorithm Overview:**
Decomposes complex decision into pairwise comparisons using Saaty's scale.

**Saaty's Comparison Scale:**
```
1 = Equal importance
3 = Moderate importance
5 = Strong importance
7 = Very strong importance
9 = Extreme importance
2, 4, 6, 8 = Intermediate values
```

**Step-by-Step Methodology:**

**Step 1: Create Pairwise Comparison Matrix**
```
         Cost  Quality  Delivery  Risk
Cost     [1,    3,       5,       7  ]
Quality  [1/3,  1,       3,       5  ]
Delivery [1/5,  1/3,     1,       3  ]
Risk     [1/7,  1/5,     1/3,     1  ]

Note: aᵢⱼ = 1/aⱼᵢ (reciprocal property)
```

**Step 2: Calculate Priority Vector (Eigenvector Method)**
```
A·w = λₘₐₓ·w

where:
- A = pairwise comparison matrix
- w = priority vector (weights)
- λₘₐₓ = principal eigenvalue

Solve using power method:
1. Start with random w⁰
2. Iterate: wᵏ⁺¹ = A·wᵏ / ||A·wᵏ||
3. Converge to principal eigenvector
4. Normalize: w = eigenvector / sum(eigenvector)
```

**Step 3: Calculate Consistency Ratio**
```
Consistency Index (CI):
CI = (λₘₐₓ - n) / (n - 1)

Random Consistency Index (RI):
n:  1    2    3     4     5     6     7     8
RI: 0    0   0.58  0.90  1.12  1.24  1.32  1.41

Consistency Ratio (CR):
CR = CI / RI

Acceptance Criterion:
- CR < 0.10: Acceptable consistency
- CR ≥ 0.10: Revise comparisons
```

**Implementation:**
```python
def calculate_ahp_weights(pairwise_matrix):
    # Calculate eigenvalues and eigenvectors
    eigenvalues, eigenvectors = np.linalg.eig(pairwise_matrix)
    
    # Get principal eigenvector
    max_idx = np.argmax(eigenvalues.real)
    principal_eigenvector = eigenvectors[:, max_idx].real
    
    # Normalize to get weights
    weights = principal_eigenvector / principal_eigenvector.sum()
    
    # Calculate consistency ratio
    lambda_max = eigenvalues[max_idx].real
    n = len(pairwise_matrix)
    CI = (lambda_max - n) / (n - 1)
    
    RI = {3: 0.58, 4: 0.90, 5: 1.12}  # Random index table
    CR = CI / RI[n]
    
    return weights, CR
```

**Step 4: Rank Alternatives**
```python
def rank_alternatives(suppliers_df, criteria_weights):
    # Normalize each criterion
    normalized = suppliers_df / suppliers_df.sum(axis=0)
    
    # Calculate weighted scores
    scores = (normalized * criteria_weights).sum(axis=1)
    
    return scores
```

**Real-World Example:**
```python
# Pairwise comparisons from decision maker
comparisons = {
    ('cost', 'quality'): 3,      # Cost 3x more important than quality
    ('cost', 'delivery'): 5,     # Cost 5x more important than delivery
    ('quality', 'delivery'): 2   # Quality 2x more important than delivery
}

# Calculate weights
weights, consistency_ratio = calculate_ahp_weights(comparisons)

if consistency_ratio < 0.10:
    print(f"Consistent! CR = {consistency_ratio:.3f}")
    rankings = rank_alternatives(suppliers_df, weights)
else:
    print("Inconsistent comparisons, please revise")
```

**Advantages of AHP:**
1. **Structured Decision-Making**: Breaks complex problems into hierarchy
2. **Consistency Check**: CR ensures logical comparisons
3. **Stakeholder Alignment**: Multiple decision-makers can provide inputs
4. **Sensitivity Analysis**: Test robustness of rankings

---

## 7. Explainable AI & Ethics

### 7.1 SHAP (SHapley Additive exPlanations)

**Theoretical Foundation:**
Based on Shapley values from cooperative game theory.

**Shapley Value Definition:**
```
φᵢ(v) = Σ [|S|!(|N|-|S|-1)! / |N|!] · [v(S ∪ {i}) - v(S)]
      S⊆N\{i}

where:
- N = set of all features
- S = subset of features
- v(S) = model prediction using features in S
- φᵢ = contribution of feature i
```

**SHAP Properties:**
```
1. Local Accuracy:
   f(x) = φ₀ + Σᵢφᵢ(x)

2. Missingness:
   xᵢ = 0 ⟹ φᵢ = 0

3. Consistency:
   f'(x) - f'(x\i) ≥ f(x) - f(x\i) ⟹ φᵢ(f', x) ≥ φᵢ(f, x)
```

**TreeExplainer Algorithm:**
For tree-based models (XGBoost, Random Forest), uses efficient polynomial-time computation.

**Implementation:**
```python
import shap

# Create explainer
explainer = shap.TreeExplainer(xgboost_model)

# Calculate SHAP values
shap_values = explainer.shap_values(X)

# SHAP value interpretation:
# - Positive: Feature increases prediction
# - Negative: Feature decreases prediction
# - Magnitude: Strength of effect
```

**Visualization Types:**

**1. Force Plot (Single Prediction):**
```python
shap.force_plot(
    explainer.expected_value,
    shap_values[0, :],
    X.iloc[0, :]
)
# Shows how features push prediction above/below baseline
```

**2. Summary Plot (Feature Importance):**
```python
shap.summary_plot(shap_values, X)
# Combines feature importance with feature effects
```

**3. Dependence Plot (Feature Interaction):**
```python
shap.dependence_plot('quality_score', shap_values, X)
# Shows how feature value affects predictions
```

**Real-World Application:**
```
Supplier SUP_0001 predicted score: 0.72

SHAP Explanation:
Base value: 0.50 (average score)

Features pushing score UP (+0.22):
+ quality_score = 0.85:      +0.12
+ esg_score = 0.80:          +0.08
+ on_time_delivery = 0.90:   +0.05

Features pushing score DOWN (-0.03):
- years_in_business = 5:     -0.03
```

### 7.2 LIME (Local Interpretable Model-agnostic Explanations)

**Algorithm Overview:**
Explains individual predictions by learning interpretable local approximation.

**Methodology:**

**Step 1: Perturb Data**
```python
# Generate perturbations around instance x
perturbed_samples = x + np.random.normal(0, 0.1, (n_samples, n_features))
```

**Step 2: Get Model Predictions**
```python
predictions = model.predict(perturbed_samples)
```

**Step 3: Weight by Proximity**
```python
# Kernel function (exponential)
distances = euclidean_distances(perturbed_samples, x)
weights = np.exp(-(distances ** 2) / kernel_width ** 2)
```

**Step 4: Learn Linear Model**
```python
# Fit weighted linear regression
explainer = Ridge(alpha=1)
explainer.fit(perturbed_samples, predictions, sample_weight=weights)

# Coefficients = feature importance
explanation = dict(zip(feature_names, explainer.coef_))
```

**Implementation:**
```python
from lime.lime_tabular import LimeTabularExplainer

explainer = LimeTabularExplainer(
    X_train.values,
    feature_names=feature_names,
    mode='regression',
    kernel_width=3
)

explanation = explainer.explain_instance(
    x,  # Instance to explain
    model.predict,
    num_features=10
)

# Get feature contributions
explanation.as_list()
# [('quality_score > 0.8', 0.15), ('esg_score > 0.7', 0.08), ...]
```

**Interpretation:**
```
LIME creates a simple, interpretable model (linear regression) 
that locally approximates the complex model around the prediction point.

Feature: quality_score > 0.8
Contribution: +0.15
Meaning: For suppliers with quality_score > 0.8, 
the prediction increases by 0.15 on average.
```

### 7.3 Bias Detection & Fairness

**Objective**: Ensure model doesn't discriminate based on protected attributes.

**Metrics:**

**1. Demographic Parity:**
```
P(ŷ=1|A=a) = P(ŷ=1|A=b)

for all groups a, b

Example:
P(high_score | country=USA) ≈ P(high_score | country=India)
```

**2. Equalized Odds:**
```
P(ŷ=1|y=1, A=a) = P(ŷ=1|y=1, A=b)  # True positive rate
P(ŷ=1|y=0, A=a) = P(ŷ=1|y=0, A=b)  # False positive rate
```

**3. Correlation Analysis:**
```python
def detect_bias(feature, predictions):
    # Calculate correlation
    if feature.dtype == 'object':
        # Categorical: use Spearman correlation
        encoded = LabelEncoder().fit_transform(feature)
        correlation, p_value = spearmanr(encoded, predictions)
    else:
        # Numerical: use Pearson correlation
        correlation, p_value = pearsonr(feature, predictions)
    
    # Interpret
    if abs(correlation) > 0.5 and p_value < 0.05:
        return "Strong bias detected"
    elif abs(correlation) > 0.3 and p_value < 0.05:
        return "Moderate bias detected"
    else:
        return "No significant bias"
```

**Group Analysis:**
```python
# Compare predictions across groups
def group_analysis(feature, predictions):
    groups = pd.DataFrame({
        'group': feature,
        'prediction': predictions
    })
    
    stats = groups.groupby('group').agg({
        'prediction': ['mean', 'std', 'count']
    })
    
    return stats
```

**Real-World Application:**
```
Bias Detection on 'country':

Group Analysis:
Country  | Avg Prediction | Std Dev | Count
---------|---------------|---------|------
USA      | 0.72          | 0.15    | 25
China    | 0.68          | 0.18    | 30
Germany  | 0.75          | 0.12    | 20
India    | 0.65          | 0.20    | 25

Correlation: 0.12 (p=0.15)
Interpretation: No significant bias based on country
```

---

## 8. Natural Language Processing (Contract Analysis)

### 8.1 spaCy Pipeline

**Architecture:**
```
Raw Text → Tokenizer → Tagger → Parser → NER → Custom Components
```

**Components:**

**1. Tokenization:**
```python
import spacy

nlp = spacy.load('en_core_web_sm')
doc = nlp("The supplier shall deliver goods by March 31, 2025.")

tokens = [token.text for token in doc]
# ['The', 'supplier', 'shall', 'deliver', 'goods', 'by', 'March', '31', ',', '2025', '.']
```

**2. Part-of-Speech Tagging:**
```python
pos_tags = [(token.text, token.pos_) for token in doc]
# [('supplier', 'NOUN'), ('shall', 'AUX'), ('deliver', 'VERB'), ...]
```

**3. Dependency Parsing:**
```python
dependencies = [(token.text, token.dep_, token.head.text) for token in doc]
# [('supplier', 'nsubj', 'deliver'), ('goods', 'dobj', 'deliver'), ...]
```

**4. Named Entity Recognition:**
```python
entities = [(ent.text, ent.label_) for ent in doc.ents]
# [('March 31, 2025', 'DATE')]
```

### 8.2 Contract Clause Extraction

**Key Information Extraction:**

```python
def extract_contract_entities(text):
    doc = nlp(text)
    
    entities = {
        'dates': [],
        'money': [],
        'organizations': [],
        'products': [],
        'locations': []
    }
    
    for ent in doc.ents:
        if ent.label_ == 'DATE':
            entities['dates'].append(ent.text)
        elif ent.label_ == 'MONEY':
            entities['money'].append(ent.text)
        elif ent.label_ == 'ORG':
            entities['organizations'].append(ent.text)
        elif ent.label_ == 'PRODUCT':
            entities['products'].append(ent.text)
        elif ent.label_ in ['GPE', 'LOC']:
            entities['locations'].append(ent.text)
    
    return entities
```

**Risk Clause Detection:**
```python
risk_patterns = [
    r'(?i)(liability|indemnif|penalty|damages)',
    r'(?i)(termination|breach|default)',
    r'(?i)(force majeure|act of god)',
    r'(?i)(confidential|proprietary|intellectual property)'
]

def detect_risk_clauses(text):
    doc = nlp(text)
    risk_clauses = []
    
    for sent in doc.sents:
        for pattern in risk_patterns:
            if re.search(pattern, sent.text):
                risk_clauses.append({
                    'clause': sent.text,
                    'risk_type': pattern,
                    'severity': calculate_severity(sent.text)
                })
    
    return risk_clauses
```

### 8.3 Sentiment Analysis

**Approach**: Analyze tone of contract language.

```python
from textblob import TextBlob

def analyze_contract_sentiment(text):
    blob = TextBlob(text)
    
    # Polarity: -1 (negative) to +1 (positive)
    polarity = blob.sentiment.polarity
    
    # Subjectivity: 0 (objective) to 1 (subjective)
    subjectivity = blob.sentiment.subjectivity
    
    return {
        'polarity': polarity,
        'subjectivity': subjectivity,
        'tone': 'favorable' if polarity > 0.1 else 'unfavorable' if polarity < -0.1 else 'neutral'
    }
```

### 8.4 Transformer Models (Optional Enhancement)

**BERT for Contract Understanding:**
```python
from transformers import AutoTokenizer, AutoModel

tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
model = AutoModel.from_pretrained('bert-base-uncased')

def embed_contract_clause(text):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
    outputs = model(**inputs)
    
    # Use [CLS] token embedding
    embedding = outputs.last_hidden_state[:, 0, :].detach().numpy()
    
    return embedding
```

---

## 9. Transparency & Supply Chain Visualization

### 9.1 Supply Chain Network Analysis

**Graph Representation:**
```python
G = {
    'nodes': [
        {'id': 'OEM', 'type': 'manufacturer'},
        {'id': 'SUP_001', 'type': 'tier1'},
        {'id': 'SUP_002', 'type': 'tier2'},
    ],
    'edges': [
        {'source': 'SUP_002', 'target': 'SUP_001', 'weight': 1000000},
        {'source': 'SUP_001', 'target': 'OEM', 'weight': 5000000},
    ]
}
```

**Network Metrics:**

**1. Centrality Measures:**
```python
# Degree Centrality
degree_centrality = len(supplier_connections) / (total_nodes - 1)

# Betweenness Centrality (supply chain bottlenecks)
def betweenness_centrality(node, graph):
    shortest_paths_through_node = 0
    total_shortest_paths = 0
    
    for s in graph.nodes:
        for t in graph.nodes:
            if s != t and s != node and t != node:
                paths = all_shortest_paths(s, t, graph)
                paths_through_node = [p for p in paths if node in p]
                
                shortest_paths_through_node += len(paths_through_node)
                total_shortest_paths += len(paths)
    
    return shortest_paths_through_node / total_shortest_paths
```

**2. Supply Chain Resilience:**
```python
def calculate_resilience(graph):
    # Node redundancy
    redundancy = average_degree / max_degree
    
    # Path diversity
    diversity = avg_alternate_paths / total_paths
    
    # Geographic distribution
    geo_diversity = unique_countries / total_suppliers
    
    resilience_score = (
        redundancy * 0.4 +
        diversity * 0.3 +
        geo_diversity * 0.3
    )
    
    return resilience_score
```

### 9.2 Geographic Risk Mapping

**Geopolitical Risk Score Calculation:**
```python
def calculate_geopolitical_risk(country):
    factors = {
        'political_stability': get_wgi_score(country, 'political_stability'),
        'regulatory_quality': get_wgi_score(country, 'regulatory_quality'),
        'rule_of_law': get_wgi_score(country, 'rule_of_law'),
        'control_of_corruption': get_wgi_score(country, 'corruption'),
        'trade_freedom': get_economic_freedom_index(country)
    }
    
    # Aggregate (lower WGI scores = higher risk)
    risk_score = 1 - weighted_average(factors)
    
    return risk_score
```

**Heatmap Generation:**
```python
import plotly.graph_objects as go

def create_risk_heatmap(suppliers_df):
    risk_by_country = suppliers_df.groupby('country').agg({
        'geopolitical_risk_score': 'mean',
        'supplier_id': 'count'
    })
    
    fig = go.Figure(data=go.Choropleth(
        locations=risk_by_country.index,
        z=risk_by_country['geopolitical_risk_score'],
        locationmode='country names',
        colorscale='Reds',
        colorbar_title='Risk Score'
    ))
    
    return fig
```

---

## 10. Model Training & Deployment

### 10.1 Training Pipeline

**Complete Training Workflow:**

```python
class ModelTrainer:
    def train_all_models(self):
        # 1. Load data
        data = data_loader.load_suppliers()
        
        # 2. Feature engineering
        X, y = self.prepare_training_data(data)
        
        # 3. Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # 4. Train multiple models
        models = {
            'xgboost': self.train_xgboost(X_train, y_train),
            'random_forest': self.train_random_forest(X_train, y_train),
            'gradient_boosting': self.train_gradient_boosting(X_train, y_train),
            'svm': self.train_svm(X_train, y_train),
            'neural_network': self.train_neural_network(X_train, y_train)
        }
        
        # 5. Evaluate
        results = {}
        for name, model in models.items():
            y_pred = model.predict(X_test)
            results[name] = {
                'r2_score': r2_score(y_test, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_test, y_pred))
            }
        
        # 6. Save models
        for name, model in models.items():
            joblib.dump(model, f'models/{name}.pkl')
        
        return results
```

### 10.2 Cross-Validation

**K-Fold Cross-Validation:**
```python
from sklearn.model_selection import cross_val_score

def evaluate_with_cv(model, X, y, cv=5):
    # R² scores across folds
    r2_scores = cross_val_score(model, X, y, cv=cv, scoring='r2')
    
    # RMSE scores
    rmse_scores = -cross_val_score(
        model, X, y, cv=cv, 
        scoring='neg_root_mean_squared_error'
    )
    
    return {
        'r2_mean': r2_scores.mean(),
        'r2_std': r2_scores.std(),
        'rmse_mean': rmse_scores.mean(),
        'rmse_std': rmse_scores.std()
    }
```

### 10.3 Hyperparameter Tuning

**Grid Search:**
```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    'max_depth': [3, 5, 7, 9],
    'learning_rate': [0.01, 0.05, 0.1, 0.2],
    'n_estimators': [50, 100, 200],
    'subsample': [0.6, 0.8, 1.0]
}

grid_search = GridSearchCV(
    XGBRegressor(),
    param_grid,
    cv=5,
    scoring='r2',
    n_jobs=-1,
    verbose=1
)

grid_search.fit(X_train, y_train)

best_model = grid_search.best_estimator_
best_params = grid_search.best_params_
```

**Randomized Search (Faster):**
```python
from sklearn.model_selection import RandomizedSearchCV

param_distributions = {
    'max_depth': np.arange(3, 15),
    'learning_rate': np.logspace(-3, 0, 50),
    'n_estimators': np.arange(50, 500, 50),
    'subsample': np.linspace(0.5, 1.0, 10)
}

random_search = RandomizedSearchCV(
    XGBRegressor(),
    param_distributions,
    n_iter=50,  # Number of parameter combinations to try
    cv=5,
    scoring='r2',
    n_jobs=-1,
    random_state=42
)

random_search.fit(X_train, y_train)
```

### 10.4 Model Monitoring

**Performance Tracking:**
```python
class ModelMonitor:
    def monitor_predictions(self, model, X_new):
        predictions = model.predict(X_new)
        
        # Check for prediction drift
        drift_score = self.calculate_drift(predictions)
        
        if drift_score > threshold:
            alert("Model drift detected! Retrain recommended.")
        
        # Log predictions
        self.log_predictions(predictions, X_new)
    
    def calculate_drift(self, new_predictions):
        # Compare distribution to training predictions
        ks_statistic, p_value = ks_2samp(
            self.training_predictions,
            new_predictions
        )
        
        return ks_statistic
```

---

## Appendix A: Mathematical Formulas Summary

### Classification Metrics
```
Accuracy = (TP + TN) / (TP + TN + FP + FN)
Precision = TP / (TP + FP)
Recall = TP / (TP + FN)
F1-Score = 2 · (Precision · Recall) / (Precision + Recall)
```

### Regression Metrics
```
MAE = (1/n) Σ|yᵢ - ŷᵢ|
MSE = (1/n) Σ(yᵢ - ŷᵢ)²
RMSE = √MSE
R² = 1 - (Σ(yᵢ - ŷᵢ)²) / (Σ(yᵢ - ȳ)²)
```

### Statistical Tests
```
T-Test:
t = (x̄₁ - x̄₂) / √(s₁²/n₁ + s₂²/n₂)

Chi-Square Test:
χ² = Σ[(Oᵢ - Eᵢ)² / Eᵢ]

Kolmogorov-Smirnov Test:
D = max|F₁(x) - F₂(x)|
```

---

## Appendix B: Best Practices

### 1. Data Quality
- **Missing Values**: Use domain knowledge for imputation
- **Outliers**: Investigate before removal (might be valid)
- **Class Imbalance**: Use SMOTE, class weights, or stratified sampling

### 2. Feature Engineering
- **Domain Knowledge**: Leverage supply chain expertise
- **Feature Selection**: Use Boruta, RFE, or LASSO
- **Scaling**: StandardScaler for distance-based algorithms

### 3. Model Selection
- **Small Data (<1000 samples)**: Random Forest, Gradient Boosting
- **Large Data (>10000 samples)**: XGBoost, Neural Networks
- **Interpretability Required**: Linear models, Decision Trees
- **Best Performance**: Ensemble methods

### 4. Deployment
- **API Design**: RESTful, versioned, documented (OpenAPI)
- **Model Versioning**: Track model versions with metadata
- **Monitoring**: Log predictions, detect drift, schedule retraining
- **A/B Testing**: Compare new models before full deployment

---

## Appendix C: References

1. **TOPSIS**: Hwang, C.L. and Yoon, K. (1981). Multiple Attribute Decision Making
2. **AHP**: Saaty, T.L. (1980). The Analytic Hierarchy Process
3. **XGBoost**: Chen, T. and Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System
4. **SHAP**: Lundberg, S.M. and Lee, S.I. (2017). A Unified Approach to Interpreting Model Predictions
5. **LIME**: Ribeiro, M.T., Singh, S., and Guestrin, C. (2016). "Why Should I Trust You?"
6. **Isolation Forest**: Liu, F.T., Ting, K.M., and Zhou, Z.H. (2008). Isolation Forest

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-12  
**Author**: AI Supplier Selection Platform Team
