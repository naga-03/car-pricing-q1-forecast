"""
Inference Service Module for Car Pricing & Q1 Forecast.
Provides structured prediction APIs for the dashboard and external consumers.
"""

import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

class VehicleValuationService:
    """Production service for car price prediction and time-series forecasting."""

    def __init__(self, models_dir: str = 'models'):
        self.models_dir = models_dir
        self.intrinsic_model = None
        self.full_model = None
        self.metadata = {}
        self.time_series_summary = {}
        self.load_artifacts()

    def load_artifacts(self):
        """Load trained models and configuration metadata."""
        intrinsic_path = os.path.join(self.models_dir, 'price_model_intrinsic.joblib')
        if os.path.exists(intrinsic_path):
            self.intrinsic_model = joblib.load(intrinsic_path)

        full_path = os.path.join(self.models_dir, 'price_model_full.joblib')
        if os.path.exists(full_path):
            self.full_model = joblib.load(full_path)

        meta_path = os.path.join(self.models_dir, 'model_metadata.json')
        if os.path.exists(meta_path):
            with open(meta_path, 'r') as f:
                self.metadata = json.load(f)

        ts_path = os.path.join(self.models_dir, 'time_series_summary.json')
        if os.path.exists(ts_path):
            with open(ts_path, 'r') as f:
                self.time_series_summary = json.load(f)

    def get_supported_categories(self) -> Dict[str, list]:
        """Return lists of recognized makes, bodies, states, and transmissions."""
        if 'categories' in self.metadata:
            return self.metadata['categories']
        return {
            'makes': ['Ford', 'Chevrolet', 'Toyota', 'Nissan', 'Honda', 'BMW', 'Hyundai'],
            'bodies': ['Sedan', 'SUV', 'Pickup/Truck', 'Hatchback', 'Coupe', 'Minivan', 'Convertible'],
            'states': ['CA', 'FL', 'TX', 'PA', 'GA', 'NJ', 'OH', 'NC', 'IL'],
            'transmissions': ['automatic', 'manual']
        }

    def predict_price(
        self,
        year: int,
        make: str,
        body: str,
        state: str,
        condition: float,
        odometer: float,
        transmission: str = 'automatic',
        mmr: Optional[float] = None,
        use_mmr: bool = False
    ) -> Dict[str, Any]:
        """
        Predict vehicle selling price.
        If use_mmr is True and mmr is provided, uses Full Benchmark Model.
        Otherwise, uses Intrinsic Valuation Model (no MMR required).
        """
        # Determine current temporal baseline (2015 dataset baseline)
        ref_year = 2015
        vehicle_age = max(0, ref_year - int(year))
        mileage_per_year = round(float(odometer) / (vehicle_age + 1), 1)

        # Categorical normalization against known sets
        known_makes = self.metadata.get('categories', {}).get('makes', [])
        known_bodies = self.metadata.get('categories', {}).get('bodies', [])
        known_states = self.metadata.get('categories', {}).get('states', [])

        make_clean = make.title() if make.title() in known_makes else 'Other'
        body_clean = body.title() if body.title() in known_bodies else 'Other'
        state_clean = state.upper() if state.upper() in known_states else 'Other'
        trans_clean = 'manual' if 'man' in transmission.lower() else 'automatic'

        if use_mmr and mmr is not None and self.full_model is not None:
            features_df = pd.DataFrame([{
                'mmr': float(mmr),
                'year': int(year),
                'vehicle_age': vehicle_age,
                'condition': float(condition),
                'odometer': float(odometer),
                'mileage_per_year': mileage_per_year,
                'make_cat': make_clean,
                'body_cat': body_clean,
                'state_cat': state_clean,
                'transmission': trans_clean
            }])
            raw_pred = float(self.full_model.predict(features_df)[0])
            mae = self.metadata.get('full_models', {}).get('XGBoost with MMR', {}).get('mae', 924.0)
            model_used = 'Market Benchmark Model (With MMR)'
        else:
            if self.intrinsic_model is None:
                raise RuntimeError("Intrinsic pricing model not loaded.")
            features_df = pd.DataFrame([{
                'year': int(year),
                'vehicle_age': vehicle_age,
                'condition': float(condition),
                'odometer': float(odometer),
                'mileage_per_year': mileage_per_year,
                'make_cat': make_clean,
                'body_cat': body_clean,
                'state_cat': state_clean,
                'transmission': trans_clean
            }])
            raw_pred = float(self.intrinsic_model.predict(features_df)[0])
            mae = self.metadata.get('intrinsic_models', {}).get('XGBoost Regressor', {}).get('mae', 2505.0)
            model_used = 'Intrinsic Valuation Model (Vehicle Attributes Only)'

        # Clamp prediction to sensible range
        pred_price = max(500.0, round(raw_pred, 2))
        lower_bound = max(500.0, round(pred_price - mae, 2))
        upper_bound = round(pred_price + mae, 2)

        # Market tier assessment
        avg_market = self.metadata.get('benchmarks', {}).get('avg_selling_price', 14000.0)
        diff_pct = round(((pred_price - avg_market) / avg_market) * 100, 1)

        tier = "Average Market Segment"
        if diff_pct > 35:
            tier = "Premium / Luxury Segment"
        elif diff_pct < -35:
            tier = "Budget / Value Segment"

        return {
            'predicted_price': pred_price,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'mae_margin': round(mae, 2),
            'market_tier': tier,
            'market_benchmark_diff_pct': diff_pct,
            'model_used': model_used,
            'input_summary': {
                'year': year,
                'make': make,
                'body': body,
                'condition': condition,
                'odometer': odometer,
                'vehicle_age': vehicle_age,
                'mileage_per_year': mileage_per_year
            }
        }

    def get_forecast_summary(self) -> Dict[str, Any]:
        """Return structured time-series history and forecast projections."""
        return self.time_series_summary

    def get_model_benchmarks(self) -> Dict[str, Any]:
        """Return model comparison tables and feature importances."""
        return {
            'intrinsic_comparison': self.metadata.get('intrinsic_models', {}),
            'full_comparison': self.metadata.get('full_models', {}),
            'top_features': self.metadata.get('top_features_importance', []),
            'training_samples': self.metadata.get('training_samples', 0)
        }

if __name__ == '__main__':
    service = VehicleValuationService()
    test_res = service.predict_price(
        year=2013, make='BMW', body='Sedan', state='CA', condition=40, odometer=45000
    )
    print("Sample Intrinsic Prediction:", test_res)
    test_res_mmr = service.predict_price(
        year=2013, make='BMW', body='Sedan', state='CA', condition=40, odometer=45000, mmr=22000, use_mmr=True
    )
    print("Sample Full MMR Prediction:", test_res_mmr)
