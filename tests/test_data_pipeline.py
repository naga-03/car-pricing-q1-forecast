"""Unit tests for Car Pricing Data Pipeline."""
import pytest
import pandas as pd
from src.data_pipeline import clean_make, clean_body_type, parse_sale_date, load_and_clean_data

def test_clean_make():
    assert clean_make('ford') == 'Ford'
    assert clean_make('BMW') == 'BMW'
    assert clean_make('mercedes-benz') == 'Mercedes-Benz'
    assert clean_make('vw') == 'Volkswagen'
    assert clean_make(None) == 'Unknown'

def test_clean_body_type():
    assert clean_body_type('sedan') == 'Sedan'
    assert clean_body_type('g sedan') == 'Sedan'
    assert clean_body_type('SUV') == 'SUV'
    assert clean_body_type('crew cab') == 'Pickup/Truck'
    assert clean_body_type('convertible') == 'Convertible'
    assert clean_body_type('unknown_custom') == 'Other'

def test_parse_sale_date():
    s = pd.Series(['Tue Dec 16 2014 12:30:00 GMT-0800 (PST)', 'Thu Jan 15 2015 04:30:00 GMT-0800 (PST)'])
    parsed = parse_sale_date(s)
    assert parsed.dt.year.tolist() == [2014, 2015]
    assert parsed.dt.month.tolist() == [12, 1]

def test_load_and_clean_sample():
    df, meta = load_and_clean_data(sample_size=1000)
    assert len(df) > 0
    assert 'vehicle_age' in df.columns
    assert 'mileage_per_year' in df.columns
    assert 'is_q1' in df.columns
    assert meta['cleaned_count'] > 0
