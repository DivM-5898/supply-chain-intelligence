# AI-Driven Fraud & Disruption Prediction System

## Project Overview
This project implements machine learning solutions for detecting fraudulent activities and predicting supply chain disruptions in real-time.

## Real-World Supply Chain Challenge
Supply chains face two critical risks:
1. **Fraud**: Invoice fraud, payment manipulation, counterfeit suppliers, document forgery
2. **Disruptions**: Natural disasters, geopolitical events, supplier failures, logistics breakdowns

These issues cost companies billions annually and can severely impact operations. Current manual detection methods are slow and miss sophisticated fraud patterns.

## AI-Driven Solution

### 1. Fraud Detection System
- **Anomaly Detection**: Isolation Forest, One-Class SVM for unusual transaction patterns
- **Classification Models**: Random Forest, XGBoost, Neural Networks for fraud prediction
- **Document Verification**: Computer Vision + NLP for invoice/document authenticity
- **Supplier Authentication**: Network analysis and behavioral profiling

### 2. Disruption Prediction System
- **Time Series Forecasting**: LSTM, ARIMA, Prophet for demand/supply predictions
- **Risk Scoring**: Ensemble models for geopolitical, environmental, financial risks
- **Early Warning System**: Real-time monitoring with ML-based alerts
- **Impact Assessment**: Predictive models for disruption severity

## Project Structure
```
.
├── src/
│   ├── fraud_detection/          # Fraud detection models
│   │   ├── anomaly_detection.py
│   │   ├── invoice_fraud.py
│   │   ├── payment_fraud.py
│   │   └── supplier_verification.py
│   ├── disruption_prediction/    # Disruption prediction models
│   │   ├── time_series_models.py
│   │   ├── risk_scoring.py
│   │   ├── impact_prediction.py
│   │   └── early_warning.py
│   ├── preprocessing/            # Data preprocessing
│   │   ├── feature_engineering.py
│   │   ├── data_cleaning.py
│   │   └── data_loader.py
│   └── utils/                    # Utilities
│       ├── model_evaluation.py
│       ├── visualization.py
│       └── config.py
├── data/
│   ├── raw/                      # Raw data
│   ├── processed/                # Processed data
│   └── models/                   # Saved models
├── notebooks/                    # Jupyter notebooks
│   ├── 01_EDA.ipynb
│   ├── 02_fraud_modeling.ipynb
│   └── 03_disruption_modeling.ipynb
├── api/                          # REST API
│   ├── app.py
│   └── endpoints/
├── tests/                        # Unit tests
├── docs/                         # Documentation
└── requirements.txt              # Dependencies
```

## Key Features

### Fraud Detection
1. **Transaction Anomaly Detection**
   - Detect unusual payment amounts, frequencies, patterns
   - Identify outlier behaviors in supplier transactions

2. **Invoice Fraud Detection**
   - Duplicate invoice detection
   - Price manipulation identification
   - Fake vendor detection

3. **Document Verification**
   - OCR + NLP for document authenticity
   - Pattern recognition for forged documents

4. **Supplier Risk Profiling**
   - Behavioral analysis
   - Network graph analysis for suspicious connections

### Disruption Prediction
1. **Demand Forecasting**
   - LSTM-based time series prediction
   - Seasonal pattern recognition

2. **Supply Risk Assessment**
   - Geopolitical risk scoring
   - Weather/natural disaster prediction impact
   - Financial health monitoring

3. **Logistics Disruption Prediction**
   - Route risk analysis
   - Carrier reliability prediction
   - Port congestion forecasting

4. **Multi-source Risk Aggregation**
   - News sentiment analysis
   - Social media monitoring
   - Economic indicators

## Technology Stack
- **ML Frameworks**: scikit-learn, XGBoost, TensorFlow/Keras
- **Time Series**: Prophet, statsmodels
- **NLP**: spaCy, transformers, NLTK
- **Computer Vision**: OpenCV, PIL
- **API**: FastAPI
- **Data Processing**: pandas, numpy
- **Visualization**: matplotlib, seaborn, plotly
- **Monitoring**: MLflow

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [x] Project structure setup
- [ ] Data collection and preparation
- [ ] Exploratory Data Analysis (EDA)
- [ ] Feature engineering pipeline

### Phase 2: Fraud Detection Models (Weeks 3-4)
- [ ] Anomaly detection implementation
- [ ] Invoice fraud classification
- [ ] Payment pattern analysis
- [ ] Model evaluation and tuning

### Phase 3: Disruption Prediction Models (Weeks 5-6)
- [ ] Time series forecasting models
- [ ] Risk scoring algorithms
- [ ] Early warning system
- [ ] Integration with external data sources

### Phase 4: Integration & API (Week 7)
- [ ] REST API development
- [ ] Real-time prediction endpoints
- [ ] Model serving infrastructure
- [ ] Alert notification system

### Phase 5: Dashboard & Deployment (Week 8)
- [ ] Monitoring dashboard
- [ ] Visualization components
- [ ] Documentation
- [ ] Deployment and testing

## Getting Started

### Installation
```bash
# Clone the repository
git clone <repo-url>
cd supply-chain-intelligence

# Switch to fraud-prediction branch
git checkout feature/fraud-prediction

# Install dependencies
pip install -r requirements.txt
```

### Usage
```python
# Example: Fraud Detection
from src.fraud_detection.invoice_fraud import InvoiceFraudDetector

detector = InvoiceFraudDetector()
result = detector.predict(invoice_data)
print(f"Fraud Probability: {result['fraud_probability']}")

# Example: Disruption Prediction
from src.disruption_prediction.time_series_models import DisruptionPredictor

predictor = DisruptionPredictor()
forecast = predictor.predict_disruption(supplier_id, days_ahead=30)
```

### API Endpoints
```bash
# Fraud detection
POST /api/v1/fraud/detect
POST /api/v1/fraud/invoice/verify

# Disruption prediction
POST /api/v1/disruption/predict
GET /api/v1/disruption/risk-score/{supplier_id}
```

## Model Performance Targets
- **Fraud Detection**: Precision > 90%, Recall > 85%
- **Disruption Prediction**: MAPE < 15% for 30-day forecasts
- **False Positive Rate**: < 5%
- **Inference Time**: < 100ms per prediction

## Ethical Considerations
- Data privacy and GDPR compliance
- Bias detection and mitigation in fraud models
- Transparent decision-making with explainable AI (SHAP, LIME)
- Regular audit trails and human-in-the-loop validation

## Contributors
- Divyansh Maiwar

## License
MIT License
