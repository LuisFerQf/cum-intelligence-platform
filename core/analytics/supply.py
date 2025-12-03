"""
Módulo analítico: Oferta, riesgo y desabastecimiento del mercado farmacéutico colombiano.
Autor: LuisFerQf – Cum Intelligence Platform
"""

import pandas as pd


def compute_lab_count(df):
    """Cuenta cuántos laboratorios fabrican cada principio activo."""
    return (
        df.groupby("PRINCIPIO ACTIVO")["NOMBRE DEL TITULAR"]
        .nunique()
        .reset_index(name="NUM_LABORATORIOS")
    )


def detect_monopolies(df):
    """Identifica moléculas con 1 solo laboratorio (riesgo alto)."""
    labs = compute_lab_count(df)
    return labs[labs["NUM_LABORATORIOS"] == 1]


def atc_risk_map(df):
    """Evalúa riesgo por grupo ATC."""
    risk = (
        df.groupby("CÓDIGO ATC")["NOMBRE DEL TITULAR"]
        .nunique()
        .reset_index(name="NUM_LABORATORIOS")
    )
    
    risk["RIESGO_ATC"] = pd.cut(
        risk["NUM_LABORATORIOS"],
        bins=[0, 1, 3, 10, 1000],
        labels=["CRÍTICO", "ALTO", "MEDIO", "BAJO"]
    )
    
    return risk


def discontinued_products(df):
    """Identifica productos discontinuados por estado INVIMA."""
    estados_cierre = [
        "VENCIDO",
        "NO RENOVADO",
        "CANCELADO",
        "DESCONTINUADO"
    ]
    mask = df["ESTADO REGISTRO"].str.upper().isin(estados_cierre)
    return df[mask]


def supply_concentration(df):
    """Ranking de laboratorios más dominantes."""
    return (
        df["NOMBRE DEL TITULAR"]
        .value_counts()
        .reset_index(name="NUM_PRODUCTOS")
        .rename(columns={"index": "LABORATORIO"})
    )


def atc_distribution(df):
    """Distribución de número de productos por ATC."""
    return (
        df["CÓDIGO ATC"]
        .value_counts()
        .reset_index(name="NUM_PRODUCTOS")
        .rename(columns={"index": "ATC"})
    )
