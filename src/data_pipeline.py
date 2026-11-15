"""
Data Pipeline Module for Car Pricing & Forecasting Analysis.
Handles loading, cleaning, standardization, and feature extraction.
"""

import os
import re
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, Optional

# Standard mappings for vehicle body types
BODY_TYPE_MAPPING = {
    'sedan': 'Sedan',
    'g sedan': 'Sedan',
    'suv': 'SUV',
    'coupe': 'Coupe',
    'g coupe': 'Coupe',
    'convertible': 'Convertible',
    'g convertible': 'Convertible',
    'hatchback': 'Hatchback',
    'wagon': 'Wagon',
    'minivan': 'Minivan',
    'van': 'Minivan',
    'crew cab': 'Pickup/Truck',
    'supercrew': 'Pickup/Truck',
    'extended cab': 'Pickup/Truck',
    'quad cab': 'Pickup/Truck',
    'regular cab': 'Pickup/Truck',
    'supercab': 'Pickup/Truck',
    'king cab': 'Pickup/Truck',
    'double cab': 'Pickup/Truck',
    'cab': 'Pickup/Truck',
    'access cab': 'Pickup/Truck',
    'mega cab': 'Pickup/Truck',
    'club cab': 'Pickup/Truck',
    'koup': 'Coupe',
}

def clean_body_type(val: Any) -> str:
    """Normalize body type into standard clean taxonomy."""
    if pd.isna(val) or not isinstance(val, str):
        return 'Other'
    val_clean = val.strip().lower()
    for key, mapped in BODY_TYPE_MAPPING.items():
        if key in val_clean:
            return mapped
    return 'Other'

def clean_make(val: Any) -> str:
    """Normalize make strings."""
    if pd.isna(val) or not isinstance(val, str):
        return 'Unknown'
    clean = val.strip().title()
    # Normalize common abbreviations
    if clean.lower() in ['vw', 'volkswagen']:
        return 'Volkswagen'
    if clean.lower() in ['mercedes-benz', 'mercedes', 'mercedes-b']:
        return 'Mercedes-Benz'
    if clean.lower() in ['bmw']:
        return 'BMW'
    if clean.lower() in ['gmc']:
        return 'GMC'
    if clean.lower() in ['infiniti']:
        return 'Infiniti'
    return clean

def parse_sale_date(series: pd.Series) -> pd.Series:
    """
    Robust extraction of datetime from saledate strings like:
    'Tue Dec 16 2014 12:30:00 GMT-0800 (PST)'
    """
    # Slice the date string e.g. Dec 16 2014
    cleaned = series.astype(str).str.slice(4, 15)
    return pd.to_datetime(cleaned, format='%b %d %Y', errors='coerce')

def load_and_clean_data(
    csv_path: str = 'car_pricing_dataset.csv',
    sample_size: Optional[int] = None,
    filter_outliers: bool = True
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Load raw car pricing dataset, clean features, and prepare for ML & Time Series.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at path: {csv_path}")

    # Read dataset
    df = pd.read_csv(csv_path, nrows=sample_size)
    initial_count = len(df)

    # 1. Clean categorical text
    df['make'] = df['make'].apply(clean_make)
    df['body_clean'] = df['body'].apply(clean_body_type)
    df['state'] = df['state'].astype(str).str.strip().str.upper()
    df['transmission'] = df['transmission'].fillna('automatic').astype(str).str.lower()
    df['transmission'] = df['transmission'].apply(lambda x: 'manual' if 'man' in x else 'automatic')

    # 2. Parse dates
    df['sale_date'] = parse_sale_date(df['saledate'])
    
    # Fill any failed date parsing with median date
    if df['sale_date'].isna().any():
        median_date = df['sale_date'].dropna().median()
        df['sale_date'] = df['sale_date'].fillna(median_date)

    df['sale_year'] = df['sale_date'].dt.year
    df['sale_month'] = df['sale_date'].dt.month
    df['sale_week'] = df['sale_date'].dt.isocalendar().week
    df['sale_dayofweek'] = df['sale_date'].dt.dayofweek
    df['is_q1'] = df['sale_month'].isin([1, 2, 3]).astype(int)

    # 3. Numeric cleanup & conversions
    numeric_cols = ['year', 'condition', 'odometer', 'mmr', 'sellingprice']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop records with crucial missing values
    df = df.dropna(subset=['year', 'sellingprice', 'odometer', 'condition'])

    # 4. Feature engineering
    df['vehicle_age'] = (df['sale_year'] - df['year']).clip(lower=0)
    df['mileage_per_year'] = (df['odometer'] / (df['vehicle_age'] + 1)).round(1)

    # 5. Outlier filtering (realistic automotive boundaries)
    if filter_outliers:
        df = df[
            (df['sellingprice'] >= 500) & (df['sellingprice'] <= 250000) &
            (df['odometer'] >= 50) & (df['odometer'] <= 450000) &
            (df['year'] >= 1990) & (df['year'] <= 2016) &
            (df['condition'] >= 1) & (df['condition'] <= 50)
        ]

    metadata = {
        'initial_count': initial_count,
        'cleaned_count': len(df),
        'date_range': (str(df['sale_date'].min().date()), str(df['sale_date'].max().date())),
        'unique_makes': int(df['make'].nunique()),
        'top_makes': df['make'].value_counts().head(10).to_dict(),
        'top_bodies': df['body_clean'].value_counts().to_dict(),
        'top_states': df['state'].value_counts().head(10).to_dict(),
        'avg_price': float(df['sellingprice'].mean()),
        'avg_odometer': float(df['odometer'].mean()),
    }

    return df, metadata

if __name__ == '__main__':
    data, meta = load_and_clean_data(sample_size=10000)
    print("Metadata summary:", meta)
