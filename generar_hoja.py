import io
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas


def generar_hoja_servicio(
    nombre="",
    direccion="",
    telefono="",
    fecha="",
    hora="",
    folio="",
    origen="",
    servicio="",
    tecnico="",
    template_path="assets/Hoja de servicio de Maxi Clean.pdf"
):
    IMAGE_WIDTH = 772
    IMAGE_HEIGHT = 1000

    reader = PdfReader(template_path)
    page = reader.pages[0]

    pdf_width = float(page.mediabox.width)
    pdf_height = float(page.mediabox.height)

    scale_x = pdf_width / IMAGE_WIDTH
    scale_y = pdf_height / IMAGE_HEIGHT

    def to_pdf_coords(img_x, img_y, img_x2, img_y2):
        x0 = img_x * scale_x
        y0 = pdf_height - (img_y2 * scale_y)
        x1 = img_x2 * scale_x
        y1 = pdf_height - (img_y * scale_y)
        return x0, y0, x1, y1

    campos = [
        # Folio/Orden
        (580, 112, 760, 128, folio, 9),
        # Nombre
        (10, 173, 380, 188, nombre, 9),
        # Dirección
        (10, 210, 762, 225, direccion, 9),
        # Ciudad fija
        (55, 272, 185, 287, "Zapopan, Jalisco", 9),
        # Teléfono
        (305, 272, 430, 287, telefono, 9),
        # Fecha programada
        (55, 332, 130, 347, fecha, 9),
        # Hora programada
        (145, 332, 255, 347, hora, 9),
        # Técnico
        (260, 332, 490, 347, tecnico, 9),
        # Medio/Fuente
        (590, 332, 762, 347, origen, 9),
    ]

    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(pdf_width, pdf_height))
    c.setFillColorRGB(0, 0, 0)

    for (ix, iy, ix2, iy2, texto, fsize) in campos:
        if not texto:
            continue
        x0, y0, x1, y1 = to_pdf_coords(ix, iy, ix2, iy2)
        cy = y0 + (y1 - y0) / 2 - fsize / 3
        c.setFont("Helvetica", fsize)
        c.drawString(x0 + 2, cy, str(texto))

    c.save()
    packet.seek(0)

    overlay_reader = PdfReader(packet)
    overlay_page = overlay_reader.pages[0]

    writer = PdfWriter()
    page.merge_page(overlay_page)
    writer.add_page(page)

    if len(reader.pages) > 1:
        writer.add_page(reader.pages[1])

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output.read()