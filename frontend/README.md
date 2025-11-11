# HTML Frontend Dashboard - Setup Guide

## Overview

The frontend has been rebuilt as a professional HTML/CSS/JavaScript application with modern UI/UX, replacing Streamlit.

## Features

- **Modern Design**: Professional UI with Bootstrap 5, custom CSS, and smooth animations
- **Interactive Charts**: Plotly.js for 3D visualizations, bar charts, heatmaps, and geographic maps
- **Responsive Layout**: Mobile-friendly design with collapsible sidebar
- **Real-time Updates**: Dynamic content loading and API integration
- **Professional UX**: Loading states, error handling, success notifications

## Running the Application

### Prerequisites

1. Backend API must be running on `http://localhost:8000`
2. Python 3.x installed

### Start Frontend Server

```bash
cd frontend
python server.py
```

The frontend will be available at: **http://localhost:8080**

### Start Backend Server (if not running)

```bash
cd backend
uvicorn main:app --reload
```

Backend API will be available at: **http://localhost:8000**

## Project Structure

```
frontend/
├── index.html              # Main HTML file
├── server.py               # HTTP server for frontend
├── assets/
│   ├── css/
│   │   └── style.css       # Custom CSS styles
│   └── js/
│       ├── api.js          # API client
│       ├── app.js          # Main application logic
│       └── pages/
│           ├── home.js
│           ├── supplier-evaluation.js
│           ├── risk-profiling.js
│           ├── fraud-prediction.js
│           ├── nlp-contract.js
│           ├── decision-support.js
│           ├── ethics-compliance.js
│           └── transparency.js
```

## Pages Overview

1. **Home** - Executive vision, architecture overview, success metrics
2. **Supplier Evaluation** - ML model predictions, rankings, feature importance
3. **Risk Profiling** - Risk predictions, anomaly detection, geographic maps
4. **Fraud Prediction** - Fraud detection models, probability scores
5. **NLP Contract Analyzer** - Contract upload, entity extraction, risk analysis
6. **Decision Support** - TOPSIS and AHP multi-criteria optimization
7. **Ethics & Compliance** - SHAP/LIME explanations, bias detection, ESG scores
8. **Transparency & Resilience** - Global maps, network visualization, resilience metrics

## Browser Compatibility

- Chrome/Edge (recommended)
- Firefox
- Safari
- Opera

## API Configuration

The API base URL is configured in `assets/js/api.js`:

```javascript
const API_CONFIG = {
    BASE_URL: 'http://localhost:8000/api/v1',
    TIMEOUT: 30000
};
```

For production, update this to your backend URL.

## Troubleshooting

1. **CORS Errors**: Ensure backend CORS is configured to allow requests from frontend origin
2. **API Connection Failed**: Verify backend is running on port 8000
3. **Charts Not Displaying**: Check browser console for Plotly.js loading errors
4. **Page Not Loading**: Check browser console for JavaScript errors

## Development

To modify the frontend:

1. Edit HTML in `index.html`
2. Modify styles in `assets/css/style.css`
3. Update page logic in `assets/js/pages/[page-name].js`
4. Refresh browser to see changes (no rebuild needed)

## Production Deployment

For Render deployment:

1. Update `API_CONFIG.BASE_URL` in `api.js` to your backend URL
2. Use a production web server (nginx, Apache) or Render's static site hosting
3. Ensure CORS is properly configured on backend

