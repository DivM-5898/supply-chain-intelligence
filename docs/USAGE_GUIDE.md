# Usage Guide - Fraud & Disruption Prediction System

## Table of Contents
1. [Quick Start](#quick-start)
2. [Fraud Detection](#fraud-detection)
3. [Disruption Prediction](#disruption-prediction)
4. [API Usage](#api-usage)
5. [Training Models](#training-models)
6. [Deployment](#deployment)

## Quick Start

### Installation
```bash
# Clone repository
git clone <repo-url>
cd supply-chain-intelligence
git checkout feature/fraud-prediction

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the API
```bash
# Start the FastAPI server
cd api
python app.py

# Or using uvicorn directly
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Access the interactive API documentation at: http://localhost:8000/docs

## Fraud Detection

### 1. Transaction Anomaly Detection

#### Python Code
```python
from src.fraud_detection.anomaly_detection import TransactionAnomalyDetector
import pandas as pd

# Load transaction data
transactions = pd.read_csv('data/raw/transactions.csv')

# Initialize detector
detector = TransactionAnomalyDetector(contamination=0.05)

# Train on historical data
detector.fit(transactions, use_pca=True)

# Detect anomalies in new transactions
new_transactions = pd.read_csv('data/raw/new_transactions.csv')
results = detector.predict(new_transactions, ensemble=True)

# Get anomaly scores
print(f"Anomalies detected: {results['ensemble_predictions'].sum()}")

# Get explanation for a specific transaction
explanation = detector.get_anomaly_explanation(new_transactions, sample_idx=0)
print(explanation)
```

### 2. Invoice Fraud Detection

#### Python Code
```python
from src.fraud_detection.invoice_fraud import InvoiceFraudDetector, extract_invoice_features
import pandas as pd
import numpy as np

# Load invoice data with labels
invoices = pd.read_csv('data/raw/invoices_labeled.csv')

# Extract features
features = extract_invoice_features(invoices)

# Prepare labels
y = invoices['is_fraud'].values

# Initialize and train detector
detector = InvoiceFraudDetector(model_type='xgboost')
metrics = detector.fit(features, y, validation_split=0.2)

# Predict on new invoices
new_invoices = pd.read_csv('data/raw/new_invoices.csv')
new_features = extract_invoice_features(new_invoices)

results = detector.predict(new_features, return_proba=True, check_duplicates=True)

# High-risk invoices
high_risk = results['fraud_probability'] > 0.7
print(f"High-risk invoices: {high_risk.sum()}")

# Feature importance
importance = detector.get_feature_importance(top_n=10)
print(importance)

# Save model
detector.save_model('data/models/invoice_fraud_detector.pkl')
```

### 3. API-based Fraud Detection

#### cURL Example
```bash
# Detect transaction fraud
curl -X POST "http://localhost:8000/api/v1/fraud/detect/transaction" \
  -H "Content-Type: application/json" \
  -d '{
    "transactions": [
      {
        "transaction_id": "TXN001",
        "supplier_id": "SUP123",
        "amount": 50000.00,
        "timestamp": "2025-01-15T14:30:00",
        "payment_method": "wire_transfer"
      }
    ]
  }'

# Detect invoice fraud
curl -X POST "http://localhost:8000/api/v1/fraud/detect/invoice" \
  -H "Content-Type: application/json" \
  -d '{
    "invoices": [
      {
        "invoice_number": "INV-2025-001",
        "supplier_id": "SUP123",
        "amount": 75000.00,
        "invoice_date": "2025-01-15",
        "payment_terms": "Net 30",
        "line_items": 5
      }
    ]
  }'
```

#### Python Requests
```python
import requests
import json

# Transaction fraud detection
transaction_data = {
    "transactions": [
        {
            "transaction_id": "TXN001",
            "supplier_id": "SUP123",
            "amount": 50000.00,
            "timestamp": "2025-01-15T14:30:00",
            "payment_method": "wire_transfer"
        }
    ]
}

response = requests.post(
    "http://localhost:8000/api/v1/fraud/detect/transaction",
    json=transaction_data
)

result = response.json()
print(f"Fraud detected: {result['fraud_detected']}")
print(f"Predictions: {result['predictions']}")
```

## Disruption Prediction

### 1. Time Series Forecasting with LSTM

#### Python Code
```python
from src.disruption_prediction.time_series_models import DisruptionPredictor
import pandas as pd
import numpy as np

# Load historical demand data
demand_data = pd.read_csv('data/raw/demand_history.csv', index_col='date', parse_dates=True)

# Initialize predictor
predictor = DisruptionPredictor(model_type='lstm')

# Train model
metrics = predictor.fit(
    demand_data['quantity'],
    validation_split=0.2,
    epochs=50,
    batch_size=32
)

# Predict 30 days ahead
historical_values = demand_data['quantity'].values[-60:]  # Last 60 days
forecast = predictor.predict(steps_ahead=30, X=historical_values)

print(f"30-day forecast: {forecast}")

# Save model
predictor.save_model('data/models/lstm_demand_predictor')
```

### 2. ARIMA for Time Series

```python
from src.disruption_prediction.time_series_models import DisruptionPredictor
import pandas as pd

# Load data
data = pd.read_csv('data/raw/supply_chain_metrics.csv', index_col='date', parse_dates=True)

# Initialize ARIMA predictor
predictor = DisruptionPredictor(model_type='arima')

# Train
metrics = predictor.fit(data['metric_value'], order=(5, 1, 2))

# Forecast
forecast = predictor.predict(steps_ahead=14)  # 2 weeks ahead

print(f"Forecast: {forecast}")
```

### 3. Risk Score Calculation

```python
from src.disruption_prediction.time_series_models import RiskScoreCalculator

# Initialize calculator
calculator = RiskScoreCalculator()

# Supplier risk data (scores from 0 to 1)
supplier_data = {
    'geopolitical': 0.7,    # High geopolitical risk
    'financial': 0.4,       # Moderate financial risk
    'operational': 0.3,     # Low operational risk
    'environmental': 0.6,   # High environmental risk
    'supplier_specific': 0.5  # Medium supplier-specific risk
}

# Calculate risk score
result = calculator.calculate_risk_score(supplier_data)

print(f"Risk Level: {result['risk_level']}")
print(f"Total Score: {result['total_risk_score']:.2f}")
print(f"Recommendations: {result['recommendations']}")
```

### 4. API-based Disruption Prediction

```bash
# Predict disruptions
curl -X POST "http://localhost:8000/api/v1/disruption/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "supplier_id": "SUP123",
    "historical_data": {
      "values": [100, 105, 103, 110, 108, 115, 120, 118, 125, 130]
    },
    "steps_ahead": 30
  }'

# Calculate risk score
curl -X POST "http://localhost:8000/api/v1/disruption/risk-score" \
  -H "Content-Type: application/json" \
  -d '{
    "supplier_id": "SUP123",
    "geopolitical": 0.7,
    "financial": 0.4,
    "operational": 0.3,
    "environmental": 0.6,
    "supplier_specific": 0.5
  }'

# Get supplier risk score
curl -X GET "http://localhost:8000/api/v1/disruption/risk-score/SUP123"
```

## Training Models

### Fraud Detection Model Training

```python
from src.fraud_detection.invoice_fraud import InvoiceFraudDetector, extract_invoice_features
import pandas as pd

# Load labeled training data
df = pd.read_csv('data/processed/invoices_training.csv')

# Split features and labels
X = extract_invoice_features(df)
y = df['is_fraud'].values

# Train model
detector = InvoiceFraudDetector(model_type='xgboost')
metrics = detector.fit(X, y, validation_split=0.2)

# Evaluate
print(f"Validation AUC: {metrics['val_auc']:.4f}")

# Save model
detector.save_model('data/models/invoice_fraud_detector_v1.pkl')
```

### Disruption Prediction Model Training

```python
from src.disruption_prediction.time_series_models import DisruptionPredictor
import pandas as pd

# Load time series data
data = pd.read_csv('data/processed/demand_history.csv', parse_dates=['date'])
ts_data = pd.Series(data['demand'].values, index=data['date'])

# Train LSTM model
predictor = DisruptionPredictor(model_type='lstm')
metrics = predictor.fit(
    ts_data,
    validation_split=0.2,
    epochs=100,
    batch_size=32
)

print(f"Validation MAE: {metrics['val_mae']:.4f}")
print(f"Validation RMSE: {metrics['val_rmse']:.4f}")

# Save model
predictor.save_model('data/models/lstm_predictor_v1')
```

## Deployment

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t supply-chain-fraud-predictor .
docker run -p 8000:8000 supply-chain-fraud-predictor
```

### Production Considerations

1. **Model Serving**: Use model versioning and load pre-trained models
2. **Monitoring**: Implement MLflow or Weights & Biases for model tracking
3. **Scalability**: Deploy with Kubernetes for auto-scaling
4. **Security**: Add authentication (OAuth2, API keys)
5. **Logging**: Implement structured logging with ELK stack
6. **Database**: Connect to PostgreSQL/MongoDB for storing predictions
7. **Caching**: Use Redis for caching frequent requests

## Performance Targets

- **Inference Latency**: < 100ms per prediction
- **Fraud Detection Precision**: > 90%
- **Fraud Detection Recall**: > 85%
- **Disruption Forecast MAPE**: < 15% for 30-day horizon
- **API Throughput**: > 1000 requests/minute

## Troubleshooting

### Common Issues

1. **Model Not Fitted Error**
   - Solution: Train the model first or load a pre-trained model

2. **Memory Error with LSTM**
   - Solution: Reduce batch size or lookback window

3. **Poor Fraud Detection Performance**
   - Solution: Collect more labeled data, tune hyperparameters

4. **Time Series Forecast Instability**
   - Solution: Check for stationarity, apply differencing, use ARIMA

## Next Steps

1. Integrate with your existing data pipeline
2. Collect and label more training data
3. Implement A/B testing for model versions
4. Set up monitoring and alerting
5. Create dashboards for visualization

## Support

For issues or questions:
- Create an issue in the GitHub repository
- Contact: [your-email]
