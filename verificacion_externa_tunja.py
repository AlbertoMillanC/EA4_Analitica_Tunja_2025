import pandas as pd

df = pd.read_csv("empresas_tunja_2025_limpio.csv")

print("=== VERIFICACIÓN EXTERNA INDEPENDIENTE (TUNJA 2025 · ACTIVAS) ===")
print(f"1. Total empresas activas (PN + PJ): {len(df):,}")

for k, v in df["tipo_empresa"].value_counts().items():
    print(f"   - {k}: {v:,} ({v / len(df) * 100:.1f}%)")

print("\n2. Distribución por Macro-Rubro:")
for k, v in df["rubro"].value_counts().items():
    print(f"   - {k}: {v:,} ({v / len(df) * 100:.1f}%)")

print("\n3. Top 5 Barrios:")
for k, v in df["barrio"].value_counts().head(5).items():
    print(f"   - {k}: {v:,} ({v / len(df) * 100:.1f}%)")

print("\n4. Cruce Persona Jurídica vs. Macro-Rubro (Top 3):")
pj = df[df["tipo_empresa"] == "Persona Jurídica"]
for k, v in pj["rubro"].value_counts().head(3).items():
    print(f"   - {k}: {v:,} ({v / len(pj) * 100:.1f}% de las Jurídicas)")
