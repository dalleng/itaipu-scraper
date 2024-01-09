import csv
import os
import re
import requests
from urllib.parse import unquote
from bs4 import BeautifulSoup
from datetime import datetime

ADMISION_COLUMN = 2
FUNCION_COLUMN = 3
NIVEL_COLUMN = 4


def extract_rows(table, col_element="td"):
    rows = []
    for row in table.find_all('tr'):
        rows.append([col.text.strip() for col in row.find_all(col_element)])
    return rows


def parse_table(table):
    head = table.find("thead")
    body = table.find("tbody")
    headers = extract_rows(head, col_element="th")
    body = extract_rows(body)
    return headers + body


def fetch_content(url):
    response = requests.get(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    )
    response.encoding = "utf-8"
    match = re.search(r"unescape\('(.*)'\)", response.text)
    content = unquote(match.group(1), encoding='latin-1').strip()
    return content


def get_salario_for_nivel(
    f, salarios, salario_comisionados, salario_directores
):
    nivel = f[NIVEL_COLUMN]
    funcion = f[FUNCION_COLUMN].strip()
    comisionado_to_index = {
        "COMISIONADO DE NIVEL UNIVERSITARIO": 0,
        "COMISIONADO DE NIVEL NO UNIVERSITARIO": 1
    }
    directores_to_index = {
        "CONSEJER": 3,
        "DTOR.ARE": 2,
        "DTOR.GRA": 1
    }
    m = re.match(r"(\d+)-([A|B|C])", nivel)
    salario = ''
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
        salario = salario.replace('.', '')
        yield f + [salario]


def normalize_date(funcionarios):
    yield next(funcionarios)
    for f in funcionarios:
        try:
            admission_date = datetime.strptime(f[ADMISION_COLUMN], '%d/%m/%y')
        except ValueError:
            admission_date = datetime.strptime(f[ADMISION_COLUMN], '%m/%d/%y')
        f[ADMISION_COLUMN] = admission_date.strftime('%Y-%m-%d')
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
    url = os.environ.get("scrape_url", 'https://nomina.itaipu.info/')
    html_str = fetch_content(url)

    soup = BeautifulSoup(html_str, "html.parser")
    tables = soup.find_all("table")
    nomina, tabla_salarial, salario_comisionados, _, salario_directores, *__ = [t for t in tables]

    funcionarios = parse_table(nomina)
    salarios = parse_table(tabla_salarial)
    salario_comisionados = parse_table(salario_comisionados)
    salario_comisionados = [
        salario_comisionados[1][1],
        salario_comisionados[2][1]
    ]
    salario_directores = parse_table(salario_directores)

    filename = os.environ.get(
        "output_filename_template", "nomina_itaipu_{}.csv"
    )
    filename = filename.format(datetime.now().strftime('%Y-%m-%d'))

    with open(filename, 'w') as file:
        writer = csv.writer(file)
        funcionarios = replace_headers(funcionarios)
        funcionarios = clean_cedula(normalize_date(add_salary_to_funcionarios(
            funcionarios, salarios, salario_comisionados, salario_directores
        )))
        for f in funcionarios:
            writer.writerow(f)


if __name__ == '__main__':
    main()
