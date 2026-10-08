from fpdf import FPDF

lines = [
    "DATA SHEET",
    "",
    "Item: Industrial Air Compressor",
    "Model: AC-75",
    "",
    "Motor power: 7.5 kW",
    "Supply: 415 V, 3-phase",
    "Maximum working pressure: 10 bar",
]

pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", size=12)

for line in lines:
    pdf.cell(0, 8, line, new_x="LMARGIN", new_y="NEXT")

pdf.output("sample_datasheet_2.pdf")
print("Created sample_datasheet_2.pdf")