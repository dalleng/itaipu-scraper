import csv
import logging
import os
from datetime import datetime
from io import BytesIO

import requests
from openpyxl import load_workbook

from main import REQUEST_HEADERS

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

CATEGORIA_SUFFIX = " BASICO CAT."
DATE_FORMATS = ["%d/%m/%Y", "%d/%m/%y", "%m/%d/%y", "%m/%d/%Y"]


def fetch_xlsx_sheet(url):
    logging.info(f"Fetching xlsx {url=}")
    r = requests.get(url, headers=REQUEST_HEADERS)
    r.raise_for_status()
    wb = load_workbook(BytesIO(r.content), read_only=True, data_only=True)
    ws = wb.active
    if ws is None:
        raise RuntimeError(f"No active worksheet in {url}")
    return ws


def fetch_salary_scale(url):
    ws = fetch_xlsx_sheet(url)
    rows = ws.iter_rows(values_only=True)
    headers = next(rows)
    cat_idx = headers.index("Categoria")
    bas_idx = headers.index("Basico")
    scale: dict[str, int] = {}
    for row in rows:
        cat_raw = row[cat_idx]
        bas = row[bas_idx]
        if cat_raw is None or bas is None:
            continue
        cat = str(cat_raw).strip()
        if cat.endswith(CATEGORIA_SUFFIX):
            cat = cat[: -len(CATEGORIA_SUFFIX)].strip()
        scale[cat] = int(str(bas))
    logging.info(f"Loaded {len(scale)} salary-scale entries")
    return scale


def normalize_date(raw):
    raw = str(raw).strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    raise ValueError(f"Could not parse date: {raw}")


def resolve_basico(raw, salary_scale):
    raw_str = str(raw).strip()
    try:
        return "", int(raw_str)
    except ValueError:
        pass
    if raw_str not in salary_scale:
        raise KeyError(f"Categoria {raw_str!r} not found in salary scale")
    return raw_str, salary_scale[raw_str]


def fetch_nomina(url, salary_scale):
    ws = fetch_xlsx_sheet(url)
    rows = ws.iter_rows(values_only=True)
    headers = list(next(rows))
    idx = {h: headers.index(h) for h in ("Cedula", "Nombre", "Basico", "Ingreso", "Sede")}
    out: list[list[str]] = [
        ["cedula", "nombre", "fecha_de_admision", "categoria", "salario", "sede"]
    ]
    for row in rows:
        cedula = row[idx["Cedula"]]
        if cedula is None or str(cedula).strip() == "":
            logging.info(f"Skipping row with empty cedula: {row}")
            continue
        categoria, salario = resolve_basico(row[idx["Basico"]], salary_scale)
        sede = row[idx["Sede"]]
        out.append([
            str(cedula).strip().replace(".", ""),
            str(row[idx["Nombre"]]).strip(),
            normalize_date(row[idx["Ingreso"]]),
            categoria,
            str(salario),
            str(sede).strip() if sede is not None else "",
        ])
    return out


def main():
    web1 = os.environ.get(
        "scrape_url_web1",
        "https://www.eby.gov.py/sueldos/nominas/assets/WEB1.xlsx",
    )
    web2 = os.environ.get(
        "scrape_url_web2",
        "https://www.eby.gov.py/sueldos/nominas/assets/WEB2.xlsx",
    )

    salary_scale = fetch_salary_scale(web1)
    rows = fetch_nomina(web2, salary_scale)

    template = os.environ.get(
        "output_filename_template",
        "data/yacyreta/nomina_yacyreta_{}.csv",
    )
    filename = template.format(datetime.now().strftime("%Y-%m-%d"))
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    logging.info(f"Writing {len(rows) - 1} rows to {filename}")
    with open(filename, "w") as f:
        writer = csv.writer(f)
        for r in rows:
            writer.writerow(r)


if __name__ == "__main__":
    main()
