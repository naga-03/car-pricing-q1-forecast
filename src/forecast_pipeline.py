"""
Time-Series Aggregation & Q1 Demand Forecasting Pipeline.
Aggregates historical sales into weekly and monthly series, builds seasonal lag features,
and generates multi-step forward forecasts for Q1 with prediction intervals.
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
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from src.data_pipeline import load_and_clean_data

def aggregate_time_series(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Aggregate transactional data into weekly and monthly time series.
    """
    df = df.copy()
    # Normalize date to start of week (Monday)
    df['week_start'] = df['sale_date'].dt.to_period('W').dt.start_time
    df['year_month'] = df['sale_date'].dt.to_period('M').dt.start_time

    # Weekly aggregation
    weekly = df.groupby('week_start').agg(
        sales_volume=('sellingprice', 'count'),
        total_revenue=('sellingprice', 'sum'),
        avg_price=('sellingprice', 'mean'),
        avg_odometer=('odometer', 'mean'),
        avg_condition=('condition', 'mean'),
    ).reset_index()

    weekly['avg_price'] = weekly['avg_price'].round(2)
    weekly['avg_odometer'] = weekly['avg_odometer'].round(1)
    weekly['avg_condition'] = weekly['avg_condition'].round(2)
    weekly['is_q1'] = weekly['week_start'].dt.month.isin([1, 2, 3]).astype(int)
    weekly['month'] = weekly['week_start'].dt.month
    weekly['week_of_year'] = weekly['week_start'].dt.isocalendar().week.astype(int)

    # Monthly aggregation
    monthly = df.groupby('year_month').agg(
        sales_volume=('sellingprice', 'count'),
        total_revenue=('sellingprice', 'sum'),
        avg_price=('sellingprice', 'mean')
    ).reset_index()
    monthly['is_q1'] = monthly['year_month'].dt.month.isin([1, 2, 3]).astype(int)

    return weekly, monthly

def create_time_series_features(weekly_df: pd.DataFrame) -> pd.DataFrame:
    """Build lag and rolling features for time-series volume forecasting."""
    df = weekly_df.copy().sort_values('week_start').reset_index(drop=True)
    df['time_step'] = np.arange(len(df))

    # Lags
    df['vol_lag_1'] = df['sales_volume'].shift(1)
    df['vol_lag_2'] = df['sales_volume'].shift(2)
    df['vol_lag_4'] = df['sales_volume'].shift(4)

    # Rolling statistics
    df['vol_roll_mean_3'] = df['sales_volume'].shift(1).rolling(window=3, min_periods=1).mean()
    df['vol_roll_mean_6'] = df['sales_volume'].shift(1).rolling(window=6, min_periods=1).mean()

    # Cyclical calendar features
    df['sin_week'] = np.sin(2 * np.pi * df['week_of_year'] / 52.0)
    df['cos_week'] = np.cos(2 * np.pi * df['week_of_year'] / 52.0)
    df['sin_month'] = np.sin(2 * np.pi * df['month'] / 12.0)
    df['cos_month'] = np.cos(2 * np.pi * df['month'] / 12.0)

    return df

def generate_q1_forecast(
    weekly_features: pd.DataFrame,
    horizon_weeks: int = 12
) -> Tuple[pd.DataFrame, Dict[str, Any], Any]:
    """
    Train a time-series forecasting model and generate forward Q1 forecast.
    """
    # Drop initial rows with NaNs from lag creation
    train_data = weekly_features.dropna(subset=['vol_lag_1', 'vol_lag_2', 'vol_lag_4']).copy()

    feature_cols = [
        'time_step', 'is_q1', 'month', 'week_of_year',
        'vol_lag_1', 'vol_lag_2', 'vol_lag_4',
        'vol_roll_mean_3', 'vol_roll_mean_6',
        'sin_week', 'cos_week', 'sin_month', 'cos_month'
    ]

    X = train_data[feature_cols]
    y = train_data['sales_volume'].values

    # Train XGBoost Time-Series Regressor
    ts_model = XGBRegressor(
        n_estimators=100,
        learning_rate=0.06,
        max_depth=4,
        subsample=0.85,
        random_state=42
    )
    ts_model.fit(X, y)

    # Residual analysis for confidence intervals
    fitted_vals = ts_model.predict(X)
    residuals = y - fitted_vals
    resid_std = float(np.std(residuals))
    mae = float(mean_absolute_error(y, fitted_vals))
    r2 = float(r2_score(y, fitted_vals))

    metrics = {
        'ts_r2': round(r2, 4),
        'ts_mae': round(mae, 1),
        'resid_std': round(resid_std, 1)
    }

    # Recursive multi-step forecast forward into upcoming Q1
    last_row = weekly_features.iloc[-1].copy()
    last_date = last_row['week_start']
    last_step = int(last_row['time_step'])

    forecast_records = []
    current_series = weekly_features['sales_volume'].tolist()

    for i in range(1, horizon_weeks + 1):
        f_date = last_date + pd.Timedelta(weeks=i)
        f_month = f_date.month
        f_week = int(f_date.isocalendar().week)
        f_is_q1 = 1 if f_month in [1, 2, 3] else 0

        # Lags from dynamic rolling series
        lag1 = current_series[-1]
        lag2 = current_series[-2] if len(current_series) >= 2 else lag1
        lag4 = current_series[-4] if len(current_series) >= 4 else lag2

        roll3 = np.mean(current_series[-3:])
        roll6 = np.mean(current_series[-6:])

        sin_w = np.sin(2 * np.pi * f_week / 52.0)
        cos_w = np.cos(2 * np.pi * f_week / 52.0)
        sin_m = np.sin(2 * np.pi * f_month / 12.0)
        cos_m = np.cos(2 * np.pi * f_month / 12.0)

        step_features = pd.DataFrame([{
            'time_step': last_step + i,
            'is_q1': f_is_q1,
            'month': f_month,
            'week_of_year': f_week,
            'vol_lag_1': lag1,
            'vol_lag_2': lag2,
            'vol_lag_4': lag4,
            'vol_roll_mean_3': roll3,
            'vol_roll_mean_6': roll6,
            'sin_week': sin_w,
            'cos_week': cos_w,
            'sin_month': sin_m,
            'cos_month': cos_m
        }])[feature_cols]

        pred_vol = float(ts_model.predict(step_features)[0])
        # Ensure volume stays non-negative
        pred_vol = max(100.0, pred_vol)
        current_series.append(pred_vol)

        # Confidence bounds (80% and 95%)
        lower_80 = max(0.0, pred_vol - 1.28 * resid_std)
        upper_80 = pred_vol + 1.28 * resid_std
        lower_95 = max(0.0, pred_vol - 1.96 * resid_std)
        upper_95 = pred_vol + 1.96 * resid_std

        forecast_records.append({
            'week_start': f_date.strftime('%Y-%m-%d'),
            'month': f_month,
            'week_of_year': f_week,
            'is_q1': f_is_q1,
            'forecast_volume': round(pred_vol),
            'lower_80': round(lower_80),
            'upper_80': round(upper_80),
            'lower_95': round(lower_95),
            'upper_95': round(upper_95),
            'conservative': round(pred_vol * 0.90),
            'optimistic': round(pred_vol * 1.10)
        })

    forecast_df = pd.DataFrame(forecast_records)
    return forecast_df, metrics, ts_model

def run_forecast_pipeline(
    csv_path: str = 'car_pricing_dataset.csv',
    output_dir: str = 'models',
    data_dir: str = 'data'
) -> Dict[str, Any]:
    """Execute full time-series aggregation, model training, and forecast export."""
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)

    print("Loading full dataset for time-series extraction...")
    df, meta = load_and_clean_data(csv_path=csv_path, sample_size=None)

    weekly, monthly = aggregate_time_series(df)
    weekly_features = create_time_series_features(weekly)

    # Save historical weekly series for rapid dashboard visualization
    weekly_csv_path = os.path.join(data_dir, 'weekly_sales_history.csv')
    weekly.to_csv(weekly_csv_path, index=False)
    print(f"Saved weekly history ({len(weekly)} weeks) to {weekly_csv_path}")

    forecast_df, ts_metrics, ts_model = generate_q1_forecast(weekly_features, horizon_weeks=12)

    # Save forecaster model
    ts_model_path = os.path.join(output_dir, 'q1_volume_forecaster.joblib')
    joblib.dump(ts_model, ts_model_path)
    print(f"Saved time-series forecaster to {ts_model_path}")

    # Prepare structured JSON summary for dashboard
    q1_projected_total = int(forecast_df['forecast_volume'].sum())
    jan_forecast = int(forecast_df[forecast_df['month'] == 1]['forecast_volume'].sum()) if (forecast_df['month'] == 1).any() else int(forecast_df['forecast_volume'].iloc[:4].sum())
    feb_forecast = int(forecast_df[forecast_df['month'] == 2]['forecast_volume'].sum()) if (forecast_df['month'] == 2).any() else int(forecast_df['forecast_volume'].iloc[4:8].sum())
    mar_forecast = int(forecast_df[forecast_df['month'] == 3]['forecast_volume'].sum()) if (forecast_df['month'] == 3).any() else int(forecast_df['forecast_volume'].iloc[8:].sum())

    history_records = []
    for _, row in weekly.iterrows():
        history_records.append({
            'date': row['week_start'].strftime('%Y-%m-%d'),
            'volume': int(row['sales_volume']),
            'avg_price': float(row['avg_price']),
            'total_revenue': float(row['total_revenue']),
            'is_q1': int(row['is_q1'])
        })

    summary_payload = {
        'metrics': ts_metrics,
        'q1_projected_volume': q1_projected_total,
        'q1_monthly_breakdown': {
            'January': jan_forecast,
            'February': feb_forecast,
            'March': mar_forecast
        },
        'scenarios': {
            'baseline': q1_projected_total,
            'conservative': int(q1_projected_total * 0.90),
            'optimistic': int(q1_projected_total * 1.10)
        },
        'forecast_weeks': forecast_df.to_dict(orient='records'),
        'historical_series': history_records
    }

    summary_path = os.path.join(output_dir, 'time_series_summary.json')
    with open(summary_path, 'w') as f:
        json.dump(summary_payload, f, indent=2)
    print(f"Saved time-series summary to {summary_path}")

    return summary_payload

if __name__ == '__main__':
    run_forecast_pipeline()
