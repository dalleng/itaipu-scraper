import csv
import os
import re
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from datetime import datetime
import logging

ADMISION_COLUMN = 2
FUNCION_COLUMN = 3
NIVEL_COLUMN = 4


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def extract_rows(table, col_element="td"):
    rows = []
    for row in table.find_all("tr"):
        rows.append([col.text.strip() for col in row.find_all(col_element)])
    return rows


def parse_table(table):
    head = table.find("thead")
    body = table.find("tbody")
    headers = extract_rows(head, col_element="th")
    body = extract_rows(body)
    return headers + body


REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def fetch_page(url):
    logging.info(f"Fetching page {url=}")
    response = requests.get(url, headers=REQUEST_HEADERS)
    response.encoding = "utf-8"
    return response.text


def fetch_employees(url, html_text):
    # Extract JSON filename from the fetch() call in the page script
    logging.info("Looking for JSON file with employees")
    match = re.search(r"fetch\(['\"]\./(.*?\.json)['\"]", html_text)
    assert match is not None, "Could not find JSON data URL in page"
    json_url = urljoin(url, match.group(1))
    logging.info(f"JSON url found {json_url=}")

    data = requests.get(json_url, headers=REQUEST_HEADERS).json()

    # First 2 elements are metadata (date and column headers); skip them
    col_headers = ["CI N°", "NOMBRE Y APELLIDO", "FECHA DE ADMISIÓN", "FUNCIÓN", "NIVEL", "SEDE", "OBSERVACIÓN"]
    key_map = [
        "EMPLEADOS DE LA ITAIPU BINACIONAL - MD",
        "Column2",
        "Column3",
        "Column4",
        "Column5",
        "Column6",
        "Column7",
    ]
    rows = [col_headers]
    for emp in data[2:]:
        ci = emp.get(key_map[0])
        # Filter out entries without a CI value
        if not ci:
            logging.info(f"Found row without CI {emp=}")
            continue
        rows.append([emp.get(k, "") for k in key_map])
    return rows


def get_salario_for_nivel(f, salarios, salario_comisionados, salario_directores):
    nivel = f[NIVEL_COLUMN]
    funcion = f[FUNCION_COLUMN].strip()
    comisionado_to_index = {
        "COMISIONADO DE NIVEL UNIVERSITARIO": 0,
        "COMISIONADO DE NIVEL NO UNIVERSITARIO": 1,
    }
    directores_to_index = {"CONSEJER": 3, "DTOR.ARE": 2, "DTOR.GRA": 1}
    m = re.match(r"(\d+)-([A|B|C])", nivel)
    salario = ""
    if m:
        row, col = m.groups()
        row = int(row) - 5
        col = {"A": 1, "B": 2, "C": 3}.get(col)
        salario = salarios[row][col]
    elif (index_comisionado := comisionado_to_index.get(funcion)) is not None:
        salario = salario_comisionados[index_comisionado]
    elif (index_director := directores_to_index.get(nivel)) is not None:
        salario = salario_directores[index_director][2]
    return salario


def add_salary_to_funcionarios(
    funcionarios, salarios, salario_comisionados, salario_directores
):
    yield funcionarios[0] + ["salario"]
    for f in funcionarios[1:]:
        salario = get_salario_for_nivel(
            f, salarios, salario_comisionados, salario_directores
        )
        salario = salario.replace(".", "")
        yield f + [salario]


def normalize_date(funcionarios):
    formats = ["%d/%m/%Y", "%d/%m/%y", "%m/%d/%y", "%m/%d/%Y"]
    yield next(funcionarios)
    for f in funcionarios:
        raw = f[ADMISION_COLUMN]
        admission_date = None
        for fmt in formats:
            try:
                admission_date = datetime.strptime(raw, fmt)
                break
            except ValueError:
                continue
        if admission_date is None:
            raise ValueError(f"Could not parse date: {raw}")
        f[ADMISION_COLUMN] = admission_date.strftime("%Y-%m-%d")
        yield f


def clean_cedula(funcionarios):
    yield next(funcionarios)
    for f in funcionarios:
        f[0] = f[0].replace(".", "")
        yield f


def replace_headers(funcionarios):
    header_map = {
        "CI N°": "cedula",
        "NOMBRE Y APELLIDO": "nombre_y_apellido",
        "FECHA DE ADMISIÓN": "fecha_de_admision",
        "FUNCIÓN": "funcion",
        "NIVEL": "nivel",
        "SEDE": "sede",
        "OBSERVACIÓN": "observacion",
        "SALARIO": "salario",
    }
    funcionarios[0] = [header_map[header] for header in funcionarios[0]]
    return funcionarios


def main():
    url = os.environ.get("scrape_url", "https://nomina.itaipu.info/")
    html_text = fetch_page(url)

    soup = BeautifulSoup(html_text, "html.parser")
    tables = soup.find_all("table")
    _, tabla_salarial, salario_comisionados, _, salario_directores, *__ = [
        t for t in tables
    ]

    funcionarios = fetch_employees(url, html_text)
    logging.info("Extracting salary tables")
    salarios = parse_table(tabla_salarial)
    salario_comisionados = parse_table(salario_comisionados)
    salario_comisionados = [salario_comisionados[1][1], salario_comisionados[2][1]]
    salario_directores = parse_table(salario_directores)

    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    template = os.environ.get("output_filename_template", "nomina_itaipu_{}.csv")
    filename = os.path.join(data_dir, template.format(datetime.now().strftime("%Y-%m-%d")))
    logging.info(f"Writing to file {filename=}...")

    with open(filename, "w") as file:
        writer = csv.writer(file)
        funcionarios = replace_headers(funcionarios)
        funcionarios = clean_cedula(
            normalize_date(
                add_salary_to_funcionarios(
                    funcionarios, salarios, salario_comisionados, salario_directores
                )
            )
        )
        for f in funcionarios:
            writer.writerow(f)


if __name__ == "__main__":
    main()
