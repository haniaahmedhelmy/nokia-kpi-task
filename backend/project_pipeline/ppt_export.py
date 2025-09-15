import xlwings as xw
from pptx import Presentation
from pptx.util import Inches
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
EXCEL_PATH = BASE_DIR / "report.xlsx"
PPT_PATH = BASE_DIR / "report.pptx"
CHART_IMG = BASE_DIR / "chart.png"

def export_to_ppt():
    app = xw.App(visible=False)
    wb = xw.Book(EXCEL_PATH)
    ws = wb.sheets["Report"]

    chart = ws.charts[0]
    chart.api[1].Export(str(CHART_IMG))

    wb.close()
    app.quit()

    prs = Presentation()
    slide_layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(slide_layout)

    slide.shapes.add_picture(str(CHART_IMG), Inches(1), Inches(1), Inches(8), Inches(5))

    if PPT_PATH.exists():
        PPT_PATH.unlink()
    prs.save(PPT_PATH)

    print(f"PowerPoint exported: {PPT_PATH}")
    return PPT_PATH
