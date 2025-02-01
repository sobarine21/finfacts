import streamlit as st
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
import base64
import io


# --- Streamlit App ---
st.set_page_config(page_title="Factsheet Generator", page_icon=":bar_chart:", layout="wide")
st.title("Comprehensive Factsheet Generator")

# 1. File Uploads
col1, col2, col3 = st.columns(3)

with col1:
    csv_file = st.file_uploader("Upload CSV Data", type="csv")
with col2:
    logo_file = st.file_uploader("Upload Logo (optional)", type=["png", "jpg", "jpeg"])

# 2. Download CSV Template
if st.button("Download CSV Template"):
    csv_template = """Fund Name,Investment Strategy,Management Fee,Brokerage Fee,Investment Objective,Fund Composition,January,February,March,April,May,June,SAPY_January,SAPY_February,SAPY_March,SAPY_April,SAPY_May,SAPY_June
    Example Fund,Value Investing,1.0%,0.5%,Long-term growth,Stocks: 60%, Bonds: 30%, Real Estate: 10%,0.5%,1.2%,0.7%,-0.2%,1.5%,0.8%,1.0%,2.0%,1.5%,1.8%
    """
    st.download_button(
        label="Download CSV Template",
        data=csv_template,
        file_name="factsheet_template.csv",
        mime="text/csv",
    )

# 3. Generate Factsheet Button
if csv_file:
    if st.button("Generate Factsheet"):
        try:
            df = pd.read_csv(csv_file)

            # --- Data Validation (Ensure all columns exist) ---
            required_columns = [
                "Fund Name", "Investment Strategy", "Management Fee", "Brokerage Fee", "Investment Objective",
                "Fund Composition", "January", "February", "March", "April", "May", "June",
                "SAPY_January", "SAPY_February", "SAPY_March", "SAPY_April", "SAPY_May", "SAPY_June"
            ]
            if not all(col in df.columns for col in required_columns):
                st.error(f"CSV is missing required columns: {required_columns}")
                st.stop()

            # --- Performance Data Restructuring ---
            performance_data = {}
            for index, row in df.iterrows():
                performance_data[row["Fund Name"]] = {
                    "January": row["January"], "February": row["February"], "March": row["March"],
                    "April": row["April"], "May": row["May"], "June": row["June"],
                    "SAPY": {
                        "January": row["SAPY_January"] if "SAPY_January" in df.columns else None,
                        "February": row["SAPY_February"] if "SAPY_February" in df.columns else None,
                        "March": row["SAPY_March"] if "SAPY_March" in df.columns else None,
                        "April": row["SAPY_April"] if "SAPY_April" in df.columns else None,
                        "May": row["SAPY_May"] if "SAPY_May" in df.columns else None,
                        "June": row["SAPY_June"] if "SAPY_June" in df.columns else None,
                    }
                }

            # --- PDF Generation ---
            for index, row in df.iterrows():
                fund_data = row.to_dict()
                fund_data["performance_data"] = performance_data.get(fund_data.get("Fund Name"))

                pdf_buffer = BytesIO()
                doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
                styles = getSampleStyleSheet()
                story = []

                # --- Logo Handling ---
                if logo_file:
                    try:
                        img = Image(logo_file, width=1*inch, height=1*inch)  # Adjust size as needed
                        story.append(img)
                        story.append(Spacer(1, 0.2 * inch))
                    except Exception as e:
                        st.warning(f"Error with logo: {e}")

                # --- Fund Overview ---
                story.append(Paragraph(f"{fund_data['Fund Name']} Factsheet", styles['Title']))
                story.append(Spacer(1, 0.2 * inch))
                story.append(Paragraph(f"Investment Strategy: {fund_data['Investment Strategy']}", styles['Normal']))
                story.append(Spacer(1, 0.2 * inch))
                story.append(Paragraph(f"Investment Objective: {fund_data['Investment Objective']}", styles['Normal']))
                story.append(Spacer(1, 0.2 * inch))
                story.append(Paragraph(f"Fund Composition: {fund_data['Fund Composition']}", styles['Normal']))
                story.append(Spacer(1, 0.4 * inch))

                # --- Table 1: Metrics ---
                metrics_data = [
                    ["Metric", "Value"],
                    ["Management Fee", fund_data.get("Management Fee")],
                    ["Brokerage Fee", fund_data.get("Brokerage Fee")],
                ]
                table = Table(metrics_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), '#CCCCCC'),
                    ('GRID', (0, 0), (-1, -1), 1, '#000000')
                ]))
                story.append(table)
                story.append(Spacer(1, 0.4 * inch))

                # --- Table 2: Performance Data ---
                performance_table_data = [["Month", "Portfolio", "SAPY"]]
                for month, values in fund_data["performance_data"].items():
                    if month != "SAPY":  # Skip "SAPY"
                        performance_table_data.append([month, values, fund_data["performance_data"]["SAPY"].get(month, "")])

                performance_table = Table(performance_table_data)
                performance_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), '#CCCCCC'),
                    ('GRID', (0, 0), (-1, -1), 1, '#000000')
                ]))
                story.append(performance_table)
                story.append(Spacer(1, 0.4 * inch))

                # --- Graph 1: Bar Chart for Performance ---
                months = ["January", "February", "March", "April", "May", "June"]
                portfolio_performance = [fund_data["performance_data"][month] for month in months]

                fig, ax = plt.subplots(figsize=(6, 4))
                ax.bar(months, portfolio_performance, color='skyblue', label="Portfolio")
                ax.set_title("Monthly Portfolio Performance")
                ax.set_xlabel("Month")
                ax.set_ylabel("Return (%)")
                ax.legend()

                # Save chart as image and add to PDF
                graph_buffer = BytesIO()
                plt.savefig(graph_buffer, format='png')
                plt.close(fig)
                graph_buffer.seek(0)
                img = Image(graph_buffer, width=5 * inch, height=3 * inch)
                story.append(img)
                story.append(Spacer(1, 0.4 * inch))

                # --- Download Button for Factsheet PDF ---
                doc.build(story)
                pdf_bytes = pdf_buffer.getvalue()

                st.download_button(
                    label=f"Download Factsheet for {fund_data.get('Fund Name')}",
                    data=pdf_bytes,
                    file_name=f"factsheet_{fund_data.get('Fund Name')}.pdf",
                    mime="application/pdf",
                )

        except Exception as e:
            st.error(f"An error occurred: {e}")

