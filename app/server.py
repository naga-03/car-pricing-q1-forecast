"""
FastAPI Backend Server for AutoPrice AI (MyDash Analytics).
Serves the REST API for model predictions, Q1 sales analytics, and static UI.
"""

import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from typing import Optional, Dict, Any
from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel, Field

from src.predict import VehicleValuationService

app = FastAPI(
    title="AutoPrice AI | MyDash Analytics",
    description="Enterprise API for Vehicle Price Prediction & Q1 Sales Analytics",
    version="2.0.0"
)

# Global service instance
service = VehicleValuationService()

# Load precomputed analytics
ANALYTICS_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'q1_analytics.json')
q1_data = {}
if os.path.exists(ANALYTICS_PATH):
    with open(ANALYTICS_PATH, 'r') as f:
        q1_data = json.load(f)

# Request schema for price prediction
class PredictionRequest(BaseModel):
    year: int = Field(2013, ge=1990, le=2016)
    make: str = Field("BMW")
    body: str = Field("Sedan")
    state: str = Field("CA")
    condition: float = Field(38.0, ge=1.0, le=50.0)
    odometer: float = Field(45000.0, ge=100.0, le=400000.0)
    transmission: str = Field("automatic")
    use_mmr: bool = Field(False)
    mmr: Optional[float] = Field(None, ge=100.0)

# Serve static files if directory exists
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
os.makedirs(STATIC_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
def serve_index():
    """Serve the main redesigned dashboard SPA."""
    index_file = os.path.join(STATIC_DIR, 'index.html')
    if os.path.exists(index_file):
        with open(index_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>MyDash Analytics Dashboard UI Loading...</h1>")

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AutoPrice AI MyDash",
        "models_loaded": service.intrinsic_model is not None and service.full_model is not None
    }

@app.get("/api/categories")
def get_categories():
    """Return recognized vehicle categories for dropdown filters."""
    return service.get_supported_categories()

@app.get("/api/overview")
def get_overview():
    """Return dynamic metrics for both Car Price Prediction and Q1 Sales Analysis."""
    benchmarks = service.get_model_benchmarks()
    intrinsic_eval = benchmarks.get('intrinsic_comparison', {}).get('XGBoost Regressor', {})
    
    kpis = q1_data.get('kpis', {
        'total_records_dataset': 558837,
        'cleaned_records': 540618,
        'avg_car_price': 13903.85,
        'min_car_price': 500.0,
        'max_car_price': 230000.0,
        'q1_total_revenue': 4704658042.0,
        'q1_total_orders': 346161,
        'q1_units_sold': 346161,
        'q1_avg_order_value': 13590.95,
        'q1_top_make': "Ford",
        'q1_top_body': "Sedan"
    })

    # Combine with ML model metrics
    kpis['model_r2'] = intrinsic_eval.get('r2', 0.8029)
    kpis['model_mae'] = intrinsic_eval.get('mae', 2505.06)
    kpis['model_rmse'] = intrinsic_eval.get('rmse', 4108.13)
    kpis['model_mape'] = intrinsic_eval.get('mape', 25.89)

    return {
        'kpis': kpis,
        'weekly_trajectory': q1_data.get('weekly_trajectory', []),
        'monthly_performance': q1_data.get('monthly_performance', []),
        'body_distribution': q1_data.get('body_distribution', {}),
        'body_percentages': q1_data.get('body_percentages', {}),
        'state_distribution': q1_data.get('state_distribution', {}),
        'top_models': q1_data.get('top_models', []),
        'top_makes': q1_data.get('top_makes', []),
        'ranked_vehicles': q1_data.get('ranked_vehicles', []),
        'forecast_summary': service.get_forecast_summary()
    }

@app.post("/api/predict")
def predict_car_price(req: PredictionRequest):
    """Predict vehicle selling price using trained ML models."""
    try:
        result = service.predict_price(
            year=req.year,
            make=req.make,
            body=req.body,
            state=req.state,
            condition=req.condition,
            odometer=req.odometer,
            transmission=req.transmission,
            mmr=req.mmr if req.use_mmr else None,
            use_mmr=req.use_mmr
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/q1-analysis")
def get_q1_analysis(
    month: Optional[int] = None,
    make: Optional[str] = None,
    state: Optional[str] = None
):
    """Return filtered Q1 business intelligence analytics."""
    monthly_data = q1_data.get('monthly_performance', [])
    if month is not None and isinstance(month, int):
        monthly_data = [m for m in monthly_data if m.get('month_num') == month]

    return {
        'kpis': q1_data.get('kpis', {}),
        'monthly_performance': monthly_data,
        'body_distribution': q1_data.get('body_distribution', {}),
        'state_distribution': q1_data.get('state_distribution', {}),
        'top_models': q1_data.get('top_models', []),
        'top_makes': q1_data.get('top_makes', []),
        'weekly_trajectory': q1_data.get('weekly_trajectory', []),
        'insights': [
            "Q1 volume peaked in February at 161,507 units ($2.22B total transaction value).",
            "Sedans and SUVs drove 70.3% of all Q1 inventory movement across wholesale remarketing hubs.",
            "Florida, California, and Pennsylvania led all geographical regions in sales volume.",
            "Ford, Chevrolet, and Nissan captured the largest market share in unit sales."
        ]
    }

@app.get("/api/model-benchmarks")
def get_model_benchmarks():
    """Return comparative metrics and feature importances."""
    return service.get_model_benchmarks()

@app.get("/api/reports/summary")
def get_report_summary():
    """Generate high-level report payload for export."""
    return {
        "title": "AutoPrice AI Executive Report",
        "generated_at": "2026-11-15T22:30:00Z",
        "kpis": q1_data.get('kpis', {}),
        "model_performance": service.get_model_benchmarks(),
        "q1_summary": q1_data.get('monthly_performance', [])
    }

# Mount static folder
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get("PORT", 8501))
    uvicorn.run("app.server:app", host="0.0.0.0", port=port, reload=False)
