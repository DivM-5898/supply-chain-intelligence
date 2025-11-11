# Deployment Guide

## Prerequisites

- Python 3.9+
- GitHub account
- Render account (free tier)
- PostgreSQL database (optional, Render provides)

## Local Development Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd AI_IN_OPERATIONS
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Generate Sample Data

```bash
python -m services.data_generator
```

### 4. Train Models

```bash
python -m services.model_trainer
```

### 5. Run Backend

```bash
uvicorn main:app --reload
```

Backend will be available at `http://localhost:8000`

### 6. Frontend Setup

```bash
cd frontend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 7. Configure API URL

Edit `frontend/config/api_config.py`:
```python
BACKEND_URL = "http://localhost:8000"
```

### 8. Run Frontend

```bash
streamlit run main.py
```

Frontend will be available at `http://localhost:8501`

## Render Deployment

### Backend Deployment

1. **Create New Web Service on Render**
   - Connect your GitHub repository
   - Select the repository
   - Configure:
     - Name: `supplier-selection-backend`
     - Environment: `Python 3`
     - Build Command: `cd backend && pip install -r requirements.txt`
     - Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

2. **Environment Variables**
   - `DATABASE_URL`: PostgreSQL connection string (if using database)
   - `OPENAI_API_KEY`: Mock key for demo (optional)

3. **Generate Data and Train Models**
   - Use Render shell or add to build command:
   ```bash
   cd backend && python -m services.data_generator && python -m services.model_trainer
   ```

### Frontend Deployment

1. **Create New Web Service on Render**
   - Connect your GitHub repository
   - Select the repository
   - Configure:
     - Name: `supplier-selection-frontend`
     - Environment: `Python 3`
     - Build Command: `cd frontend && pip install -r requirements.txt`
     - Start Command: `cd frontend && streamlit run main.py --server.port $PORT --server.address 0.0.0.0`

2. **Environment Variables**
   - `BACKEND_API_URL`: Your backend service URL (e.g., `https://supplier-selection-backend.onrender.com`)

### Database Setup (Optional)

1. **Create PostgreSQL Database on Render**
   - Add PostgreSQL service
   - Copy connection string
   - Add to backend environment variables as `DATABASE_URL`

## Post-Deployment

1. **Verify Backend**
   - Visit `https://your-backend.onrender.com/docs`
   - Test API endpoints

2. **Verify Frontend**
   - Visit `https://your-frontend.onrender.com`
   - Test all tabs and functionalities

3. **Monitor Logs**
   - Check Render logs for errors
   - Verify data generation and model training

## Troubleshooting

### Backend Issues

- **Import Errors**: Ensure all dependencies are in `requirements.txt`
- **Port Issues**: Use `$PORT` environment variable
- **Data Not Found**: Run data generator in build command

### Frontend Issues

- **API Connection**: Verify `BACKEND_API_URL` is correct
- **Module Not Found**: Check Python path and imports
- **Streamlit Errors**: Ensure all dependencies are installed

### Common Issues

1. **Models Not Found**: Run model trainer before starting backend
2. **CORS Errors**: Check CORS configuration in backend
3. **Timeout Errors**: Increase timeout in API client
4. **Memory Issues**: Render free tier has memory limits

## Maintenance

- Regularly update dependencies
- Monitor model performance
- Retrain models with new data
- Backup model files and data

