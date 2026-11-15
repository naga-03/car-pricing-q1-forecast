"""Direct route handler unit tests for FastAPI MyDash Analytics Server."""
import pytest
from app.server import (
    health_check,
    get_overview,
    predict_car_price,
    get_q1_analysis,
    get_categories,
    get_report_summary,
    PredictionRequest
)

def test_health_endpoint():
    data = health_check()
    assert data["status"] == "healthy"
    assert data["models_loaded"] is True

def test_overview_endpoint():
    data = get_overview()
    assert "kpis" in data
    assert data["kpis"]["total_records_dataset"] == 558837
    assert data["kpis"]["model_r2"] > 0.75
    assert len(data["weekly_trajectory"]) > 0
    assert len(data["top_models"]) > 0
    assert len(data["monthly_performance"]) == 3

def test_predict_endpoint_intrinsic():
    payload = PredictionRequest(
        year=2013,
        make="BMW",
        body="Sedan",
        state="CA",
        condition=38.0,
        odometer=45000.0,
        transmission="automatic",
        use_mmr=False
    )
    data = predict_car_price(payload)
    assert "predicted_price" in data
    assert data["predicted_price"] > 1000
    assert "lower_bound" in data
    assert "upper_bound" in data
    assert "market_tier" in data

def test_predict_endpoint_with_mmr():
    payload = PredictionRequest(
        year=2013,
        make="BMW",
        body="Sedan",
        state="CA",
        condition=38.0,
        odometer=45000.0,
        transmission="automatic",
        use_mmr=True,
        mmr=22000.0
    )
    data = predict_car_price(payload)
    assert "predicted_price" in data
    assert 18000 < data["predicted_price"] < 26000

def test_q1_analysis_endpoint():
    data = get_q1_analysis()
    assert "monthly_performance" in data
    assert len(data["monthly_performance"]) == 3
    assert len(data["insights"]) > 0

def test_categories_endpoint():
    data = get_categories()
    assert "makes" in data
    assert "bodies" in data
    assert "BMW" in data["makes"]

def test_report_summary_endpoint():
    data = get_report_summary()
    assert "title" in data
    assert "kpis" in data
