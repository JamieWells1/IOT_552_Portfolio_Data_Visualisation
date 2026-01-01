import matplotlib
matplotlib.use("Agg")

from flask import Flask, render_template_string, send_file
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from io import BytesIO
import base64

app = Flask(__name__)
plt.style.use("seaborn-v0_8-whitegrid")


def generate_scenario1_chart():
    fig, ax = plt.subplots(figsize=(14, 7))
    np.random.seed(42)
    
    dates = pd.date_range(start="2020-01-01", end="2024-12-31", freq="ME")
    trend = np.linspace(100, 160, len(dates))
    
    seasonal = np.zeros(len(dates))
    for i, date in enumerate(dates):
        month = date.month
        if month == 11: seasonal[i] = 35
        elif month == 12: seasonal[i] = 55
        elif month == 1: seasonal[i] = -15  # jan dip
        elif month in [6, 7]: seasonal[i] = 15
        elif month == 2: seasonal[i] = -10

    # some random noise
    noise = np.random.normal(0, 8, len(dates))
    sales = np.maximum(trend + seasonal + noise, 50)

    forecast_dates = pd.date_range(start="2025-01-01", end="2025-12-31", freq="ME")
    forecast_trend = np.linspace(160, 175, 12)
    forecast_seasonal = np.zeros(12)
    for i, date in enumerate(forecast_dates):
        month = date.month
        if month == 11: forecast_seasonal[i] = 40
        elif month == 12: forecast_seasonal[i] = 60
        elif month == 1: forecast_seasonal[i] = -15
        elif month in [6, 7]: forecast_seasonal[i] = 18
        elif month == 2: forecast_seasonal[i] = -10

    forecast_values = forecast_trend + forecast_seasonal
    confidence_multiplier = np.linspace(1, 2.5, 12)
    lower_bound = forecast_values - (15 * confidence_multiplier)
    upper_bound = forecast_values + (15 * confidence_multiplier)

    ax.plot(dates, sales, color="#2E86AB", linewidth=2.5, label="Historical Sales (Electronics)")
    ax.plot(forecast_dates, forecast_values, color="#E94F37", linewidth=2.5, linestyle="--", label="Forecast")
    ax.fill_between(forecast_dates, lower_bound, upper_bound, color="#E94F37", alpha=0.2, label="95% Confidence Interval")
    ax.axvline(x=dates[-1], color="#666666", linestyle=":", linewidth=1.5, alpha=0.7)

    for idx in [11, 23, 35, 47, 59]:
        if idx < len(dates):
            ax.annotate("Holiday\nPeak", xy=(dates[idx], sales[idx]), xytext=(dates[idx], sales[idx] + 25),
                       fontsize=9, ha="center", color="#666666", arrowprops=dict(arrowstyle="->", color="#999999"))

    ax.annotate("Predicted Peak:\n£235k ± £37k", xy=(forecast_dates[11], forecast_values[11]),
               xytext=(forecast_dates[8], forecast_values[11] + 35), fontsize=10, ha="center", color="#E94F37",
               fontweight="bold", bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFF5F5", edgecolor="#E94F37"),
               arrowprops=dict(arrowstyle="->", color="#E94F37"))

    ax.set_xlabel("Date", fontsize=12, fontweight="bold")
    ax.set_ylabel("Sales (£000s)", fontsize=12, fontweight="bold")
    ax.set_title("Time-Series Sales Forecast: Electronics Category\nPredictive Analysis for Holiday Demand Planning", fontsize=14, fontweight="bold")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(loc="upper left")
    ax.set_ylim(40, 280)
    plt.tight_layout()
    return fig


def generate_scenario2_chart():
    fig, ax = plt.subplots(figsize=(12, 8))
    
    data = {
        "Factor": ["Month-to-month contract", "3+ support calls (60 days)", "Tenure < 6 months",
                   "Electronic check payment", "Fiber optic internet", "No online security add-on",
                   "No tech support add-on", "Paperless billing", "Senior citizen",
                   "1-year contract", "Bank transfer payment", "2-year contract"],
        "Churn Rate": [42.7, 38.2, 34.5, 33.1, 30.8, 28.4, 26.1, 24.3, 21.6, 11.3, 8.7, 2.8],
        "Sample Size": [3875, 892, 1456, 2365, 3096, 3498, 3473, 4171, 1142, 1473, 1286, 1695]
    }

    df = pd.DataFrame(data).sort_values("Churn Rate", ascending=True)
    colors = ["#E94F37" if r >= 30 else "#F39237" if r >= 20 else "#F9C846" if r >= 10 else "#2E8B57" for r in df["Churn Rate"]]
    
    bars = ax.barh(df["Factor"], df["Churn Rate"], color=colors, edgecolor="white", height=0.7)

    for bar, rate, n in zip(bars, df["Churn Rate"], df["Sample Size"]):
        ax.text(bar.get_width() + 0.8, bar.get_y() + bar.get_height()/2, f"{rate:.1f}%", va="center", fontweight="bold")
        ax.text(bar.get_width() - 1, bar.get_y() + bar.get_height()/2, f"n={n:,}", va="center", ha="right", color="white", fontsize=9)

    ax.set_xlabel("Churn Rate (%)", fontsize=12, fontweight="bold")
    ax.set_title("Diagnostic Analysis: Customer Churn Rate by Segment\nIdentifying Key Drivers of 15% Churn Increase", fontsize=14, fontweight="bold")
    ax.set_xlim(0, 52)
    ax.axvline(x=26.5, color="#333333", linestyle="--", linewidth=1.5, alpha=0.7)
    ax.text(27, len(df) - 0.5, "Overall: 26.5%", fontsize=10, fontweight="bold")

    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(facecolor="#E94F37", label="High Risk (≥30%)"), Patch(facecolor="#F39237", label="Medium Risk (20-30%)"),
                       Patch(facecolor="#F9C846", label="Low-Medium (10-20%)"), Patch(facecolor="#2E8B57", label="Low Risk (<10%)")],
              loc="lower right", fontsize=9)

    plt.tight_layout()
    return fig


def fig_to_base64(fig):
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=150, bbox_inches="tight", facecolor="white")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    plt.close(fig)
    return image_base64


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>IOT552U Visualisations</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #1a1a2e, #16213e); min-height: 100vh; padding: 40px 20px; margin: 0; }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { color: white; text-align: center; margin-bottom: 40px; }
        .chart-section { background: white; border-radius: 16px; padding: 30px; margin-bottom: 40px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
        .chart-title { font-size: 1.4rem; color: #333; margin-bottom: 20px; }
        img { max-width: 100%; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Data Analysis Visualisations</h1>
        <section class="chart-section">
            <h2 class="chart-title">Scenario 1: Retail Holiday Demand Forecasting</h2>
            <img src="data:image/png;base64,{{ scenario1_chart }}">
        </section>
        <section class="chart-section">
            <h2 class="chart-title">Scenario 2: Telecom Customer Churn Analysis</h2>
            <img src="data:image/png;base64,{{ scenario2_chart }}">
        </section>
    </div>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, 
                                  scenario1_chart=fig_to_base64(generate_scenario1_chart()),
                                  scenario2_chart=fig_to_base64(generate_scenario2_chart()))

if __name__ == "__main__":
    print("\nServer running at http://localhost:5001\n")
    app.run(debug=True, host="0.0.0.0", port=5001)
