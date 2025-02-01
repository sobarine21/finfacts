import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# Streamlit UI
st.set_page_config(page_title="Convertible Bond Fund Factsheet", layout="wide")

st.title("📄 One-Pager Convertible Bond Fund Fact Sheet Generator")

# Upload logo
logo = st.file_uploader("Upload Company Logo", type=["png", "jpg", "jpeg"])

# Upload data file
data_file = st.file_uploader("Upload CSV Data File", type=["csv"])
if data_file:
    df = pd.read_csv(data_file)

# Company Details
company_name = st.text_input("Enter Company Name", "Your Company Name")
fund_value = st.text_input("Enter Convertible Bond Funds ($)", "$ XXXX")
date = st.text_input("Enter Date", "XX-XX-XXXX")

# Generate Charts
st.subheader("📊 ROI Timeline")
years = ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
interest = [10, 20, 30, 40, 50]  # Example ROI Data

fig, ax = plt.subplots()
ax.plot(years, interest, marker="o", linestyle="-", color="blue")
ax.set_ylabel("ROI %")
ax.set_title("Convertible Bond ROI Timeline")
st.pyplot(fig)

st.subheader("📈 Annual Returns by Bond Type")
bond_types = ["Convertible Bonds", "Traditional Bonds", "Stocks"]
returns = [6.1, 7.5, -2.0]

fig, ax = plt.subplots()
ax.bar(bond_types, returns, color=["blue", "green", "red"])
ax.set_ylabel("Total Annual Returns %")
st.pyplot(fig)

st.subheader("📉 Price of Convertible Bonds vs Stock Price")
prices = {"Bond Price": [95, 100, 105, 110, 120], "Stock Price": [30, 40, 50, 60, 70]}

fig, ax = plt.subplots()
ax.plot(prices["Stock Price"], prices["Bond Price"], marker="o", linestyle="-", label="Bond Price")
ax.set_xlabel("Stock Price")
ax.set_ylabel("Bond Price")
ax.legend()
st.pyplot(fig)

# Pie Chart
st.subheader("🟢 Types of Convertible Bonds Issued")
labels = ["Reverse Convertibles", "Mandatory Bonds", "Vanilla Convertible Bonds"]
sizes = [30, 40, 30]
fig, ax = plt.subplots()
ax.pie(sizes, labels=labels, autopct="%1.1f%%", colors=["#4CAF50", "#FFC107", "#2196F3"])
st.pyplot(fig)

# Display Data Table
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

    # Save PDF
    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer

# Button to Download PDF
if st.button("📥 Generate PDF Factsheet"):
    pdf_data = generate_pdf()
    st.download_button("Download PDF", pdf_data, "factsheet.pdf", "application/pdf")
