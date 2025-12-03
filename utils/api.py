import requests
import pandas as pd

BASE_URL = "https://www.datos.gov.co/api/v3/views/i7cb-raxc/query.json"


def get_cum_page(limit=5000, offset=0):
    """
    Descarga una página de datos del CUM vía API.
    """
    params = {
        "limit": limit,
        "offset": offset
    }

    r = requests.get(BASE_URL, params=params)

    if r.status_code != 200:
        raise Exception(f"Error API {r.status_code}: {r.text}")

    data = r.json()

    # Extraer datos y metadatos
    rows = data.get("data", [])
    meta_cols = data.get("meta", {}).get("view", {}).get("columns", [])
    colnames = [c["name"] for c in meta_cols]

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df.columns = colnames[:len(df.columns)]

    return df


def get_full_cum():
    """
    Descarga TODO el CUM usando paginación
    """
    all_data = []
    offset = 0
    limit = 5000

    while True:
        df = get_cum_page(limit=limit, offset=offset)
        if df.empty:
            break

        all_data.append(df)
        offset += limit

    full_df = pd.concat(all_data, ignore_index=True)
    return full_df
