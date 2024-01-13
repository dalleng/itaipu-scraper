#! /bin/bash

if [[ "$1" == "--bootstrap" ]]; then
    # scrape site from the web archive from 2023-09-03
    scrape_url=https://web.archive.org/web/20230309222819/http://www.nomina.itaipu.info/ output_filename_template=nomina_itaipu_2023-09-03.csv python main.py
    python create_or_update_db.py nomina_itaipu_2023-09-03.csv

    # scrape site from the web archive from 2023-05-08
    scrape_url=https://web.archive.org/web/20230508021538/http://nomina.itaipu.info/ output_filename_template=nomina_itaipu_2023-05-08.csv python main.py
    python create_or_update_db.py nomina_itaipu_2023-05-08.csv

    # scrape site from the web archive from 2023-05-16
    scrape_url=https://web.archive.org/web/20230516195208/http://nomina.itaipu.info/ output_filename_template=nomina_itaipu_2023-05-16.csv python main.py
    python create_or_update_db.py nomina_itaipu_2023-05-16.csv

    python create_or_update_db.py nomina_itaipu_2023-12-16.csv
fi

python main.py
python create_or_update_db.py
