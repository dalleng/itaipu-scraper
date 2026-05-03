# itaipu-scraper

## ES

Scraper automatizado que extrae datos de las nóminas públicas de [Itaipu Binacional](https://nomina.itaipu.info/) y de la [Entidad Binacional Yacyretá (EBY)](https://www.eby.gov.py/sueldos/nominas/funcionarios) (ambas del lado paraguayo) y los publica como bases de datos consultables en [itaipu.diegoallen.me](https://itaipu.diegoallen.me).

Ambos sitios oficiales dificultan intencionalmente la extracción de datos: deshabilitan copiar y pegar, bloquean las herramientas de desarrollo del navegador, e implementan otras medidas para impedir el acceso programático a información que es pública.

### Qué hace

1. **Extrae** los datos de empleados de ambas nóminas. Para Yacyretá también se incluyen los componentes de bonificaciones publicados.
2. **Procesa** los datos: limpia cédulas, normaliza fechas, y resuelve códigos de categoría a salarios usando las tablas salariales publicadas.
3. **Almacena** cada extracción como snapshot en una base de datos SQLite con búsqueda full-text (una DB por entidad: `itaipu.db`, `yacyreta.db`).
4. **Publica** las bases de datos en [itaipu.diegoallen.me](https://itaipu.diegoallen.me) usando [Datasette](https://datasette.io), ofreciendo una interfaz web y API REST para consultar los datos.

### Cómo funciona

- `scrape_itaipu.py` — Scraper de Itaipu. Descarga el HTML de la nómina, extrae las tablas salariales y los datos JSON de empleados, los procesa y genera un CSV en `data/itaipu/`.
- `scrape_yacyreta.py` — Scraper de Yacyretá. Descarga `WEB1.xlsx` (escala salarial), `WEB2.xlsx` (nómina) y `WEB3.xlsx` (bonificaciones) del sitio de EBY, los une por cédula (con WEB2 como fuente canónica para columnas compartidas) y genera un CSV en `data/yacyreta/`.
- `create_or_update_db.py` — Importa los CSVs a SQLite. Usa checksums SHA256 para evitar duplicados y crea índices full-text sobre cédula y nombre.
- `scrape.sh {itaipu|yacyreta} [--bootstrap]` — Script orquestador. Toma como argumento la entidad a procesar; `--bootstrap` solo aplica para itaipu (importa snapshots históricos desde el Internet Archive).

### Automatización

Dos workflows de GitHub Actions ejecutan los scrapers diariamente y los despliegan a la misma instancia de Datasette:

- `.github/workflows/scrape_itaipu.yml` — corre a las 00:00 UTC.
- `.github/workflows/scrape_yacyreta.yml` — corre a las 01:00 UTC.

Cada workflow hace scrape, importa a su DB, commitea CSV+DB al repo, y despliega el resultado a Datasette.

### Stack

- **Python 3.12** — BeautifulSoup4, requests, openpyxl, sqlite-utils, Datasette
- **SQLite** — Almacenamiento con búsqueda full-text (FTS)
- **GitHub Actions** — CI/CD y ejecución diaria de los scrapers

---

## EN

Automated scraper that extracts public payroll data from [Itaipu Binacional](https://nomina.itaipu.info/) and the [Entidad Binacional Yacyretá (EBY)](https://www.eby.gov.py/sueldos/nominas/funcionarios) (both Paraguayan side) and publishes it as searchable databases at [itaipu.diegoallen.me](https://itaipu.diegoallen.me).

Both official sites intentionally make data extraction difficult: they disable copy and paste, block browser developer tools, and implement other measures to prevent programmatic access to what is public information.

### What it does

1. **Scrapes** employee data from both payrolls. For Yacyretá the published bonificaciones components are included as well.
2. **Processes** the data: cleans ID numbers, normalizes dates, and resolves category codes to numeric salaries against the published salary tables.
3. **Stores** each scrape as a snapshot in a SQLite database with full-text search (one DB per entity: `itaipu.db`, `yacyreta.db`).
4. **Publishes** both databases to [itaipu.diegoallen.me](https://itaipu.diegoallen.me) using [Datasette](https://datasette.io), providing a web interface and REST API to query the data.

### How it works

- `scrape_itaipu.py` — Itaipu scraper. Downloads the payroll HTML, extracts salary tables and employee JSON data, processes them, and outputs a CSV to `data/itaipu/`.
- `scrape_yacyreta.py` — Yacyretá scraper. Downloads `WEB1.xlsx` (salary scale), `WEB2.xlsx` (nomina) and `WEB3.xlsx` (bonificaciones) from the EBY site, joins them on cedula (WEB2 wins for shared columns), and outputs a CSV to `data/yacyreta/`.
- `create_or_update_db.py` — Imports CSVs into SQLite. Uses SHA256 checksums to avoid duplicates and creates full-text indexes on ID number and name fields.
- `scrape.sh {itaipu|yacyreta} [--bootstrap]` — Orchestration script. Takes the target entity as an argument; `--bootstrap` only applies to itaipu (imports historical snapshots from the Internet Archive).

### Automation

Two GitHub Actions workflows run the scrapers daily and deploy to the same Datasette instance:

- `.github/workflows/scrape_itaipu.yml` — runs at 00:00 UTC.
- `.github/workflows/scrape_yacyreta.yml` — runs at 01:00 UTC.

Each workflow scrapes, imports to its DB, commits CSV+DB to the repo, and deploys the result to Datasette.

### Stack

- **Python 3.12** — BeautifulSoup4, requests, openpyxl, sqlite-utils, Datasette
- **SQLite** — Storage with full-text search (FTS)
- **GitHub Actions** — CI/CD and daily scraper execution
