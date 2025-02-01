import streamlit as st
import pandas as pd
from jinja2 import Environment
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from io import BytesIO
import base64

# --- Streamlit App ---
st.set_page_config(page_title="Factsheet Generator", page_icon=":bar_chart:", layout="wide")  # Set page layout
st.title("Factsheet Generator")

# 1. File Uploads
col1, col2, col3 = st.columns(3)  # Create columns for layout

with col1:
    csv_file = st.file_uploader("Upload CSV Data", type="csv")
with col2:
    template_file = st.file_uploader("Upload HTML Template (optional)", type="html")  # Optional template
with col3:
    logo_file = st.file_uploader("Upload Logo (optional)", type=["png", "jpg", "jpeg"])

# 2. Generate Button
if csv_file:  # Only require CSV
    if st.button("Generate Factsheet"):
        try:
            # --- Data Processing ---
            df = pd.read_csv(csv_file)

            # --- Data Validation (Customize required columns) ---
            required_columns = ["Fund Name", "Investment Strategy", "Management Fee", "Brokerage Fee", "January", "February", "March", "April", "May", "June", "SAPY_January", "SAPY_February", "SAPY_March", "SAPY_April", "SAPY_May", "SAPY_June"]
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

            # --- PDF Generation (ReportLab) ---
            for index, row in df.iterrows():
                fund_data = row.to_dict()
                fund_data["performance_data"] = performance_data.get(fund_data.get("Fund Name"))

                pdf_buffer = BytesIO()
                doc = SimpleDocTemplate(pdf_buffer)
                styles = getSampleStyleSheet()
                story = []

                # --- Logo Handling (ReportLab) ---
                if logo_file:
                    try:  # Handle potential image errors
                        img = Image(logo_file, width=1*inch, height=1*inch)  # Adjust size as needed
                        story.append(img)
                        story.append(Spacer(1, 0.2 * inch))
                    except Exception as e:
                        st.warning(f"Error with logo: {e}")  # Display warning, but continue

                story.append(Paragraph(f"{fund_data.get('Fund Name')} Factsheet", styles['h1']))
                story.append(Spacer(1, 0.2 * inch))

                story.append(Paragraph(f"Investment Strategy: {fund_data.get('Investment Strategy')}", styles['Normal']))
                story.append(Spacer(1, 0.2 * inch))

                # --- Table 1 (Metrics) ---
                table_data = [
                    ["Metric", "Value"],
                    ["Management Fee", fund_data.get('Management Fee')],
                    ["Brokerage Fee", fund_data.get('Brokerage Fee')]
                ]
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), '#CCCCCC'),
                    ('GRID', (0, 0), (-1, -1), 1, '#000000')
                ]))
                story.append(table)
                story.append(Spacer(1, 0.2 * inch))

                # --- Table 2 (Performance) ---
                performance_table_data = [["Month", "Portfolio", "SAPY"]]
                for month, values in fund_data["performance_data"].items() if month != "SAPY":
                    performance_table_data.append([month, values, fund_data["performance_data"]["SAPY"][month] if fund_data["performance_data"]["SAPY"] else ""])

                performance_table = Table(performance_table_data)
                performance_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), '#CCCCCC'),
                    ('GRID', (0, 0), (-1, -1), 1, '#000000')
                ]))

                story.append(performance_table)

                doc.build(story)
                pdf_bytes = pdf_buffer.getvalue()

                # --- Download Link ---
                st.download_button(
                    label=f"Download Factsheet for {fund_data.get('Fund Name')}",
                    data=pdf_bytes,
                    file_name=f"generated_factsheet_{fund_data.get('Fund Name')}.pdf",
                    mime="application/pdf",
                )

        except Exception as e:
            st.error(f"An error occurred: {e}")


# --- Example CSV Data (for demonstration) ---
csv_data = """
Fund Name,Investment Strategy,Management Fee,Brokerage Fee,January,February,March,April,May,June,SAPY_January,SAPY_February,SAPY_March,SAPY_April,SAPY_May,SAPY_June
Growth Port,Value Investing,1.5%,0.6%,-0.1%,0.94%,8.49%,1.46%,-1.85%,-1.56%,-3.0%,1.6%,7.1%,1.7%,-4.09%,-4.09%
Hedefine,Growth Investing,1.2%,0.5%,0.5%,1.2%,7.8%,2.1%,-1.2%,-1.0%,-2.5%,2.0%,6.5%,2.5%,-3.5%,-3.8%
New Europe Property,Real Estate,1.0%,0.7%,-0.8%,0.7%,9.2%,1.0%,-2.2%,-1.7%,-3.2%,1.2%,8.0%,1.9%,-4.5%,-4.2%
"""

# --- Optional HTML template (If user doesn't upload one, ReportLab is used) ---
template_str = ""  # Empty, as ReportLab generates the PDF
