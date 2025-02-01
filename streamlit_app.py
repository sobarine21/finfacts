import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# Streamlit Page Configuration
st.set_page_config(page_title="Convertible Bond Fund Factsheet", layout="wide")

# Title & Description
st.title("📄 One Pager Convertible Bond Fund Fact Sheet Generator")
st.write("Generate a professional one-page factsheet with ROI trends, pricing, and bond details.")

# Upload Company Logo
logo = st.file_uploader("📌 Upload Company Logo (PNG/JPG)", type=["png", "jpg", "jpeg"])

# Upload Data File
data_file = st.file_uploader("📥 Upload CSV Data File for Bond Details", type=["csv"])
if data_file:
    df = pd.read_csv(data_file)

# Company Information
st.header("🏢 Company Information")
col1, col2 = st.columns(2)
with col1:
    company_name = st.text_input("Enter Company Name", "Your Company Name")
with col2:
    fund_value = st.text_input("Enter Convertible Bond Funds ($)", "$ XXXX")
date = st.text_input("Enter Date (MM-DD-YYYY)", "XX-XX-XXXX")

# ROI Timeline
st.subheader("📊 Convertible Bond ROI Timeline")
years = ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
interest = [10, 20, 30, 40, 50]  # Example Interest Growth

fig, ax = plt.subplots()
ax.plot(years, interest, marker="o", linestyle="-", color="blue")
ax.set_ylabel("ROI %")
ax.set_title("ROI Timeline (Invest $1000)")
st.pyplot(fig)

# Annual Returns Bar Chart
st.subheader("📈 Annual Returns for Different Bond Types")
bond_types = ["Convertible Bonds", "Traditional Bonds", "Stocks"]
returns = [6.1, 7.5, -2.0]

fig, ax = plt.subplots()
ax.bar(bond_types, returns, color=["blue", "green", "red"])
ax.set_ylabel("Total Annual Returns %")
st.pyplot(fig)

# Convertible Bond Pricing Chart
st.subheader("📉 Price of Convertible Bonds vs Stock Price")
prices = {"Bond Price": [95, 100, 105, 110, 120], "Stock Price": [30, 40, 50, 60, 70]}

fig, ax = plt.subplots()
ax.plot(prices["Stock Price"], prices["Bond Price"], marker="o", linestyle="-", label="Bond Price")
ax.set_xlabel("Stock Price")
ax.set_ylabel("Bond Price")
ax.legend()
st.pyplot(fig)

# Pie Chart for Bond Types
st.subheader("🟢 Types of Convertible Bonds Issued")
labels = ["Reverse Convertibles", "Mandatory Bonds", "Vanilla Convertible Bonds"]
sizes = [30, 40, 30]
fig, ax = plt.subplots()
ax.pie(sizes, labels=labels, autopct="%1.1f%%", colors=["#4CAF50", "#FFC107", "#2196F3"])
st.pyplot(fig)

# Bond Cases Table
st.subheader("📊 Convertible Bonds Comparison Table")
if data_file:
    st.write(df)

# Generate PDF
def generate_pdf():
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 50, "One Pager Convertible Bond Fund Fact Sheet")

    # Company Info
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, height - 80, f"Company: {company_name}")
    pdf.drawString(50, height - 100, f"Convertible Bond Funds: {fund_value}")
    pdf.drawString(50, height - 120, f"Date: {date}")

    # Add Logo
    if logo:
        img = ImageReader(logo)
        pdf.drawImage(img, width - 150, height - 150, width=100, height=100)

    # ROI Timeline
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, height - 180, "ROI Timeline (Invest $1000)")
    y_pos = height - 200
    for year, roi in zip(years, interest):
        pdf.setFont("Helvetica", 12)
        pdf.drawString(50, y_pos, f"{year}: {roi}% Interest")
        y_pos -= 20

    # Bond Pricing Table
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y_pos - 20, "Convertible Bonds Pricing")
    y_pos -= 40
    for stock_price, bond_price in zip(prices["Stock Price"], prices["Bond Price"]):
        pdf.setFont("Helvetica", 12)
        pdf.drawString(50, y_pos, f"Stock Price: ${stock_price} -> Bond Price: ${bond_price}")
        y_pos -= 20

    # Pie Chart Summary
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y_pos - 20, "Types of Convertible Bonds Issued")
    y_pos -= 40
    for label, size in zip(labels, sizes):
        pdf.setFont("Helvetica", 12)
        pdf.drawString(50, y_pos, f"{label}: {size}%")
        y_pos -= 20

    # Save PDF
    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer

# Button to Download PDF
if st.button("📥 Generate PDF Factsheet"):
    pdf_data = generate_pdf()
    st.download_button("Download PDF", pdf_data, "factsheet.pdf", "application/pdf")
