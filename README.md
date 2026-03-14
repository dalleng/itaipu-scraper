# itaipu-scraper

## ES

Scraper automatizado que extrae datos de la nómina pública de [Itaipu Binacional](https://nomina.itaipu.info/) (lado Paraguayo) y los publica en una base de datos consultable en [itaipu.vercel.app](https://itaipu.vercel.app).

El sitio oficial de nómina de Itaipu dificulta intencionalmente la extracción de datos: deshabilita copiar y pegar, bloquea las herramientas de desarrollo del navegador, e implementa otras medidas para impedir el acceso programático a información que es pública.

### Qué hace

1. **Extrae** los datos de empleados (cédula, nombre, función, nivel salarial, sede, fecha de admisión y salario) del sitio oficial de nómina de Itaipu.
2. **Procesa** los datos: limpia cédulas, normaliza fechas, y calcula salarios cruzando el nivel de cada empleado con las tablas salariales publicadas.
3. **Almacena** cada extracción como snapshot en una base de datos SQLite con búsqueda full-text.
4. **Publica** la base de datos en [itaipu.vercel.app](https://itaipu.vercel.app) usando [Datasette](https://datasette.io), ofreciendo una interfaz web y API REST para consultar los datos.

### Cómo funciona

- `main.py` — Scraper principal. Descarga el HTML de la nómina, extrae las tablas salariales y los datos JSON de empleados, los procesa y genera un archivo CSV en `data/`.
- `create_or_update_db.py` — Importa los CSVs a SQLite. Usa checksums SHA256 para evitar duplicados y crea índices full-text sobre cédula y nombre.
- `scrape.sh` — Script orquestador que ejecuta el scraper y luego actualiza la base de datos.

### Automatización

Un workflow de GitHub Actions (`scrape.yml`) ejecuta el scraper diariamente a medianoche. El flujo:

### Stack

- **Python 3.12** — BeautifulSoup4, requests, sqlite-utils, Datasette
- **SQLite** — Almacenamiento con búsqueda full-text (FTS)
- **Vercel** — Hosting serverless
- **GitHub Actions** — CI/CD y ejecución diaria del scraper

---

## EN

Automated scraper that extracts public payroll data from [Itaipu Binacional](https://nomina.itaipu.info/) (Paraguayan side) and publishes it as a searchable database at [itaipu.vercel.app](https://itaipu.vercel.app).

Itaipu's official payroll website intentionally makes data extraction difficult: it disables copy and paste, blocks browser developer tools, and implements other measures to prevent programmatic access to what is public information.

### What it does

1. **Scrapes** employee data (ID number, name, role, salary level, office, hire date, and salary) from Itaipu's official payroll website.
2. **Processes** the data: cleans ID numbers, normalizes dates, and calculates salaries by matching each employee's level against the published salary tables.
3. **Stores** each scrape as a snapshot in a SQLite database with full-text search.
4. **Publishes** the database to [itaipu.vercel.app](https://itaipu.vercel.app) using [Datasette](https://datasette.io), providing a web interface and REST API to query the data.

### How it works

- `main.py` — Main scraper. Downloads the payroll HTML, extracts salary tables and employee JSON data, processes them, and outputs a CSV file to `data/`.
- `create_or_update_db.py` — Imports CSVs into SQLite. Uses SHA256 checksums to avoid duplicates and creates full-text indexes on ID number and name fields.
- `scrape.sh` — Orchestration script that runs the scraper and then updates the database.

### Automation

A GitHub Actions workflow (`scrape.yml`) runs the scraper daily at midnight.

### Stack

- **Python 3.12** — BeautifulSoup4, requests, sqlite-utils, Datasette
- **SQLite** — Storage with full-text search (FTS)
- **Vercel** — Serverless hosting
- **GitHub Actions** — CI/CD and daily scraper execution

