import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials
from config import USUARIOS
import uuid
import plotly.express as px
import os

from supabase import create_client
supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)


NOMBRE_APP = "CRM Dashboard"
ICONO_APP = "🧹"

st.set_page_config(
    page_title=NOMBRE_APP,
    page_icon=ICONO_APP,
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* ── FONDO GENERAL ── */
    .stApp {
        background-color: #0F1117;
        color: #F0F2F6;
    }

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A1D2E 0%, #0F1117 100%);
        border-right: 1px solid #2D2F3E;
    }
    [data-testid="stSidebar"] * { color: #F0F2F6 !important; }
    [data-testid="stSidebar"] > div:first-child { padding-top: 0rem !important; }
    section[data-testid="stSidebar"] > div { padding-top: 0.5rem !important; }

    /* ── MÉTRICAS ── */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1A1D2E 0%, #16192A 100%) !important;
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #3D3F50;
        border-top: 2px solid #6C63FF;
    }
    [data-testid="stMetricValue"] {
        font-size: clamp(16px, 2vw, 30px) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #C8CADB !important;
        font-size: 14px !important;
        font-weight: 500 !important;
    }

    /* ── TÍTULOS ── */
    h1 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
        letter-spacing: -0.5px;
    }
    h2, h3 {
        color: #A78BFA !important;
        font-weight: 600 !important;
        font-size: 1.3rem !important;
    }

    /* ── TEXTO GENERAL ── */
    p, span, div, label {
        color: #F0F2F6 !important;
        font-size: 15px !important;
    }

    /* ── LABELS DE INPUTS ── */
    .stSelectbox label,
    .stTextInput label,
    .stNumberInput label,
    .stDateInput label,
    .stSlider label,
    .stCheckbox label,
    .stTextArea label,
    .stTimeInput label {
        color: #F0F2F6 !important;
        font-size: 15px !important;
        font-weight: 500 !important;
    }

    /* ── INPUTS ── */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #1A1D2E !important;
        border: 1px solid #4D4F65 !important;
        border-radius: 8px !important;
        color: #F0F2F6 !important;
        font-size: 15px !important;
    }

    /* ── SELECTBOX CERRADO ── */
    .stSelectbox > div > div {
        background-color: #1A1D2E !important;
        border: 1px solid #4D4F65 !important;
        border-radius: 8px !important;
        color: #F0F2F6 !important;
        font-size: 15px !important;
    }

    /* ── DROPDOWN ABIERTO — fondo blanco letra negra ── */
    [data-baseweb="popover"] * {
        background-color: #FFFFFF !important;
        color: #111111 !important;
    }
    [data-baseweb="menu"] {
        background-color: #FFFFFF !important;
    }
    [data-baseweb="menu"] li {
        color: #111111 !important;
        font-size: 15px !important;
        font-weight: 500 !important;
    }
    [data-baseweb="menu"] li:hover {
        background-color: #E8E8F0 !important;
        color: #000000 !important;
    }
    [data-baseweb="option"] {
        color: #111111 !important;
        background-color: #FFFFFF !important;
        font-size: 15px !important;
        font-weight: 500 !important;
    }
    [data-baseweb="option"]:hover,
    [data-baseweb="option"][aria-selected="true"] {
        background-color: #E8E8F0 !important;
        color: #000000 !important;
    }
    /* Forzar texto negro en TODOS los elementos dentro del popover */
    [data-baseweb="popover"] span,
    [data-baseweb="popover"] div,
    [data-baseweb="popover"] p,
    [data-baseweb="popover"] li {
        color: #111111 !important;
        background-color: transparent !important;
    }
    /* Excepción: el highlight de selección actual */
    [aria-selected="true"] {
        background-color: #EFEFFF !important;
        color: #111111 !important;
    }

    /* ── BOTONES NORMALES ── */
    .stButton > button {
        background: linear-gradient(135deg, #6C63FF 0%, #A78BFA 100%);
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 15px;
        width: 100%;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    .stButton > button:hover {
        opacity: 0.85;
        border: none;
    }

    /* ── FORM SUBMIT BUTTON ── */
    [data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #6C63FF 0%, #A78BFA 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        border-radius: 8px !important;
        width: 100% !important;
        padding: 12px 24px !important;
    }
    [data-testid="stFormSubmitButton"] > button:hover {
        opacity: 0.85 !important;
        border: none !important;
    }
    button[kind="formSubmit"],
    button[kind="primaryFormSubmit"],
    button[kind="secondaryFormSubmit"] {
        background: linear-gradient(135deg, #6C63FF 0%, #A78BFA 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }

    /* ── FORM CONTAINER ── */
    .stForm {
        background-color: #1A1D2E !important;
        border: 1px solid #3D3F50 !important;
        border-radius: 12px !important;
        padding: 24px !important;
    }

    /* ── DATAFRAME ── */
    .stDataFrame {
        border: 1px solid #3D3F50;
        border-radius: 12px;
        overflow: hidden;
    }

    /* ── CAPTION ── */
    .stCaption {
        color: #C8CADB !important;
        font-size: 13px !important;
    }

    /* ── DIVISORES ── */
    hr { border-color: #3D3F50 !important; }

    /* ── EXPANDER ── */
    .streamlit-expanderHeader {
        background-color: #1A1D2E !important;
        border: 1px solid #3D3F50 !important;
        border-radius: 8px !important;
        color: #F0F2F6 !important;
        font-size: 15px !important;
    }

    /* ── ALERTS ── */
    .stSuccess {
        background-color: #0D2818 !important;
        border: 1px solid #10B981 !important;
        border-radius: 8px !important;
        color: #FFFFFF !important;
    }
    .stError {
        background-color: #2D0F0F !important;
        border: 1px solid #EF4444 !important;
        border-radius: 8px !important;
        color: #FFFFFF !important;
    }
    .stWarning {
        background-color: #2D1F0F !important;
        border: 1px solid #F59E0B !important;
        border-radius: 8px !important;
        color: #FFFFFF !important;
    }
    .stInfo {
        background-color: #0F1D2D !important;
        border: 1px solid #6C63FF !important;
        border-radius: 8px !important;
        color: #FFFFFF !important;
    }

    /* ── MARKDOWN BOLD ── */
    strong { color: #FFFFFF !important; }

    /* ── PLACEHOLDER ── */
    input::placeholder {
        color: #9B9DB0 !important;
        opacity: 1 !important;
    }

    /* ── PÁGINA SERVICIOS — fondo visible ── */
    .js-plotly-plot {
        background-color: #1A1D2E !important;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_gspread_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",  # ← quita el .readonly
        "https://www.googleapis.com/auth/drive"           # ← quita el .readonly
    ]
    creds = Credentials.from_service_account_info(
        dict(st.secrets["google_credentials"]),
        scopes=scopes
    )
    return gspread.authorize(creds)
import time
def asignar_ids_clientes():
    import unicodedata

    client = get_gspread_client()
    sheet_ids = st.session_state.get("SHEET_IDS", {})

    def normalizar(nombre, tel=""):
        nombre = str(nombre).strip().lower()
        nombre = unicodedata.normalize("NFKD", nombre)
        nombre = "".join(c for c in nombre if not unicodedata.combining(c))
        nombre = " ".join(nombre.split())
        # Incluir los últimos 4 dígitos del tel para distinguir homónimos
        tel = str(tel).strip().replace("-", "").replace(" ", "")
        sufijo = tel[-4:] if len(tel) >= 4 else tel
        return f"{nombre}_{sufijo}"

    datos_sheets = {}
    for año, sheet_id in sheet_ids.items():
        if not sheet_id:
            continue
        try:
            sh = client.open_by_key(sheet_id)
            ws = sh.get_worksheet(0)

            # ── Verificar si ya existe columna ID Cliente ──
            headers = ws.row_values(1)
            if "ID Cliente" in headers:
                st.info(f"Sheet {año} ya tiene columna ID Cliente — se actualizarán los IDs sin insertar columna nueva.")
                col_id = headers.index("ID Cliente") + 1  # base 1
                col_nombre = headers.index("Nombre") + 1 if "Nombre" in headers else None
                col_tel = headers.index("Tel") + 1 if "Tel" in headers else None
                datos_sheets[año] = {
                    "ws": ws, "sh": sh,
                    "ya_tiene_columna": True,
                    "col_id": col_id,
                    "col_nombre": col_nombre,
                    "col_tel": col_tel,
                    "total_filas": len(ws.col_values(col_nombre)) if col_nombre else 0
                }
            else:
                col_nombre = headers.index("Nombre") + 1 if "Nombre" in headers else 4
                col_tel = headers.index("Tel") + 1 if "Tel" in headers else 5
                col_nombres = ws.col_values(col_nombre)
                col_tels = ws.col_values(col_tel)
                datos_sheets[año] = {
                    "ws": ws, "sh": sh,
                    "ya_tiene_columna": False,
                    "col_nombre": col_nombre,
                    "col_tel": col_tel,
                    "nombres": col_nombres,
                    "tels": col_tels
                }
        except Exception as e:
            st.warning(f"No se pudo leer el sheet {año}: {e}")

    if not datos_sheets:
        st.error("No hay sheets disponibles.")
        return

    # ── Construir mapa nombre+tel → ID ──
    mapa_id = {}
    contador = 1

    for año, data in datos_sheets.items():
        ws = data["ws"]
        if data["ya_tiene_columna"]:
            col_nombre = data["col_nombre"]
            col_tel = data["col_tel"]
            nombres = ws.col_values(col_nombre)[1:] if col_nombre else []
            tels = ws.col_values(col_tel)[1:] if col_tel else []
        else:
            nombres = data["nombres"][1:]
            tels = data["tels"][1:] if len(data.get("tels", [])) > 1 else [""] * len(nombres)

        for i, nombre in enumerate(nombres):
            if not nombre or str(nombre).strip() in ["", "nan"]:
                continue
            tel = tels[i] if i < len(tels) else ""
            clave = normalizar(nombre, tel)
            if clave not in mapa_id:
                mapa_id[clave] = contador
                contador += 1

    st.info(f"Se identificaron {contador - 1} clientes únicos (por nombre + teléfono).")

    # ── Insertar columna o actualizar IDs ──
    for año, data in datos_sheets.items():
        ws = data["ws"]
        sh = data["sh"]

        try:
            if not data["ya_tiene_columna"]:
                # Insertar columna D nueva
                sheet_tab_id = ws.id
                sh.batch_update({"requests": [{
                    "insertDimension": {
                        "range": {
                            "sheetId": sheet_tab_id,
                            "dimension": "COLUMNS",
                            "startIndex": 3,
                            "endIndex": 4
                        },
                        "inheritFromBefore": False
                    }
                }]})
                ws.update_cell(1, 4, "ID Cliente")
                col_id = 4
                col_nombre = data["col_nombre"] + 1  # se desplazó
                col_tel = data["col_tel"] + 1
            else:
                col_id = data["col_id"]
                col_nombre = data["col_nombre"]
                col_tel = data["col_tel"]

            # Leer nombres y tels actuales
            nombres = ws.col_values(col_nombre)[1:]
            tels = ws.col_values(col_tel)[1:] if col_tel else []

            updates = []
            for i, nombre in enumerate(nombres):
                if not nombre or str(nombre).strip() in ["", "nan"]:
                    continue
                tel = tels[i] if i < len(tels) else ""
                clave = normalizar(nombre, tel)
                id_cliente = mapa_id.get(clave, "")
                updates.append({
                    "range": f"{chr(64 + col_id)}{i + 2}",
                    "values": [[id_cliente]]
                })

            for i in range(0, len(updates), 100):
                ws.batch_update(updates[i:i+100])

            st.success(f"✅ Sheet {año} — {len(updates)} filas actualizadas")

        except Exception as e:
            st.error(f"Error en sheet {año}: {e}")

    st.success("🎉 Listo — IDs únicos asignados por nombre + teléfono")
    st.cache_data.clear()

# 🔥 FUNCIÓN AGREGAR CLIENTES (igual pero mejorada leve)
def agregar_a_sheets(data):
    client = get_gspread_client()
    sheet_id = SHEET_IDS[data["Año"].iloc[0]]
    sh = client.open_by_key(sheet_id)
    worksheet = sh.get_worksheet(0)

    # 🔥 folio único
    folio = str(int(datetime.now().timestamp()))

    worksheet.append_row([
        folio,                      # Folio sistema
        "",                         # Folio interno
        data["Fecha"].iloc[0],      # Fecha
        data["Nombre"].iloc[0],     # Nombre
        data["Tel"].iloc[0],        # Tel
        "",                         # Dirección
        data["Origen"].iloc[0],     # Origen
        data["Monto"].iloc[0],      # Monto
        data["Servicio"].iloc[0],   # Servicio
        "",                         # Comentarios
        "", "", ""                  # 90 días, 6 meses, 1 año
    ])

# ── LOGIN ──
def login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            "<h1 style='text-align:center; color:#2B5BAA; font-size:2.5rem;'>CRM</h1>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<h3 style='text-align:center; color:#2B5BAA;'>Iniciar sesión</h3>",
            unsafe_allow_html=True
        )
        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("login_form"):
            email = st.text_input("Email", placeholder="Tu email")
            password = st.text_input(
                "Contraseña",
                type="password",
                placeholder="Tu contraseña"
            )
            submitted = st.form_submit_button(
                "Entrar",
                use_container_width=True
            )

            if submitted:
                try:
                    response = supabase.auth.sign_in_with_password({
                        "email": email,
                        "password": password
                    })

                    user_data = supabase.table("usuarios")\
                        .select("*")\
                        .eq("auth_id", response.user.id)\
                        .single()\
                        .execute()

                    st.session_state["usuario"] = user_data.data["username"]
                    st.session_state["empresa"] = user_data.data["empresa"]
                    st.session_state["sistema"] = user_data.data["sistema"]
                    st.session_state["auth_id"] = str(response.user.id)
                    st.session_state["empresa_id"] = user_data.data["id"]
                    st.session_state["access_token"] = response.session.access_token
                    st.rerun()

                except Exception as e:
                    st.error("Email o contraseña incorrectos")


if "usuario" not in st.session_state:
    login()
    st.stop()

if "cache_limpiado" not in st.session_state:
    st.cache_data.clear()
    st.session_state["cache_limpiado"] = True

app_config = USUARIOS.get(st.session_state["usuario"], {}).get("app", {})
NOMBRE_APP = app_config.get("nombre", "CRM Dashboard")

# ── CARGAR DATOS DESDE SUPABASE ──
@st.cache_data(ttl=300)
def cargar_datos(empresa_id, access_token):
    try:
        client = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"]
        )
        client.postgrest.auth(access_token)

        todos = []
        page = 0
        page_size = 500

        while True:
            response = client.table("clientes")\
                .select("*")\
                .eq("empresa_id", empresa_id)\
                .range(page * page_size, (page + 1) * page_size - 1)\
                .execute()

            if not response.data:
                break

            todos.extend(response.data)

            if len(response.data) < page_size:
                break

            page += 1

        if not todos:
            return pd.DataFrame()

        df = pd.DataFrame(todos)
        df = df.rename(columns={
            "comentarios": "Comentarios con llamada posterior a venta",
            "nombre": "Nombre",
            "tel": "Tel",
            "direccion": "Dirección",
            "origen": "Origen",
            "monto": "Monto",
            "servicio": "Servicio",
            "fecha": "Fecha",
            "año": "Año",
            "cliente_id": "ID Cliente"
        })
        return df

    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame()

empresa_id = st.session_state.get("empresa_id", "")
access_token = st.session_state.get("access_token", "")
df = cargar_datos(empresa_id, access_token)

if df is None or df.empty:
    df = pd.DataFrame({
        "Nombre": [], "Tel": [], "Fecha": [], "Monto": [],
        "Servicio": [], "Origen": [],
        "Comentarios con llamada posterior a venta": [], "Año": []
    })

df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
df["Monto"] = pd.to_numeric(df["Monto"], errors="coerce")
df["Mes"] = df["Fecha"].dt.month
df["Año"] = pd.to_numeric(df["Año"], errors="coerce").astype("Int64")

años_disponibles = sorted(df["Año"].dropna().unique().tolist())
if not años_disponibles:
    años_disponibles = [datetime.now().year]
años_sin_2026 = años_disponibles
# ── SIDEBAR ──
with st.sidebar:
    logo_path = USUARIOS[st.session_state["usuario"]].get("app", {}).get("logo")
    if logo_path:
        try:
            logo_path_full = os.path.join(os.path.dirname(os.path.abspath(__file__)), logo_path)
            st.image(logo_path_full, width=120)
        except Exception as e:
            pass

    st.markdown(f"<h3 style='color:white'>{st.session_state['empresa']}</h3>", unsafe_allow_html=True)
    st.markdown("---")

    paginas = ["Resumen", "Ventas", "Clientes", "Servicios", "Follow Up", "Agenda", "Cotizaciones", "Chat"]

    if "pagina" not in st.session_state:
        st.session_state["pagina"] = "Resumen"

    for p in paginas:
        if st.button(p, key=f"sidebar_{p}", use_container_width=True):
            st.session_state["pagina"] = p

    st.markdown("---")
    st.caption("Datos actualizados cada 5 min")

    if st.button("Actualizar datos", key="sidebar_actualizar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")

    if st.button("Cerrar sesión", key="sidebar_logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


    # ── RESUMEN ──
    # 🔥 IMPORTANTE: ESTO VA FUERA DEL SIDEBAR
pagina = st.session_state["pagina"]
def limpiar_numero(valor):
    if pd.isna(valor):
        return 0

    valor = str(valor)
    valor = valor.replace("$", "")
    valor = valor.replace(",", "")
    valor = valor.replace(" ", "")

    if valor == "-" or valor == "":
        return 0

    try:
        return float(valor)
    except:
        return 0

def cargar_finanzas(url):
    try:
        df = pd.read_csv(url, header=None)
    except Exception as e:
        st.error(f"Error descargando CSV: {e}")
        return None, None, None

    def sumar_columna_desde_fila(keyword, col_idx, filas_max=50):
        # Encontrar fila del keyword
        fila_inicio = None
        for i, row in df.iterrows():
            if str(row.iloc[0]).strip() == keyword:
                fila_inicio = i
                break
        if fila_inicio is None:
            return 0

        # Buscar fila del siguiente keyword para saber dónde parar
        fila_fin = fila_inicio + filas_max

        total = 0
        for i in range(fila_inicio, min(fila_fin, len(df))):
            try:
                val = df.iloc[i, col_idx]
                limpio = str(val).replace("$", "").replace(",", "").replace("`", "").strip()
                num = float(limpio)
                if num > 0:
                    total += num
            except:
                continue
        return total

    # Detectar si es estructura semanal (columna 42 = Total Mes)
    es_semanal = df.iloc[8, 42] == "Total Mes" if len(df.columns) > 42 else False

    if es_semanal:
        # Sumar columna 42 entre ENTRADAS y SALIDAS
        ingresos = sumar_columna_desde_fila("ENTRADAS", 42, filas_max=15)
        gastos = sumar_columna_desde_fila("SALIDAS", 42, filas_max=15)
    else:
        # Estructura mensual normal — buscar max en fila de Total Entradas/Salidas
        def buscar_total(keyword):
            filas = df[df.astype(str).apply(
                lambda row: row.str.contains(keyword, case=False, na=False).any(),
                axis=1
            )]
            if filas.empty:
                return 0
            fila = filas.iloc[0]
            valores = []
            for v in fila:
                try:
                    limpio = str(v).replace("$", "").replace(",", "").replace("`", "").strip()
                    num = float(limpio)
                    if num > 0:
                        valores.append(num)
                except:
                    continue
            return max(valores) if valores else 0

        ingresos = buscar_total("Total Entradas")
        gastos = buscar_total("Total Salidas")

    utilidad = ingresos - gastos
    return ingresos, gastos, utilidad
# ── RESUMEN ──
if pagina == "Resumen":
    st.title(NOMBRE_APP)

    # ─────────────────────────────
    # 🔔 BANNER DE RECORDATORIOS
    # ─────────────────────────────
    if "meses_recordatorio" not in st.session_state:
        st.session_state["meses_recordatorio"] = 6

    meses_recordatorio = st.session_state["meses_recordatorio"]

    df_banner = df.copy()
    df_banner["Fecha"] = pd.to_datetime(df_banner["Fecha"], errors="coerce")

    ultimo_banner = df_banner.groupby("Nombre").agg(
        Ultima_Visita=("Fecha", "max")
    ).reset_index()
    ultimo_banner["Meses_sin_servicio"] = (
        (datetime.now() - ultimo_banner["Ultima_Visita"]).dt.days / 30
    ).round(1)

    clientes_pendientes = ultimo_banner[
        ultimo_banner["Meses_sin_servicio"] >= meses_recordatorio
    ]

    if not clientes_pendientes.empty:
        col_banner, col_config = st.columns([4, 1])
        with col_banner:
            if st.button(
                f"🔔 {len(clientes_pendientes)} clientes llevan {meses_recordatorio}+ meses sin servicio — Ver en Follow Up →",
                use_container_width=True,
                key="btn_banner_followup"
            ):
                st.session_state["pagina"] = "Follow Up"
                st.session_state["followup_meses_override"] = meses_recordatorio
                st.rerun()
        with col_config:
            if st.button(
                "⚙️ Configurar",
                key="btn_config_recordatorio",
                use_container_width=True
            ):
                st.session_state["mostrar_config_recordatorio"] = not st.session_state.get(
                    "mostrar_config_recordatorio", False
                )

        if st.session_state.get("mostrar_config_recordatorio", False):
            nuevo_umbral = st.slider(
                "Avisar cuando un cliente lleve X meses sin servicio:",
                1, 24, meses_recordatorio,
                key="slider_recordatorio"
            )
            if nuevo_umbral != meses_recordatorio:
                st.session_state["meses_recordatorio"] = nuevo_umbral
                st.rerun()

    st.markdown("---")

    # ─────────────────────────────
    # 📊 VENTAS Y FLUJO DE EFECTIVO
    # ─────────────────────────────
    st.subheader("📊 Ventas")

    año_resumen = st.selectbox(
        "Año:",
        años_sin_2026,
        index=len(años_sin_2026)-1
    )

    df_r = df[df["Año"] == año_resumen]

    total_ventas = df_r["Monto"].sum()
    total_clientes = df_r["Nombre"].nunique()
    ticket_promedio = df_r["Monto"].mean()
    total_servicios = len(df_r)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ventas totales", f"${total_ventas:,.0f}")
    col2.metric("Clientes únicos", f"{total_clientes:,}")
    col3.metric("Ticket promedio", f"${ticket_promedio:,.0f}")
    col4.metric("Servicios realizados", f"{total_servicios:,}")

    if año_resumen > min(años_sin_2026):
        df_ant = df[df["Año"] == año_resumen - 1]
        ventas_ant = df_ant["Monto"].sum()
        diferencia = total_ventas - ventas_ant
        porcentaje = (diferencia / ventas_ant * 100) if ventas_ant > 0 else 0
        color = "green" if diferencia > 0 else "red"
        simbolo = "▲" if diferencia > 0 else "▼"
        st.markdown(
            f"<p style='color:{color}; font-size:16px'>{simbolo} Comparado con {año_resumen-1}: "
            f"${abs(diferencia):,.0f} ({porcentaje:+.1f}%)</p>",
            unsafe_allow_html=True
        )

    # ─────────────────────────────
    # 💰 FLUJO DE EFECTIVO
    # ─────────────────────────────
    st.subheader("💰 Flujo de efectivo")

    finanzas_usuario = USUARIOS[st.session_state["usuario"]].get("finanzas", {})

    if finanzas_usuario:
        años_finanzas = list(finanzas_usuario.keys())
        año_finanzas = st.selectbox(
            "Año financiero:",
            años_finanzas,
            index=len(años_finanzas)-1
        )
        try:
            ingresos, gastos, utilidad = cargar_finanzas(finanzas_usuario[año_finanzas])
            if ingresos is not None:
                col1, col2, col3 = st.columns(3)
                col1.metric("💰 Ingresos", f"${ingresos:,.0f}")
                col2.metric("💸 Gastos", f"${gastos:,.0f}")
                col3.metric("🟢 Utilidad", f"${utilidad:,.0f}")
            else:
                st.warning("No se pudieron leer los datos del sheet")
        except Exception as e:
            st.error("Error cargando finanzas")
            st.write(e)
    else:
        st.info("No hay datos de flujo de efectivo configurados.")
    # ── VENTAS ──
elif pagina == "Ventas":
    st.title("Análisis de Ventas")

    ventas_año = df[df["Año"].isin(años_sin_2026)].groupby("Año")["Monto"].sum().reset_index()
    ventas_año.columns = ["Año", "Total"]
    st.subheader("Ventas totales por año")
    st.bar_chart(ventas_año.set_index("Año"))

    st.subheader("Comparación mensual")
    años_sel = st.multiselect("Años:", años_sin_2026, default=años_sin_2026[-2:])
    if años_sel:
        import plotly.express as px

        df_f = df[df["Año"].isin(años_sel)]
        pivot = df_f.groupby(["Año","Mes"])["Monto"].sum().reset_index()
        pivot = pivot.pivot(index="Mes", columns="Año", values="Monto").fillna(0)
        pivot = pivot.sort_index()

        nombres_meses = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",
                         7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}
        pivot.index = pivot.index.map(nombres_meses)

        pivot_reset = pivot.reset_index()
        pivot_reset.columns.name = None

        fig = px.line(
            pivot_reset,
            x="Mes",
            y=[col for col in pivot_reset.columns if col != "Mes"],
            labels={"value": "Ventas", "variable": "Año"},
            category_orders={"Mes": ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]}
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Proyección 2026")
        mes_actual = datetime.now().month
        meses_con_datos_2026 = df[(df["Año"]==2026) & (df["Monto"]>0)]["Mes"].nunique()
        ventas_2026_acum = df[df["Año"]==2026]["Monto"].sum() if 2026 in df["Año"].values else 0
        ventas_2025_mismos_meses = df[(df["Año"]==2025) & (df["Mes"] <= mes_actual)]["Monto"].sum()
        ventas_2025_total = df[df["Año"]==2025]["Monto"].sum()

        if ventas_2025_mismos_meses > 0 and ventas_2026_acum > 0:
            factor_crecimiento = ventas_2026_acum / ventas_2025_mismos_meses
            proyeccion = ventas_2025_total * factor_crecimiento
            tendencia = ((factor_crecimiento - 1) * 100)
            color = "green" if factor_crecimiento >= 1 else "red"
        else:
            proyeccion = ventas_2025_total
            tendencia = 0
            color = "gray"

        col1, col2, col3 = st.columns(3)
        col1.metric("Proyección anual 2026", f"${proyeccion:,.0f}")
        col2.metric("Ventas reales 2026", f"${ventas_2026_acum:,.0f}")
        col3.metric("Tendencia vs 2025", f"{tendencia:+.1f}%")
        st.markdown(
            f"<p style='color:{color}'>Basado en {meses_con_datos_2026} mes(es) de datos reales de 2026</p>",
            unsafe_allow_html=True
        )

        st.subheader("Detalle mes a mes — 2026 vs 2025")
        nombres_meses_completos = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
                                   7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}
        resumen_meses = []
        for m in range(1, mes_actual + 1):
            v2025 = df[(df["Año"]==2025) & (df["Mes"]==m)]["Monto"].sum()
            v2026 = df[(df["Año"]==2026) & (df["Mes"]==m)]["Monto"].sum() if 2026 in df["Año"].values else 0
            diff = v2026 - v2025
            pct = ((diff / v2025) * 100) if v2025 > 0 else 0
            resumen_meses.append({
                "Mes": nombres_meses_completos[m],
                "2025": f"${v2025:,.0f}",
                "2026": f"${v2026:,.0f}",
                "Diferencia": f"${diff:,.0f}",
                "Variación": f"{pct:+.1f}%"
            })
        st.dataframe(pd.DataFrame(resumen_meses), use_container_width=True, hide_index=True)

    # ─────────────────────────────
    # 📈 CONVERSIÓN DE FOLLOW UP
    # ─────────────────────────────
    st.markdown("---")
    st.subheader("📈 Conversión de Follow Up")

    if "followup_resultados" not in st.session_state:
        st.session_state["followup_resultados"] = []

    resultados = st.session_state["followup_resultados"]

    if resultados:
        import collections
        conteo_resultados = collections.Counter(r["resultado"] for r in resultados)
        total_contactados = len(resultados)
        agendaron = conteo_resultados.get("Agendó", 0)
        tasa = (agendaron / total_contactados * 100) if total_contactados > 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Total contactados", total_contactados)
        col2.metric("Agendaron", agendaron)
        col3.metric("Tasa de conversión", f"{tasa:.1f}%")

        df_res = pd.DataFrame(resultados)
        conteo_df = df_res["resultado"].value_counts().reset_index()
        conteo_df.columns = ["Resultado", "Cantidad"]
        st.bar_chart(conteo_df.set_index("Resultado"))

        with st.expander("Ver detalle completo"):
            st.dataframe(
                pd.DataFrame(resultados)[["timestamp", "nombre", "resultado", "bloque"]],
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("Aún no hay resultados de follow up registrados. Márcalos en la página Follow Up.")
        # CLIENTES
elif pagina == "Clientes":
    import urllib.parse
    import base64
    import streamlit.components.v1 as components

    st.title("Origen de Clientes")

    año_origen = st.selectbox("Año:", años_sin_2026)
    df_o = df[df["Año"] == año_origen].copy()

    df_o["Origen"] = (
        df_o["Origen"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    origenes_config = USUARIOS[st.session_state["usuario"]].get("origenes", {})
    df_o["Origen"] = df_o["Origen"].replace(origenes_config)
    df_o["Origen"] = df_o["Origen"].replace(["", "nan"], "Sin especificar")

    origen = df_o["Origen"].value_counts().reset_index()
    origen.columns = ["Canal", "Clientes"]
    st.bar_chart(origen.set_index("Canal"))
    st.dataframe(origen, use_container_width=True)

    # 🧠 HISTORIAL
    st.markdown("### 🧠 Historial de clientes")

    df_hist = df.copy()
    df_hist["Monto"] = pd.to_numeric(df_hist["Monto"], errors="coerce")
    df_hist["Fecha"] = pd.to_datetime(df_hist["Fecha"], errors="coerce")
    df_hist["ID Cliente"] = pd.to_numeric(df_hist["ID Cliente"], errors="coerce")

    historial = df_hist.groupby("ID Cliente").agg(
        Nombre=("Nombre", "last"),
        Total_Gastado=("Monto", "sum"),
        Servicios=("Monto", "count"),
        Ultima_Visita=("Fecha", "max"),
        Ticket_Promedio=("Monto", "mean"),
        Tel=("Tel", "last"),
        Direccion=("Dirección", "last")
    ).reset_index()

    historial = historial.sort_values(by="Total_Gastado", ascending=False)

    cliente_buscar = st.text_input("🔍 Buscar cliente (nombre o ID)", key=f"buscador_historial_{año_origen}")
    if cliente_buscar:
        historial = historial[
            historial["Nombre"].str.contains(cliente_buscar, case=False, na=False) |
            historial["ID Cliente"].astype(str).str.contains(cliente_buscar, na=False)
        ]

    historial_mostrar = historial.copy()
    historial_mostrar["Total_Gastado"] = historial_mostrar["Total_Gastado"].apply(lambda x: f"${x:,.0f}")
    historial_mostrar["Ticket_Promedio"] = historial_mostrar["Ticket_Promedio"].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else "-")
    historial_mostrar["Ultima_Visita"] = historial_mostrar["Ultima_Visita"].dt.strftime("%d/%m/%Y").fillna("-")
    historial_mostrar["Direccion"] = historial_mostrar["Direccion"].fillna("-")
    historial_mostrar = historial_mostrar[[
        "ID Cliente", "Nombre", "Tel", "Direccion",
        "Total_Gastado", "Servicios", "Ultima_Visita", "Ticket_Promedio"
    ]]
    historial_mostrar.columns = [
        "ID", "Nombre", "Tel", "Dirección",
        "Total Gastado", "Servicios", "Última Visita", "Ticket Promedio"
    ]

    st.markdown("### 🏆 Top clientes")
    top_clientes = historial.head(10)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("💰 Mejor cliente", top_clientes.iloc[0]["Nombre"] if not top_clientes.empty else "-")
    with col2:
        st.metric("💵 Mayor gasto", f"${top_clientes.iloc[0]['Total_Gastado']:,.0f}" if not top_clientes.empty else "$0")
    st.dataframe(historial_mostrar, use_container_width=True, hide_index=True)

    # 👤 PERFIL + EDICIÓN
    st.markdown("### 👤 Perfil del cliente")
    clientes_lista = historial["Nombre"].dropna().unique().tolist()
    cliente_sel = st.selectbox("Selecciona un cliente", clientes_lista)

    if cliente_sel:
        id_sel = historial[historial["Nombre"] == cliente_sel]["ID Cliente"].iloc[0]
        df_cliente = df_hist[df_hist["ID Cliente"] == id_sel].copy()
        df_cliente = df_cliente.sort_values(by="Fecha", ascending=False)

        total = df_cliente["Monto"].sum()
        visitas = len(df_cliente)
        ultima = df_cliente["Fecha"].max()
        promedio = df_cliente["Monto"].mean()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total gastado", f"${total:,.0f}")
        col2.metric("Servicios", visitas)
        col3.metric("Última visita", ultima.strftime("%d/%m/%Y") if pd.notnull(ultima) else "-")
        col4.metric("Ticket promedio", f"${promedio:,.0f}")

        # Datos actuales del cliente
        ultima_fila = df_cliente.iloc[0]
        tel_actual = str(ultima_fila.get("Tel", ""))
        dir_actual = str(ultima_fila.get("Dirección", ""))

        # ── EDITAR CLIENTE ──
        st.markdown("### ✏️ Editar datos del cliente")
        with st.form("editar_cliente_form"):
            nuevo_nombre = st.text_input("Nombre", value=cliente_sel)
            nuevo_tel = st.text_input("Teléfono", value=tel_actual if tel_actual != "nan" else "")
            nueva_dir = st.text_input("Dirección", value=dir_actual if dir_actual != "nan" else "")
            guardar = st.form_submit_button("💾 Guardar cambios", use_container_width=True)

            if guardar:
                try:
                    client_auth = create_client(
                        st.secrets["SUPABASE_URL"],
                        st.secrets["SUPABASE_KEY"]
                    )
                    client_auth.postgrest.auth(st.session_state.get("access_token", ""))

                    # Actualizar todos los registros de este cliente
                    client_auth.table("clientes").update({
                        "nombre": nuevo_nombre,
                        "tel": nuevo_tel,
                        "direccion": nueva_dir
                    }).eq("empresa_id", st.session_state["empresa_id"])\
                      .eq("cliente_id", int(id_sel))\
                      .execute()

                    st.success(f"✅ Datos de {nuevo_nombre} actualizados en todos sus registros.")
                    st.cache_data.clear()
                    import time as t
                    t.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al actualizar: {e}")

        st.markdown("### 📋 Historial completo")
        mostrar = df_cliente[[
            "Fecha", "Nombre", "Servicio", "Monto", "Origen",
            "Comentarios con llamada posterior a venta"
        ]].copy()
        mostrar.columns = ["Fecha", "Nombre", "Servicio", "Monto", "Origen", "Comentarios"]
        st.dataframe(mostrar, use_container_width=True, hide_index=True)

    # 🔴 CLIENTES PERDIDOS
    st.markdown("## 🔴 Oportunidades de recuperación")

    df_lost = df_hist.copy()
    hoy = datetime.now()

    ultimo = df_lost.groupby("ID Cliente").agg(
        Nombre=("Nombre", "last"),
        Ultima_Visita=("Fecha", "max"),
        Total_Gastado=("Monto", "sum"),
        Tel=("Tel", "last")
    ).reset_index()
    ultimo["Meses_sin_servicio"] = ((hoy - ultimo["Ultima_Visita"]).dt.days / 30).round(1)

    col1, col2 = st.columns(2)
    with col1:
        meses_min = st.slider("Meses sin servicio", 3, 24, 6)
    with col2:
        monto_min = st.number_input("Monto mínimo ($)", value=1500)

    perdidos = ultimo[
        (ultimo["Meses_sin_servicio"] >= meses_min) &
        (ultimo["Total_Gastado"] >= monto_min)
    ]
    perdidos = perdidos.sort_values(by="Total_Gastado", ascending=False)

    col1, col2, col3 = st.columns(3)
    col1.metric("Clientes recuperables", len(perdidos))
    col2.metric("Dinero en riesgo", f"${perdidos['Total_Gastado'].sum():,.0f}")
    col3.metric(
        "Meses promedio sin servicio",
        f"{perdidos['Meses_sin_servicio'].mean():.1f}" if not perdidos.empty else "0"
    )

    st.markdown("### 📋 Lista priorizada")
    perdidos_mostrar = perdidos[["ID Cliente", "Nombre", "Tel", "Total_Gastado", "Meses_sin_servicio"]].copy()
    perdidos_mostrar["Total_Gastado"] = perdidos_mostrar["Total_Gastado"].apply(lambda x: f"${x:,.0f}")
    st.dataframe(perdidos_mostrar, use_container_width=True, hide_index=True)

    # 🚀 CONTACTO MASIVO
    st.markdown("## 🚀 Contacto masivo")

    if not perdidos.empty:
        PLANTILLAS_MASIVAS = {
            "Recordatorio": "Hola {nombre}, te contactamos de {empresa}. Hace tiempo no realizas un servicio con nosotros. ¿Te gustaría agendar?",
            "Promoción": "Hola {nombre}, en {empresa} tenemos una promoción especial. ¿Te interesa?",
            "Seguimiento": "Hola {nombre}, te damos seguimiento desde {empresa}. ¿Cómo fue tu servicio?",
            "Reactivación": "Hola {nombre}, te extrañamos en {empresa} 😄 ¿Agendamos esta semana?"
        }

        empresa = st.session_state.get("empresa", "")
        plantilla_sel_masiva = st.selectbox(
            "Plantilla para todos",
            list(PLANTILLAS_MASIVAS.keys()),
            key="plantilla_masiva_clientes"
        )
        mensaje_base_masivo = PLANTILLAS_MASIVAS[plantilla_sel_masiva]

        urls_perdidos = []
        for _, row in perdidos.iterrows():
            tel = str(row["Tel"]).replace("-", "").replace(" ", "")
            if tel and tel != "nan":
                tel_completo = "52" + tel
                mensaje = mensaje_base_masivo.format(nombre=row["Nombre"], empresa=empresa)
                urls_perdidos.append((
                    row["Nombre"],
                    f"https://wa.me/{tel_completo}?text={urllib.parse.quote(mensaje)}"
                ))

        if urls_perdidos:
            cols = st.columns(3)
            for i, (nombre_btn, url_btn) in enumerate(urls_perdidos):
                with cols[i % 3]:
                    st.link_button(f"💬 {nombre_btn}", url_btn)

            html_links_cl = ""
            for nombre_link, url_link in urls_perdidos:
                html_links_cl += f'<a href="{url_link}" target="_blank" style="display:block;background-color:#25D366;color:white;text-decoration:none;padding:12px 16px;border-radius:8px;margin-bottom:8px;font-size:15px;font-family:sans-serif;">💬 {nombre_link}</a>'

            pagina_html_cl = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Contacto masivo</title>
            <style>body{{font-family:sans-serif;padding:24px;max-width:500px;margin:auto;background:#f9f9f9;}}h2{{color:#128C7E;}}p{{color:#555;margin-bottom:20px;}}</style></head>
            <body><h2>📋 {len(urls_perdidos)} clientes a contactar</h2><p>Haz click en cada nombre para abrir WhatsApp Web.</p>{html_links_cl}</body></html>"""

            b64_cl = base64.b64encode(pagina_html_cl.encode("utf-8")).decode("utf-8")
            components.html(f'<a href="data:text/html;base64,{b64_cl}" target="_blank" style="display:block;background-color:#128C7E;color:white;text-decoration:none;text-align:center;border-radius:8px;padding:14px 24px;font-size:16px;font-family:sans-serif;margin-top:8px;">🚀 Abrir panel de contacto masivo ({len(urls_perdidos)} contactos)</a>', height=65)

    # 💬 CONTACTO INDIVIDUAL
    st.markdown("### 💬 Contacto rápido")

    if not perdidos.empty:
        PLANTILLAS_IND = {
            "Recordatorio": "Hola {nombre}, te contactamos de {empresa}. Hace tiempo no realizas un servicio con nosotros. ¿Te gustaría agendar?",
            "Promoción": "Hola {nombre}, en {empresa} tenemos una promoción especial. ¿Te interesa?",
            "Seguimiento": "Hola {nombre}, te damos seguimiento desde {empresa}. ¿Cómo fue tu servicio?",
            "Reactivación": "Hola {nombre}, te extrañamos en {empresa} 😄 ¿Agendamos esta semana?"
        }

        cliente_sel_contacto = st.selectbox(
            "Selecciona cliente",
            perdidos["Nombre"],
            key="select_contacto"
        )

        cliente_data = perdidos[perdidos["Nombre"] == cliente_sel_contacto].iloc[0]
        tel = str(cliente_data["Tel"]).replace("-", "").replace(" ", "")
        if tel and tel != "nan":
            tel = "52" + tel

        plantilla_ind_cl = st.selectbox(
            "Plantilla",
            list(PLANTILLAS_IND.keys()),
            key="plantilla_ind_clientes"
        )
        mensaje = PLANTILLAS_IND[plantilla_ind_cl].format(
            nombre=cliente_sel_contacto,
            empresa=st.session_state.get("empresa", "tu negocio")
        )
        mensaje_edit = st.text_area("Mensaje", value=mensaje, key="msg_edit_clientes")

        if tel and tel != "52nan":
            url = f"https://wa.me/{tel}?text={urllib.parse.quote(mensaje_edit)}"
            st.link_button("💬 Abrir WhatsApp", url)
        else:
            st.warning("Este cliente no tiene teléfono válido")

    # ── FOLLOW UP ──
elif pagina == "Follow Up":
    st.title("Clientes para Follow Up")
    import urllib.parse
    import json
    import base64
    import streamlit.components.v1 as components
    from datetime import datetime

    if "followup_historial" not in st.session_state:
        st.session_state["followup_historial"] = []
    if "followup_resultados" not in st.session_state:
        st.session_state["followup_resultados"] = []

    ultimo = df.groupby("Nombre").agg(Fecha=("Fecha","max")).reset_index()
    ultimo.columns = ["Nombre", "Ultimo servicio"]

    tels = df[["Nombre","Tel"]].drop_duplicates(subset="Nombre")
    comentarios = df.sort_values("Fecha").drop_duplicates(subset="Nombre", keep="last")[
        ["Nombre","Comentarios con llamada posterior a venta"]
    ]

    ultimo = ultimo.merge(tels, on="Nombre", how="left")
    ultimo = ultimo.merge(comentarios, on="Nombre", how="left")
    ultimo.columns = ["Nombre", "Ultimo servicio", "Tel", "Comentario"]

    # ── Si viene del banner, usar ese umbral; si no, el slider ──
    meses_default = st.session_state.pop("followup_meses_override", None)

    col1, col2 = st.columns(2)
    with col1:
        meses = st.slider(
            "Sin servicio hace más de X meses:",
            1, 24,
            meses_default if meses_default is not None else 6
        )
    with col2:
        mes_filtro = st.selectbox(
            "Mes del último servicio:",
            ["Todos","Enero","Febrero","Marzo","Abril","Mayo","Junio",
             "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
        )

    fecha_limite = datetime.now() - timedelta(days=meses * 30)
    sin_servicio = ultimo[ultimo["Ultimo servicio"] < fecha_limite].copy()

    meses_dict = {
        "Enero":1,"Febrero":2,"Marzo":3,"Abril":4,"Mayo":5,"Junio":6,
        "Julio":7,"Agosto":8,"Septiembre":9,"Octubre":10,"Noviembre":11,"Diciembre":12
    }

    if mes_filtro != "Todos":
        sin_servicio = sin_servicio[
            sin_servicio["Ultimo servicio"].dt.month == meses_dict[mes_filtro]
        ]

    sin_servicio = sin_servicio.sort_values("Ultimo servicio")

    hoy = datetime.now()
    def get_columna_followup(ultima_fecha):
        if pd.isna(ultima_fecha):
            return 13
        meses_sin = (hoy - ultima_fecha).days / 30
        if meses_sin < 3:
            return 11
        elif meses_sin < 8:
            return 12
        else:
            return 13

    st.metric("Clientes a contactar", len(sin_servicio))
    st.dataframe(sin_servicio, use_container_width=True)

    st.markdown("### 🚀 Enviar mensaje a todos")

    PLANTILLAS_MENSAJES = {
        "Seguimiento": "Hola {nombre}, te contactamos de {empresa}. Solo para dar seguimiento a tu último servicio. ¿Cómo fue tu experiencia?",
        "Recordatorio": "Hola {nombre}, en {empresa} te recordamos que ya pasó tiempo desde tu último servicio. ¿Te gustaría agendar?",
        "Promoción": "Hola {nombre}, en {empresa} tenemos una promoción especial disponible. ¿Te interesa aprovecharla?",
        "Reactivación": "Hola {nombre}, te extrañamos en {empresa} 😄 Tenemos disponibilidad esta semana. ¿Agendamos?"
    }

    plantilla_masiva = st.selectbox(
        "Plantilla:",
        list(PLANTILLAS_MENSAJES.keys()),
        key="plantilla_masiva_followup"
    )

    mensaje_masivo_preview = PLANTILLAS_MENSAJES[plantilla_masiva].format(
        nombre="[Nombre]",
        empresa=st.session_state.get("empresa", "nuestro negocio")
    )
    mensaje_masivo_edit = st.text_area(
        "Edita el mensaje ({nombre} y {empresa} se reemplazan automáticamente):",
        value=mensaje_masivo_preview,
        key="mensaje_masivo_edit"
    )

    TAMANO_BLOQUE = 20

    if not sin_servicio.empty:
        clientes_validos = sin_servicio[
            sin_servicio["Tel"].notna() &
            (sin_servicio["Tel"].astype(str).str.strip() != "") &
            (sin_servicio["Tel"].astype(str).str.strip() != "nan")
        ].reset_index(drop=True)

        total_bloques = (len(clientes_validos) + TAMANO_BLOQUE - 1) // TAMANO_BLOQUE

        st.caption(f"📦 {len(clientes_validos)} clientes divididos en {total_bloques} bloque(s) de {TAMANO_BLOQUE}")

        bloque_sel = st.selectbox(
            "Selecciona bloque a enviar:",
            [f"Bloque {i+1} ({i*TAMANO_BLOQUE+1}-{min((i+1)*TAMANO_BLOQUE, len(clientes_validos))})"
             for i in range(total_bloques)],
            key="bloque_sel"
        )

        idx_bloque = int(bloque_sel.split(" ")[1]) - 1
        inicio = idx_bloque * TAMANO_BLOQUE
        fin = inicio + TAMANO_BLOQUE
        clientes_bloque = clientes_validos.iloc[inicio:fin]

        urls_bloque = []
        for _, row in clientes_bloque.iterrows():
            tel = str(row["Tel"]).replace("-", "").replace(" ", "").strip()
            tel_completo = "52" + tel
            mensaje_final = mensaje_masivo_edit.format(
                nombre=row["Nombre"],
                empresa=st.session_state.get("empresa", "nuestro negocio")
            )
            mensaje_encoded = urllib.parse.quote(mensaje_final)
            urls_bloque.append((row["Nombre"], f"https://wa.me/{tel_completo}?text={mensaje_encoded}"))

        st.markdown(f"**Clientes en este bloque ({len(clientes_bloque)}):**")
        cols = st.columns(3)
        for i, (nombre_btn, url_btn) in enumerate(urls_bloque):
            with cols[i % 3]:
                st.link_button(f"💬 {nombre_btn}", url_btn)

        # ── PANEL DE ENVÍO MASIVO ──
        html_links = ""
        for nombre_link, url_link in urls_bloque:
            html_links += f"""
            <a href="{url_link}" target="_blank" style="
                display:block; background-color:#25D366; color:white;
                text-decoration:none; padding:12px 16px; border-radius:8px;
                margin-bottom:8px; font-size:15px; font-family:sans-serif;
            ">💬 {nombre_link}</a>
            """

        pagina_html = f"""
        <!DOCTYPE html><html><head><meta charset="utf-8">
        <title>WhatsApp Follow Up — Bloque {idx_bloque + 1}</title>
        <style>
            body{{font-family:sans-serif;padding:24px;max-width:500px;margin:auto;background:#f9f9f9;}}
            h2{{color:#128C7E;}}p{{color:#555;margin-bottom:20px;}}
        </style></head>
        <body>
            <h2>📋 Bloque {idx_bloque + 1} — {len(urls_bloque)} contactos</h2>
            <p>Haz click en cada nombre para abrir WhatsApp Web en una pestaña nueva.</p>
            {html_links}
        </body></html>
        """

        b64 = base64.b64encode(pagina_html.encode("utf-8")).decode("utf-8")
        components.html(f"""
        <a href="data:text/html;base64,{b64}" target="_blank" style="
            display:block; background-color:#128C7E; color:white;
            text-decoration:none; text-align:center; border-radius:8px;
            padding:14px 24px; font-size:16px; font-family:sans-serif; margin-top:8px;
        ">🚀 Abrir panel de envío — Bloque {idx_bloque + 1} ({len(urls_bloque)} contactos)</a>
        """, height=65)

        st.markdown("---")

        # ── REGISTRO DE RESULTADO ──
        st.markdown("### ✅ Marcar resultado del bloque")
        st.caption("Registra qué pasó con cada cliente. Esto alimenta el dashboard de conversión en Resumen.")

        OPCIONES_RESULTADO = ["Agendó", "No contestó", "Número inválido", "No le interesa", "Pendiente"]

        with st.expander(f"Registrar resultados — Bloque {idx_bloque + 1}"):
            resultados_bloque = {}
            for _, row in clientes_bloque.iterrows():
                resultados_bloque[row["Nombre"]] = st.selectbox(
                    row["Nombre"],
                    OPCIONES_RESULTADO,
                    index=4,
                    key=f"resultado_{row['Nombre']}_{idx_bloque}"
                )

        if st.button(f"✅ Guardar resultados y marcar bloque {idx_bloque+1} como enviado", use_container_width=True):
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
            errores_update = []

            with st.spinner("Guardando..."):
                try:
                    for nombre_r, resultado_r in resultados_bloque.items():
                        st.session_state["followup_resultados"].append({
                            "nombre": nombre_r,
                            "resultado": resultado_r,
                            "timestamp": timestamp,
                            "bloque": idx_bloque + 1
                        })

                    client = get_gspread_client()
                    sheet_ids = st.session_state.get("SHEET_IDS", {})

                    for _, row in clientes_bloque.iterrows():
                        nombre_cliente = row["Nombre"]
                        col_followup = get_columna_followup(row["Ultimo servicio"])

                        for año, sheet_id in sheet_ids.items():
                            if not sheet_id:
                                continue
                            try:
                                sh = client.open_by_key(sheet_id)
                                worksheet = sh.get_worksheet(0)
                                celdas = worksheet.findall(nombre_cliente)
                                for celda in celdas:
                                    resultado_celda = resultados_bloque.get(nombre_cliente, "Ok")
                                    worksheet.update_cell(celda.row, col_followup, resultado_celda)
                            except Exception as e:
                                errores_update.append(f"{nombre_cliente} ({año}): {e}")

                    st.session_state["followup_historial"].append({
                        "bloque": idx_bloque + 1,
                        "timestamp": timestamp,
                        "mes_filtro": mes_filtro,
                        "clientes": len(clientes_bloque),
                        "plantilla": plantilla_masiva,
                        "nombres": [n for n, _ in urls_bloque],
                        "resultados": resultados_bloque
                    })

                    st.success(f"✅ Bloque {idx_bloque+1} guardado — {timestamp}")
                    if errores_update:
                        st.warning(f"Algunos no se pudieron actualizar: {errores_update[:3]}")
                    st.cache_data.clear()

                except Exception as e:
                    st.error(f"Error guardando: {e}")

    if st.session_state["followup_historial"]:
        st.markdown("### 📋 Historial de envíos esta sesión")
        for h in reversed(st.session_state["followup_historial"]):
            with st.expander(f"Bloque {h['bloque']} — {h['timestamp']} — {h['clientes']} clientes — {h['mes_filtro']}"):
                st.caption(f"Plantilla: {h['plantilla']}")
                if "resultados" in h:
                    for nombre_h, resultado_h in h["resultados"].items():
                        st.write(f"• {nombre_h}: **{resultado_h}**")
                else:
                    st.write(", ".join(h['nombres']))

    st.markdown("---")

    st.markdown("### 💬 Enviar mensaje individual")

    if not sin_servicio.empty:
        cliente_sel = st.selectbox(
            "Selecciona cliente:",
            sin_servicio.apply(lambda x: f"{x['Nombre']} - {x['Tel']}", axis=1)
        )

        nombre = cliente_sel.split(" - ")[0]
        telefono = cliente_sel.split(" - ")[1].replace("-", "").replace(" ", "")

        plantilla_ind = st.selectbox(
            "Selecciona plantilla",
            list(PLANTILLAS_MENSAJES.keys()),
            key="plantilla_individual"
        )

        mensaje_base = PLANTILLAS_MENSAJES[plantilla_ind]
        mensaje_generado = mensaje_base.format(
            nombre=nombre,
            empresa=st.session_state.get("empresa", "nuestro negocio")
        )

        mensaje = st.text_area("Mensaje", value=mensaje_generado)

        if telefono and telefono != "nan":
            telefono = "52" + telefono
            mensaje_encoded = urllib.parse.quote(mensaje)
            whatsapp_url = f"https://wa.me/{telefono}?text={mensaje_encoded}"
            st.link_button("Enviar mensaje por WhatsApp", whatsapp_url)
        else:
            st.warning("Cliente sin teléfono válido")
# CHATBOT
elif pagina == "Chat":
    st.title("🤖 Asistente del negocio")

    st.markdown("### 💡 Ejemplos de preguntas")
    st.markdown("""
    - ¿Cuánto vendí este mes?
    - ¿Cuánto vendí el mes pasado?
    - ¿Cuánto vendí en los últimos 3 meses?
    - ¿Cuánto vendí este año?
    - ¿Quién es mi mejor cliente?
    - ¿Qué clientes no han venido en 6 meses?
    - ¿Cuántos clientes tengo?
    """)

    pregunta = st.text_input("Haz una pregunta:")

    if pregunta:

        pregunta_lower = pregunta.lower()

        hoy = datetime.now()
        mes_actual = hoy.month
        año_actual = hoy.year

        # 💰 VENTAS ESTE MES
        if "este mes" in pregunta_lower:
            df_mes = df[
                (df["Mes"] == mes_actual) &
                (df["Año"] == año_actual)
            ]
            total = df_mes["Monto"].sum()
            st.success(f"Ventas este mes ({mes_actual}/{año_actual}): ${total:,.0f}")

        # 📅 MES PASADO
        elif "mes pasado" in pregunta_lower:
            if mes_actual == 1:
                mes = 12
                año = año_actual - 1
            else:
                mes = mes_actual - 1
                año = año_actual

            df_mes = df[
                (df["Mes"] == mes) &
                (df["Año"] == año)
            ]
            total = df_mes["Monto"].sum()
            st.success(f"Ventas mes pasado ({mes}/{año}): ${total:,.0f}")

        # 📊 ÚLTIMOS 3 MESES
        elif "3 meses" in pregunta_lower:
            fecha_limite = hoy - timedelta(days=90)

            df_3m = df.copy()
            df_3m["Fecha"] = pd.to_datetime(df_3m["Fecha"], errors="coerce")

            df_3m = df_3m[df_3m["Fecha"] >= fecha_limite]

            total = df_3m["Monto"].sum()
            st.success(f"Ventas últimos 3 meses: ${total:,.0f}")

        # 📆 ESTE AÑO
        elif "este año" in pregunta_lower:
            df_año = df[df["Año"] == año_actual]
            total = df_año["Monto"].sum()
            st.success(f"Ventas {año_actual}: ${total:,.0f}")

        # 💰 VENTAS GENERALES (fallback)
        elif "ventas" in pregunta_lower:
            df_año = df[df["Año"] == año_actual]
            total = df_año["Monto"].sum()
            st.success(f"Ventas {año_actual}: ${total:,.0f}")

        # 🏆 MEJOR CLIENTE
        elif "mejor cliente" in pregunta_lower:
            if not df.empty:
                agrupado = df.groupby("Nombre")["Monto"].sum()
                top = agrupado.idxmax()
                total_top = agrupado.max()
                st.success(f"Tu mejor cliente es {top} con ${total_top:,.0f}")
            else:
                st.warning("No hay datos disponibles")

        # 👥 TOTAL CLIENTES
        elif "clientes" in pregunta_lower and "perdidos" not in pregunta_lower:
            total_clientes = df["Nombre"].nunique()
            st.success(f"Tienes {total_clientes} clientes únicos")

        # 🔴 CLIENTES PERDIDOS
        elif "perdidos" in pregunta_lower or "no han venido" in pregunta_lower:

            df_lost = df.copy()
            df_lost["Fecha"] = pd.to_datetime(df_lost["Fecha"], errors="coerce")
            df_lost["Monto"] = pd.to_numeric(df_lost["Monto"], errors="coerce")

            ultimo = df_lost.groupby("Nombre").agg(
                Ultima_Visita=("Fecha", "max"),
                Total_Gastado=("Monto", "sum"),
                Tel=("Tel", "last")
            ).reset_index()

            ultimo["Meses_sin_servicio"] = ((hoy - ultimo["Ultima_Visita"]).dt.days / 30).round(1)

            perdidos = ultimo[ultimo["Meses_sin_servicio"] >= 6]

            if not perdidos.empty:
                st.dataframe(perdidos)
            else:
                st.success("No hay clientes perdidos 🎉")

        # ❌ NO ENTENDIDO
        else:
            st.warning("Aún no entiendo esa pregunta 😅")
    # AGENDA
elif pagina == "Agenda":
    st.title("📅 Agenda de Servicios")
    import urllib.parse
    from datetime import datetime, timedelta

    SHEET_IDS = USUARIOS[st.session_state["usuario"]].get("sheets", {})

    def get_supabase_auth():
        client_auth = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"]
        )
        client_auth.postgrest.auth(st.session_state.get("access_token", ""))
        return client_auth

    def limpiar_valor(val, default=""):
        if val is None:
            return default
        try:
            if pd.isna(val):
                return default
        except:
            pass
        return val

    def fecha_relativa(fecha):
        hoy = datetime.now().date()
        diff = (fecha - hoy).days
        dias_es = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        if diff == 0:
            return "hoy"
        elif diff == 1:
            return "mañana"
        elif diff == 2:
            return "pasado mañana"
        elif 3 <= diff <= 6:
            return f"el {dias_es[fecha.weekday()]}"
        else:
            return fecha.strftime("%d/%m/%Y")

    df_a = df.copy()
    df_a["Fecha"] = pd.to_datetime(df_a["Fecha"], errors="coerce")
    df_a["Monto"] = pd.to_numeric(df_a["Monto"], errors="coerce")
    df_a["ID Cliente"] = pd.to_numeric(df_a["ID Cliente"], errors="coerce")

    plantillas = USUARIOS[st.session_state["usuario"]].get("plantillas", {})
    empresa = st.session_state.get("empresa", "")

    fecha_sel = st.date_input("Selecciona una fecha", datetime.now(), key="agenda_fecha_1")
    df_dia = df_a[df_a["Fecha"].dt.date == fecha_sel]

    total_dia = df_dia["Monto"].sum()
    col1, col2 = st.columns(2)
    col1.metric("Servicios ese día", len(df_dia))
    col2.metric("Ingresos del día", f"${total_dia:,.0f}")
    st.markdown("---")

    if df_dia.empty:
        st.info("No hay servicios agendados para este día.")
    else:
        for _, row in df_dia.iterrows():
            with st.container():
                realizado = row.get("realizado", False)
                estado = "✅ Realizado" if realizado else "⏳ Pendiente"
                hora_str = limpiar_valor(row.get("hora"))
                fecha_row = row["Fecha"].date() if pd.notnull(row["Fecha"]) else None
                fecha_txt = fecha_relativa(fecha_row) if fecha_row else ""

                st.markdown(f"""
                **👤 Cliente:** {limpiar_valor(row.get('Nombre'))}  
                **🆔 ID:** {limpiar_valor(row.get('ID Cliente'))}  
                **📞 Tel:** {limpiar_valor(row.get('Tel'))}  
                **📍 Dirección:** {limpiar_valor(row.get('Dirección'))}  
                **🧼 Servicio:** {limpiar_valor(row.get('Servicio'))}  
                **📅 Fecha:** {fecha_txt}{f' a las {hora_str}' if hora_str else ''}  
                **💰 Monto:** ${row.get('Monto', 0) or 0:,.0f}  
                **Estado:** {estado}
                """)
                tel = str(row.get("Tel", "")).replace("-", "").replace(" ", "")
                if tel and tel != "nan":
                    tel_completo = "52" + tel
                    # Mensaje con fecha relativa
                    fecha_msg = fecha_relativa(fecha_row) if fecha_row else ""
                    hora_msg = f" a las {hora_str}" if hora_str else ""
                    mensaje_template = plantillas.get("confirmacion",
                        f"Hola {{nombre}}, confirmamos tu servicio con {{empresa}} para {fecha_msg}{hora_msg}.")
                    mensaje = mensaje_template.format(
                        nombre=limpiar_valor(row.get("Nombre")),
                        empresa=empresa,
                        fecha=fecha_msg,
                        hora=hora_msg
                    )
                    url = f"https://wa.me/{tel_completo}?text={urllib.parse.quote(mensaje)}"
                    st.markdown(f"[💬 Enviar WhatsApp]({url})")
                else:
                    st.warning("Cliente sin teléfono")
                st.markdown("---")

    st.markdown("### ➕ Agendar nuevo servicio")

    # ── BOTÓN VACIAR — key dinámico para limpiar el form ──
    if "form_key" not in st.session_state:
        st.session_state["form_key"] = 0

    if st.button("🗑️ Vaciar campos", key="vaciar_campos"):
        st.session_state["form_key"] += 1
        st.session_state["agenda_limpiar"] = True
        st.rerun()

    limpiar = st.session_state.pop("agenda_limpiar", False)

    clientes_info = df_a.groupby("ID Cliente").agg(
        Nombre=("Nombre", "last"),
        Telefonos=("Tel", lambda x: " / ".join(
            str(t) for t in x.dropna().unique()
            if str(t).strip() not in ["", "nan"]
        )),
        Direccion=("Dirección", "last"),
        Origen_ultimo=("Origen", "last")
    ).reset_index()
    clientes_info["ID Cliente"] = pd.to_numeric(clientes_info["ID Cliente"], errors="coerce")
    clientes_info = clientes_info.dropna(subset=["ID Cliente"])
    clientes_info["ID Cliente"] = clientes_info["ID Cliente"].astype(int)
    clientes_info = clientes_info.sort_values("Nombre")

    opciones_clientes = [""] + [
        f"[{int(row['ID Cliente'])}] {row['Nombre']}"
        for _, row in clientes_info.iterrows()
    ]

    cliente_sel = st.selectbox(
        "Cliente existente (opcional) — busca por nombre o ID",
        opciones_clientes,
        index=0,
        key=f"cliente_agenda_sel_{st.session_state['form_key']}"
    )

    tel_default = ""
    dir_default = ""
    id_cliente_default = None
    nombre_default = ""

    if cliente_sel and not limpiar:
        try:
            id_extraido = int(cliente_sel.split("]")[0].replace("[", "").strip())
            fila_cliente = clientes_info[clientes_info["ID Cliente"] == id_extraido]
            if not fila_cliente.empty:
                tel_default = fila_cliente.iloc[0]["Telefonos"]
                dir_default = str(fila_cliente.iloc[0]["Direccion"]) if pd.notnull(fila_cliente.iloc[0]["Direccion"]) else ""
                id_cliente_default = id_extraido
                nombre_default = fila_cliente.iloc[0]["Nombre"]
        except:
            pass

    ORIGENES = ["Rep", "Int", "Rec", "Face", "Amigo", "Club", "Maristas"]

    with st.form(f"agendar_servicio_{st.session_state['form_key']}"):
        nombre = st.text_input("Nombre del cliente", value=nombre_default)
        telefono = st.text_input("Teléfono(s)", value=tel_default)
        direccion = st.text_input("Dirección", value=dir_default)
        servicio = st.text_input("Servicio")
        origen_input = st.selectbox(
            "Origen",
            ORIGENES,
            index=0 if cliente_sel else 1
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            fecha = st.date_input("Fecha", datetime.now())
        with col2:
            hora = st.time_input("Hora", value=None)
        with col3:
            monto = st.number_input("Monto", min_value=0)

        submitted = st.form_submit_button("Agendar")

        if submitted:
            if not nombre.strip():
                st.error("El nombre del cliente es obligatorio.")
            else:
                try:
                    client_auth = get_supabase_auth()

                    # ── ID cliente correcto ──
                    id_cliente = None
                    if id_cliente_default and str(id_cliente_default) not in ["", "nan", "None"]:
                        id_cliente = int(id_cliente_default)
                    else:
                        # Buscar el max ID en Supabase para asignar el siguiente
                        max_id_resp = client_auth.table("clientes")\
                            .select("cliente_id")\
                            .eq("empresa_id", st.session_state["empresa_id"])\
                            .not_.is_("cliente_id", "null")\
                            .order("cliente_id", desc=True)\
                            .limit(1)\
                            .execute()
                        if max_id_resp.data and max_id_resp.data[0]["cliente_id"]:
                            id_cliente = int(max_id_resp.data[0]["cliente_id"]) + 1
                        else:
                            id_cliente = 1

                    hora_str = hora.strftime("%H:%M") if hora else None

                    client_auth.table("clientes").insert({
                        "empresa_id": st.session_state["empresa_id"],
                        "cliente_id": id_cliente,
                        "nombre": nombre,
                        "tel": telefono,
                        "direccion": direccion,
                        "servicio": servicio,
                        "fecha": fecha.isoformat(),
                        "monto": float(monto),
                        "origen": origen_input,
                        "año": fecha.year,
                        "realizado": False,
                        "hora": hora_str
                    }).execute()

                    fecha_txt = fecha_relativa(fecha)
                    hora_txt = f" a las {hora_str}" if hora_str else ""
                    st.success(f"✅ Servicio agendado para {nombre} (ID: {id_cliente}) — {fecha_txt}{hora_txt}")
                    st.cache_data.clear()
                    if "evento_seleccionado" in st.session_state:
                        del st.session_state["evento_seleccionado"]
                    import time as t
                    t.sleep(1)
                    st.rerun()

                except Exception as e:
                    st.error(f"Error al agendar: {e}")

    st.markdown("---")

    from streamlit_calendar import calendar

    st.markdown("### 📅 Calendario de servicios")

    df_cal = df_a[df_a["Fecha"].dt.year >= 2021].copy()
    df_cal = df_cal.dropna(subset=["Fecha"])

    eventos = []
    for _, row in df_cal.iterrows():
        realizado = row.get("realizado", False)
        color = "#2B5BAA" if realizado else "#F59E0B"
        hora_ev = limpiar_valor(row.get("hora"))
        titulo = f"{'✅' if realizado else '⏳'} {limpiar_valor(row.get('Nombre'))} — {limpiar_valor(row.get('Servicio'))}"
        if hora_ev:
            titulo += f" ({hora_ev})"
        eventos.append({
            "title": titulo,
            "start": row["Fecha"].strftime("%Y-%m-%d"),
            "end": row["Fecha"].strftime("%Y-%m-%d"),
            "backgroundColor": color,
            "borderColor": color,
            "extendedProps": {
                "id": str(row.get("id", "")),
            }
        })

    opciones_calendario = {
        "initialView": "dayGridMonth",
        "locale": "es",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,listWeek"
        },
        "height": 600,
    }

    resultado_cal = calendar(
        events=eventos,
        options=opciones_calendario,
        key=f"calendario_principal_{st.session_state.get('agenda_refresh', 0)}"
    )

    if resultado_cal and resultado_cal.get("eventClick"):
        evento_click = resultado_cal["eventClick"]["event"]
        id_click = evento_click.get("extendedProps", {}).get("id")
        if id_click:
            st.session_state["evento_seleccionado"] = {"id": id_click}

    if "evento_seleccionado" in st.session_state:
        ev = st.session_state["evento_seleccionado"]
        id_click = ev["id"]

        df_evento = df_cal[df_cal["id"].astype(str) == str(id_click)]

        if not df_evento.empty:
            row = df_evento.iloc[0]
            realizado = row.get("realizado", False)
            hora_row = limpiar_valor(row.get("hora"))
            fecha_row = row["Fecha"].date() if pd.notnull(row["Fecha"]) else None
            fecha_txt = fecha_relativa(fecha_row) if fecha_row else ""

            st.markdown("---")
            st.markdown("### 📋 Detalle del servicio")

            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"""
                **👤 Cliente:** {limpiar_valor(row.get('Nombre'))}  
                **🆔 ID:** {limpiar_valor(row.get('ID Cliente'))}  
                **📞 Tel:** {limpiar_valor(row.get('Tel'))}  
                **📍 Dirección:** {limpiar_valor(row.get('Dirección'))}  
                **🧼 Servicio:** {limpiar_valor(row.get('Servicio'))}  
                **📅 Fecha:** {fecha_txt}{f' a las {hora_row}' if hora_row else ''}  
                **💰 Monto:** ${row.get('Monto', 0) or 0:,.0f}  
                **🔍 Origen:** {limpiar_valor(row.get('Origen'))}  
                **💬 Comentarios:** {limpiar_valor(row.get('Comentarios con llamada posterior a venta'))}  
                **Estado:** {'✅ Realizado' if realizado else '⏳ Pendiente'}
                """)
            with col2:
                if st.button("✖ Cerrar detalle", use_container_width=True):
                    del st.session_state["evento_seleccionado"]
                    st.rerun()

            tel_ev = str(row.get("Tel", "")).replace("-", "").replace(" ", "")
            if tel_ev and tel_ev not in ["nan", ""]:
                tel_ev = "52" + tel_ev
                hora_msg = f" a las {hora_row}" if hora_row else ""
                mensaje_confirmacion = f"Hola {limpiar_valor(row.get('Nombre'))}, confirmamos tu servicio con {empresa} para {fecha_txt}{hora_msg}."
                url = f"https://wa.me/{tel_ev}?text={urllib.parse.quote(mensaje_confirmacion)}"
                st.markdown(f"[💬 Enviar recordatorio]({url})")

            # ── MARCAR COMO REALIZADO ──
            if not realizado:
                if st.button("✅ Marcar como realizado y guardar en Sheets", use_container_width=True, type="primary"):
                    try:
                        client_auth = get_supabase_auth()
                        client_auth.table("clientes").update({
                            "realizado": True
                        }).eq("id", id_click).execute()

                        año_row = int(row.get("Año", row["Fecha"].year))
                        if año_row in SHEET_IDS:
                            client_gs = get_gspread_client()
                            sheet_id = SHEET_IDS[año_row]
                            sh = client_gs.open_by_key(sheet_id)
                            worksheet = sh.get_worksheet(0)

                            col_b = worksheet.col_values(2)
                            ultimo_folio = 0
                            for v in col_b[1:]:
                                try:
                                    num = int(str(v).strip().split("/")[0])
                                    if num < 10000:
                                        ultimo_folio = max(ultimo_folio, num)
                                except:
                                    continue

                            siguiente_folio = ultimo_folio + 1
                            folio_interno = f"{siguiente_folio}/{str(año_row)[-2:]}"

                            origen_real = limpiar_valor(row.get("Origen"), "Int")
                            if origen_real.lower() in ["agenda", ""]:
                                origen_real = "Int"

                            id_cli = row.get("ID Cliente")
                            id_cli_limpio = int(id_cli) if id_cli and str(id_cli) not in ["", "nan", "None"] and pd.notnull(id_cli) else ""

                            # Verde SOLO si origen es Rep
                            es_rep = origen_real.lower() == "rep"

                            # Rojo si comentarios negativos
                            comentario = limpiar_valor(row.get("Comentarios con llamada posterior a venta"), "").lower()
                            cliente_no_contactar = any(p in comentario for p in [
                                "no se llama", "no contactar", "no vuelve", "cliente no deseable", "muy mal"
                            ])

                            nueva_fila = [
                                siguiente_folio,
                                folio_interno,
                                row["Fecha"].strftime("%m/%d/%Y"),
                                id_cli_limpio,
                                limpiar_valor(row.get("Nombre")),
                                limpiar_valor(row.get("Tel")),
                                limpiar_valor(row.get("Dirección")),
                                origen_real,
                                float(row.get("Monto", 0)) if pd.notnull(row.get("Monto", 0)) else 0,
                                limpiar_valor(row.get("Servicio")),
                                limpiar_valor(row.get("Comentarios con llamada posterior a venta")),
                                "", "", ""
                            ]

                            col_c = worksheet.col_values(3)
                            datos_col_c = col_c[1:]
                            primera_vacia = None
                            for i, v in enumerate(datos_col_c):
                                if str(v).strip() == "":
                                    primera_vacia = i + 2
                                    break
                            if primera_vacia is None:
                                primera_vacia = len(datos_col_c) + 2

                            worksheet.insert_row(nueva_fila, primera_vacia)

                            if cliente_no_contactar:
                                worksheet.format(f"A{primera_vacia}", {
                                    "backgroundColor": {"red": 0.9, "green": 0.2, "blue": 0.2}
                                })
                            elif es_rep:
                                worksheet.format(f"A{primera_vacia}", {
                                    "backgroundColor": {"red": 0.2, "green": 0.8, "blue": 0.2}
                                })

                            st.success("✅ Servicio marcado como realizado y guardado en Sheets.")
                        else:
                            st.success("✅ Marcado como realizado. No hay sheet configurado para este año.")

                        st.cache_data.clear()
                        del st.session_state["evento_seleccionado"]
                        st.session_state["agenda_refresh"] = st.session_state.get("agenda_refresh", 0) + 1
                        import time as t
                        t.sleep(1)
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.success("✅ Este servicio ya fue realizado y guardado en Sheets.")

            # ── EDITAR DATOS ──
            st.markdown("#### ✏️ Editar datos del servicio")
            with st.form("editar_servicio_form"):
                edit_nombre = st.text_input("Nombre", value=limpiar_valor(row.get("Nombre")))
                edit_tel = st.text_input("Teléfono", value=limpiar_valor(row.get("Tel")))
                edit_dir = st.text_input("Dirección", value=limpiar_valor(row.get("Dirección")))
                edit_servicio = st.text_input("Servicio", value=limpiar_valor(row.get("Servicio")))
                edit_monto = st.number_input(
                    "Monto", min_value=0,
                    value=int(row.get("Monto", 0)) if pd.notnull(row.get("Monto", 0)) else 0
                )
                origen_actual = limpiar_valor(row.get("Origen"), "Int")
                edit_origen = st.selectbox(
                    "Origen", ORIGENES,
                    index=ORIGENES.index(origen_actual) if origen_actual in ORIGENES else 1
                )
                guardar_edicion = st.form_submit_button("💾 Guardar cambios", use_container_width=True)

                if guardar_edicion:
                    try:
                        client_auth = get_supabase_auth()
                        client_auth.table("clientes").update({
                            "nombre": edit_nombre,
                            "tel": edit_tel,
                            "direccion": edit_dir,
                            "servicio": edit_servicio,
                            "monto": float(edit_monto),
                            "origen": edit_origen
                        }).eq("id", id_click).execute()

                        st.success("✅ Servicio actualizado correctamente.")
                        st.cache_data.clear()
                        del st.session_state["evento_seleccionado"]
                        st.session_state["agenda_refresh"] = st.session_state.get("agenda_refresh", 0) + 1
                        import time as t
                        t.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al editar: {e}")

            # ── EDITAR FECHA Y HORA ──
            st.markdown("#### 📅 Corregir fecha y hora del servicio")
            with st.form("editar_fecha_form"):
                col1, col2 = st.columns(2)
                with col1:
                    nueva_fecha = st.date_input("Nueva fecha:", value=row["Fecha"].date())
                with col2:
                    nueva_hora = st.time_input("Nueva hora:", value=None)
                confirmar_edicion = st.form_submit_button("📅 Cambiar fecha/hora", use_container_width=True)

                if confirmar_edicion:
                    try:
                        client_auth = get_supabase_auth()
                        nueva_hora_str = nueva_hora.strftime("%H:%M") if nueva_hora else None
                        client_auth.table("clientes").update({
                            "fecha": nueva_fecha.isoformat(),
                            "año": nueva_fecha.year,
                            "hora": nueva_hora_str
                        }).eq("id", id_click).execute()

                        st.success(f"✅ Fecha cambiada a {nueva_fecha.strftime('%d/%m/%Y')}")
                        st.cache_data.clear()
                        del st.session_state["evento_seleccionado"]
                        st.session_state["agenda_refresh"] = st.session_state.get("agenda_refresh", 0) + 1
                        import time as t
                        t.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al cambiar fecha: {e}")

            # ── ELIMINAR ──
            st.markdown("#### 🗑️ Eliminar servicio")
            with st.form("borrar_form"):
                st.warning("Esta acción no se puede deshacer.")
                confirmar_borrado = st.checkbox("Confirmo que quiero eliminar este servicio")
                borrar_btn = st.form_submit_button("🗑️ Eliminar", use_container_width=True)

                if borrar_btn:
                    if not confirmar_borrado:
                        st.error("Marca la casilla de confirmación antes de eliminar.")
                    else:
                        try:
                            client_auth = get_supabase_auth()
                            client_auth.table("clientes").delete().eq("id", id_click).execute()
                            st.success("✅ Servicio eliminado correctamente.")
                            st.cache_data.clear()
                            del st.session_state["evento_seleccionado"]
                            st.session_state["agenda_refresh"] = st.session_state.get("agenda_refresh", 0) + 1
                            import time as t
                            t.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al eliminar: {e}")
        else:
            st.warning("No se encontró el servicio seleccionado.")
            if st.button("Limpiar selección"):
                del st.session_state["evento_seleccionado"]
                st.rerun()
    # ── COTIZACIONES ──
elif pagina == "Cotizaciones":
    import base64
    import streamlit.components.v1 as components

    st.title("Cotizador de Servicios")

    cotizador = USUARIOS[st.session_state["usuario"]].get("cotizador", {})

    PAQUETES = cotizador.get("paquetes", [])
    MINIMO = cotizador.get("minimo", 0)
    PRECIOS = cotizador.get("precios", {})
    SERVICIOS_CON_CANTIDAD = cotizador.get("servicios_cantidad", [])
    SERVICIOS_CON_PLAZAS = cotizador.get("servicios_plazas", [])
    SERVICIOS_CON_SILLAS = cotizador.get("servicios_sillas", [])
    INTRO = cotizador.get("intro", "")
    PURT_DESC = cotizador.get("purt_descripcion", "")
    PURT_COSTO = cotizador.get("purt_costo", 0)
    DESC_PAQUETES = cotizador.get("descripcion_paquetes", {})
    DESCUENTOS = cotizador.get("descuentos_paquete", {})
    CIERRE = cotizador.get("cierre", "")
    FIRMA = cotizador.get("firma", "")

    if not PAQUETES or not PRECIOS:
        st.info("Este usuario no tiene cotizador configurado.")
        st.stop()

    st.markdown("### Agregar servicios a la cotización")

    if "items_cotizacion" not in st.session_state:
        st.session_state["items_cotizacion"] = []

    col1, col2 = st.columns([3, 1])

    with col1:
        servicio = st.selectbox("Servicio:", list(PRECIOS.keys()))

    with col2:
        if servicio in SERVICIOS_CON_CANTIDAD:
            cantidad = st.number_input("m2:", min_value=1, value=1)
            label_cantidad = "m2"
        elif servicio in SERVICIOS_CON_PLAZAS:
            cantidad = st.number_input("Plazas:", min_value=1, value=1)
            label_cantidad = "plazas"
        elif servicio in SERVICIOS_CON_SILLAS:
            cantidad = st.number_input("Sillas:", min_value=1, value=1)
            label_cantidad = "sillas"
        else:
            cantidad = 1
            label_cantidad = "unidad"

    precio_data = {
        "Paquete": PAQUETES,
        "Precio": [f"${PRECIOS[servicio][p] * cantidad:,.0f}" for p in PAQUETES]
    }
    st.dataframe(pd.DataFrame(precio_data), use_container_width=True, hide_index=True)

    if st.button("Agregar a cotización", use_container_width=True):
        st.session_state["items_cotizacion"].append({
            "Servicio": servicio,
            "Cantidad": cantidad,
            "Label": label_cantidad,
            "Precios": {p: PRECIOS[servicio][p] * cantidad for p in PAQUETES}
        })

    if st.session_state["items_cotizacion"]:
        st.markdown("---")
        st.markdown("### Resumen — todos los paquetes")

        filas = []
        for item in st.session_state["items_cotizacion"]:
            fila = {"Servicio": f"{item['Servicio']} ({item['Cantidad']} {item['Label']})"}
            for p in PAQUETES:
                fila[p] = f"${item['Precios'][p]:,.0f}"
            filas.append(fila)

        totales = {"Servicio": "TOTAL"}
        for p in PAQUETES:
            total_p = sum(i["Precios"][p] for i in st.session_state["items_cotizacion"])
            descuento = DESCUENTOS.get(p, 0)
            total_con_descuento = total_p * (1 - descuento / 100)
            total_final = max(total_con_descuento, MINIMO)
            nota = " *" if total_p < MINIMO else ""
            totales[p] = f"${total_final:,.0f}{nota}"

        filas.append(totales)
        st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)

        # ── MENSAJE PROFESIONAL ──
        st.markdown("### Mensaje para cliente")

        nombre_cliente = st.text_input("Nombre del cliente (opcional):")
        incluir_purt = st.checkbox("Incluir descripción de PURT", value=bool(PURT_DESC))

        lineas = []

        if nombre_cliente:
            lineas.append(f"Estimado/a {nombre_cliente},\n")

        if INTRO:
            lineas.append(INTRO)
            lineas.append("")

        if incluir_purt and PURT_DESC:
            lineas.append(PURT_DESC)
            lineas.append("")

        lineas.append("El servicio de acuerdo a su solicitud tiene una inversión de:\n")

        for p in PAQUETES:
            total_p = sum(i["Precios"][p] for i in st.session_state["items_cotizacion"])
            descuento = DESCUENTOS.get(p, 0)
            total_con_descuento = total_p * (1 - descuento / 100)
            total_final = max(total_con_descuento, MINIMO)

            lineas.append(f"Paquete {p}:")
            if p in DESC_PAQUETES:
                lineas.append(DESC_PAQUETES[p])

            for item in st.session_state["items_cotizacion"]:
                lineas.append(f"{item['Servicio']} ({item['Cantidad']} {item['Label']}): ${item['Precios'][p]:,.0f}")

            if incluir_purt and PURT_COSTO > 0:
                lineas.append(f"PURT: ${PURT_COSTO:,.0f}")

            if descuento > 0:
                lineas.append(f"Descuento por volumen {descuento}%")

            lineas.append(f"TOTAL: ${total_final:,.0f}")
            lineas.append("")

        if CIERRE:
            lineas.append(CIERRE)

        if FIRMA:
            lineas.append(FIRMA)

        st.text_area("Copia este mensaje:", "\n".join(lineas), height=400)

        # ── PDF ──
        st.markdown("### 📄 Descargar cotización")

        nombre_pdf = nombre_cliente if nombre_cliente else "Cliente"
        fecha_pdf = datetime.now().strftime("%d/%m/%Y")
        empresa_pdf = st.session_state.get("empresa", "")

        filas_pdf = ""
        for p in PAQUETES:
            total_p = sum(i["Precios"][p] for i in st.session_state["items_cotizacion"])
            descuento = DESCUENTOS.get(p, 0)
            total_con_descuento = total_p * (1 - descuento / 100)
            total_final = max(total_con_descuento, MINIMO)

            servicios_html = ""
            for item in st.session_state["items_cotizacion"]:
                servicios_html += f"""
                <tr>
                    <td style='padding:6px 12px; border-bottom:1px solid #eee;'>
                        {item['Servicio']} ({item['Cantidad']} {item['Label']})
                    </td>
                    <td style='padding:6px 12px; text-align:right; border-bottom:1px solid #eee;'>
                        ${item['Precios'][p]:,.0f}
                    </td>
                </tr>
                """

            if incluir_purt and PURT_COSTO > 0:
                servicios_html += f"""
                <tr>
                    <td style='padding:6px 12px; border-bottom:1px solid #eee;'>PURT</td>
                    <td style='padding:6px 12px; text-align:right; border-bottom:1px solid #eee;'>
                        ${PURT_COSTO:,.0f}
                    </td>
                </tr>
                """

            if descuento > 0:
                servicios_html += f"""
                <tr>
                    <td style='padding:6px 12px; border-bottom:1px solid #eee; color:#888;'>
                        Descuento {descuento}%
                    </td>
                    <td style='padding:6px 12px; text-align:right; border-bottom:1px solid #eee; color:#888;'>
                        -${total_p * descuento / 100:,.0f}
                    </td>
                </tr>
                """

            desc_paquete_html = f"<p style='color:#555; font-size:13px; margin:4px 0 8px 0;'>{DESC_PAQUETES[p]}</p>" if p in DESC_PAQUETES else ""

            filas_pdf += f"""
            <div style="margin-bottom:24px; border:1px solid #ddd; border-radius:8px; overflow:hidden;">
                <div style="background:#2B5BAA; color:white; padding:10px 16px; font-weight:bold; font-size:15px;">
                    Paquete {p}
                </div>
                <div style="padding:8px 12px;">
                    {desc_paquete_html}
                </div>
                <table style="width:100%; border-collapse:collapse; font-size:14px;">
                    {servicios_html}
                    <tr style="background:#f0f4ff;">
                        <td style="padding:10px 12px; font-weight:bold;">TOTAL</td>
                        <td style="padding:10px 12px; text-align:right; font-weight:bold; font-size:16px;">
                            ${total_final:,.0f}
                        </td>
                    </tr>
                </table>
            </div>
            """

        intro_html = f"<p style='margin-bottom:16px;'>{INTRO}</p>" if INTRO else ""
        purt_html = f"<p style='margin-bottom:16px; color:#555;'>{PURT_DESC}</p>" if (incluir_purt and PURT_DESC) else ""
        cierre_html = f"<p style='margin-top:8px;'>{CIERRE}</p>" if CIERRE else ""
        firma_html = f"<p style='margin-top:4px; color:#555;'>{FIRMA}</p>" if FIRMA else ""

        html_pdf = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Cotización — {nombre_pdf}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    padding: 48px;
                    max-width: 680px;
                    margin: auto;
                    color: #333;
                    font-size: 14px;
                }}
                h1 {{ color: #2B5BAA; margin-bottom: 4px; font-size: 28px; }}
                .meta {{ color: #666; font-size: 13px; margin-bottom: 24px; line-height: 1.8; }}
                .divider {{ border: none; border-top: 1px solid #eee; margin: 24px 0; }}
                .footer {{ margin-top: 40px; font-size: 13px; color: #888;
                           border-top: 1px solid #eee; padding-top: 16px; }}
                @media print {{
                    body {{ padding: 24px; }}
                }}
            </style>
        </head>
        <body>
            <h1>Cotización de servicios</h1>
            <div class="meta">
                <strong>Para:</strong> {nombre_pdf}<br>
                <strong>De:</strong> {empresa_pdf}<br>
                <strong>Fecha:</strong> {fecha_pdf}
            </div>

            <hr class="divider">

            {intro_html}
            {purt_html}

            <p style="margin-bottom:20px;">
                El servicio de acuerdo a su solicitud tiene una inversión de:
            </p>

            {filas_pdf}

            <div class="footer">
                {cierre_html}
                {firma_html}
            </div>
        </body>
        </html>
        """

        b64_pdf = base64.b64encode(html_pdf.encode("utf-8")).decode("utf-8")
        nombre_archivo = f"cotizacion_{nombre_pdf.replace(' ', '_')}_{datetime.now().strftime('%d%m%Y')}.html"

        components.html(f"""
        <a href="data:text/html;base64,{b64_pdf}"
           download="{nombre_archivo}"
           style="
               display:block;
               background-color:#2B5BAA;
               color:white;
               text-decoration:none;
               text-align:center;
               border-radius:8px;
               padding:14px 24px;
               font-size:16px;
               font-family:Arial, sans-serif;
               margin-top:8px;
           ">
            📄 Descargar cotización
        </a>
        """, height=65)

        st.caption("Se descarga como archivo HTML. Ábrelo en el navegador y usa Cmd+P / Ctrl+P → Guardar como PDF.")

        st.markdown("---")

        if st.button("Limpiar cotización", use_container_width=True):
            st.session_state["items_cotizacion"] = []
            st.rerun()