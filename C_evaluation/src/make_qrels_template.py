"""Create a retrieval relevance annotation template for Member C."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


DEFAULT_INPUT = "B_classifier/outputs/final_2100_predictions.csv"
DEFAULT_OUTPUT = "C_evaluation/data/retrieval_qrels_template.csv"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    columns = [
        "query_id",
        "aspect",
        "query",
        "game",
        "rank",
        "review_id",
        "bm25_score",
        "review_text",
    ]
    missing = set(columns) - set(df.columns)
    if missing:
        raise ValueError(f"Input is missing required columns: {sorted(missing)}")

    template = df[columns].copy()
    template["doc_relevance"] = ""
    template["aspect_relevance"] = ""
    template["annotator"] = ""
    template["notes"] = ""

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    template.to_csv(output, index=False)
    print(f"Saved qrels template to {output}")


if __name__ == "__main__":
    main()
