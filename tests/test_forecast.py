"""Unit tests for Time-Series Aggregation & Forecast."""
import pytest
from src.predict import VehicleValuationService

@pytest.fixture
def service():
    return VehicleValuationService()

def test_forecast_summary_structure(service):
    summary = service.get_forecast_summary()
    assert 'q1_projected_volume' in summary
    assert summary['q1_projected_volume'] > 0
    assert 'q1_monthly_breakdown' in summary
    assert 'January' in summary['q1_monthly_breakdown']
    assert 'scenarios' in summary
    assert summary['scenarios']['conservative'] < summary['scenarios']['baseline']
    assert summary['scenarios']['optimistic'] > summary['scenarios']['baseline']
    assert len(summary['forecast_weeks']) == 12
    assert len(summary['historical_series']) > 0

def test_model_benchmarks(service):
    benchmarks = service.get_model_benchmarks()
    assert 'intrinsic_comparison' in benchmarks
    assert 'XGBoost Regressor' in benchmarks['intrinsic_comparison']
    assert 'top_features' in benchmarks
    assert len(benchmarks['top_features']) > 0
