#! /bin/bash
set -e

TODAY=$(date -u +%Y-%m-%d)

if [[ "$1" == "--bootstrap" ]]; then
    # scrape site from the web archive from 2023-09-03
    python itaipu.py \
        --url https://web.archive.org/web/20230309222819/http://www.nomina.itaipu.info/ \
        --output data/itaipu/nomina_itaipu_2023-09-03.csv
    python create_or_update_db.py --csv data/itaipu/nomina_itaipu_2023-09-03.csv

    # scrape site from the web archive from 2023-05-08
    python itaipu.py \
        --url https://web.archive.org/web/20230508021538/http://nomina.itaipu.info/ \
        --output data/itaipu/nomina_itaipu_2023-05-08.csv
    python create_or_update_db.py --csv data/itaipu/nomina_itaipu_2023-05-08.csv

    # scrape site from the web archive from 2023-05-16
    python itaipu.py \
        --url https://web.archive.org/web/20230516195208/http://nomina.itaipu.info/ \
        --output data/itaipu/nomina_itaipu_2023-05-16.csv
    python create_or_update_db.py --csv data/itaipu/nomina_itaipu_2023-05-16.csv

    python create_or_update_db.py --csv data/itaipu/nomina_itaipu_2023-12-16.csv
fi

python itaipu.py
python create_or_update_db.py

python scrape_yacyreta.py
python create_or_update_db.py --db yacyreta.db --csv "data/yacyreta/nomina_yacyreta_${TODAY}.csv"
