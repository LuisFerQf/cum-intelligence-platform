"""
Módulo Enterprise para conexión al CUM
Incluye:
- Descarga paginada optimizada
- Normalización de columnas
- Validación de respuesta
- Estructura base para procesamientos futuros
"""

import requests
import pandas as pd

BASE_URL = "https://www.datos.gov.co/api/v3/views/i7cb-raxc/query.json"


def fetch_page(limit=5000, offset=0):
    """Descarga una página del CUM desde la API oficial."""
    params = {"limit": limit, "offset": offset}

    response = requests.get(BASE_URL, params=params, timeout=30)

    if response.status_code != 200:
        raise Exception(f"Error API {response.status_code}: {response.text}")

    json_data = response.json()

    rows = json_data.get("data", [])
    meta_cols = json_data.get("meta", {}).get("view", {}).get("columns", [])
    colnames = [c["name"] for c in meta_cols]

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df.columns = colnames[:len(df.columns)]
    return df


def load_cum_full():
    """Descarga TODO el CUM usando paginación optimizada."""
    frames = []
    offset = 0
    limit = 5000

    while True:
        df = fetch_page(limit=limit, offset=offset)
        if df.empty:
            break
        frames.append(df)
        offset += limit

    full_df = pd.concat(frames, ignore_index=True)

    return full_df
