"""Unit tests for ML Valuation and Inference Service."""
import pytest
from src.predict import VehicleValuationService

@pytest.fixture
def service():
    return VehicleValuationService()

def test_service_initialization(service):
    assert service.intrinsic_model is not None
    assert service.full_model is not None
    assert len(service.metadata) > 0

def test_intrinsic_price_prediction(service):
    res = service.predict_price(
        year=2014,
        make='Toyota',
        body='Sedan',
        state='CA',
        condition=35,
        odometer=50000,
        transmission='automatic'
    )
    assert 'predicted_price' in res
    assert res['predicted_price'] > 1000
    assert res['lower_bound'] < res['predicted_price']
    assert res['upper_bound'] > res['predicted_price']
    assert 'model_used' in res
    assert 'Intrinsic' in res['model_used']

def test_full_price_prediction_with_mmr(service):
    res = service.predict_price(
        year=2014,
        make='Toyota',
        body='Sedan',
        state='CA',
        condition=35,
        odometer=50000,
        transmission='automatic',
        mmr=14000,
        use_mmr=True
    )
    assert 'predicted_price' in res
    assert 10000 < res['predicted_price'] < 18000
    assert res['mae_margin'] < 1500
    assert 'With MMR' in res['model_used']

def test_unseen_categories_handling(service):
    res = service.predict_price(
        year=2012,
        make='NonExistentBrand123',
        body='FuturisticHovercraft',
        state='ZZ',
        condition=30,
        odometer=60000
    )
    assert 'predicted_price' in res
    assert res['predicted_price'] > 500
