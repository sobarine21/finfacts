import streamlit as st
import pandas as pd
from jinja2 import Environment
import weasyprint
import base64
from io import BytesIO

# --- Streamlit App ---
st.title("Factsheet Generator")

# 1. File Uploads
csv_file = st.file_uploader("Upload CSV Data", type="csv")
template_file = st.file_uploader("Upload HTML Template", type="html")
logo_file = st.file_uploader("Upload Logo (optional)", type=["png", "jpg", "jpeg"])

# 2. Generate Button
if csv_file and template_file:
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

            # --- Template Rendering and PDF Generation ---
            env = Environment()  # No loader needed for in-memory templates
            template = env.from_string(template_file.getvalue().decode("utf-8"))  # Use template content directly

            for index, row in df.iterrows():  # Iterate for multiple factsheets
                fund_data = row.to_dict()
                fund_data["performance_data"] = performance_data.get(fund_data.get("Fund Name"))

                # --- Logo Handling ---
                if logo_file:
                    logo_base64 = base64.b64encode(logo_file.read()).decode("utf-8")
                    fund_data["logo_base64"] = logo_base64
                else:
                    fund_data["logo_base64"] = None  # Explicitly set to None if no logo

                html_output = template.render(fund_data)

                # --- PDF Generation (In-memory) ---
                pdf_bytes = weasyprint.HTML(string=html_output).write_pdf() # In-memory PDF

                # --- Download Link ---
                st.download_button(
                    label=f"Download Factsheet for {fund_data.get('Fund Name')}",
                    data=pdf_bytes,
                    file_name=f"generated_factsheet_{fund_data.get('Fund Name')}.pdf",
                    mime="application/pdf",
                )



        except Exception as e:
            st.error(f"An error occurred: {e}")



# --- Example Template (factsheet_template.html) ---
# (This is now a multiline string in the code)

template_str = """
<!DOCTYPE html>
<html>
<head>
    <title>Factsheet</title>
    <style>
        body { font-family: sans-serif; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 8px; border: 1px solid #ddd; text-align: left; }
        .logo { max-width: 200px; }
    </style>
</head>
<body>

    {% if logo_base64 %}
    <img src="data:image/png;base64,{{ logo_base64 }}" alt="Logo" class="logo">
    {% endif %}

    <h1>{{ Fund Name }} Factsheet</h1>

    <p><strong>Investment Strategy:</strong> {{ Investment Strategy }}</p>

    <table>
        <thead>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Management Fee</td>
                <td>{{ Management Fee }}</td>
            </tr>
            <tr>
                <td>Brokerage Fee</td>
                <td>{{ Brokerage Fee }}</td>
            </tr>
        </tbody>
    </table>

    <h2>Performance (Year to Date)</h2>
    <table>
        <thead>
            <tr>
                <th>Month</th>
                <th>Portfolio</th>
                <th>SAPY</th>
            </tr>
        </thead>
        <tbody>
            {% for month, values in performance_data.items() if month != "SAPY" %}
            <tr>
                <td>{{ month }}</td>
                <td>{{ values }}</td>
                <td>{{ performance_data.SAPY[month] if performance_data.SAPY }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

</body>
</html>
"""

# --- Example CSV Data (factsheet_data.csv) ---
csv_data = """
Fund Name,Investment Strategy,Management Fee,Brokerage Fee,January,February,March,April,May,June,SAPY_January,SAPY_February,SAPY_March,SAPY_April,SAPY_May,SAPY_June
Growth Port,Value Investing,1.5%,0.6%,-0.1%,0.94%,8.49%,1.46%,-1.85%,-1.56%,-3.0%,1.6%,7.1%,1.7%,-4.09%,-4.09%
Hedefine,Growth Investing,1.2%,0.5%,0.5%,1.2%,7.8%,2.1%,-1.2%,-1.0%,-2.5%,2.0%,6.5%,2.5%,-3.5%,-3.8%
New Europe Property,Real Estate,1.0%,0.7%,-0.8%,0.7%,9.2%,1.0%,-2.2%,-1.7%,-3.2%,1.2%,8.0%,1.9%,-4.5%,-4.2%
"""
