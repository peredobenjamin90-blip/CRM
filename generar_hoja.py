import io
import urllib.request
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
    items=None,
    subtotal=0,
    descuento=0,
    descuento_pct=0,
    iva=0,
    total=0,
    tecnico="",
    ciudad="",
    servicio="",
    cantidad="",
    paquete="",
    template_path="assets/Hoja de servicio de Maxi Clean.pdf"
):
    IMAGE_WIDTH = 772
    IMAGE_HEIGHT = 1000

    if template_path and str(template_path).startswith("http"):
        with urllib.request.urlopen(template_path) as response:
            pdf_data = response.read()
        reader = PdfReader(io.BytesIO(pdf_data))
    else:
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

    if not items:
        partes = [s.strip() for s in servicio.split(",", 1)] if "," in servicio else [servicio]
        items = [{
            "servicio": partes[0],
            "cantidad": cantidad or 1,
            "paquete": paquete,
            "precio_unitario": 0,
            "subtotal": total or subtotal
        }]
        if len(partes) > 1:
            items.append({"servicio": partes[1], "cantidad": "", "paquete": "", "precio_unitario": 0, "subtotal": 0})

    campos_fijos = [
        (70, 173, 380, 188, nombre, 9),
        (70, 210, 762, 225, direccion, 9),
        (65, 272, 240, 287, ciudad, 9),
        (310, 272, 510, 287, telefono, 9),
        (32, 342, 138, 356, fecha, 9),
        (142, 342, 248, 356, hora, 9),
        (295, 342, 530, 356, tecnico, 9),
        (594, 342, 762, 356, origen, 9),
    ]

    Y_RENGLONES = [572, 590, 608, 626, 644, 662, 680]
    ABREV_PAQUETE = {
        "Healthy": "Hlth",
        "Premium": "Prem",
        "Protección": "Prot",
        "Ecológico": "Ecol",
        "Sencillo": "Senc",
    }
    campos_items = []
    for i, item in enumerate(items[:7]):
        if i >= len(Y_RENGLONES):
            break
        y = Y_RENGLONES[i]
        dy = 14
        serv_txt = str(item.get("servicio", ""))
        cant_txt = str(item.get("cantidad", "")) if item.get("cantidad") else ""
        paq_raw = str(item.get("paquete", ""))
        paq_txt = ABREV_PAQUETE.get(paq_raw, paq_raw)
        pu_txt = f"${item.get('precio_unitario', 0):,.0f}" if item.get("precio_unitario") else ""
        sub_txt = f"${item.get('subtotal', 0):,.0f}" if item.get("subtotal") else ""

        if serv_txt:
            campos_items.append((70, y, 450, y + dy, serv_txt, 9))
        if paq_txt:
            campos_items.append((455, y, 520, y + dy, paq_txt, 9))
        if cant_txt:
            campos_items.append((522, y, 575, y + dy, cant_txt, 9))
        if pu_txt:
            campos_items.append((578, y, 660, y + dy, pu_txt, 9))
        if sub_txt:
            campos_items.append((663, y, 762, y + dy, sub_txt, 9))

    # --- Totales (coordenadas del template Maxi Clean) ---
    # subtotal (755) y total (840) ya caen bien; ajusta Y_DESCUENTO / Y_IVA si no aterrizan en su fila
    Y_SUBTOTAL = 755
    Y_DESCUENTO = 783
    Y_IVA = 811
    Y_TOTAL = 840
    dy_tot = 14
    X_VAL_1, X_VAL_2 = 663, 762      # celda del valor (derecha)
    X_LBL_1, X_LBL_2 = 586, 660      # celda de la etiqueta (izquierda)

    campos_totales = []
    # Subtotal (la etiqueta ya viene impresa en el template)
    if subtotal and subtotal > 0:
        campos_totales.append((X_VAL_1, Y_SUBTOTAL, X_VAL_2, Y_SUBTOTAL + dy_tot, f"${subtotal:,.0f}", 9))
    # Descuento: etiqueta + valor (el template no trae la etiqueta impresa)
    if descuento and descuento > 0:
        etiqueta_desc = f"Descuento {descuento_pct:.0f}%" if descuento_pct else "Descuento"
        campos_totales.append((X_LBL_1, Y_DESCUENTO, X_LBL_2, Y_DESCUENTO + dy_tot, etiqueta_desc, 8))
        campos_totales.append((X_VAL_1, Y_DESCUENTO, X_VAL_2, Y_DESCUENTO + dy_tot, f"-${descuento:,.0f}", 9))
    # IVA: etiqueta + valor
    if iva and iva > 0:
        campos_totales.append((X_LBL_1, Y_IVA, X_LBL_2, Y_IVA + dy_tot, "IVA 16%", 8))
        campos_totales.append((X_VAL_1, Y_IVA, X_VAL_2, Y_IVA + dy_tot, f"${iva:,.0f}", 9))
    # Total (la etiqueta ya viene impresa)
    if total and total > 0:
        campos_totales.append((X_VAL_1, Y_TOTAL, X_VAL_2, Y_TOTAL + dy_tot, f"${total:,.0f}", 9))

    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(pdf_width, pdf_height))
    c.setFillColorRGB(0, 0, 0)

    FONT_BUMP = 5  # sube este número si quieres la letra aún más grande
    for (ix, iy, ix2, iy2, texto, fsize) in campos_fijos + campos_items + campos_totales:
        if not texto:
            continue
        fsize = fsize + FONT_BUMP
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