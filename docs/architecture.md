# Architecture Documentation

## System Architecture Overview

The AI Supplier Selection & Risk Management Dashboard is a full-stack application with clear separation between frontend and backend components, designed for deployment on Render's free tier.

## Architecture Layers

### 1. User Layer
- **Technology**: Streamlit web interface
- **Components**: 7 specialized tabs for different analytical capabilities
- **Features**: Interactive visualizations, real-time updates, mobile-responsive design

### 2. Application Layer
- **Backend**: FastAPI REST API
- **Frontend**: Streamlit application
- **Components**:
  - Navigation handler
  - Session management
  - Model orchestration
  - API client for backend communication

### 3. AI Layer
- **ML Models**:
  - XGBoost (Supplier Scoring)
  - Random Forest (Supplier Scoring, Fraud Detection)
  - Logistic Regression (Risk Prediction)
  - Gradient Boosting (Fraud Detection)
  - Isolation Forest (Anomaly Detection)

- **NLP Models**:
  - BERT (Sentiment Analysis)
  - spaCy (Named Entity Recognition)

- **Decision Support**:
  - TOPSIS (Multi-criteria optimization)
  - AHP (Analytic Hierarchy Process)

- **Explainability**:
  - SHAP (Model interpretability)
  - LIME (Local explanations)

### 4. Data Layer
- **Data Sources**:
  - Supplier performance data
  - Financial metrics
  - Delivery history
  - Risk events
  - Geopolitical risk data
  - Contract documents

- **Preprocessing**:
  - Feature engineering
  - Data normalization
  - Missing value handling

### 5. Storage Layer
- **Database**: PostgreSQL (Render free tier)
- **File Storage**: Contract documents, model outputs
- **Model Storage**: Trained model files (.pkl)

### 6. Deployment Layer
- **Backend**: FastAPI on Render
- **Frontend**: Streamlit on Render
- **Version Control**: GitHub
- **CI/CD**: Automated deployment pipeline

## Data Flow

1. **User Input** → Streamlit Frontend
2. **API Request** → FastAPI Backend
3. **Data Loading** → Data Loader Service
4. **Preprocessing** → Preprocessing Pipeline
5. **Model Prediction** → ML/NLP Services
6. **Results** → API Response
7. **Visualization** → Streamlit Frontend

## API Endpoints

### Supplier Evaluation
- `POST /api/v1/suppliers/evaluate` - Evaluate suppliers
- `GET /api/v1/suppliers/compare-models` - Compare models
- `GET /api/v1/suppliers/feature-importance/{model_type}` - Feature importance

### Risk Profiling
- `POST /api/v1/risk/predict` - Predict risk
- `POST /api/v1/risk/anomalies` - Detect anomalies
- `GET /api/v1/risk/data-sources` - Data sources

### Fraud Detection
- `POST /api/v1/fraud/predict` - Predict fraud
- `POST /api/v1/fraud/compare-models` - Compare models

### NLP Contract
- `POST /api/v1/contracts/analyze` - Analyze contract
- `POST /api/v1/contracts/upload` - Upload contract
- `GET /api/v1/contracts/contracts` - List contracts

### Decision Support
- `POST /api/v1/decision/topsis` - TOPSIS ranking
- `POST /api/v1/decision/ahp` - AHP ranking

### Ethics & Compliance
- `POST /api/v1/ethics/explain` - Explain prediction
- `POST /api/v1/ethics/shap-values` - SHAP values
- `POST /api/v1/ethics/bias-detection` - Detect bias
- `GET /api/v1/ethics/esg-scores` - ESG scores

### Transparency
- `GET /api/v1/transparency/geographic-risk` - Geographic risk
- `GET /api/v1/transparency/supplier-network` - Supplier network
- `GET /api/v1/transparency/resilience-metrics` - Resilience metrics
- `GET /api/v1/transparency/transparency-scores` - Transparency scores

## Deployment Architecture

### Render Services

**Backend Service:**
- Type: Web Service
- Environment: Python
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Frontend Service:**
- Type: Web Service
- Environment: Python
- Build Command: `pip install -r requirements.txt`
- Start Command: `streamlit run main.py --server.port $PORT --server.address 0.0.0.0`

## Security Considerations

- CORS configuration for frontend-backend communication
- Environment variables for sensitive data
- Input validation using Pydantic models
- Error handling and logging

## Scalability

- Modular architecture allows independent scaling
- Stateless API design
- Caching for model predictions
- Efficient data loading and preprocessing

