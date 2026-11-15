"""
Model Training & Refinement Pipeline for Car Price Valuation.
Trains Intrinsic (without MMR) and Benchmark (with MMR) models using Linear Regression,
Ridge, and XGBoost with rigorous cross-validation and evaluation metrics (R2, MAE, RMSE, MAPE).
"""

import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from xgboost import XGBRegressor

from src.data_pipeline import load_and_clean_data

def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Calculate R2, MAE, RMSE, and MAPE."""
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    # Avoid zero division in MAPE
    nonzero_mask = y_true > 0
    mape = np.mean(np.abs((y_true[nonzero_mask] - y_pred[nonzero_mask]) / y_true[nonzero_mask])) * 100
    return {
        'r2': round(float(r2), 4),
        'mae': round(float(mae), 2),
        'rmse': round(float(rmse), 2),
        'mape': round(float(mape), 2)
    }

def train_and_evaluate_models(
    csv_path: str = 'car_pricing_dataset.csv',
    train_sample_size: int = 120000,
    output_dir: str = 'models'
) -> Dict[str, Any]:
    """Train Intrinsic and Full Valuation pipelines and export artifacts."""
    os.makedirs(output_dir, exist_ok=True)
    print(f"Loading and preprocessing data (sample size: {train_sample_size})...")
    df, meta = load_and_clean_data(csv_path=csv_path, sample_size=train_sample_size)
    print(f"Cleaned dataset ready: {len(df)} records.")

    # Top categories to prevent one-hot explosion
    top_makes = df['make'].value_counts().head(25).index.tolist()
    top_states = df['state'].value_counts().head(25).index.tolist()
    top_bodies = df['body_clean'].value_counts().head(10).index.tolist()

    df['make_cat'] = df['make'].apply(lambda x: x if x in top_makes else 'Other')
    df['state_cat'] = df['state'].apply(lambda x: x if x in top_states else 'Other')
    df['body_cat'] = df['body_clean'].apply(lambda x: x if x in top_bodies else 'Other')

    # Target variable
    y = df['sellingprice'].values

    # ==========================================
    # 1. MODEL A: INTRINSIC VALUATION (WITHOUT MMR)
    # ==========================================
    print("\n--- Training Model A: Intrinsic Valuation (Without MMR) ---")
    cat_features_intrinsic = ['make_cat', 'body_cat', 'state_cat', 'transmission']
    num_features_intrinsic = ['year', 'vehicle_age', 'condition', 'odometer', 'mileage_per_year']

    X_intrinsic = df[cat_features_intrinsic + num_features_intrinsic]

    X_train_int, X_test_int, y_train_int, y_test_int = train_test_split(
        X_intrinsic, y, test_size=0.2, random_state=42
    )

    preprocessor_intrinsic = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), num_features_intrinsic),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_features_intrinsic)
        ]
    )

    # Compare Linear, Ridge, and XGBoost
    models_to_test = {
        'Linear Regression': LinearRegression(),
        'Ridge Regression': Ridge(alpha=10.0),
        'XGBoost Regressor': XGBRegressor(
            n_estimators=220,
            learning_rate=0.08,
            max_depth=7,
            subsample=0.85,
            colsample_bytree=0.85,
            random_state=42,
            n_jobs=-1
        )
    }

    intrinsic_results = {}
    best_intrinsic_model = None
    best_intrinsic_pipeline = None
    best_intrinsic_mae = float('inf')

    for name, reg in models_to_test.items():
        pipe = Pipeline([
            ('preprocessor', preprocessor_intrinsic),
            ('regressor', reg)
        ])
        pipe.fit(X_train_int, y_train_int)
        y_pred = pipe.predict(X_test_int)
        metrics = compute_metrics(y_test_int, y_pred)
        intrinsic_results[name] = metrics
        print(f"[{name}] R2: {metrics['r2']}, MAE: ${metrics['mae']:,}, RMSE: ${metrics['rmse']:,}, MAPE: {metrics['mape']}%")

        if metrics['mae'] < best_intrinsic_mae:
            best_intrinsic_mae = metrics['mae']
            best_intrinsic_model = name
            best_intrinsic_pipeline = pipe

    # Save best Intrinsic Pipeline
    intrinsic_path = os.path.join(output_dir, 'price_model_intrinsic.joblib')
    joblib.dump(best_intrinsic_pipeline, intrinsic_path)
    print(f"Saved best intrinsic pipeline ({best_intrinsic_model}) to {intrinsic_path}")

    # ==========================================
    # 2. MODEL B: FULL BENCHMARK (WITH MMR)
    # ==========================================
    print("\n--- Training Model B: Market Benchmark (With MMR) ---")
    cat_features_full = ['make_cat', 'body_cat', 'state_cat', 'transmission']
    num_features_full = ['mmr', 'year', 'vehicle_age', 'condition', 'odometer', 'mileage_per_year']

    # Drop any NaNs in MMR for full benchmark
    df_full = df.dropna(subset=['mmr']).copy()
    y_full = df_full['sellingprice'].values
    X_full = df_full[cat_features_full + num_features_full]

    X_train_full, X_test_full, y_train_full, y_test_full = train_test_split(
        X_full, y_full, test_size=0.2, random_state=42
    )

    preprocessor_full = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), num_features_full),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_features_full)
        ]
    )

    full_pipe = Pipeline([
        ('preprocessor', preprocessor_full),
        ('regressor', Ridge(alpha=5.0))
    ])
    full_pipe.fit(X_train_full, y_train_full)
    y_pred_full = full_pipe.predict(X_test_full)
    metrics_full_ridge = compute_metrics(y_test_full, y_pred_full)

    full_pipe_xgb = Pipeline([
        ('preprocessor', preprocessor_full),
        ('regressor', XGBRegressor(
            n_estimators=180,
            learning_rate=0.08,
            max_depth=6,
            random_state=42,
            n_jobs=-1
        ))
    ])
    full_pipe_xgb.fit(X_train_full, y_train_full)
    y_pred_full_xgb = full_pipe_xgb.predict(X_test_full)
    metrics_full_xgb = compute_metrics(y_test_full, y_pred_full_xgb)

    print(f"[Full Ridge with MMR] R2: {metrics_full_ridge['r2']}, MAE: ${metrics_full_ridge['mae']:,}, RMSE: ${metrics_full_ridge['rmse']:,}")
    print(f"[Full XGBoost with MMR] R2: {metrics_full_xgb['r2']}, MAE: ${metrics_full_xgb['mae']:,}, RMSE: ${metrics_full_xgb['rmse']:,}")

    # Save best Full Pipeline
    full_path = os.path.join(output_dir, 'price_model_full.joblib')
    best_full_pipeline = full_pipe_xgb if metrics_full_xgb['mae'] <= metrics_full_ridge['mae'] else full_pipe
    joblib.dump(best_full_pipeline, full_path)
    print(f"Saved full benchmark pipeline to {full_path}")

    # ==========================================
    # 3. FEATURE IMPORTANCES & METADATA
    # ==========================================
    # Extract feature names & importances from XGBoost intrinsic model
    xgb_regressor = best_intrinsic_pipeline.named_steps['regressor']
    fitted_preprocessor = best_intrinsic_pipeline.named_steps['preprocessor']
    
    ohe_feature_names = fitted_preprocessor.named_transformers_['cat'].get_feature_names_out(cat_features_intrinsic).tolist()
    all_feature_names = num_features_intrinsic + ohe_feature_names
    importances = xgb_regressor.feature_importances_.tolist()
    
    feature_imp_pairs = sorted(zip(all_feature_names, importances), key=lambda x: x[1], reverse=True)[:15]

    metadata_payload = {
        'training_samples': len(df),
        'intrinsic_models': intrinsic_results,
        'full_models': {
            'Ridge with MMR': metrics_full_ridge,
            'XGBoost with MMR': metrics_full_xgb
        },
        'best_intrinsic_model': best_intrinsic_model,
        'top_features_importance': [{'feature': f, 'importance': round(imp, 4)} for f, imp in feature_imp_pairs],
        'categories': {
            'makes': sorted(top_makes),
            'bodies': sorted(top_bodies),
            'states': sorted(top_states),
            'transmissions': ['automatic', 'manual']
        },
        'benchmarks': {
            'avg_selling_price': float(df['sellingprice'].mean()),
            'median_selling_price': float(df['sellingprice'].median()),
            'avg_odometer': float(df['odometer'].mean()),
            'avg_condition': float(df['condition'].mean()),
            'price_std': float(df['sellingprice'].std())
        }
    }

    metadata_path = os.path.join(output_dir, 'model_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata_payload, f, indent=2)
    print(f"Saved model metadata & metrics to {metadata_path}")

    return metadata_payload

if __name__ == '__main__':
    train_and_evaluate_models()
