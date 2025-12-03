import streamlit as st
import pandas as pd
from core.api.cum_api import load_cum_full
from core.supply.supply import (
    normalize_cum,
    get_discontinued,
    get_possible_shortages,
    labs_per_nit,
    supply_overview
)

st.set_page_config(page_title="CUM Intelligence Platform", layout="wide")

st.title("🧠 CUM Intelligence Platform")
st.write("Analítica avanzada del CUM — Colombia 🇨🇴")

@st.cache_data(show_spinner=True)
def load_data():
    df = load_cum_full()
    df = normalize_cum(df)
    return df

st.header("📥 Cargando datos del CUM...")
df = load_data()

st.success("Datos cargados correctamente!")

# --- PANEL PRINCIPAL ---
st.header("📊 Supply Overview — Información General")
overview = supply_overview(df)
st.json(overview)

# --- DESCONTINUADOS ---
st.header("❌ Medicamentos Descontinuados")
disc = get_discontinued(df)
st.dataframe(disc)

# --- RIESGO DE DESABASTECIMIENTO ---
st.header("⚠ Riesgos de Abastecimiento")
shortage = get_possible_shortages(df)
st.dataframe(shortage)

# --- LABORATORIOS ÚNICOS POR NIT ---
st.header("🏭 Laboratorios únicos por NIT")
labs = labs_per_nit(df)
st.dataframe(labs)
