# MyDash: AutoPrice AI – Car Pricing & Q1 Sales Intelligence Platform

A commercial-grade analytics platform unifying **Car Price Prediction using Machine Learning** and **Q1 Sales Analysis using Data Analytics**. Features a modern dark-themed dashboard inspired by the **MyDash** design system, an electric blue accent palette, real-time vehicle valuation, and multi-step demand forecasting.

---

## 🎨 MyDash Design System & Aesthetics

* **Color Palette**:
  * Main Background: `#151B1D` (Deep near-black charcoal)
  * Navigation Bar: `#20282B` (Dark charcoal header with active blue indicator line)
  * Cards & Panels: `#222A2D` with subtle `#303A3E` borders and subtle shadows
  * Primary Accent: `#3979F6` (Electric Blue)
  * Success & Positive Metrics: `#27B879` (Vibrant Emerald Green)
  * Secondary Accents: `#20B9C9` (Cyan), `#9861D5` (Purple), `#EAB308` (Gold)
  * Typography: Crisp `#F1F4F6` primary text with `#929DA5` secondary text
* **Design Language**:
  * Top horizontal navigation with active item curve-underline
  * Compact statistic KPI panels arranged horizontally
  * Smooth electric blue area charts with custom floating dark tooltips
  * Donut charts with clean percentage readouts
  * Radial inventory velocity gauge
  * Ranked data tables with alternating row backgrounds and hover highlight
  * Fully responsive across desktop, laptop, tablet, and mobile

---

## 🚀 Key Modules & Pages

### 1. 📊 Dashboard Overview
Displays key metrics from both analytics projects:
* **Car Price Prediction KPIs**:
  * Total Dataset Records: **558,837** (540,618 cleaned)
  * Average Car Price: **$13,904** (Median: $11,800)
  * Price Range: **$500 – $230,000**
  * Model Accuracy ($R^2$): **0.8029** (MAE: **$2,505.06**)
* **Q1 Sales Analysis KPIs**:
  * Total Q1 Revenue: **$4.70 Billion** ($4,704,658,042)
  * Total Q1 Transactions: **346,161 units**
  * Average Order Value: **$13,591**
  * Peak Month: **February (161,507 units)**
  * Top Make & Body: **Ford (60,053 units)** & **Sedan (153,996 units)**
* **Visual Widgets**:
  * Weekly Revenue & Sales Trajectory (Area Chart in Electric Blue)
  * Top-Selling Vehicle Models (Ranked table with avatars and volume)
  * Progress Target Card (78% Target Met) & Profit Card ($4.70B Q1 Turnover)
  * Body Style Distribution (Donut Chart) & Radial Velocity Gauge (68%)
  * Monthly Sales Performance (Electric Blue Bar Chart)

### 2. 🚗 Car Price Intelligence (Prediction Engine)
Dedicated machine learning valuation interface:
* **Features Supported**: Brand/Make, Body Style, Year (1995–2016), Market State, Transmission, Odometer Mileage, Wholesale Condition Score (1–50), and optional MMR Benchmark toggle.
* **Valuation Card**:
  * Large valuation readout in bold typography
  * Calibrated confidence interval ($\pm\text{MAE}$ margin)
  * Market Tier badge (`Premium / Luxury Segment` vs `Average Market Segment`)
* **Model Reliability Scorecard**:
  * Intrinsic XGBoost ($R^2=0.8029$, $\text{MAE}=\$2,505$, $\text{RMSE}=\$4,108$, $\text{MAPE}=25.89\%$)
  * Benchmark Model with MMR ($R^2=0.9713$, $\text{MAE}=\$924.31$)

### 3. 📈 Q1 Sales Analysis
Dedicated Business Intelligence dashboard:
* **Interactive Filters**: Filter by Month Window (All Q1, Jan, Feb, Mar), Body Style, and Region/State.
* **4-Grid Visualizations**:
  1. Q1 Revenue Trajectory (Area Chart)
  2. Monthly Performance Comparison (Bar Chart)
  3. Product / Category Performance (Donut Chart)
  4. Regional Sales Distribution (Top 10 States Bar Chart)
* **Ranked Vehicles Table** with search and live calculations.
* **Strategic Business Insights & Findings** cards.

### 4. 📑 Reports & ⚙️ Settings
* One-click JSON and CSV summary report downloads.
* Full machine learning audit log.
* Platform configurations (currency, default model, themes).

---

## ⚡ Quickstart & Execution (Using `py`)

### 1. Launch the Dashboard
Run the platform using the Python launcher script:

```powershell
.\py.ps1 run_app.py
```
*(Or double-click [run_dashboard.bat](file:///c:/Users/nagal/Downloads/projects/car-pricing-q1-forecast-1/run_dashboard.bat))*.

The dashboard will open automatically in your browser at:  
👉 **`http://localhost:8501`**  
👉 **API Docs**: `http://localhost:8501/docs`

### 2. Run the Full Test Suite
Execute the 17 unit and API integration tests:

```powershell
.\py.ps1 -m pytest tests -v
```

### 3. (Optional) Run Streamlit Legacy Mode
If you prefer the multi-tab Streamlit dashboard:

```powershell
.\py.ps1 run_app.py --streamlit
```

---

## 🐳 Docker & Container Deployment

### Build and Run with Docker
```bash
# Build production image
docker build -t mydash-autoprice:latest .

# Run container on port 8501
docker run -d -p 8501:8501 --name mydash_platform mydash-autoprice:latest
```

Open `http://localhost:8501` in your browser.

### Docker Compose
```bash
docker compose up -d --build
```

---

## 🌐 Production REST API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the MyDash single-page analytics application |
| `GET` | `/api/health` | Service health status and model load verification |
| `GET` | `/api/overview` | Dynamic KPIs, area chart data, and top models from both projects |
| `POST` | `/api/predict` | Computes vehicle fair-market valuation and confidence interval |
| `GET` | `/api/q1-analysis` | Filterable Q1 sales metrics by month, body style, and state |
| `GET` | `/api/categories` | Returns supported makes, body styles, and states |
| `GET` | `/api/reports/summary` | Structured summary payload for report downloads |
| `GET` | `/docs` | Interactive Swagger UI API documentation |

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
