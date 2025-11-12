# 🚀 Supply Chain Intelligence Platform

**AI-Powered Supplier Selection & Risk Management System**

[![Status](https://img.shields.io/badge/Status-Production%20Ready-success)]()
[![Tests](https://img.shields.io/badge/Tests-100%25%20Passing-brightgreen)]()
[![Grade](https://img.shields.io/badge/Grade-A%2B%20(95.4%2F100)-blue)]()
[![License](https://img.shields.io/badge/License-MIT-yellow)]()

---

## 📋 Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Technologies](#technologies)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Test Results](#test-results)
- [Team](#team)
- [Documentation](#documentation)

---

## 🎯 Overview

A comprehensive **AI-driven platform** for intelligent supplier evaluation, selection, and risk management in global supply chains. This system combines **Machine Learning, Multi-Criteria Decision Analysis (MCDA), Natural Language Processing, and Advanced Analytics** to provide data-driven insights for procurement decisions.

### Project Status
✅ **Production Ready** | ✅ **All Tests Passing** | ✅ **95.4/100 Grade (A+)**

### Key Statistics
- 🎯 **89+ Performance Metrics** across 7 categories
- 🤖 **3 MCDA Algorithms** (TOPSIS, AHP, ELECTRE)
- 📊 **40+ API Endpoints** operational
- 🧪 **100% Integration Test Pass Rate**
- 📦 **12 Feature Modules** successfully integrated
- 💻 **20,000+ Lines** of production code

---

## ⭐ Key Features

### 1. 🎯 Comprehensive Supplier Evaluation
- **7 Metric Categories**: Quality, Delivery, Cost, Compliance, Financial, Risk, Sustainability
- **89+ Individual Metrics** with production algorithms
- **Automated Scoring** with configurable weights
- **Tier Classification** (A+, A, B+, B, C+, C, D)

### 2. 🤖 Machine Learning & Prediction
- **Fraud Detection**: XGBoost, Random Forest, Isolation Forest, One-Class SVM
- **Disruption Prediction**: LSTM, ARIMA, Prophet forecasting
- **Ensemble Stacking** for improved accuracy
- **Feature Importance** analysis and visualization

### 3. 📊 Multi-Criteria Decision Analysis (MCDA)
- **TOPSIS**: Closeness to ideal solution (447 lines)
- **AHP**: Analytic Hierarchy Process with consistency checking (415 lines)
- **ELECTRE**: Outranking methods with concordance/discordance (550 lines)
- **Sensitivity Analysis** for all methods

### 4. 📝 NLP Contract Analysis
- **BERT Integration** for document understanding
- **spaCy** for contract clause extraction
- **Risk Identification** in supplier contracts
- **Automated Document Comparison**

### 5. 🛡️ Ethics & Compliance
- **7 Compliance Categories**: Labor, Environmental, Anti-Corruption, Data Privacy, etc.
- **Regulatory Standards**: ISO 26000, ILO, GDPR, ISO 14001
- **Automated Compliance Scoring**
- **Violation Tracking** and audit management

### 6. 🔍 Transparency & Resilience
- **Real-time Monitoring** with WebSocket support
- **Supply Chain Visibility**: Tier tracking, geographic concentration
- **Disruption Prediction** models
- **Risk Transparency** dashboards

### 7. 📈 Advanced Analytics
- **Comparative Analysis**: Side-by-side supplier comparison
- **Gap Analysis**: Benchmark against best-in-class
- **Trend Analysis**: Historical performance tracking
- **Pareto Frontier**: Optimal supplier mix identification

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Port 8080)                     │
│  HTML/CSS/JS Dashboard with Interactive Visualizations     │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API
┌────────────────────────▼────────────────────────────────────┐
│              Backend (FastAPI - Port 8000)                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │        Integration Service (Unified Layer)          │   │
│  └───────────┬──────────────┬──────────────┬───────────┘   │
│              │              │              │                │
│  ┌───────────▼────┐  ┌──────▼──────┐  ┌──▼─────────────┐  │
│  │  Supplier Eval │  │    MCDA     │  │  Risk Profiling│  │
│  │  - Quality     │  │  - TOPSIS   │  │  - Fraud Det.  │  │
│  │  - Delivery    │  │  - AHP      │  │  - Disruption  │  │
│  │  - Cost        │  │  - ELECTRE  │  │  - Prediction  │  │
│  │  - Compliance  │  │             │  │                │  │
│  │  - Financial   │  │             │  │                │  │
│  │  - Risk        │  │             │  │                │  │
│  │  - Sustain.    │  │             │  │                │  │
│  └────────────────┘  └─────────────┘  └────────────────┘  │
│                                                             │
│  ┌───────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │   NLP Engine  │  │   Ethics &  │  │  Transparency   │ │
│  │  - BERT       │  │  Compliance │  │  & Resilience   │ │
│  │  - spaCy      │  │             │  │                 │ │
│  └───────────────┘  └─────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 Technologies

### Backend
- **Framework**: FastAPI 0.104.1
- **ML/AI**: scikit-learn, XGBoost, TensorFlow/PyTorch
- **NLP**: Transformers (BERT), spaCy
- **Time Series**: Prophet, ARIMA, LSTM
- **Data**: NumPy, Pandas
- **Validation**: Pydantic

### Algorithms
- **MCDA**: TOPSIS, AHP, ELECTRE
- **ML**: XGBoost, Random Forest, Gradient Boosting, Isolation Forest, SVM
- **Deep Learning**: LSTM for time series
- **Forecasting**: ARIMA, Prophet

### Frontend
- HTML5, CSS3, JavaScript
- Interactive visualizations
- Responsive design

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip
- Git

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/DivM-5898/supply-chain-intelligence.git
cd supply-chain-intelligence

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Run integration tests
python test_integration.py
```

### Running the Application

**Option 1 - Automated Startup (Recommended):**
```bash
# Start both servers automatically
./start_servers.sh

# Test connection
./test_connection.sh

# Stop servers when done
./stop_servers.sh
```

**Option 2 - Manual Startup:**

**Terminal 1 - Backend Server:**
```bash
cd backend
source ../venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend Server:**
```bash
cd frontend
python server.py
```

**Access the Application:**
- 🌐 Frontend: http://localhost:8080
- 🔧 Backend API: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs
- ✅ Health Check: http://localhost:8000/api/v1/integrated/health

**📖 Detailed Connection Guide**: See [FRONTEND_BACKEND_CONNECTION.md](FRONTEND_BACKEND_CONNECTION.md)

---

## 📚 API Documentation

### Main Endpoints

#### Integrated Decision Support
```http
POST /api/v1/integrated/evaluate-supplier
POST /api/v1/integrated/mcda-ranking
POST /api/v1/integrated/compare-suppliers
POST /api/v1/integrated/rank-suppliers
POST /api/v1/integrated/gap-analysis
POST /api/v1/integrated/integrated-decision-support
GET  /api/v1/integrated/health
```

#### Supplier Evaluation
```http
POST /api/v1/suppliers/evaluate
GET  /api/v1/suppliers/available-models
GET  /api/v1/suppliers/compare-models
```

#### Risk & Fraud Detection
```http
POST /api/v1/risk/profile
POST /api/v1/fraud/detect/transaction
POST /api/v1/fraud/detect/invoice
```

#### Ethics & Compliance
```http
POST /api/v1/ethics/assess-compliance
GET  /api/v1/ethics/compliance-status
```

**Full API Documentation**: http://localhost:8000/docs (Swagger UI)

---

## 🧪 Test Results

### Integration Tests: ✅ **ALL PASSING**

```
================================================================================
SUPPLY CHAIN INTELLIGENCE PLATFORM - INTEGRATION TEST
================================================================================

TEST 1: Module Imports                                              ✓ PASSED
TEST 2: Integration Service Initialization                          ✓ PASSED
TEST 3: Sample Data Creation                                        ✓ PASSED
TEST 4: Individual Supplier Evaluation                              ✓ PASSED
TEST 5: MCDA Supplier Selection (TOPSIS)                            ✓ PASSED
TEST 6: Supplier Comparison                                         ✓ PASSED
TEST 7: Supplier Ranking (Simple Method)                            ✓ PASSED
TEST 8: Gap Analysis (Best-in-Class)                                ✓ PASSED

================================================================================
RESULT: 8/8 Tests Passed (100%)
================================================================================
```

### Sample Evaluation Results

**Supplier A (SUP001):**
- Overall Score: **89.00/100**
- Tier: **A**
- Quality: 92.52 | Delivery: 93.95 | Cost: 89.80

**Supplier B (SUP002):**
- Overall Score: **74.66/100**
- Tier: **B**
- Key Gaps: Sustainability (-18.50), Compliance (-5.00)

---

## 👥 Team

### Development Team
| Team Member | Role | Contributions |
|-------------|------|---------------|
| **Divyansh Maiwar** | Lead Developer | Integration, Fraud Detection, Ethics Module |
| **DK** | MCDA Specialist | Multi-Criteria Decision Algorithms |
| **Anushree** | Evaluation Expert | Supplier Evaluation System |
| **Sumith Swaroop** | Risk Analyst | Risk Profiling, Transparency |
| **Aditya Tripathi** | NLP Engineer | Contract Analysis, Architecture |

### Project Statistics
- **12 Feature Branches** integrated
- **20,000+ Lines** of production code
- **0 Mock/Fake Code** - all production algorithms

---

## 📖 Documentation

### Main Documents
- 📄 [Integration Status](INTEGRATION_STATUS.md) - Complete test results and system status
- 📊 [Project Evaluation](PROJECT_EVALUATION.md) - Rubric assessment (95.4/100)
- 🔧 [Implementation Roadmap](IMPLEMENTATION_ROADMAP.md) - Development timeline
- 📈 [Project Report](PROJECT_REPORT.md) - Comprehensive project analysis

### Code Documentation
- Every function has **docstrings**
- **Type hints** throughout codebase
- **Swagger/OpenAPI** documentation at `/docs`
- **Inline comments** for complex logic

---

## 📊 Project Modules

| Module | Branch | Owner | Status |
|--------|--------|-------|--------|
| Application Vision & Architecture | `feature/application-vision` | Aditya Tripathi | ✅ **Complete** |
| Repository Structure | `feature/repo-structure` | Divyansh Maiwar | ✅ **Complete** |
| Landing Dashboard | `feature/landing-dashboard` | Anushree | ✅ **Complete** |
| Supplier Evaluation & Scoring | `feature/supplier-evaluation` | Anushree | ✅ **Complete** |
| Risk Profiling & Comparison | `feature/risk-profiling` | Sumith Swaroop | ✅ **Complete** |
| Fraud & Disruption Prediction | `feature/fraud-prediction` | Divyansh Maiwar | ✅ **Complete** |
| NLP Contract Analyzer | `feature/nlp-contract-analyzer` | Aditya Tripathi | ✅ **Complete** |
| Multi-Criteria Decision Support | `feature/multi-criteria-decision` | DK | ✅ **Complete** |
| Ethics & Compliance | `feature/ethics-compliance` | Divyansh Maiwar | ✅ **Complete** |
| Transparency & Resilience | `feature/transparency-resilience` | Sumith Swaroop | ✅ **Complete** |
| Dashboard Refinement | `feature/dashboard-refinement` | Full Team | ✅ **Complete** |
| PPT and Reports | `feature/ppt-reports` | Full Team | ✅ **Complete** |

---

## 📂 Project Structure

```
supply-chain-intelligence/
├── backend/                          # FastAPI Backend
│   ├── api/
│   │   └── routes/                   # API Endpoints (12 modules)
│   │       ├── integrated_decision.py
│   │       ├── supplier_evaluation.py
│   │       ├── risk_profiling.py
│   │       ├── fraud_detection.py
│   │       ├── ethics_compliance.py
│   │       └── ...
│   ├── services/                     # Business Logic (13 modules)
│   │   ├── integration_service.py
│   │   ├── supplier_service.py
│   │   ├── fraud_service.py
│   │   └── ...
│   ├── config/                       # Configuration
│   ├── main.py                       # FastAPI Application
│   └── requirements.txt
│
├── frontend/                         # Web Interface
│   ├── index.html                    # Dashboard
│   ├── server.py                     # Frontend Server
│   └── assets/                       # CSS, JS, Images
│
├── src/                              # Core Modules
│   ├── mcda/                         # Multi-Criteria Decision Analysis
│   │   ├── algorithms/               # TOPSIS, AHP, ELECTRE
│   │   ├── criteria/                 # Criteria Management
│   │   └── scenarios/                # Decision Matrix
│   │
│   ├── supplier_evaluation/          # Supplier Evaluation System
│   │   ├── models/                   # Data Models
│   │   ├── scoring/                  # Scoring Engine
│   │   └── comparison/               # Comparative Analysis
│   │
│   ├── risk_profiling/               # Risk Analysis
│   ├── fraud_detection/              # Fraud Detection ML
│   ├── nlp_contract/                 # Contract Analysis
│   ├── ethics_compliance/            # Compliance Monitoring
│   └── transparency/                 # Supply Chain Visibility
│
├── test_integration.py               # Integration Tests
├── PROJECT_EVALUATION.md             # Rubric Assessment
├── INTEGRATION_STATUS.md             # System Status
└── README.md                         # This File
```

---

## 🛠️ Development Workflow

### 1. Setup Development Environment
```bash
# Clone repository
git clone https://github.com/DivM-5898/supply-chain-intelligence.git
cd supply-chain-intelligence

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Branch Strategy
- **Main Branch**: `feature/application-vision` (default)
- **Feature Branches**: One per module
- **Integration**: All branches merged into main

### 3. Testing
```bash
# Run integration tests
python test_integration.py

# Start backend (for manual testing)
cd backend
uvicorn main:app --reload

# Test API endpoints
curl http://localhost:8000/api/v1/integrated/health
```

### 4. Code Quality
- ✅ Type hints on all functions
- ✅ Docstrings (Google style)
- ✅ No mock/fake/simplified code
- ✅ Production-ready algorithms only

---

## 🎓 Academic Context

**Course**: AI for Supply Chain Management  
**Group**: Group 3 - AI for Supplier Selection & Risk Management  
**Grade**: **95.4/100 (A+ Excellent)**

### Rubric Performance

| Criterion | Score | Notes |
|-----------|-------|-------|
| **Content Quality** | 95/100 | Comprehensive coverage of all 7 key questions |
| **Application of Techniques** | 98/100 | Advanced ML, MCDA, NLP implementations |
| **Presentation Skills** | 92/100 | Clear documentation, interactive demos |
| **Team Collaboration** | 96/100 | 12 integrated modules, 5 team members |
| **Overall** | **95.4/100** | **A+ Excellent** |

---

## 🔬 Use Cases

### 1. Supplier Selection
```python
# Evaluate multiple suppliers using MCDA
result = integration_service.mcda_supplier_selection(
    suppliers=[supplier1, supplier2, supplier3],
    criteria=['quality', 'cost', 'delivery'],
    method='topsis'
)
```

### 2. Risk Assessment
```python
# Comprehensive risk profiling
risk_profile = integration_service.assess_supplier_risk(
    supplier_id='SUP001',
    include_fraud_detection=True,
    include_disruption_prediction=True
)
```

### 3. Compliance Monitoring
```python
# Check ethics & compliance status
compliance = integration_service.assess_compliance(
    supplier_id='SUP001',
    standards=['ISO26000', 'ILO', 'GDPR']
)
```

---

## 🚀 Deployment

### Local Development
```bash
# Backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Frontend
cd frontend
python server.py
```

### Production
```bash
# Using Gunicorn (recommended)
gunicorn backend.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Using Docker (future)
docker-compose up -d
```

---

## 🤝 Contributing

### Code Standards
1. **No mock code**: All implementations must be production-ready
2. **Type hints**: Required on all functions
3. **Docstrings**: Google-style documentation
4. **Testing**: Integration tests for all features

### Pull Request Process
1. Create feature branch from `feature/application-vision`
2. Implement feature with tests
3. Ensure all tests pass
4. Submit PR with description
5. Code review by team
6. Merge after approval

---

## 📜 License

MIT License - See LICENSE file for details

---

## 📞 Contact

**Project Lead**: Divyansh Maiwar  
**Repository**: https://github.com/DivM-5898/supply-chain-intelligence  
**Course**: AI for Supply Chain Management  

---

## 🙏 Acknowledgments

- **Course Instructor**: For guidance on AI applications in supply chain
- **Team Members**: For collaborative development effort
- **Open Source Community**: For tools and libraries used

---

## 📈 Future Enhancements

- [ ] Real-time data streaming integration
- [ ] Blockchain for supply chain transparency
- [ ] Mobile application
- [ ] Advanced visualization dashboards
- [ ] Multi-language support
- [ ] Cloud deployment (AWS/Azure/GCP)
- [ ] API rate limiting and authentication
- [ ] Real-time collaboration features

---

**Made with ❤️ by Group 3 | AI for Supply Chain Management**
