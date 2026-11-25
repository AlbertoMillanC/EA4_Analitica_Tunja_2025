import json
import pandas as pd
import numpy as np

CSV_PATH = "empresas_tunja_2025_limpio.csv"
AUDIT_PATH = "audit_tunja_2025.json"
OUT_HTML = "dashboard_comercial_tunja.html"

def main():
    df = pd.read_csv(CSV_PATH)
    with open(AUDIT_PATH, "r", encoding="utf-8") as f:
        audit = json.load(f)

    # Top 15 barrios reales (sin SIN BARRIO)
    top_barrios = (
        df[df["barrio"] != "SIN BARRIO"]["barrio"]
        .value_counts()
        .head(15)
        .index.tolist()
    )
    df["barrio_grupo"] = np.where(
        df["barrio"].isin(top_barrios) | (df["barrio"] == "SIN BARRIO"),
        df["barrio"],
        "OTROS BARRIOS",
    )

    # Cubo compacto por dimensiones comerciales (solo conteos de empresas)
    group_cols = ["tipo_empresa", "organizacion", "rubro", "barrio_grupo", "tramo_antiguedad"]
    cube_df = df.groupby(group_cols, as_index=False).size()
    cube_records = [
        [r.tipo_empresa, r.organizacion, r.rubro, r.barrio_grupo, r.tramo_antiguedad, int(r.size)]
        for r in cube_df.itertuples(index=False)
    ]

    payload = {
        "meta": {
            "total_empresas": int(len(df)),
            "rubros": df["rubro"].value_counts().index.tolist(),
            "barrios": top_barrios + ["OTROS BARRIOS", "SIN BARRIO"],
            "organizaciones": df["organizacion"].value_counts().index.tolist(),
            "tramos": [
                "Recientes (2021–2025)",
                "En crecimiento (2016–2020)",
                "Consolidadas (2011–2015)",
                "Históricas (≤ 2010)",
                "Sin fecha",
            ],
        },
        "audit": audit,
        "cube": cube_records,
    }
    payload_json = json.dumps(payload, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>EA4 — Análisis Comercial de Tunja 2025 · Analítica de Datos (IU Digital)</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <style>
    body {{ background-color: #f8fafc; color: #0f172a; font-family: 'Inter', system-ui, -apple-system, sans-serif; }}
    .card {{ background: #ffffff; border: 1px solid #e2e8f0; border-radius: 0.75rem; box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05); }}
    .select-light {{ background: #ffffff; border: 1px solid #cbd5e1; color: #0f172a; border-radius: 0.5rem; padding: 0.45rem 0.75rem; font-size: 0.875rem; }}
    .select-light:focus {{ outline: 2px solid #0284c7; border-color: #0284c7; }}
    .badge {{ font-size: 0.75rem; padding: 0.15rem 0.65rem; border-radius: 9999px; font-weight: 600; }}
  </style>
</head>
<body class="min-h-screen p-4 md:p-6">
  <div class="max-w-7xl mx-auto space-y-5">

    <!-- Banner Institucional -->
    <div class="card px-5 py-3.5 bg-gradient-to-r from-sky-50 via-white to-emerald-50 border-sky-200 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-2 text-xs text-slate-700">
      <div class="space-y-0.5">
        <div class="font-bold text-slate-900 text-sm">Institución Universitaria Digital de Antioquia (IU Digital)</div>
        <div><strong>Materia:</strong> Analítica de Datos (Grupo PREICA2602B020125) · <strong>Docente:</strong> Mateo del Gallego</div>
      </div>
      <div class="space-y-0.5 lg:text-right">
        <div><strong class="text-sky-700">Actividad:</strong> S30 · Unidad 3 · Evidencia de Aprendizaje 4 (EA4)</div>
        <div><strong class="text-emerald-700">Integrantes:</strong> Gilliam Argel Monterroza · Carlos Alberto Millán Castaño · Jorge Eliecer Uribe Pulgarin</div>
      </div>
    </div>

    <!-- Header -->
    <header class="card p-5 md:p-6 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
      <div>
        <div class="flex flex-wrap items-center gap-2 mb-2">
          <span class="badge bg-sky-100 text-sky-800 border border-sky-200">EA4 · Dashboard con IA</span>
          <span class="badge bg-emerald-100 text-emerald-800 border border-emerald-200">Cámara de Comercio de Tunja · Corte 2025</span>
          <span class="badge bg-indigo-100 text-indigo-800 border border-indigo-200">Solo Empresas Activas (MA)</span>
        </div>
        <h1 class="text-2xl md:text-3xl font-bold text-slate-900 tracking-tight">
          Radiografía Comercial de Tunja (2025): Persona Natural vs. Persona Jurídica
        </h1>
        <p class="text-sm text-slate-600 mt-1 max-w-4xl">
          <strong>Pregunta de investigación:</strong> ¿Cómo se distribuyen las empresas activas de Tunja en 2025 según su naturaleza jurídica (Persona Natural vs. Persona Jurídica), sus macro-rubros de actividad económica y su concentración por barrios?
        </p>
      </div>
      <div class="bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 text-xs text-slate-600 shrink-0 max-w-xs">
        <div class="font-semibold text-slate-900 mb-1">Alcance del universo limpio:</div>
        Se excluyeron <strong>533</strong> inactivos (IA) y <strong>8,643</strong> establecimientos para evitar doble conteo. Las ESAL y sociedades se unificaron en <strong>Persona Jurídica</strong>.
      </div>
    </header>

    <!-- Filtros -->
    <section class="card p-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 items-end">
      <div>
        <label class="block text-xs font-medium text-slate-600 mb-1">Tipo de Empresa</label>
        <select id="filterTipo" class="select-light w-full">
          <option value="ALL">Todas (Natural + Jurídica)</option>
          <option value="Persona Natural">Persona Natural</option>
          <option value="Persona Jurídica">Persona Jurídica (Sociedades y ESAL)</option>
        </select>
      </div>
      <div>
        <label class="block text-xs font-medium text-slate-600 mb-1">Macro-Rubro</label>
        <select id="filterRubro" class="select-light w-full">
          <option value="ALL">Todos los rubros</option>
        </select>
      </div>
      <div>
        <label class="block text-xs font-medium text-slate-600 mb-1">Barrio</label>
        <select id="filterBarrio" class="select-light w-full">
          <option value="ALL">Todos los barrios</option>
        </select>
      </div>
      <div>
        <label class="block text-xs font-medium text-slate-600 mb-1">Forma Jurídica Específica</label>
        <select id="filterOrg" class="select-light w-full">
          <option value="ALL">Todas las formas</option>
        </select>
      </div>
      <div>
        <button id="btnReset" class="w-full bg-slate-800 hover:bg-slate-700 text-white text-sm font-medium py-2 px-3 rounded-lg transition">
          Restablecer Filtros
        </button>
      </div>
    </section>

    <!-- KPIs -->
    <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 border-l-4 border-l-slate-700">
        <div class="text-xs font-medium text-slate-500 uppercase tracking-wider">Empresas Activas (2025)</div>
        <div id="kpiTotal" class="text-2xl font-bold text-slate-900 mt-1">—</div>
        <div id="kpiTotalSub" class="text-xs text-slate-500 mt-1">—</div>
      </div>
      <div class="card p-4 border-l-4 border-l-sky-500">
        <div class="text-xs font-medium text-slate-500 uppercase tracking-wider">Persona Natural</div>
        <div id="kpiPN" class="text-2xl font-bold text-sky-600 mt-1">—</div>
        <div id="kpiPNSub" class="text-xs text-slate-500 mt-1">—</div>
      </div>
      <div class="card p-4 border-l-4 border-l-emerald-500">
        <div class="text-xs font-medium text-slate-500 uppercase tracking-wider">Persona Jurídica</div>
        <div id="kpiPJ" class="text-2xl font-bold text-emerald-600 mt-1">—</div>
        <div id="kpiPJSub" class="text-xs text-slate-500 mt-1">—</div>
      </div>
      <div class="card p-4 border-l-4 border-l-amber-500">
        <div class="text-xs font-medium text-slate-500 uppercase tracking-wider">Rubro y Barrio Líder</div>
        <div id="kpiTopRubro" class="text-lg font-bold text-amber-600 mt-1 truncate">—</div>
        <div id="kpiTopBarrio" class="text-xs text-slate-600 mt-1 truncate">—</div>
      </div>
    </section>

    <!-- Gráficos Fila 1 -->
    <section class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="card p-5 lg:col-span-2">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-base font-semibold text-slate-900">1. Empresas por Macro-Rubro (Natural vs. Jurídica)</h2>
          <span class="text-xs text-slate-500">Número de empresas activas</span>
        </div>
        <div class="h-80"><canvas id="chartRubros"></canvas></div>
      </div>

      <div class="card p-5">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-base font-semibold text-slate-900">2. Proporción Jurídica</h2>
          <span class="text-xs text-slate-500">Natural vs. Jurídica</span>
        </div>
        <div class="h-80"><canvas id="chartTipo"></canvas></div>
      </div>
    </section>

    <!-- Gráficos Fila 2 -->
    <section class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="card p-5">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-base font-semibold text-slate-900">3. Top 12 Barrios con Mayor Número de Empresas</h2>
          <span class="text-xs text-slate-500">Concentración territorial</span>
        </div>
        <div class="h-72"><canvas id="chartBarrios"></canvas></div>
      </div>

      <div class="card p-5">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-base font-semibold text-slate-900">4. Antigüedad de Matrícula (Natural vs. Jurídica)</h2>
          <span class="text-xs text-slate-500">Tramos por año de registro</span>
        </div>
        <div class="h-72"><canvas id="chartAntiguedad"></canvas></div>
      </div>
    </section>

    <!-- Embudo de Limpieza + Tabla -->
    <section class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="card p-5">
        <h2 class="text-base font-semibold text-slate-900 mb-2">5. Embudo de Limpieza de Datos</h2>
        <p class="text-xs text-slate-500 mb-3">
          Depuración desde la sábana bruta 2025 hasta el universo único de empresas activas (sin doble conteo de establecimientos):
        </p>
        <div class="h-64"><canvas id="chartFunnel"></canvas></div>
      </div>

      <div class="card p-5 lg:col-span-2 flex flex-col">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-3">
          <h2 class="text-base font-semibold text-slate-900">Detalle por Macro-Rubro y Tipo de Empresa</h2>
          <input type="text" id="tableSearch" placeholder="Buscar rubro o tipo..." class="select-light w-full sm:w-64" />
        </div>
        <div class="overflow-x-auto max-h-72">
          <table class="w-full text-sm text-left">
            <thead class="text-xs uppercase text-slate-500 border-b border-slate-200 sticky top-0 bg-slate-50">
              <tr>
                <th class="py-2 pr-3">Macro-Rubro</th>
                <th class="py-2 px-3">Tipo de Empresa</th>
                <th class="py-2 px-3 text-right">Empresas</th>
                <th class="py-2 pl-3 text-right">% del Filtro</th>
              </tr>
            </thead>
            <tbody id="detailTableBody" class="divide-y divide-slate-100 text-slate-700"></tbody>
          </table>
        </div>
      </div>
    </section>

    <footer class="text-xs text-slate-500 text-center pb-4">
      Fuente: Listado anonimizado basado en Cámara de Comercio de Tunja (Municipio 15001, corte 2025). Solo matrículas activas (MA) de Persona Natural y Persona Jurídica (11,802 empresas) · IU Digital de Antioquia.
    </footer>
  </div>

<script>
const DATA = {payload_json};
// Índices del cubo: 0: tipo_empresa, 1: organizacion, 2: rubro, 3: barrio_grupo, 4: tramo_antiguedad, 5: count

const fmtNum = (n) => new Intl.NumberFormat('es-CO').format(n);

const elTipo = document.getElementById('filterTipo');
const elRubro = document.getElementById('filterRubro');
const elBarrio = document.getElementById('filterBarrio');
const elOrg = document.getElementById('filterOrg');
const elSearch = document.getElementById('tableSearch');

DATA.meta.rubros.forEach(r => {{
  const o = document.createElement('option'); o.value = r; o.textContent = r; elRubro.appendChild(o);
}});
DATA.meta.barrios.forEach(b => {{
  const o = document.createElement('option'); o.value = b; o.textContent = b; elBarrio.appendChild(o);
}});
DATA.meta.organizaciones.forEach(org => {{
  const o = document.createElement('option'); o.value = org; o.textContent = org; elOrg.appendChild(o);
}});

Chart.defaults.color = '#334155';
Chart.defaults.borderColor = '#e2e8f0';

let chartRubros, chartTipo, chartBarrios, chartAntiguedad, chartFunnel;

function render() {{
  const fTipo = elTipo.value;
  const fRubro = elRubro.value;
  const fBarrio = elBarrio.value;
  const fOrg = elOrg.value;

  const rows = DATA.cube.filter(r =>
    (fTipo === 'ALL' || r[0] === fTipo) &&
    (fRubro === 'ALL' || r[2] === fRubro) &&
    (fBarrio === 'ALL' || r[3] === fBarrio) &&
    (fOrg === 'ALL' || r[1] === fOrg)
  );

  let total = 0, pn = 0, pj = 0;
  const rubroPN = new Map(), rubroPJ = new Map(), rubroTot = new Map();
  const barrioMap = new Map();
  const tramoPN = new Map(), tramoPJ = new Map();
  const tableMap = new Map();

  for (const r of rows) {{
    const n = r[5];
    total += n;
    if (r[0] === 'Persona Natural') {{
      pn += n;
      rubroPN.set(r[2], (rubroPN.get(r[2]) || 0) + n);
      tramoPN.set(r[4], (tramoPN.get(r[4]) || 0) + n);
    }} else {{
      pj += n;
      rubroPJ.set(r[2], (rubroPJ.get(r[2]) || 0) + n);
      tramoPJ.set(r[4], (tramoPJ.get(r[4]) || 0) + n);
    }}
    rubroTot.set(r[2], (rubroTot.get(r[2]) || 0) + n);
    if (r[3] !== 'OTROS BARRIOS') {{
      barrioMap.set(r[3], (barrioMap.get(r[3]) || 0) + n);
    }}
    const tKey = r[2] + '||' + r[0];
    const prev = tableMap.get(tKey) || {{ rubro: r[2], tipo: r[0], n: 0 }};
    prev.n += n;
    tableMap.set(tKey, prev);
  }}

  // KPIs
  const pctPN = total ? ((pn / total) * 100).toFixed(1) : '0.0';
  const pctPJ = total ? ((pj / total) * 100).toFixed(1) : '0.0';
  document.getElementById('kpiTotal').textContent = fmtNum(total);
  document.getElementById('kpiTotalSub').textContent = `De ${{fmtNum(DATA.meta.total_empresas)}} empresas activas totales`;
  document.getElementById('kpiPN').textContent = `${{fmtNum(pn)}} (${{pctPN}}%)`;
  document.getElementById('kpiPNSub').textContent = 'Comerciantes y profesionales independientes';
  document.getElementById('kpiPJ').textContent = `${{fmtNum(pj)}} (${{pctPJ}}%)`;
  document.getElementById('kpiPJSub').textContent = 'SAS, Ltda, Anónimas, ESAL y Solidarias';

  const topRub = [...rubroTot.entries()].sort((a, b) => b[1] - a[1])[0];
  const topBar = [...barrioMap.entries()].sort((a, b) => b[1] - a[1])[0];
  document.getElementById('kpiTopRubro').textContent = topRub ? `${{topRub[0]}}` : '—';
  document.getElementById('kpiTopBarrio').textContent = topBar
    ? `Barrio líder: ${{topBar[0]}} (${{fmtNum(topBar[1])}} empresas)`
    : 'Barrio líder: —';

  // 1. Chart Rubros (PN vs PJ apilado horizontal)
  const rubSorted = [...rubroTot.entries()].sort((a, b) => b[1] - a[1]).map(x => x[0]);
  if (chartRubros) chartRubros.destroy();
  chartRubros = new Chart(document.getElementById('chartRubros'), {{
    type: 'bar',
    data: {{
      labels: rubSorted,
      datasets: [
        {{ label: 'Persona Natural', data: rubSorted.map(k => rubroPN.get(k) || 0), backgroundColor: '#0284c7' }},
        {{ label: 'Persona Jurídica', data: rubSorted.map(k => rubroPJ.get(k) || 0), backgroundColor: '#10b981' }},
      ]
    }},
    options: {{
      indexAxis: 'y', responsive: true, maintainAspectRatio: false,
      plugins: {{ legend: {{ position: 'bottom' }} }},
      scales: {{ x: {{ stacked: true, beginAtZero: true }}, y: {{ stacked: true }} }}
    }}
  }});

  // 2. Chart Tipo (Dona)
  if (chartTipo) chartTipo.destroy();
  chartTipo = new Chart(document.getElementById('chartTipo'), {{
    type: 'doughnut',
    data: {{
      labels: ['Persona Natural', 'Persona Jurídica'],
      datasets: [{{ data: [pn, pj], backgroundColor: ['#0284c7', '#10b981'], borderColor: '#ffffff', borderWidth: 3 }}]
    }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      plugins: {{ legend: {{ position: 'bottom' }} }}
    }}
  }});

  // 3. Chart Top 12 Barrios
  const barSorted = [...barrioMap.entries()].sort((a, b) => b[1] - a[1]).slice(0, 12);
  if (chartBarrios) chartBarrios.destroy();
  chartBarrios = new Chart(document.getElementById('chartBarrios'), {{
    type: 'bar',
    data: {{
      labels: barSorted.map(x => x[0]),
      datasets: [{{ label: 'Empresas', data: barSorted.map(x => x[1]), backgroundColor: '#f59e0b', borderRadius: 4 }}]
    }},
    options: {{
      indexAxis: 'y', responsive: true, maintainAspectRatio: false,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{ x: {{ beginAtZero: true }} }}
    }}
  }});

  // 4. Chart Antigüedad
  const tramos = DATA.meta.tramos.filter(t => (tramoPN.get(t) || 0) + (tramoPJ.get(t) || 0) > 0);
  if (chartAntiguedad) chartAntiguedad.destroy();
  chartAntiguedad = new Chart(document.getElementById('chartAntiguedad'), {{
    type: 'bar',
    data: {{
      labels: tramos,
      datasets: [
        {{ label: 'Persona Natural', data: tramos.map(t => tramoPN.get(t) || 0), backgroundColor: '#0284c7' }},
        {{ label: 'Persona Jurídica', data: tramos.map(t => tramoPJ.get(t) || 0), backgroundColor: '#10b981' }},
      ]
    }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      plugins: {{ legend: {{ position: 'bottom' }} }},
      scales: {{ y: {{ beginAtZero: true }} }}
    }}
  }});

  // 5. Chart Embudo de Limpieza
  const aud = DATA.audit;
  if (chartFunnel) chartFunnel.destroy();
  chartFunnel = new Chart(document.getElementById('chartFunnel'), {{
    type: 'bar',
    data: {{
      labels: ['Brutos 2025', 'Activos (MA)', 'Empresas (PN+PJ)', 'Barrios Imputados'],
      datasets: [{{
        label: 'Registros',
        data: [aud.registros_brutos, aud.activos_totales_MA, aud.empresas_activas_final, aud.nulos_barrio_imputados],
        backgroundColor: ['#64748b', '#6366f1', '#10b981', '#f59e0b'],
        borderRadius: 4
      }}]
    }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{ y: {{ beginAtZero: true }} }}
    }}
  }});

  // Tabla
  const q = elSearch.value.trim().toLowerCase();
  const tRows = [...tableMap.values()]
    .filter(x => !q || x.rubro.toLowerCase().includes(q) || x.tipo.toLowerCase().includes(q))
    .sort((a, b) => b.n - a.n);

  document.getElementById('detailTableBody').innerHTML = tRows.map(x => {{
    const pct = total ? ((x.n / total) * 100).toFixed(1) : '0.0';
    return `<tr class="hover:bg-slate-50">
      <td class="py-2 pr-3 font-medium text-slate-900">${{x.rubro}}</td>
      <td class="py-2 px-3 text-slate-600">${{x.tipo}}</td>
      <td class="py-2 px-3 text-right font-semibold text-slate-900">${{fmtNum(x.n)}}</td>
      <td class="py-2 pl-3 text-right font-medium text-sky-700">${{pct}}%</td>
    </tr>`;
  }}).join('');
}}

[elTipo, elRubro, elBarrio, elOrg].forEach(el => el.addEventListener('change', render));
elSearch.addEventListener('input', render);
document.getElementById('btnReset').addEventListener('click', () => {{
  elTipo.value = 'ALL';
  elRubro.value = 'ALL';
  elBarrio.value = 'ALL';
  elOrg.value = 'ALL';
  elSearch.value = '';
  render();
}});

render();
</script>
</body>
</html>
"""
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Dashboard en modo claro generado: {OUT_HTML} ({len(html)//1024} KB)")

if __name__ == "__main__":
    main()
