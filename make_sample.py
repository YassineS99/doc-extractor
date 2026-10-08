from fpdf import FPDF

lines = [
    "EQUIPMENT DATASHEET",
    "",
    "Equipment: Centrifugal Process Pump",
    "Manufacturer: AquaFlow Industries",
    "Model Number: CP-250X",
    "",
    "Technical Specifications",
    "Rated motor power: 15 kW",
    "Supply voltage: 400 V, 3-phase, 50 Hz",
    "Net weight: 220 kg",
    "Maximum operating temperature: 120 deg C",
    "Maximum flow rate: 250 m3/h",
    "",
    "Applicable Standards",
    "ISO 9906 (hydraulic performance)",
    "IEC 60034-1 (rotating electrical machines)",
    "API 610 (centrifugal pumps)",
]

pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", size=12)

for line in lines:
    pdf.cell(0, 8, line, new_x="LMARGIN", new_y="NEXT")

pdf.output("sample_datasheet.pdf")
print("Created sample_datasheet.pdf")