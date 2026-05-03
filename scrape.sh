#! /bin/bash
set -e

usage() {
    echo "Usage: $0 {itaipu|yacyreta} [--bootstrap]" >&2
    echo "  --bootstrap is only valid for itaipu" >&2
    exit 1
}

target="${1:-}"
[[ -z "$target" ]] && usage
shift

TODAY=$(date -u +%Y-%m-%d)

case "$target" in
    itaipu)
        if [[ "${1:-}" == "--bootstrap" ]]; then
            python scrape_itaipu.py \
                --url https://web.archive.org/web/20230309222819/http://www.nomina.itaipu.info/ \
                --output data/itaipu/nomina_itaipu_2023-09-03.csv
            python create_or_update_db.py --csv data/itaipu/nomina_itaipu_2023-09-03.csv

            python scrape_itaipu.py \
                --url https://web.archive.org/web/20230508021538/http://nomina.itaipu.info/ \
                --output data/itaipu/nomina_itaipu_2023-05-08.csv
            python create_or_update_db.py --csv data/itaipu/nomina_itaipu_2023-05-08.csv

            python scrape_itaipu.py \
                --url https://web.archive.org/web/20230516195208/http://nomina.itaipu.info/ \
                --output data/itaipu/nomina_itaipu_2023-05-16.csv
            python create_or_update_db.py --csv data/itaipu/nomina_itaipu_2023-05-16.csv

            python create_or_update_db.py --csv data/itaipu/nomina_itaipu_2023-12-16.csv
        fi
        python scrape_itaipu.py
        python create_or_update_db.py
        ;;
    yacyreta)
        python scrape_yacyreta.py
        python create_or_update_db.py --db yacyreta.db --csv "data/yacyreta/nomina_yacyreta_${TODAY}.csv"
        ;;
    *)
        echo "Unknown target: $target" >&2
        usage
        ;;
esac
