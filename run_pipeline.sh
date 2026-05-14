#!/usr/bin/env bash
set -e

python src/fetch_reviews.py --config config/games.yaml
python src/run_bm25.py --corpus data/processed/clean_reviews.csv --queries config/queries.csv --top-k 10
python src/make_annotation_files.py

echo "Pipeline completed. Check data/processed, results, and annotation folders."
