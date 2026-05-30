"""Convert human aspect labels into query-level qrels for overlapping results.

This is useful when the available human annotation file labels reviews by aspect
instead of directly judging each query-result pair. For every retrieved result
whose ``review_id`` appears in the annotation file, the script assigns:

- aspect_relevance = 1 if the query aspect is in the human labels
- aspect_relevance = 0 otherwise

It does not create document-level relevance because the source file does not
contain query-level document usefulness judgments.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


DEFAULT_ANNOTATION = "B_classifier/annotations/final_gold_230.csv"
DEFAULT_RETRIEVAL = "B_classifier/outputs/final_2100_predictions.csv"
DEFAULT_OUTPUT = "C_evaluation/data/aspect_label_qrels.csv"


def parse_labels(value: object) -> set[str]:
    if pd.isna(value):
        return set()

    labels = str(value).lower().replace("\n", ";").replace(",", ";").split(";")
    return {label.strip() for label in labels if label.strip()}


def load_annotations(path: str) -> pd.DataFrame:
    annotation_path = Path(path)
    if annotation_path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(annotation_path)
    return pd.read_csv(annotation_path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotation", default=DEFAULT_ANNOTATION)
    parser.add_argument("--retrieval", default=DEFAULT_RETRIEVAL)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    annotations = load_annotations(args.annotation)
    retrieval = pd.read_csv(args.retrieval)

    label_column = "human_label" if "human_label" in annotations.columns else "aspect_labels"
    required_annotation = {"review_id", label_column}
    required_retrieval = {"query_id", "game", "review_id", "aspect"}
    missing_annotation = required_annotation - set(annotations.columns)
    missing_retrieval = required_retrieval - set(retrieval.columns)
    if missing_annotation:
        raise ValueError(f"Annotation file is missing columns: {sorted(missing_annotation)}")
    if missing_retrieval:
        raise ValueError(f"Retrieval file is missing columns: {sorted(missing_retrieval)}")

    annotations = annotations[["review_id", label_column]].copy()
    annotations["review_id"] = annotations["review_id"].astype(str)
    annotations["human_label_set"] = annotations[label_column].apply(parse_labels)

    judged = retrieval.copy()
    judged["review_id"] = judged["review_id"].astype(str)
    judged["aspect"] = judged["aspect"].astype(str).str.lower()
    judged = judged.merge(annotations[["review_id", "human_label_set"]], on="review_id", how="inner")

    judged["aspect_relevance"] = judged.apply(
        lambda row: 1 if row["aspect"] in row["human_label_set"] else 0,
        axis=1,
    )

    output_columns = ["query_id", "game", "review_id", "aspect_relevance"]
    output = judged[output_columns].drop_duplicates().copy()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(output_path, index=False)

    print(f"Saved {len(output)} qrels rows to {output_path}")
    print(f"Covered {output['review_id'].nunique()} unique annotated reviews.")


if __name__ == "__main__":
    main()
