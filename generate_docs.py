"""
AutoPrice AI — Comprehensive Project Documentation Generator
Generates a professional PDF for educational sharing.
"""

import os, sys, json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.platypus.flowables import Flowable

# ── Color palette ──────────────────────────────────────────────────────────────
C_DARK       = colors.HexColor("#151B1D")
C_NAV        = colors.HexColor("#20282B")
C_CARD       = colors.HexColor("#222A2D")
C_SECONDARY  = colors.HexColor("#293235")
C_BLUE       = colors.HexColor("#3979F6")
C_BLUE2      = colors.HexColor("#5890FF")
C_GREEN      = colors.HexColor("#27B879")
C_PURPLE     = colors.HexColor("#9861D5")
C_CYAN       = colors.HexColor("#20B9C9")
C_TEXT       = colors.HexColor("#F1F4F6")
C_TEXT2      = colors.HexColor("#929DA5")
C_BORDER     = colors.HexColor("#303A3E")
C_WHITE      = colors.white
C_BLACK      = colors.black
C_GREY_LIGHT = colors.HexColor("#E8EAED")
C_GREY_MID   = colors.HexColor("#C5CCD4")
C_HEADER_BG  = colors.HexColor("#1A2329")

W, H = A4  # 595.27 x 841.89 pts

# ── Load real data ─────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE, "models", "model_metadata.json")) as f:
    META = json.load(f)

with open(os.path.join(BASE, "models", "time_series_summary.json")) as f:
    TS = json.load(f)

with open(os.path.join(BASE, "data", "q1_analytics.json")) as f:
    Q1 = json.load(f)

KPI = Q1["kpis"]


# ── Custom Flowables ───────────────────────────────────────────────────────────
class ColorRect(Flowable):
    """Full-width colored rectangle (decorative banner)."""
    def __init__(self, width, height, fill_color, radius=0):
        super().__init__()
        self.width = width
        self.height = height
        self.fill_color = fill_color
        self.radius = radius

    def draw(self):
        self.canv.setFillColor(self.fill_color)
        if self.radius:
            self.canv.roundRect(0, 0, self.width, self.height, self.radius, fill=1, stroke=0)
        else:
            self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=0)


class SectionBadge(Flowable):
    """Small colored pill label above section titles."""
    def __init__(self, text, color=None, width=120, height=16):
        super().__init__()
        self.text = text
        self.color = color or C_BLUE
        self.width = width
        self.height = height

    def draw(self):
        c = self.canv
        c.setFillColor(self.color)
        c.roundRect(0, 0, self.width, self.height, 4, fill=1, stroke=0)
        c.setFillColor(C_WHITE)
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(self.width / 2, 4, self.text.upper())


# ── Style helpers ──────────────────────────────────────────────────────────────
def styles():
    base = getSampleStyleSheet()

    def ps(name, **kw):
        return ParagraphStyle(name, parent=base["Normal"], **kw)

    return {
        "cover_title": ps("ct", fontSize=36, textColor=C_WHITE,
                           leading=44, fontName="Helvetica-Bold", alignment=TA_LEFT),
        "cover_sub":   ps("cs", fontSize=15, textColor=C_BLUE,
                           leading=22, fontName="Helvetica", alignment=TA_LEFT),
        "cover_meta":  ps("cm", fontSize=10, textColor=C_TEXT2,
                           leading=15, fontName="Helvetica", alignment=TA_LEFT),
        "h1": ps("h1", fontSize=22, textColor=C_DARK, fontName="Helvetica-Bold",
                  leading=28, spaceAfter=6),
        "h2": ps("h2", fontSize=15, textColor=C_DARK, fontName="Helvetica-Bold",
                  leading=20, spaceBefore=14, spaceAfter=4),
        "h3": ps("h3", fontSize=12, textColor=C_BLUE, fontName="Helvetica-Bold",
                  leading=16, spaceBefore=10, spaceAfter=3),
        "body": ps("body", fontSize=9.5, textColor=colors.HexColor("#2C3E50"),
                    leading=15, spaceAfter=5, alignment=TA_JUSTIFY),
        "bullet": ps("bullet", fontSize=9.5, textColor=colors.HexColor("#2C3E50"),
                      leading=14, leftIndent=14, bulletIndent=0,
                      spaceBefore=1, spaceAfter=1, bulletText="•"),
        "caption": ps("caption", fontSize=8, textColor=C_TEXT2,
                       leading=12, alignment=TA_CENTER, fontName="Helvetica-Oblique"),
        "mono":    ps("mono", fontSize=8.5, textColor=colors.HexColor("#1A1A2E"),
                       fontName="Courier", leading=13, leftIndent=12,
                       backColor=colors.HexColor("#F4F6F9"), spaceAfter=4),
        "toc_item": ps("toc", fontSize=10, textColor=colors.HexColor("#2C3E50"),
                        leading=16, leftIndent=0),
        "toc_sub":  ps("tocs", fontSize=9, textColor=colors.HexColor("#5A6B7A"),
                        leading=14, leftIndent=16),
        "kpi_num":  ps("kn", fontSize=18, textColor=C_BLUE, fontName="Helvetica-Bold",
                        leading=22, alignment=TA_CENTER),
        "kpi_lbl":  ps("kl", fontSize=7.5, textColor=C_TEXT2,
                        leading=11, alignment=TA_CENTER),
        "metric_pass": ps("mp", fontSize=9, textColor=C_GREEN,
                           fontName="Helvetica-Bold", alignment=TA_CENTER),
    }


ST = styles()


def hr(color=C_BLUE, thickness=1.5):
    return HRFlowable(width="100%", thickness=thickness, color=color,
                      spaceAfter=6, spaceBefore=4)


def sp(h=6):
    return Spacer(1, h)


def para(text, style="body"):
    return Paragraph(text, ST[style])


def h1(text):
    return [sp(10), para(text, "h1"), hr(C_BLUE, 2), sp(4)]


def h2(text):
    return [para(text, "h2"), hr(C_GREY_MID, 0.8), sp(2)]


def h3(text):
    return [para(text, "h3")]


def bullets(items):
    return [para(i, "bullet") for i in items]


def mono(text):
    return [para(line if line else " ", "mono") for line in text.strip().split("\n")]


# ── Generic table ──────────────────────────────────────────────────────────────
def make_table(data, col_widths=None, header=True, alternating=True):
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    cmds = [
        ("FONTNAME",    (0, 0), (-1, 0 if not header else 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 8.5),
        ("LEADING",     (0, 0), (-1, -1), 12),
        ("TOPPADDING",  (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("GRID",        (0, 0), (-1, -1), 0.4, C_BORDER),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
    ]
    if header:
        cmds += [
            ("BACKGROUND", (0, 0), (-1, 0), C_DARK),
            ("TEXTCOLOR",  (0, 0), (-1, 0), C_WHITE),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ]
    if alternating:
        for i in range(1 if header else 0, len(data)):
            if i % 2 == (0 if header else 1):
                cmds.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F7F9FB")))
    t.setStyle(TableStyle(cmds))
    return t


# ── KPI mini-table ─────────────────────────────────────────────────────────────
def kpi_row(pairs):
    """pairs: list of (label, value) tuples."""
    n = len(pairs)
    cw = [(W - 4 * cm) / n] * n
    header = [Paragraph(v, ST["kpi_num"]) for _, v in pairs]
    labels = [Paragraph(l, ST["kpi_lbl"]) for l, _ in pairs]
    t = Table([header, labels], colWidths=cw)
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), colors.HexColor("#F0F4FF")),
        ("BOX",         (0, 0), (-1, -1), 1, C_BLUE),
        ("INNERGRID",   (0, 0), (-1, -1), 0.5, C_BORDER),
        ("TOPPADDING",  (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
    ]))
    return t


# ══════════════════════════════════════════════════════════════════════════════
# PAGE BUILDERS
# ══════════════════════════════════════════════════════════════════════════════

def build_cover(story):
    """Full dark cover page."""
    # Dark background painted via canvas callback — we approximate with big rect
    story.append(ColorRect(W - 4 * cm, 7 * cm, C_DARK))
    story.append(sp(-195))  # pull text up into rect

    story.append(Spacer(1, 1.6 * cm))
    story.append(para("AutoPrice AI", "cover_title"))
    story.append(sp(4))
    story.append(para("Car Pricing Intelligence & Q1 Sales Analytics Platform", "cover_sub"))
    story.append(sp(8))
    story.append(para("Comprehensive Project Documentation", "cover_meta"))
    story.append(para(f"Generated: {datetime.now().strftime('%B %d, %Y')}", "cover_meta"))
    story.append(para("Version 1.0  ·  Educational Edition", "cover_meta"))
    story.append(sp(28))

    # horizontal divider
    story.append(HRFlowable(width="100%", thickness=2, color=C_BLUE,
                              spaceAfter=12, spaceBefore=4))

    # summary badges row
    badges = [
        ("ML MODEL", "XGBoost R² 0.8029", C_BLUE),
        ("DATASET",  "558,837 Records",   C_PURPLE),
        ("Q1 REVENUE", "$4.70B",          C_GREEN),
        ("API",      "7 REST Endpoints",  C_CYAN),
    ]
    bdata = [[Paragraph(f"<b><font color='white'>{v}</font></b><br/>"
                         f"<font color='#AAAAAA' size='7'>{l}</font>",
                         ParagraphStyle("", fontSize=10, leading=14,
                                        alignment=TA_CENTER, fontName="Helvetica-Bold"))
              for l, v, _ in badges]]
    bt = Table(bdata, colWidths=[(W - 4 * cm) / 4] * 4)
    bt.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, 0), C_BLUE),
        ("BACKGROUND",    (1, 0), (1, 0), C_PURPLE),
        ("BACKGROUND",    (2, 0), (2, 0), C_GREEN),
        ("BACKGROUND",    (3, 0), (3, 0), C_CYAN),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("INNERGRID",     (0, 0), (-1, -1), 1, C_WHITE),
        ("BOX",           (0, 0), (-1, -1), 1, C_WHITE),
    ]))
    story.append(bt)
    story.append(sp(16))

    # tech stack row
    tech = [
        ["Technology Stack"],
        ["Python 3.10  ·  FastAPI + Uvicorn  ·  XGBoost  ·  Chart.js  ·  GitHub  ·  Render"],
    ]
    tt = Table(tech, colWidths=[W - 4 * cm])
    tt.setStyle(TableStyle([
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 9),
        ("FONTSIZE",      (0, 1), (-1, 1), 9),
        ("TEXTCOLOR",     (0, 0), (-1, -1), colors.HexColor("#444444")),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#F7F9FF")),
        ("BOX",           (0, 0), (-1, -1), 0.6, C_BORDER),
    ]))
    story.append(tt)
    story.append(PageBreak())


def build_toc(story):
    story += h1("Table of Contents")
    toc = [
        ("1", "Executive Summary", "3"),
        ("2", "Dataset Overview", "3"),
        ("3", "Data Pipeline & Preprocessing", "4"),
        ("4", "Machine Learning — Car Price Prediction", "5"),
        ("  4.1", "Problem Statement & Approach", "5"),
        ("  4.2", "Feature Engineering", "5"),
        ("  4.3", "Model Comparison & Results", "6"),
        ("  4.4", "Top Feature Importances", "6"),
        ("5", "Q1 Sales Analysis", "7"),
        ("  5.1", "Key Performance Indicators", "7"),
        ("  5.2", "Monthly Breakdown", "7"),
        ("  5.3", "Body Style Distribution", "8"),
        ("  5.4", "Top States & Models", "8"),
        ("  5.5", "Business Insights", "9"),
        ("6", "Time-Series Q1 Demand Forecasting", "9"),
        ("  6.1", "Methodology", "9"),
        ("  6.2", "Model Performance", "10"),
        ("  6.3", "12-Week Projections & Scenarios", "10"),
        ("7", "Dashboard Architecture", "11"),
        ("  7.1", "Four-Page SPA Structure", "11"),
        ("  7.2", "Technology Stack", "11"),
        ("  7.3", "Color System", "12"),
        ("8", "API Reference", "12"),
        ("9", "Deployment Guide", "13"),
        ("10", "Testing", "14"),
        ("11", "Project Structure", "14"),
        ("12", "Conclusion & Recommendations", "15"),
    ]
    tdata = [[Paragraph(f"<b>{n}</b>", ST["toc_item"]),
              Paragraph(title, ST["toc_item"] if not n.startswith("  ") else ST["toc_sub"]),
              Paragraph(f"<b>{pg}</b>", ST["toc_item"])]
             for n, title, pg in toc]
    tt = Table(tdata, colWidths=[1.1 * cm, 12.5 * cm, 1 * cm])
    tt.setStyle(TableStyle([
        ("FONTSIZE",      (0, 0), (-1, -1), 9.5),
        ("LEADING",       (0, 0), (-1, -1), 15),
        ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("ALIGN",         (2, 0), (2, -1), "RIGHT"),
        ("LINEBELOW",     (0, 0), (-1, -1), 0.3, C_GREY_LIGHT),
    ]))
    story.append(tt)
    story.append(PageBreak())


def build_executive_summary(story):
    story += h1("1. Executive Summary")
    story.append(para(
        "The <b>AutoPrice AI Platform</b> is a full-stack data analytics and machine learning "
        "application built over a wholesale vehicle auction dataset containing "
        f"<b>{KPI['total_records_dataset']:,}</b> records sourced from Manheim-style US car "
        "auctions (January 2014 – July 2015). The platform integrates two interconnected "
        "analytical workstreams:"))
    story.append(sp(4))
    story += bullets([
        "<b>Car Price Prediction</b> — A supervised regression pipeline using XGBoost to "
        "estimate the fair-market selling price of a used vehicle from intrinsic features "
        "only (make, body, year, odometer, condition, transmission, state). The model achieves "
        "R² = 0.8029 without using any dealer-benchmark leakage.",
        "<b>Q1 Sales Analysis</b> — A business-intelligence dashboard analysing "
        f"{KPI['q1_total_orders']:,} Q1 auction transactions worth "
        f"${KPI['q1_total_revenue'] / 1e9:.2f}B, covering monthly trends, body-style "
        "distribution, regional performance, and top-model rankings.",
        "<b>Demand Forecasting</b> — A lag-feature XGBoost time-series model projecting "
        "12-week Q1 auction volume with R² = 0.9982.",
        "<b>MyDash-Inspired SPA</b> — A dark-themed, four-page analytics dashboard "
        "(FastAPI + vanilla JS + Chart.js) with 7 REST endpoints, deployable on Render or Docker.",
    ])
    story.append(sp(8))
    story.append(para(
        "The project was designed for an educational audience. Every metric shown in the "
        "dashboard and in this document derives from real data — no dummy values are present. "
        "The source code is fully committed to GitHub and the live service is deployed on Render."))
    story.append(PageBreak())


def build_dataset(story):
    story += h1("2. Dataset Overview")
    story.append(para(
        "The underlying dataset is a wholesale vehicle auction record set covering used-car "
        "sales across the United States. It includes every detail needed to study market "
        "pricing, volume trends, and consumer preferences."))
    story.append(sp(6))

    story += h2("2.1 Dataset Statistics")
    story.append(kpi_row([
        ("Total Raw Records",   f"{KPI['total_records_dataset']:,}"),
        ("Cleaned Records",     f"{KPI['cleaned_records']:,}"),
        ("Q1 Transactions",     f"{KPI['q1_total_orders']:,}"),
        ("Date Range",          "Jan 2014 – Jul 2015"),
    ]))
    story.append(sp(10))

    story += h2("2.2 Schema")
    schema = [
        ["Column", "Type", "Description"],
        ["year",         "Integer", "Vehicle manufacture year"],
        ["make",         "String",  "Brand / manufacturer (Ford, BMW, Toyota…)"],
        ["model",        "String",  "Model name (Fusion, 3 Series, Camry…)"],
        ["trim",         "String",  "Trim level"],
        ["body",         "String",  "Body style (Sedan, SUV, Pickup/Truck…)"],
        ["transmission", "String",  "automatic or manual"],
        ["vin",          "String",  "Vehicle Identification Number (dropped at training)"],
        ["state",        "String",  "2-letter US state code"],
        ["condition",    "Float",   "Auction grade 1–49 (higher = better)"],
        ["odometer",     "Integer", "Miles driven"],
        ["color",        "String",  "Exterior paint color"],
        ["interior",     "String",  "Interior color"],
        ["seller",       "String",  "Auction seller ID"],
        ["mmr",          "Float",   "Manheim Market Report benchmark price"],
        ["sellingprice", "Float",   "Target variable — final auction selling price"],
        ["saledate",     "String",  "ISO 8601 datetime of sale"],
    ]
    story.append(make_table(schema,
                             col_widths=[3.2 * cm, 2 * cm, 9.4 * cm]))
    story.append(sp(8))

    story += h2("2.3 Data Quality Notes")
    story += bullets([
        "Raw dataset: 558,837 rows; after cleaning: 540,618 rows (3.3% removed).",
        "<b>saledate</b> column arrives as a US locale string "
        "('Tue Jan 20 2015 12:30:00 GMT+0000') and is parsed with a custom regex "
        "to extract day, month, year, and hour-of-day features.",
        "MMR (Manheim Market Report) is treated as a privileged benchmark. "
        "It is excluded from the primary intrinsic model to avoid benchmark leakage "
        "and is only used in a secondary reference model.",
        "Outlier boundaries: sellingprice filtered to $500–$230,000; "
        "odometer filtered to 0–300,000 miles.",
        "Body-style normalization maps free-text variants "
        "('Crew Cab', 'Extended Cab') to canonical categories "
        "(Sedan, SUV, Pickup/Truck, Coupe, Hatchback, Minivan, Wagon, Convertible, Other).",
    ])
    story.append(PageBreak())


def build_pipeline(story):
    story += h1("3. Data Pipeline & Preprocessing")
    story.append(para(
        "The data pipeline (<b>src/data_pipeline.py</b>) implements a reproducible "
        "clean-transform-engineer workflow that converts raw auction records into "
        "model-ready feature matrices."))
    story.append(sp(6))

    story += h2("3.1 Cleaning Steps")
    story += bullets([
        "Drop rows with null <i>sellingprice</i> or <i>year</i>.",
        "Parse <i>saledate</i> using regex extraction for locale-safe handling.",
        "Clip <i>sellingprice</i> to [500, 230,000] and <i>odometer</i> to [0, 300,000].",
        "Normalise body-style free text to 9 canonical categories.",
        "Lowercase transmission; keep only 'automatic' / 'manual'.",
        "Derive <b>is_q1</b> = 1 if sale month ∈ {1, 2, 3}.",
    ])
    story.append(sp(6))

    story += h2("3.2 Feature Engineering")
    feat_data = [
        ["Feature",         "Formula",                        "Purpose"],
        ["vehicle_age",     "sale_year − make_year",          "Depreciation proxy"],
        ["mileage_per_year","odometer ÷ max(vehicle_age, 1)", "Usage intensity"],
        ["is_q1",           "month ∈ {1,2,3}",                "Seasonal demand flag"],
        ["make_cat",        "One-hot encoded make (top N)",   "Brand premium signal"],
        ["body_cat",        "One-hot encoded body style",     "Segment signal"],
        ["state_cat",       "One-hot encoded state",          "Regional market"],
        ["transmission",    "Binary (auto=1, manual=0)",      "Preference signal"],
    ]
    story.append(make_table(feat_data,
                             col_widths=[3.5 * cm, 5.5 * cm, 5.6 * cm]))
    story.append(sp(6))

    story += h2("3.3 Train / Test Split")
    story += bullets([
        "80 / 20 random split with random_state=42 for reproducibility.",
        f"Training samples: {META['training_samples']:,}",
        "Target variable: <b>sellingprice</b> (USD).",
        "No data leakage — MMR is excluded from intrinsic model features.",
    ])
    story.append(PageBreak())


def build_ml(story):
    story += h1("4. Machine Learning — Car Price Prediction")

    story += h2("4.1 Problem Statement")
    story.append(para(
        "Given a vehicle's <b>intrinsic attributes only</b> (no dealer benchmark prices), "
        "predict its final wholesale auction selling price. This is a regression task with "
        "a right-skewed price distribution (mean ≈ $13,147; std ≈ $9,404)."))
    story.append(sp(4))
    story.append(para(
        "A secondary reference model that includes MMR (Manheim Market Report) is also "
        "trained to quantify how much benchmark information improves accuracy — "
        "useful for understanding the value of market intelligence data."))
    story.append(sp(8))

    story += h2("4.2 Feature Engineering")
    story += bullets([
        "Numerical: <b>year</b>, <b>odometer</b>, <b>condition</b>, "
        "<b>vehicle_age</b>, <b>mileage_per_year</b>.",
        "Categorical (one-hot): <b>make</b> (top 24 brands + 'Other'), "
        "<b>body</b> (9 categories), <b>state</b> (25 states).",
        "Binary: <b>transmission</b> (automatic=1, manual=0).",
        "Intrinsic model total features: ~60 after one-hot expansion.",
        "Full model adds: <b>mmr</b> as a single additional numerical feature.",
    ])
    story.append(sp(8))

    story += h2("4.3 Model Comparison & Results")
    story.append(para(
        "Three algorithms were evaluated on the same 20% held-out test set:"))
    story.append(sp(4))

    comp = [
        ["Model", "R²", "MAE (USD)", "RMSE (USD)", "MAPE (%)"],
        ["Linear Regression",
         f"{META['intrinsic_models']['Linear Regression']['r2']:.4f}",
         f"${META['intrinsic_models']['Linear Regression']['mae']:,.2f}",
         f"${META['intrinsic_models']['Linear Regression']['rmse']:,.2f}",
         f"{META['intrinsic_models']['Linear Regression']['mape']:.2f}%"],
        ["Ridge Regression",
         f"{META['intrinsic_models']['Ridge Regression']['r2']:.4f}",
         f"${META['intrinsic_models']['Ridge Regression']['mae']:,.2f}",
         f"${META['intrinsic_models']['Ridge Regression']['rmse']:,.2f}",
         f"{META['intrinsic_models']['Ridge Regression']['mape']:.2f}%"],
        ["★ XGBoost (Intrinsic)",
         f"{META['intrinsic_models']['XGBoost Regressor']['r2']:.4f}",
         f"${META['intrinsic_models']['XGBoost Regressor']['mae']:,.2f}",
         f"${META['intrinsic_models']['XGBoost Regressor']['rmse']:,.2f}",
         f"{META['intrinsic_models']['XGBoost Regressor']['mape']:.2f}%"],
        ["─── With MMR Benchmark ───", "", "", "", ""],
        ["Ridge + MMR",
         f"{META['full_models']['Ridge with MMR']['r2']:.4f}",
         f"${META['full_models']['Ridge with MMR']['mae']:,.2f}",
         f"${META['full_models']['Ridge with MMR']['rmse']:,.2f}",
         f"{META['full_models']['Ridge with MMR']['mape']:.2f}%"],
        ["XGBoost + MMR",
         f"{META['full_models']['XGBoost with MMR']['r2']:.4f}",
         f"${META['full_models']['XGBoost with MMR']['mae']:,.2f}",
         f"${META['full_models']['XGBoost with MMR']['rmse']:,.2f}",
         f"{META['full_models']['XGBoost with MMR']['mape']:.2f}%"],
    ]
    ct = make_table(comp, col_widths=[5.5 * cm, 2.2 * cm, 3 * cm, 3 * cm, 2 * cm])
    # highlight best intrinsic row (index 3)
    ct.setStyle(TableStyle([
        ("BACKGROUND", (0, 3), (-1, 3), colors.HexColor("#E8F5E9")),
        ("TEXTCOLOR",  (0, 3), (-1, 3), colors.HexColor("#1B5E20")),
        ("FONTNAME",   (0, 3), (-1, 3), "Helvetica-Bold"),
        # divider row
        ("BACKGROUND", (0, 4), (-1, 4), C_SECONDARY),
        ("TEXTCOLOR",  (0, 4), (-1, 4), C_WHITE),
        ("FONTNAME",   (0, 4), (-1, 4), "Helvetica-BoldOblique"),
        ("ALIGN",      (0, 4), (-1, 4), "CENTER"),
    ]))
    story.append(ct)
    story.append(sp(4))
    story.append(para(
        "<i>★ XGBoost Intrinsic is the production model used in the dashboard prediction "
        "interface. Adding MMR (benchmark reference) reduces MAE by 63% — demonstrating "
        "the significant information value of market benchmark data.</i>", "caption"))
    story.append(sp(8))

    story += h2("4.4 Top Feature Importances (XGBoost Intrinsic)")
    story.append(para(
        "XGBoost assigns a gain-based importance score to each input feature. "
        "The top 15 are shown below:"))
    story.append(sp(4))
    fi_data = [["Rank", "Feature", "Importance Score", "Insight"]]
    insights = {
        "make_cat_BMW": "BMW commands highest premium — brand is top price driver",
        "make_cat_Infiniti": "Luxury brand carries significant price uplift",
        "make_cat_Mercedes-Benz": "Premium segment strong even in wholesale auctions",
        "make_cat_Audi": "European luxury brand premium",
        "body_cat_Hatchback": "Body style strongly differentiates pricing tier",
        "odometer": "Mileage is a primary depreciation signal",
        "make_cat_Lexus": "Toyota's luxury arm commands measurable premium",
        "body_cat_Sedan": "Sedan segment drives large volume at mid price",
        "body_cat_Pickup/Truck": "Truck segment commands distinct pricing",
        "make_cat_Kia": "Value brand signals lower price range",
        "year": "Manufacture year is a standard depreciation factor",
        "make_cat_Other": "Residual brand bucket",
        "make_cat_Cadillac": "American luxury brand premium",
        "make_cat_Acura": "Honda luxury arm premium",
        "body_cat_SUV": "SUV popularity reflected in pricing",
    }
    for i, f in enumerate(META["top_features_importance"], 1):
        clean = f["feature"].replace("make_cat_", "Make: ").replace("body_cat_", "Body: ")
        fi_data.append([
            str(i), clean,
            f"{f['importance']:.4f} ({f['importance']*100:.1f}%)",
            insights.get(f["feature"], "—"),
        ])
    story.append(make_table(fi_data,
                             col_widths=[1 * cm, 4 * cm, 3.5 * cm, 6.1 * cm]))
    story.append(PageBreak())


def build_q1_analysis(story):
    story += h1("5. Q1 Sales Analysis")
    story.append(para(
        "The Q1 Sales Analysis covers the January–March 2015 auction period — the most "
        "data-dense window in the dataset, representing the core wholesale market season."))
    story.append(sp(6))

    story += h2("5.1 Key Performance Indicators")
    story.append(kpi_row([
        ("Q1 Revenue",         f"${KPI['q1_total_revenue']/1e9:.2f}B"),
        ("Total Units Sold",   f"{KPI['q1_total_orders']:,}"),
        ("Avg Order Value",    f"${KPI['q1_avg_order_value']:,.2f}"),
        ("Top Brand",         KPI['q1_top_make']),
    ]))
    story.append(sp(8))
    story.append(kpi_row([
        ("Avg Car Price (All)", f"${KPI['avg_car_price']:,.2f}"),
        ("Min Car Price",       f"${KPI['min_car_price']:,.0f}"),
        ("Max Car Price",       f"${KPI['max_car_price']:,.0f}"),
        ("Top Body Style",      KPI['q1_top_body']),
    ]))
    story.append(sp(10))

    story += h2("5.2 Monthly Performance Breakdown")
    mp = Q1["monthly_performance"]
    mp_data = [["Month", "Volume (Units)", "Revenue", "Avg Price", "Avg Odometer", "Avg Condition"]]
    for m in mp:
        mp_data.append([
            m["month_name"],
            f"{m['volume']:,}",
            f"${m['revenue']/1e9:.3f}B",
            f"${m['avg_price']:,.2f}",
            f"{m['avg_odometer']:,.0f} mi",
            f"{m['avg_condition']:.1f}",
        ])
    story.append(make_table(mp_data,
                             col_widths=[2.5 * cm, 3 * cm, 3 * cm, 2.8 * cm, 3 * cm, 3 * cm]))
    story.append(sp(4))
    story.append(para(
        "<i>February is the strongest month by volume (161,507 units) and revenue ($2.22B), "
        "reflecting mid-Q1 wholesale auction peaks. March shows a sharp drop to 45,808 "
        "units, coinciding with the data cutoff in the source dataset.</i>", "caption"))
    story.append(sp(8))

    story += h2("5.3 Body Style Distribution")
    bd = Q1["body_distribution"]
    bp = Q1["body_percentages"]
    bd_data = [["Body Style", "Units Sold", "Market Share (%)"]]
    for style, vol in sorted(bd.items(), key=lambda x: -x[1]):
        bd_data.append([style, f"{vol:,}", f"{bp.get(style, 0):.1f}%"])
    story.append(make_table(bd_data, col_widths=[5 * cm, 4 * cm, 4 * cm]))
    story.append(sp(4))
    story.append(para(
        "<i>Sedan dominates at 44.5% market share, followed by SUV at 25.8% — "
        "reflecting the two most popular US vehicle segments in the wholesale channel.</i>",
        "caption"))
    story.append(sp(8))

    story += h2("5.4 Top 10 States by Volume")
    st_data = [["Rank", "State", "Units Sold"]]
    for i, (state, vol) in enumerate(Q1["state_distribution"].items(), 1):
        st_data.append([str(i), state, f"{vol:,}"])
    story.append(make_table(st_data, col_widths=[1.5 * cm, 4 * cm, 4 * cm]))
    story.append(sp(8))

    story += h2("5.5 Top 10 Models by Volume")
    tm_data = [["Rank", "Model", "Volume", "Avg Price", "Revenue"]]
    for i, m in enumerate(Q1["top_models"], 1):
        tm_data.append([
            str(i), m["model"],
            f"{m['volume']:,}",
            f"${m['avg_price']:,.2f}",
            f"${m['revenue']/1e6:.1f}M",
        ])
    story.append(make_table(tm_data,
                             col_widths=[1.2 * cm, 3.5 * cm, 2.8 * cm, 3 * cm, 3 * cm]))
    story.append(sp(8))

    story += h2("5.6 Business Insights")
    story += bullets([
        "<b>Florida leads US wholesale volume</b> (51,518 units) — warm climate and high "
        "population density drive the highest auction throughput, followed by California "
        "(45,246) and Pennsylvania (32,408).",
        "<b>Ford F-150 generates the highest revenue per model</b> ($175.4M from 9,285 units "
        "at avg $18,886) — premium truck pricing offsets lower absolute volume.",
        "<b>Nissan Altima leads by unit volume</b> (12,748 units at avg $11,637) — "
        "high-turnover, mid-market sedan dominance typical of fleet auction channels.",
        "<b>BMW commands the highest average wholesale price</b> ($20,767 avg) among top-10 "
        "makes, confirming luxury brand retention even in the auction channel.",
        "<b>February volume spike (+16.3% vs January)</b> aligns with tax-refund season "
        "behaviour commonly observed in US used-car markets.",
    ])
    story.append(PageBreak())


def build_forecast(story):
    story += h1("6. Time-Series Q1 Demand Forecasting")
    story.append(para(
        "A dedicated XGBoost time-series regression model (<b>src/forecast_pipeline.py</b>) "
        "is trained on weekly auction volume history to project Q1 demand. "
        "This model enables operational planning — inventory sizing, staffing, and "
        "marketing spend allocation."))
    story.append(sp(6))

    story += h2("6.1 Methodology")
    story += bullets([
        "<b>Weekly aggregation</b>: raw transactions aggregated to ISO week buckets "
        "using the sale date.",
        "<b>Lag features</b>: volume at t−1, t−2, t−4 weeks (short, medium, monthly lags).",
        "<b>Rolling statistics</b>: 4-week rolling mean and 4-week rolling standard deviation.",
        "<b>Cyclical harmonics</b>: sine and cosine transforms of week-of-year "
        "(sin_week, cos_week) to capture annual seasonality without ordinal bias.",
        "<b>Calendar dummies</b>: is_q1 flag, month number.",
        "<b>XGBoost hyperparameters</b>: n_estimators=200, learning_rate=0.05, "
        "max_depth=4, subsample=0.8 — tuned for the small weekly dataset.",
        "<b>Train/test</b>: last 8 weeks held out as test set for metric evaluation.",
    ])
    story.append(sp(8))

    story += h2("6.2 Model Performance")
    story.append(kpi_row([
        ("Time-Series R²",        f"{TS['metrics']['ts_r2']:.4f}"),
        ("MAE (units/week)",      f"{TS['metrics']['ts_mae']:,.1f}"),
        ("Residual Std (σ)",      f"{TS['metrics']['resid_std']:,.1f}"),
        ("Historical Weeks",      "35"),
    ]))
    story.append(sp(6))
    story.append(para(
        "An R² of 0.9982 on the held-out test set indicates near-perfect in-sample fit. "
        "This is partly attributable to the structured weekly pattern of large peak weeks "
        "(Jan–Feb 2015) followed by rapid decline — a pattern well-captured by lag features. "
        "Users should interpret out-of-sample projections with the confidence intervals "
        "provided by the ±80% and ±95% bands."))
    story.append(sp(8))

    story += h2("6.3 12-Week Projections & Planning Scenarios")
    scen = TS["scenarios"]
    story.append(kpi_row([
        ("Baseline (Q1 Total)",     f"{scen['baseline']:,} units"),
        ("Conservative (−10%)",     f"{scen['conservative']:,} units"),
        ("Optimistic (+10%)",       f"{scen['optimistic']:,} units"),
        ("Forecast Horizon",        "12 weeks"),
    ]))
    story.append(sp(8))

    story += h2("6.4 Monthly Allocation")
    mb = TS["q1_monthly_breakdown"]
    mb_data = [
        ["Month", "Projected Units", "Share of Q1 (%)"],
        ["January",  f"{mb['January']:,}",  f"{mb['January']/scen['baseline']*100:.1f}%"],
        ["February", f"{mb['February']:,}", f"{mb['February']/scen['baseline']*100:.1f}%"],
        ["March",    f"{mb['March']:,}",    f"{mb['March']/scen['baseline']*100:.1f}%"],
        ["Q1 Total", f"{scen['baseline']:,}", "100.0%"],
    ]
    story.append(make_table(mb_data, col_widths=[5 * cm, 4 * cm, 4 * cm]))
    story.append(sp(6))
    story.append(para(
        "<i>January carries the highest projected share (35.5%), consistent with "
        "tax-refund season pre-loading and Q1 fleet auction cycles.</i>", "caption"))
    story.append(PageBreak())


def build_dashboard(story):
    story += h1("7. Dashboard Architecture")
    story.append(para(
        "The front-end is a single-page application (SPA) served directly by FastAPI's "
        "StaticFiles middleware. It uses vanilla JavaScript with Chart.js for interactivity, "
        "eliminating any Node.js build chain — the entire frontend is a single <b>index.html</b> "
        "file (~2,500 lines) alongside a <b>server.py</b> API backend."))
    story.append(sp(6))

    story += h2("7.1 Four-Page Structure")
    page_data = [
        ["Page", "Name",              "Content"],
        ["1",    "Overview Dashboard","6 KPI cards · Weekly revenue area chart · "
                 "Body-style donut chart · Monthly bar chart · Top vehicles table"],
        ["2",    "Car Price Prediction","Input form (make, body, year, odometer, "
                 "condition, transmission, state) · XGBoost prediction · "
                 "Confidence interval display · Submitted details panel"],
        ["3",    "Q1 Sales Analysis", "Date / category / region / channel filters · "
                 "Revenue area chart · Monthly bar chart · Category donut · "
                 "State bar chart · Ranked model table · Insight cards"],
        ["4",    "Demand Forecast & Reports",
                 "12-week time-series line chart with CI bands · "
                 "Monthly scenario table · Export buttons (CSV, JSON) · "
                 "Audit log panel"],
    ]
    story.append(make_table(page_data,
                             col_widths=[1 * cm, 4 * cm, 9.6 * cm]))
    story.append(sp(8))

    story += h2("7.2 Technology Stack")
    stack = [
        ["Layer",       "Technology",         "Version / Notes"],
        ["Runtime",     "Python",             "3.10.11"],
        ["Web Server",  "FastAPI + Uvicorn",  "0.100+ / ASGI, dynamic PORT"],
        ["ML Engine",   "XGBoost",            "1.7+"],
        ["Frontend",    "Vanilla JS",         "ES6 modules, no framework"],
        ["Charts",      "Chart.js",           "v4 (CDN)"],
        ["Serialisation","Joblib + JSON",     "Model & analytics artefacts"],
        ["Styling",     "Custom CSS",         "Dark-theme design system"],
        ["CI/Testing",  "pytest",             "17 tests, 4 modules"],
        ["Deployment",  "Render Web Service", "Docker or native Python"],
        ["VCS",         "GitHub",             "Branch: main"],
    ]
    story.append(make_table(stack,
                             col_widths=[3 * cm, 4 * cm, 7.6 * cm]))
    story.append(sp(8))

    story += h2("7.3 Color System")
    colors_data = [
        ["Token",             "Hex Value", "Usage"],
        ["Main Background",   "#151B1D",   "Page / body background"],
        ["Navigation BG",     "#20282B",   "Top nav bar"],
        ["Card Background",   "#222A2D",   "Dashboard panels"],
        ["Secondary BG",      "#293235",   "Chart backgrounds, table rows"],
        ["Primary Blue",      "#3979F6",   "Buttons, active states, links"],
        ["Secondary Blue",    "#5890FF",   "Hover, secondary actions"],
        ["Success Green",     "#27B879",   "Positive metrics, progress bars"],
        ["Purple",            "#9861D5",   "Secondary charts, donut segments"],
        ["Cyan",              "#20B9C9",   "Tertiary charts, badges"],
        ["Primary Text",      "#F1F4F6",   "Headings, body text on dark bg"],
        ["Secondary Text",    "#929DA5",   "Labels, captions, placeholders"],
        ["Borders",           "#303A3E",   "Card borders, table dividers"],
    ]
    story.append(make_table(colors_data,
                             col_widths=[4 * cm, 3 * cm, 7.6 * cm]))
    story.append(PageBreak())


def build_api(story):
    story += h1("8. API Reference")
    story.append(para(
        "The FastAPI backend (<b>app/server.py</b>) exposes 7 REST endpoints consumed by "
        "the dashboard SPA. All endpoints return JSON. The server binds to the PORT "
        "environment variable (default 8501) for Render compatibility."))
    story.append(sp(6))

    api_data = [
        ["#", "Method", "Path",                  "Description"],
        ["1",  "GET",   "/",                     "Serve SPA index.html"],
        ["2",  "GET",   "/api/overview",         "Dashboard KPIs (all metrics from both projects)"],
        ["3",  "POST",  "/api/predict",          "Car price prediction — accepts JSON vehicle attributes, returns predicted price + confidence interval"],
        ["4",  "GET",   "/api/q1-analysis",      "Full Q1 analytics JSON (monthly perf, body dist, state dist, top models, weekly trajectory, ranked vehicles). Supports optional filters: month, body, state, channel"],
        ["5",  "GET",   "/api/forecast",         "12-week demand forecast with baseline / conservative / optimistic scenarios, CI bands, and historical series"],
        ["6",  "GET",   "/api/model-info",       "Model metadata: feature importances, benchmark stats, supported categories"],
        ["7",  "GET",   "/health",               "Health check — returns {status: ok, version: 1.0}"],
    ]
    story.append(make_table(api_data,
                             col_widths=[0.6 * cm, 1.6 * cm, 4.5 * cm, 7.9 * cm]))
    story.append(sp(8))

    story += h2("8.1 Predict Endpoint — Request / Response")
    story.append(para("<b>POST /api/predict</b> — Request body (JSON):"))
    story += mono("""\
{
  "make": "BMW",
  "body": "Sedan",
  "year": 2014,
  "odometer": 25000,
  "condition": 35.0,
  "transmission": "automatic",
  "state": "CA"
}""")
    story.append(para("<b>Response:</b>"))
    story += mono("""\
{
  "predicted_price": 24850.00,
  "confidence_low":  21240.00,
  "confidence_high": 28460.00,
  "model_used": "XGBoost Intrinsic (R²=0.8029)"
}""")
    story.append(PageBreak())


def build_deployment(story):
    story += h1("9. Deployment Guide")

    story += h2("9.1 Local Run (Windows)")
    story += bullets([
        "Prerequisites: Python 3.10, pip, Git.",
        "Clone: <b>git clone https://github.com/naga-03/car-pricing-q1-forecast.git</b>",
        "Install: <b>pip install -r requirements.txt</b>",
        "Run: <b>.\\py.ps1 run_app.py</b> (auto-opens browser at http://localhost:8501)",
        "Alternatively: <b>uvicorn app.server:app --host 0.0.0.0 --port 8501</b>",
    ])
    story.append(sp(6))

    story += h2("9.2 Render Web Service (Recommended)")
    steps = [
        ["Step", "Action"],
        ["1", "Go to dashboard.render.com and click + New → Web Service"],
        ["2", "Connect your GitHub repository (naga-03/car-pricing-q1-forecast)"],
        ["3", "Set Runtime: Python 3"],
        ["4", "Set Build Command: pip install -r requirements.txt"],
        ["5", "Set Start Command: uvicorn app.server:app --host 0.0.0.0 --port $PORT"],
        ["6", "Set Environment Variable: PORT = 8501 (or leave for Render auto-assign)"],
        ["7", "Click Deploy Web Service — first deploy takes ~3-5 minutes"],
        ["8", "Access the live URL provided by Render (e.g. https://your-app.onrender.com)"],
    ]
    story.append(make_table(steps, col_widths=[1.2 * cm, 13.4 * cm]))
    story.append(sp(6))
    story.append(para(
        "<i>The render.yaml blueprint in the repository root enables one-click deploy "
        "via the Render Blueprint feature (New → Blueprint).</i>", "caption"))
    story.append(sp(6))

    story += h2("9.3 Docker")
    story += mono("""\
# Build image
docker build -t autoprice-ai .

# Run container
docker run -p 8501:8501 autoprice-ai

# Or use docker-compose
docker-compose up --build""")
    story.append(sp(4))
    story.append(para(
        "The Dockerfile uses <b>CMD uvicorn app.server:app --host 0.0.0.0 --port ${PORT:-8501}</b> "
        "to support dynamic port binding on any cloud platform."))
    story.append(PageBreak())


def build_testing(story):
    story += h1("10. Testing")
    story.append(para(
        "The project includes a full pytest test suite with 17 tests across 4 modules, "
        "covering the data pipeline, trained models, forecast pipeline, and API routes."))
    story.append(sp(6))

    test_data = [
        ["File",                        "Tests", "Covers"],
        ["tests/test_data_pipeline.py", "4",     "CSV loading, cleaning, feature engineering, is_q1 flag"],
        ["tests/test_models.py",        "4",     "Intrinsic model load, predict shape, MMR model, metadata JSON"],
        ["tests/test_forecast.py",      "2",     "Time-series model load, 12-week forecast output shape"],
        ["tests/test_api.py",           "7",     "All 7 API endpoints: status codes, response schema, field presence"],
        ["TOTAL",                       "17",    "All PASS — pytest exit code 0"],
    ]
    story.append(make_table(test_data, col_widths=[5.2 * cm, 1.5 * cm, 7.9 * cm]))
    story.append(sp(6))

    story.append(para("<b>Run tests:</b>"))
    story += mono(".\\py.ps1 -m pytest tests -v")
    story.append(sp(4))
    story.append(para("<b>Run with coverage:</b>"))
    story += mono(".\\py.ps1 -m pytest tests --cov=src --cov=app --cov-report=term-missing")
    story.append(PageBreak())


def build_structure(story):
    story += h1("11. Project Structure")
    story.append(para("Full repository file tree:"))
    story += mono("""\
car-pricing-q1-forecast/
├── app/
│   ├── server.py              ← FastAPI server  (7 endpoints)
│   ├── components.py          ← Plotly charts + Streamlit legacy
│   ├── main.py                ← Streamlit legacy entry point
│   └── static/
│       └── index.html         ← MyDash 4-page SPA (~2,500 lines)
├── data/
│   ├── car_pricing_dataset.csv  ← Raw dataset (Git LFS, 558,837 rows)
│   ├── q1_analytics.json        ← Pre-computed Q1 aggregations
│   └── weekly_sales_history.csv ← 35-week weekly series
├── models/
│   ├── price_model_intrinsic.joblib  ← XGBoost trained model (no MMR)
│   ├── price_model_full.joblib       ← XGBoost + MMR benchmark model
│   ├── q1_volume_forecaster.joblib   ← Time-series XGBoost model
│   ├── model_metadata.json           ← Metrics, features, categories
│   └── time_series_summary.json      ← Forecast projections + history
├── src/
│   ├── data_pipeline.py       ← Load, clean, feature-engineer
│   ├── train_models.py        ← Model training scripts
│   ├── forecast_pipeline.py   ← Time-series forecasting
│   └── predict.py             ← VehicleValuationService inference
├── tests/
│   ├── test_data_pipeline.py
│   ├── test_models.py
│   ├── test_forecast.py
│   └── test_api.py
├── generate_docs.py           ← This PDF generator
├── run_app.py                 ← Auto-open browser launcher
├── run_dashboard.bat          ← Windows 1-click launcher
├── py.ps1                     ← PowerShell Python shim
├── Dockerfile
├── docker-compose.yml
├── render.yaml                ← Render blueprint
├── requirements.txt
└── README.md""")
    story.append(PageBreak())


def build_conclusion(story):
    story += h1("12. Conclusion & Recommendations")
    story.append(para(
        "The AutoPrice AI platform demonstrates how a complete data science product can be "
        "built from a raw auction dataset through to a deployed, interactive analytics dashboard. "
        "It integrates supervised machine learning, time-series forecasting, REST API design, "
        "and modern frontend development into a single cohesive educational project."))
    story.append(sp(8))

    story += h2("12.1 Key Learnings")
    story += bullets([
        "<b>Data quality matters most</b> — 3.3% of rows were removed due to missing or "
        "out-of-range values; careful outlier handling prevented model distortion.",
        "<b>Feature leakage is a real risk</b> — MMR reduces MAE by 63%, but including "
        "it in production would be inappropriate unless the user has real-time MMR access.",
        "<b>XGBoost outperforms linear models</b> for this dataset — R² 0.80 vs 0.65 "
        "confirms the non-linear interactions between brand, body, and price.",
        "<b>Lag features dominate time-series</b> — the previous 1–4 weeks of volume "
        "explain 99.8% of variance, confirming strong autocorrelation in auction cycles.",
        "<b>ASGI over WSGI</b> — using FastAPI + Uvicorn instead of Flask or Django "
        "provides async-ready, standards-compliant JSON APIs with automatic OpenAPI docs.",
    ])
    story.append(sp(8))

    story += h2("12.2 Future Improvements")
    story += bullets([
        "<b>Real-time MMR feed</b> — Integrate live Manheim API data to serve the "
        "full-accuracy XGBoost+MMR model in production.",
        "<b>Colour / interior encoding</b> — Add colour preference heat-maps; "
        "these features were dropped but carry pricing information.",
        "<b>SHAP explainability</b> — Add SHAP force plots on the prediction page "
        "to show users which features drove each estimate.",
        "<b>Automated retraining</b> — Schedule weekly model retraining as new "
        "auction data arrives using a background worker on Render.",
        "<b>PostgreSQL persistence</b> — Move pre-computed analytics to a Render "
        "Postgres instance for filter-aware server-side aggregation.",
        "<b>Authentication</b> — Add OAuth2 / JWT for multi-tenant API access.",
        "<b>Mobile app</b> — Expose the prediction API to a React Native app "
        "for dealer lot-side instant valuation.",
    ])
    story.append(sp(8))

    story += h2("12.3 Project References")
    story += bullets([
        "GitHub Repository: https://github.com/naga-03/car-pricing-q1-forecast",
        "Live Dashboard: Deployed via Render Web Service",
        "Dataset: US Wholesale Vehicle Auction Records (Jan 2014 – Jul 2015)",
        "ML Framework: XGBoost (Chen & Guestrin, 2016)",
        "API Framework: FastAPI (Sebastián Ramírez, 2018–)",
        "Charts: Chart.js v4 (Chart.js Contributors, 2023)",
        "Design Reference: MyDash dark-theme analytics dashboard",
    ])

    story.append(sp(16))
    story.append(HRFlowable(width="100%", thickness=1.5, color=C_BLUE,
                              spaceAfter=8, spaceBefore=4))
    story.append(para(
        f"<i>AutoPrice AI Project Documentation — Generated {datetime.now().strftime('%B %d, %Y')} "
        "· For educational and sharing purposes · All metrics derived from real data.</i>",
        "caption"))


# ══════════════════════════════════════════════════════════════════════════════
# HEADERS & FOOTERS
# ══════════════════════════════════════════════════════════════════════════════

def on_page(canvas, doc):
    canvas.saveState()
    page = doc.page

    # Header bar (skip cover page 1)
    if page > 1:
        canvas.setFillColor(C_DARK)
        canvas.rect(0, H - 1.4 * cm, W, 1.4 * cm, fill=1, stroke=0)
        canvas.setFillColor(C_BLUE)
        canvas.rect(0, H - 1.4 * cm, 0.4 * cm, 1.4 * cm, fill=1, stroke=0)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.setFillColor(C_WHITE)
        canvas.drawString(1 * cm, H - 0.85 * cm, "AutoPrice AI — Project Documentation")
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(C_TEXT2)
        canvas.drawRightString(W - 1 * cm, H - 0.85 * cm,
                                datetime.now().strftime("%B %Y"))

    # Footer bar
    if page > 1:
        canvas.setFillColor(C_DARK)
        canvas.rect(0, 0, W, 1 * cm, fill=1, stroke=0)
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(C_TEXT2)
        canvas.drawString(1 * cm, 0.37 * cm,
                           "Car Pricing Intelligence & Q1 Sales Analytics Platform")
        canvas.drawRightString(W - 1 * cm, 0.37 * cm, f"Page {page}")

    canvas.restoreState()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    out_path = os.path.join(BASE, "AutoPrice_AI_Project_Documentation.pdf")

    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.6 * cm,
        title="AutoPrice AI — Project Documentation",
        author="AutoPrice AI",
        subject="Car Pricing & Q1 Sales Analytics",
    )

    story = []
    build_cover(story)
    build_toc(story)
    build_executive_summary(story)
    build_dataset(story)
    build_pipeline(story)
    build_ml(story)
    build_q1_analysis(story)
    build_forecast(story)
    build_dashboard(story)
    build_api(story)
    build_deployment(story)
    build_testing(story)
    build_structure(story)
    build_conclusion(story)

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)

    size_kb = os.path.getsize(out_path) // 1024
    print(f"\n✅  PDF generated successfully!")
    print(f"   Path : {out_path}")
    print(f"   Size : {size_kb} KB")
    print(f"   Pages: ~15 (estimated)")


if __name__ == "__main__":
    main()
