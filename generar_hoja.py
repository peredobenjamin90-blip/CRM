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
    cantidad="",
    paquete="",
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

    # Dividir servicio por coma si tiene más de uno
    partes_servicio = [s.strip() for s in servicio.split(",", 1)] if "," in servicio else [servicio]
    servicio_linea1 = partes_servicio[0]
    servicio_linea2 = partes_servicio[1] if len(partes_servicio) > 1 else ""

    campos = [
        (580, 112, 760, 128, folio, 9),
        (70, 173, 380, 188, nombre, 9),
        (70, 210, 762, 225, direccion, 9),
        (65, 272, 240, 287, "Zapopan, Jalisco", 9),
        (310, 272, 510, 287, telefono, 9),
        (32, 342, 138, 356, fecha, 9),
        (142, 342, 248, 356, hora, 9),
        (295, 342, 530, 356, tecnico, 9),
        (594, 342, 762, 356, origen, 9),
        # Descripción línea 1
        (70, 572, 490, 586, servicio_linea1, 9),
        # Paquete — bajo columna PAQUETE
        (455, 572, 520, 586, paquete, 9),
        # Cantidad — bajo columna CANTIDAD
        (522, 572, 575, 586, cantidad, 9),
    ]

    # Si hay segunda línea de servicio — más espacio
    if servicio_linea2:
        campos.append((70, 590, 490, 604, servicio_linea2, 9))

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