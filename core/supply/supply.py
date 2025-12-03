"""
Supply Intelligence Module
Este módulo analiza el CUM para detectar:
- Descontinuados
- Posibles desabastecidos (señales)
- Concentración de fabricantes
- Cantidad de laboratorios únicos por NIT
- Indicadores de riesgo de suministro
"""

import pandas as pd


def normalize_cum(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza columnas clave del CUM para análisis posterior."""
    cols = {c.lower().replace(" ", "_") for c in df.columns}

    df.columns = [c.lower().replace(" ", "_") for c in df.columns]

    # Convertir campos clave a mayúsculas para análisis limpio
    text_cols = ["nombre_comercial", "principio_activo", "descripcion_atc"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.upper()

    return df


# ------------------------------------------------------------------------
# 1. Medicamentos descontinuados en Colombia
# ------------------------------------------------------------------------
def get_discontinued(df: pd.DataFrame):
    """Retorna medicamentos marcados como DESCONTINUADOS."""
    if "estado_registro" not in df.columns:
        return pd.DataFrame()

    mask = df["estado_registro"].str.contains("DESCONTINU", na=True)

    return df[mask]


# ------------------------------------------------------------------------
# 2. Señales de posible desabastecimiento
#    (esto es un modelo preliminar)
# ------------------------------------------------------------------------
def get_possible_shortages(df: pd.DataFrame):
    """
    Señales basadas en criterios:
    - Solo 1 fabricante (riesgo alto)
    - Solo 1 titular
    - Fecha de vencimiento del registro próxima
    """

    risks = []

    # 1. Riesgo por fabricante único
    if {"titular", "principio_activo"}.issubset(df.columns):
        uniq = (
            df.groupby("principio_activo")["titular"]
            .nunique()
            .reset_index(name="n_titulares")
        )

        uniq["riesgo_fabricante_unico"] = uniq["n_titulares"].apply(
            lambda x: "ALTO" if x == 1 else "MODERADO" if x == 2 else "BAJO"
        )
        risks.append(uniq)

    # 2. Riesgo por titular único
    if {"titular", "cum"}.issubset(df.columns):
        titular_cum = (
            df.groupby("titular")["cum"]
            .nunique()
            .reset_index(name="productos_asociados")
        )
        risks.append(titular_cum)

    # Unirlos
    if len(risks) > 0:
        final = risks[0]
        for r in risks[1:]:
            final = final.merge(r, how="left")
        return final

    return pd.DataFrame()


# ------------------------------------------------------------------------
# 3. Laboratorios únicos por NIT
# ------------------------------------------------------------------------
def labs_per_nit(df: pd.DataFrame):
    """
    Retorna cuántos laboratorios únicos existen por NIT en Colombia.
    """
    if {"titular", "identificacion_titular"}.issubset(df.columns) is False:
        return pd.DataFrame()

    return (
        df.groupby("identificacion_titular")["titular"]
        .nunique()
        .reset_index(name="laboratorios_unicos")
        .sort_values("laboratorios_unicos", ascending=False)
    )


# ------------------------------------------------------------------------
# 4. Resumen resumido de suministro (nivel país)
# ------------------------------------------------------------------------
def supply_overview(df: pd.DataFrame):
    """Resumen para tablero Streamlit."""

    resumen = {
        "total_presentaciones": len(df),
        "principios_activos_unicos": df["principio_activo"].nunique()
        if "principio_activo" in df.columns else None,
        "laboratorios_unicos": df["titular"].nunique()
        if "titular" in df.columns else None,
        "porcentaje_descontinuados": round(
            100 * len(get_discontinued(df)) / len(df), 2
        ),
    }

    return resumen
