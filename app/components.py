"""
UI Components, Custom Styling, and Plotly Visualizations for Car Pricing Dashboard.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, Any, List

# Custom Modern CSS
CUSTOM_CSS = """
<style>
    /* Global font & typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* KPI Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        backdrop-filter: blur(10px);
        margin-bottom: 12px;
    }
    .metric-title {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94A3B8;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 4px;
    }
    .metric-caption {
        font-size: 0.8rem;
        color: #10B981;
    }

    /* Valuation Result Hero Banner */
    .valuation-hero {
        background: linear-gradient(135deg, #1E3A8A 0%, #1E40AF 50%, #3B82F6 100%);
        border-radius: 16px;
        padding: 28px;
        color: white;
        margin: 20px 0;
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.3);
    }
    .valuation-label {
        font-size: 0.9rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        opacity: 0.85;
    }
    .valuation-price {
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 8px 0;
    }
    .valuation-range {
        font-size: 1rem;
        opacity: 0.9;
    }
    .badge-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.2);
        margin-top: 10px;
    }
</style>
"""

def render_metric_card(title: str, value: str, caption: str = "", delta_color: str = "#10B981") -> str:
    """Return HTML for an executive stat metric card."""
    caption_html = f'<div class="metric-caption" style="color: {delta_color}">{caption}</div>' if caption else ''
    return f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        {caption_html}
    </div>
    """

def plot_q1_forecast_time_series(history_records: List[Dict], forecast_records: List[Dict]) -> go.Figure:
    """Create interactive Plotly chart combining historical sales and multi-step Q1 forecast."""
    df_hist = pd.DataFrame(history_records)
    df_hist['date'] = pd.to_datetime(df_hist['date'])
    df_fore = pd.DataFrame(forecast_records)
    df_fore['date'] = pd.to_datetime(df_fore['week_start'])

    fig = go.Figure()

    # 1. 95% Confidence Interval Band (Forecast)
    fig.add_trace(go.Scatter(
        x=pd.concat([df_fore['date'], df_fore['date'][::-1]]),
        y=pd.concat([df_fore['upper_95'], df_fore['lower_95'][::-1]]),
        fill='toself',
        fillcolor='rgba(59, 130, 246, 0.15)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=True,
        name='95% Confidence Interval'
    ))

    # 2. 80% Confidence Interval Band (Forecast)
    fig.add_trace(go.Scatter(
        x=pd.concat([df_fore['date'], df_fore['date'][::-1]]),
        y=pd.concat([df_fore['upper_80'], df_fore['lower_80'][::-1]]),
        fill='toself',
        fillcolor='rgba(59, 130, 246, 0.3)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=True,
        name='80% Confidence Interval'
    ))

    # 3. Historical Sales Volume
    fig.add_trace(go.Scatter(
        x=df_hist['date'],
        y=df_hist['volume'],
        mode='lines+markers',
        name='Historical Sales Volume',
        line=dict(color='#10B981', width=2.5),
        marker=dict(size=4)
    ))

    # 4. Forecasted Sales Volume
    fig.add_trace(go.Scatter(
        x=df_fore['date'],
        y=df_fore['forecast_volume'],
        mode='lines+markers',
        name='Q1 Projected Forecast',
        line=dict(color='#3B82F6', width=3, dash='dash'),
        marker=dict(size=6, symbol='diamond')
    ))

    # 5. Conservative & Optimistic Scenarios
    fig.add_trace(go.Scatter(
        x=df_fore['date'],
        y=df_fore['conservative'],
        mode='lines',
        name='Conservative (-10%)',
        line=dict(color='#F59E0B', width=1.5, dash='dot')
    ))
    fig.add_trace(go.Scatter(
        x=df_fore['date'],
        y=df_fore['optimistic'],
        mode='lines',
        name='Optimistic (+10%)',
        line=dict(color='#8B5CF6', width=1.5, dash='dot')
    ))

    fig.update_layout(
        title="Weekly Automotive Sales Volume: History & Upcoming Q1 Forecast",
        xaxis_title="Calendar Timeline",
        yaxis_title="Weekly Vehicle Sales Volume",
        template="plotly_dark",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=60, b=20),
        height=480
    )
    return fig

def plot_monthly_breakdown(breakdown_dict: Dict[str, int]) -> go.Figure:
    """Bar chart for Q1 monthly forecast distribution."""
    months = list(breakdown_dict.keys())
    values = list(breakdown_dict.values())
    colors = ['#3B82F6', '#60A5FA', '#93C5FD']

    fig = go.Figure(data=[
        go.Bar(
            x=months,
            y=values,
            text=[f"{v:,}" for v in values],
            textposition='auto',
            marker_color=colors
        )
    ])
    fig.update_layout(
        title="Projected Q1 Sales Demand by Month",
        xaxis_title="Month",
        yaxis_title="Units Sold",
        template="plotly_dark",
        margin=dict(l=20, r=20, t=40, b=20),
        height=320
    )
    return fig

def plot_feature_importances(features: List[Dict]) -> go.Figure:
    """Horizontal bar chart for top ML feature importances."""
    df_feat = pd.DataFrame(features).sort_values('importance', ascending=True)
    # Clean up feature names for presentation
    df_feat['display_name'] = df_feat['feature'].str.replace('make_cat_', 'Make: ') \
                                                 .str.replace('body_cat_', 'Body: ') \
                                                 .str.replace('state_cat_', 'State: ') \
                                                 .str.replace('_', ' ').str.title()

    fig = go.Figure(go.Bar(
        x=df_feat['importance'],
        y=df_feat['display_name'],
        orientation='h',
        marker=dict(
            color=df_feat['importance'],
            colorscale='Blues'
        )
    ))
    fig.update_layout(
        title="Intrinsic Price Drivers (XGBoost Relative Importance)",
        xaxis_title="Relative Feature Importance Score",
        yaxis_title="",
        template="plotly_dark",
        margin=dict(l=20, r=20, t=40, b=20),
        height=420
    )
    return fig
