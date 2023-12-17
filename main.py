import csv
import re
import requests
from urllib.parse import unquote
from bs4 import BeautifulSoup


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


def fetch_html():
    response = requests.get(
        'https://nomina.itaipu.info/',
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    )
    match = re.search(r"unescape\('(.*)'\)", response.text)
    content = unquote(match.group(1), encoding='latin-1').strip()
    return content


def main():
    html_str = fetch_html()
    soup = BeautifulSoup(html_str, "html.parser")

    tables = soup.find_all("table")
    nomina, tabla_salarial, *_ = [t for t in tables]

    funcionarios = parse_table(nomina)
    salarios = parse_table(tabla_salarial)

    filename = "nomina_itaipu.csv"

    with open(filename, 'w') as file:
        writer = csv.writer(file)
        funcionarios[0] += ["SALARIO"]
        for f in funcionarios:
            nivel = f[-1]
            m = re.match(r"(\d+)-([A|B|C])", nivel)
            salario = ''
            if m:
                row, col = m.groups()
                row = int(row) - 5
                col = {"A": 1, "B": 2, "C": 3}.get(col)
                salario = salarios[row][col]
            writer.writerow(f + [salario])


if __name__ == '__main__':
    main()
