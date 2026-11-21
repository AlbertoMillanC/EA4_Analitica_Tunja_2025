import pandas as pd

PATH_2025 = r"C:\Users\BUNANDUN\Desktop\4_SOLICITUD_CAMARA_COMERCIO_TUNJA_CODIGO_15001_ACTIVOS_2025.xlsx"
SHEET_2025 = "BASE_DETALLADA_15001_2025"

def main():
    df = pd.read_excel(PATH_2025, sheet_name=SHEET_2025, engine="openpyxl")
    print("Total registros brutos 2025:", len(df))
    print("Columnas:", list(df.columns))
    print("\nConteo por ESTADO:")
    print(df["ESTADO"].value_counts(dropna=False))
    print("\nConteo por ORGANIZACIÓN:")
    print(df["ORGANIZACIÓN"].value_counts(dropna=False))
    print("\nValores faltantes:")
    print(df[["ORGANIZACIÓN", "ESTADO", "BARRIO", "CIIU 1 (PRINCIPAL)"]].isna().sum())

if __name__ == "__main__":
    main()
