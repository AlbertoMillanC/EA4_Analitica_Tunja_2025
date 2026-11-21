import pandas as pd
import numpy as np

PATH_2025 = r"C:\Users\BUNANDUN\Desktop\4_SOLICITUD_CAMARA_COMERCIO_TUNJA_CODIGO_15001_ACTIVOS_2025.xlsx"
SHEET_2025 = "BASE_DETALLADA_15001_2025"

def clean_barrio(val):
    if pd.isna(val) or not str(val).strip():
        return "SIN BARRIO"
    s = str(val).strip()
    if " - " in s:
        s = s.split(" - ", 1)[1].strip()
    return s.upper()

def main():
    df = pd.read_excel(PATH_2025, sheet_name=SHEET_2025, engine="openpyxl")

    # Filtrar solo matrículas activas
    df_ma = df[df["ESTADO"].astype(str).str.strip() == "MA"].copy()

    # Excluir establecimientos (pertenecen a una Persona Natural o Jurídica)
    df_ma["ORG_CLEAN"] = df_ma["ORGANIZACIÓN"].astype(str).str.strip()
    df_emp = df_ma[df_ma["ORG_CLEAN"] != "Establecimiento"].copy()

    clean = pd.DataFrame(index=df_emp.index)
    clean["organizacion"] = df_emp["ORG_CLEAN"]
    clean["tipo_empresa"] = np.where(
        clean["organizacion"] == "Persona Natural",
        "Persona Natural",
        "Persona Jurídica",
    )
    clean["barrio"] = df_emp["BARRIO"].apply(clean_barrio)
    clean["ciiu_seccion"] = df_emp["CIIU 1 (PRINCIPAL)"].astype(str).str.strip().str[0].str.upper()

    print("Empresas activas limpias:", len(clean))
    print(clean["tipo_empresa"].value_counts())

if __name__ == "__main__":
    main()
