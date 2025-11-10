# AI Supplier Selection & Risk Management Dashboard

A comprehensive full-stack AI-powered platform for supplier evaluation, risk management, and procurement decision-making.

## 🎯 Project Overview

This application provides an executive-grade AI decision platform that empowers leadership with data-driven insights for supplier selection and risk management. The platform combines cutting-edge machine learning, natural language processing, and optimization algorithms to deliver actionable insights in real-time.

## 🏗️ Architecture

- **Backend**: FastAPI REST API (Python) - Handles ML models, NLP, data processing
- **Frontend**: Streamlit (Python) - Interactive dashboard with visualizations
- **Database**: PostgreSQL (Render free tier) - Data persistence
- **Deployment**: Two separate Render services (backend + frontend)

## 📋 Features

### Seven Analytical Capabilities

1. **Supplier Evaluation & Scoring** - ML-powered scoring using XGBoost and Random Forest
2. **Risk Profiling & Comparison** - Multi-dimensional risk analysis across suppliers
3. **Fraud & Disruption Prediction** - Predictive models for fraud and supply chain disruptions
4. **NLP Contract Analyzer** - BERT and spaCy for contract analysis and risk extraction
5. **Multi-Criteria Decision Support** - TOPSIS and AHP for optimal supplier selection
6. **Ethics & Compliance** - SHAP/LIME explainability and bias detection
7. **Transparency & Resilience** - Global supply chain visualization and resilience metrics

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL (for production)
- Virtual environment (recommended)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run main.py
```

### Generate Sample Data & Train Models

```bash
cd backend
python -m services.data_generator
python -m services.model_trainer
```

## 📁 Project Structure

```
AI_IN_OPERATIONS/
├── backend/          # FastAPI backend service
├── frontend/         # Streamlit frontend application
├── notebooks/        # Data exploration and model training
├── tests/           # Unit and integration tests
└── docs/            # Documentation
```

## 🛠️ Technology Stack

- **ML**: scikit-learn, XGBoost, Random Forest
- **NLP**: transformers (BERT), spaCy
- **Visualization**: Plotly, Matplotlib
- **Explainability**: SHAP, LIME
- **Decision Support**: TOPSIS, AHP
- **API**: FastAPI
- **Frontend**: Streamlit

## 📊 Key Questions Addressed

- How can AI assist in evaluating and selecting suppliers?
- What data sources are used for supplier risk profiling?
- How can ML models predict supplier disruptions or fraud?
- What role does NLP play in analyzing supplier documents?
- How can AI support multi-criteria decision-making?
- What are the ethical and compliance considerations?
- How can AI enhance transparency and resilience?

## 📝 License

MIT License

## 👥 Contributing

This is a group project for AI in Operations course.

