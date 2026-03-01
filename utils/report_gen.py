import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def generate_pdf_report(session_state_data, fig_geometry, file_buffer):
    """
    Compiles the inputs, results, and geometry plot into a PDF document.
    Writes the output directly to a file-like buffer for Streamlit downloading.
    """
    doc = SimpleDocTemplate(file_buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # 1. Document Header
    elements.append(Paragraph("RCSect - Cross Section Analysis Report", styles['Title']))
    elements.append(Spacer(1, 12))
    
    # Extract metadata
    meta = session_state_data.get("project_metadata", {})
    elements.append(Paragraph(f"Project: {meta.get('project_name', 'N/A')}", styles['Normal']))
    elements.append(Paragraph(f"Engineer: {meta.get('engineer', 'N/A')}", styles['Normal']))
    elements.append(Spacer(1, 24))

    # 2. Insert Geometry Plotly Figure
    if fig_geometry:
        # Convert Plotly figure to a static PNG byte stream
        img_bytes = fig_geometry.to_image(format="png", width=600, height=400, scale=2)
        img_buffer = io.BytesIO(img_bytes)
        
        # Insert into ReportLab
        report_img = Image(img_buffer, width=400, height=266)
        elements.append(report_img)
        elements.append(Spacer(1, 24))

    # 3. Material Properties Table
    elements.append(Paragraph("Material Properties", styles['Heading2']))
    concrete_data = session_state_data["materials"]["concrete"]
    mat_data = [
        ["Material", "Parameter", "Value"],
        ["Concrete", "f_ck", f"{concrete_data['f_ck']} MPa"],
        ["Concrete", "gamma_c", f"{concrete_data['gamma_c']}"],
    ]
    
    t_mats = Table(mat_data, colWidths=[120, 120, 120])
    t_mats.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    elements.append(t_mats)
    elements.append(Spacer(1, 24))
    
    # 4. Results Section
    elements.append(Paragraph("Analysis Results", styles['Heading2']))
    # The calculated stresses and capacities would be formatted into tables here
    
    # Build the PDF
    doc.build(elements)