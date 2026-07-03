import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from supabase import create_client
from datetime import datetime
import time
import json

SUPABASE_URL = "https://avanarshqjlripvaeqyj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF2YW5hcnNocWpscmlwdmFlcXlqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODE2NTM4MywiZXhwIjoyMDkzNzQxMzgzfQ.phii9aTtLW4GeBg1mvkRKSFETCmWAFMIroDED0U4dtk"
EMPRESA_ID   = "71e0eae4-3341-47ad-ad65-0c6bf616a272"
SHEET_ID_2026 = "1mqcHNhQEjEhKYYuY6iDOVpmPDH7br0VJITxdVx7wzls"

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
with open("chemdry-dashboard-aa66119b0d6c.json") as f:
    creds_info = json.load(f)

creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
gc   = gspread.authorize(creds)
supa = create_client(SUPABASE_URL, SUPABASE_KEY)

def limpiar_monto(valor):
    try:
        return float(str(valor).replace("$","").replace(",","").replace(" ","").strip())
    except:
        return None

def limpiar_fecha(valor):
    for fmt in ("%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(valor).strip(), fmt).date().isoformat()
        except:
            continue
    return None

print("Leyendo sheet 2026...")
sh = gc.open_by_key(SHEET_ID_2026)
ws = sh.get_worksheet(0)

valores = ws.get_all_values()
headers = valores[0]

headers_limpios = []
conteo = {}
for h in headers:
    h = h.strip()
    if h == "":
        h = "Col_vacia"
    if h in conteo:
        conteo[h] += 1
        h = f"{h}_{conteo[h]}"
    else:
        conteo[h] = 0
    headers_limpios.append(h)

df = pd.DataFrame(valores[1:], columns=headers_limpios)
print(f"{len(df)} filas encontradas. Columnas: {list(df.columns)}")

filas = []
for _, row in df.iterrows():
    nombre = str(row.get("Nombre","")).strip()
    if not nombre or nombre.lower() == "nan" or nombre == "":
        continue
    filas.append({
        "empresa_id":  EMPRESA_ID,
        "cliente_id":  int(row["ID Cliente"]) if str(row.get("ID Cliente","")).isdigit() else None,
        "fecha":       limpiar_fecha(row.get("Fecha","")),
        "nombre":      nombre,
        "tel":         str(row.get("Tel","")).strip() or None,
        "direccion":   str(row.get("Dirección","")).strip() or None,
        "origen":      str(row.get("Origen","")).strip() or None,
        "monto":       limpiar_monto(row.get("Monto", row.get(" Monto",""))),
        "servicio":    str(row.get("Servicio","")).strip() or None,
        "comentarios": str(row.get("Comentarios con llamada posterior a venta","")).strip() or None,
        "año":         2026,
        "realizado":   True
    })

print(f"{len(filas)} filas válidas para insertar")

for i in range(0, len(filas), 500):
    lote = filas[i:i+500]
    supa.table("clientes").insert(lote).execute()
    print(f"Lote {i//500 + 1}: {len(lote)} filas insertadas")
    time.sleep(0.3)

resultado = supa.table("clientes").select("*", count="exact").execute()
print(f"\n✅ Total en Supabase ahora: {resultado.count} filas")