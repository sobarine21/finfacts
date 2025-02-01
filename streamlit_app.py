import streamlit as st
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from io import BytesIO
import matplotlib.pyplot as plt
import base64

# Streamlit App Configuration
st.set_page_config(page_title="Factsheet Generator", page_icon=":bar_chart:", layout="wide")
st.title("Comprehensive Factsheet Generator")

# File Upload Section
col1, col2 = st.columns(2)
with col1:
    csv_file = st.file_uploader("Upload CSV Data", type="csv")
with col2:
    logo_file = st.file_uploader("Upload Logo (optional)", type=["png", "jpg", "jpeg"])

# Download CSV Template
if st.button("Download CSV Template"):
    csv_template = """Fund Name,Investment Strategy,Management Fee,Brokerage Fee,Investment Objective,Fund Composition,January,February,March,April,May,June,SAPY_January,SAPY_February,SAPY_March,SAPY_April,SAPY_May,SAPY_June
Example Fund,Value Investing,1.0%,0.5%,Long-term growth,Stocks: 60%, Bonds: 30%, Real Estate: 10%,0.5%,1.2%,0.7%,-0.2%,1.5%,0.8%,1.0%,2.0%,1.5%,1.8%"""
    st.download_button(label="Download CSV Template", data=csv_template, file_name="factsheet_template.csv", mime="text/csv")

# Generate Factsheet
if csv_file and st.button("Generate Factsheet"):
    df = pd.read_csv(csv_file)
    required_columns = [
        "Fund Name", "Investment Strategy", "Management Fee", "Brokerage Fee", "Investment Objective",
        "Fund Composition", "January", "February", "March", "April", "May", "June",
        "SAPY_January", "SAPY_February", "SAPY_March", "SAPY_April", "SAPY_May", "SAPY_June"
    ]
    if not all(col in df.columns for col in required_columns):
        st.error("CSV is missing required columns. Please use the provided template.")
        st.stop()
    
    for _, row in df.iterrows():
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Add Logo
        if logo_file:
            logo = Image(logo_file, width=1.5*inch, height=1.5*inch)
            story.append(logo)
        story.append(Paragraph(f"{row['Fund Name']} Factsheet", styles['Title']))
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph(f"Investment Strategy: {row['Investment Strategy']}", styles['Normal']))
        story.append(Paragraph(f"Investment Objective: {row['Investment Objective']}", styles['Normal']))
        story.append(Paragraph(f"Fund Composition: {row['Fund Composition']}", styles['Normal']))
        story.append(Spacer(1, 0.4 * inch))

        # Metrics Table
        metrics_data = [["Metric", "Value"],
                        ["Management Fee", row["Management Fee"]],
                        ["Brokerage Fee", row["Brokerage Fee"]]]
        table = Table(metrics_data, colWidths=[2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#CCCCCC'),
            ('GRID', (0, 0), (-1, -1), 1, '#000000')
        ]))
        story.append(table)
        story.append(Spacer(1, 0.4 * inch))

        # Performance Table
        performance_data = [["Month", "Portfolio", "SAPY"],
                            ["January", row["January"], row["SAPY_January"]],
                            ["February", row["February"], row["SAPY_February"]],
                            ["March", row["March"], row["SAPY_March"]],
                            ["April", row["April"], row["SAPY_April"]],
                            ["May", row["May"], row["SAPY_May"]],
                            ["June", row["June"], row["SAPY_June"]]]
        perf_table = Table(performance_data)
        perf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#CCCCCC'),
            ('GRID', (0, 0), (-1, -1), 1, '#000000')
        ]))
        story.append(perf_table)
        story.append(Spacer(1, 0.4 * inch))

        # Performance Graph
        months = ["January", "February", "March", "April", "May", "June"]
        portfolio_returns = [row[month] for month in months]
        plt.figure(figsize=(5, 3))
        plt.bar(months, portfolio_returns, color='skyblue')
        plt.xlabel("Month")
        plt.ylabel("Return (%)")
        plt.title("Monthly Portfolio Performance")
        graph_buffer = BytesIO()
        plt.savefig(graph_buffer, format='png')
        plt.close()
        graph_buffer.seek(0)
        img = Image(graph_buffer, width=5 * inch, height=3 * inch)
        story.append(img)
        story.append(Spacer(1, 0.4 * inch))

        # Generate and Download PDF
        doc.build(story)
        pdf_bytes = pdf_buffer.getvalue()
        st.download_button(
            label=f"Download Factsheet for {row['Fund Name']}",
            data=pdf_bytes,
            file_name=f"factsheet_{row['Fund Name']}.pdf",
            mime="application/pdf",
        )
