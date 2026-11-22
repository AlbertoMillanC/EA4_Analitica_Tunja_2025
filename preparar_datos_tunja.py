import json
import pandas as pd
import numpy as np

PATH_2025 = r"C:\Users\BUNANDUN\Desktop\4_SOLICITUD_CAMARA_COMERCIO_TUNJA_CODIGO_15001_ACTIVOS_2025.xlsx"
SHEET_2025 = "BASE_DETALLADA_15001_2025"

MACRO_RUBROS = {
    "G": "Comercio (Mayor y Menor)",
    "I": "Gastronomía y Hotelería",
    "C": "Industria y Manufactura",
    "S": "Servicios Personales y al Usuario",
    "R": "Servicios Personales y al Usuario",
    "T": "Servicios Personales y al Usuario",
    "M": "Servicios Profesionales y Empresariales",
    "N": "Servicios Profesionales y Empresariales",
    "J": "Servicios Profesionales y Empresariales",
    "K": "Servicios Profesionales y Empresariales",
    "L": "Servicios Profesionales y Empresariales",
    "F": "Construcción e Infraestructura",
    "Q": "Salud y Educación",
    "P": "Salud y Educación",
    "H": "Transporte y Logística",
    "A": "Agropecuario, Minería y Serv. Públicos",
    "B": "Agropecuario, Minería y Serv. Públicos",
    "D": "Agropecuario, Minería y Serv. Públicos",
    "E": "Agropecuario, Minería y Serv. Públicos",
    "O": "Agropecuario, Minería y Serv. Públicos",
}

def clean_barrio(val) -> str:
    if pd.isna(val) or not str(val).strip():
        return "SIN BARRIO"
    s = str(val).strip()
    if " - " in s:
        s = s.split(" - ", 1)[1].strip()
    return s.upper()

def map_tramo_antiguedad(anio) -> str:
    if pd.isna(anio):
        return "Sin fecha"
    a = int(anio)
    if a >= 2021:
        return "Recientes (2021–2025)"
    if a >= 2016:
        return "En crecimiento (2016–2020)"
    if a >= 2011:
        return "Consolidadas (2011–2015)"
    return "Históricas (≤ 2010)"

def main():
    print("Leyendo base 2025 de Cámara de Comercio de Tunja...")
    df = pd.read_excel(PATH_2025, sheet_name=SHEET_2025, engine="openpyxl")
    brutos = len(df)

    # 1. Filtrar solo Matrículas Activas (MA)
    df["ESTADO_CLEAN"] = df["ESTADO"].astype(str).str.strip()
    inactivos_count = int((df["ESTADO_CLEAN"] != "MA").sum())
    df_ma = df[df["ESTADO_CLEAN"] == "MA"].copy()

    # 2. Excluir Establecimientos (pertenecen a una Persona Natural o Jurídica)
    df_ma["ORG_CLEAN"] = df_ma["ORGANIZACIÓN"].astype(str).str.strip()
    establecimientos_count = int((df_ma["ORG_CLEAN"] == "Establecimiento").sum())
    df_emp = df_ma[df_ma["ORG_CLEAN"] != "Establecimiento"].copy()

    # 3. Clasificar en Persona Natural vs. Persona Jurídica (incluye ESAL, Sociedades, Solidaria, etc.)
    clean = pd.DataFrame(index=df_emp.index)
    clean["anio_corte"] = 2025
    clean["organizacion"] = df_emp["ORG_CLEAN"]
    clean["tipo_empresa"] = np.where(
        clean["organizacion"] == "Persona Natural",
        "Persona Natural",
        "Persona Jurídica",
    )

    # 4. Macro-rubros comerciales basados en sección CIIU
    ciiu_sec = df_emp["CIIU 1 (PRINCIPAL)"].astype(str).str.strip().str[0].str.upper()
    clean["rubro"] = ciiu_sec.map(MACRO_RUBROS).fillna("Otros Servicios / Sin clasificar")

    # 5. Barrios limpios e imputación de faltantes
    nulos_barrio = int(df_emp["BARRIO"].isna().sum())
    clean["barrio"] = df_emp["BARRIO"].apply(clean_barrio)

    # 6. Año de matrícula y tramo de antigüedad (sin datos personales ni dinero)
    anio_mat = pd.to_datetime(df_emp["FECHA MATRÍCULA"], errors="coerce").dt.year
    nulos_fecha = int(anio_mat.isna().sum())
    clean["anio_matricula"] = anio_mat
    clean["tramo_antiguedad"] = anio_mat.apply(map_tramo_antiguedad)

    out_csv = "empresas_tunja_2025_limpio.csv"
    clean.to_csv(out_csv, index=False, encoding="utf-8-sig")

    audit = {
        "anio_corte": 2025,
        "registros_brutos": brutos,
        "descartados_inactivos_IA": inactivos_count,
        "activos_totales_MA": int(len(df_ma)),
        "descartados_establecimientos": establecimientos_count,
        "empresas_activas_final": int(len(clean)),
        "persona_natural": int((clean["tipo_empresa"] == "Persona Natural").sum()),
        "persona_juridica": int((clean["tipo_empresa"] == "Persona Jurídica").sum()),
        "nulos_barrio_imputados": nulos_barrio,
        "nulos_fecha_matricula": nulos_fecha,
    }
    with open("audit_tunja_2025.json", "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2, ensure_ascii=False)

    print(f"CSV guardado: {out_csv} ({len(clean)} empresas)")
    print(json.dumps(audit, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
