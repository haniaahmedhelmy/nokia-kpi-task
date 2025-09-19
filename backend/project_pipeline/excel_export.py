import pandas as pd
import json
from pathlib import Path
import re
import xlwings as xw

# Define file paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = BASE_DIR / "cleaned_dataset.csv"   
SETTINGS_PATH = BASE_DIR / "settings.json"        
OUTPUT_PATH = BASE_DIR / "report.xlsx"            
CHART_IMG = BASE_DIR / "chart.png"         

# Hardcoded colors for KPIs and equations
COLOR_MAP = {
    "kpi001": "#1f77b4",   # blue
    "kpi002": "#ff7f0e",   # orange
    "kpi003": "#23e923",   # green
    "kpi004": "#d62728",   # red
    "kpi005": "#9467bd",   # purple
    "kpi006": "#8c564b",   # brown
    "kpi007": "#9DC9CC",   # pink
    "kpi008": "#962491",   # gray
    "kpi009": "#bcbd22",   # olive
    "line_equation": "#CC9D9D",  # light red for line equation
    "bar_equation": "#403F40",   # dark gray for bar equation
}

def safe_eval_equation(df: pd.DataFrame, equation: str) -> pd.Series:
    """Safely evaluate simple KPI equations (no builtins allowed)."""
    allowed = {col: df[col] for col in df.columns if col != "date"} 
    pattern = r"^[\dkpi+\-*/().\s]+$" 
    if not re.match(pattern, equation):
        raise ValueError(f"Invalid equation: {equation}")
    return eval(equation, {"__builtins__": {}}, allowed) 

def generate_excel_report():
    # Load dataset and settings
    df = pd.read_csv(DATASET_PATH, parse_dates=["date"])
    with open(SETTINGS_PATH, "r") as f:
        settings = json.load(f)
        # Ensure chart config exists
        if not settings.get("line_chart"):
            settings["line_chart"] = {"type": "list", "value": []}
        if not settings.get("bar_chart"):
            settings["bar_chart"] = {"type": "list", "value": []}

    # Apply days_back filter (limit rows)
    days_back = settings.get("days_back", 0)
    if days_back > 0:
        df = df.sort_values("date").tail(days_back)

    # Prepare chart data
    line_data, bar_data = pd.DataFrame(), pd.DataFrame()

    # Handle line chart data
    if settings["line_chart"]["type"] == "equation":
        eq = settings["line_chart"]["value"]
        if eq:
            df["line_equation"] = safe_eval_equation(df, eq)
            line_data = df[["line_equation"]]
    elif settings["line_chart"]["type"] == "list" and settings["line_chart"]["value"]:
        line_data = df[settings["line_chart"]["value"]]

    # Handle bar chart data
    if settings["bar_chart"]["type"] == "equation":
        eq = settings["bar_chart"]["value"]
        if eq:
            df["bar_equation"] = safe_eval_equation(df, eq)
            bar_data = df[["bar_equation"]]
    elif settings["bar_chart"]["type"] == "list" and settings["bar_chart"]["value"]:
        bar_data = df[settings["bar_chart"]["value"]]

    # Merge into final dataset
    combined = pd.concat([df[["date"]], line_data, bar_data], axis=1)

    # Write data to Excel
    with pd.ExcelWriter(OUTPUT_PATH, engine="xlsxwriter", datetime_format="dd-mmm") as writer:
        combined.to_excel(writer, sheet_name="Report", index=False)

        workbook = writer.book
        worksheet = writer.sheets["Report"]

        # Create base bar chart
        bar_chart = workbook.add_chart({"type": "column"})
        bar_chart.set_title({"name": "KPI Chart"})

        # X-axis formatting
        bar_chart.set_x_axis({
            "name": "Date",
            "date_axis": True,
            "num_format": "dd-mmm",
        })

        # Auto-scale chart ranges
        bar_min, bar_max = (bar_data.min().min(), bar_data.max().max()) if not bar_data.empty else (0, 1)
        line_min, line_max = (line_data.min().min(), line_data.max().max()) if not line_data.empty else (0, 1)

        # Bar chart left axis
        bar_chart.set_y_axis({
            "name": "Bar Values",
            "major_gridlines": {"visible": False},
            "min": int(bar_min * 0.95),
            "max": int(bar_max * 1.05),
        })

        # Add bar series
        for j, col in enumerate(bar_data.columns, 1 + line_data.shape[1]):
            color = COLOR_MAP.get(col, "#ff0000")
            bar_chart.add_series({
                "name":       ["Report", 0, j],
                "categories": ["Report", 1, 0, len(combined), 0],
                "values":     ["Report", 1, j, len(combined), j],
                "fill":       {"color": color},
                "border":     {"color": color},
                "y2_axis":    False,
            })

        # Create line chart
        line_chart = workbook.add_chart({"type": "line"})

        # Line chart right axis
        line_chart.set_y2_axis({
            "name": "Line Values",
            "major_gridlines": {"visible": True},
            "min": int(line_min * 0.9),
            "max": int(line_max * 1.05),
        })

        # Add line series
        for i, col in enumerate(line_data.columns, 1):
            color = COLOR_MAP.get(col, "#0000ff")
            line_chart.add_series({
                "name":       ["Report", 0, i],
                "categories": ["Report", 1, 0, len(combined), 0],
                "values":     ["Report", 1, i, len(combined), i],
                "line":       {"color": color},
                "marker":     {"type": "circle", "border": {"color": color}, "fill": {"color": color}},
                "y2_axis":    True,   
            })

        # Combine charts (bar + line)
        bar_chart.combine(line_chart)
        bar_chart.set_legend({"position": "right"})
        worksheet.insert_chart("H10", bar_chart)

    print(f"Excel report generated : {OUTPUT_PATH}")

    # Export chart as PNG using xlwings
    wb = None
    app = None
    try:
        app = xw.App(visible=False)  
        wb = xw.Book(OUTPUT_PATH)
        ws = wb.sheets["Report"]
        chart = ws.charts[0]
        chart.api[1].Export(str(BASE_DIR / "chart.png"))
        print(f"Chart exported as PNG: {CHART_IMG}")

    except Exception as e:
        print(f"Excel export failed: {e}")
    finally:
        if wb is not None:
            wb.close()
        if app is not None:
            app.quit()

