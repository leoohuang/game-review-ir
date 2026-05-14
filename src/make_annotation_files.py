"""Create annotation templates for teammates B/C.

Outputs:
- annotation/retrieval_annotation_template.csv
- annotation/aspect_annotation_sample.csv
"""
import argparse
from pathlib import Path

import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--retrieval", default="results/retrieval_results.csv")
    parser.add_argument("--corpus", default="data/processed/clean_reviews.csv")
    parser.add_argument("--retrieval-out", default="annotation/retrieval_annotation_template.csv")
    parser.add_argument("--aspect-out", default="annotation/aspect_annotation_sample.csv")
    parser.add_argument("--aspect-sample-n", type=int, default=200)
    args = parser.parse_args()

    retrieval = pd.read_csv(args.retrieval)
    retrieval_template = retrieval.copy()
    retrieval_template["doc_relevance"] = ""
    retrieval_template["aspect_relevance"] = ""
    retrieval_template["annotator"] = ""
    retrieval_template["notes"] = ""
    Path(args.retrieval_out).parent.mkdir(parents=True, exist_ok=True)
    retrieval_template.to_csv(args.retrieval_out, index=False)

    corpus = pd.read_csv(args.corpus)
    n = min(args.aspect_sample_n, len(corpus))
    aspect_sample = corpus.sample(n=n, random_state=42)[["review_id", "game", "review_text"]].copy()
    for col in ["combat", "story", "graphics", "price", "controls", "other"]:
        aspect_sample[col] = ""
    aspect_sample["annotator"] = ""
    aspect_sample["notes"] = ""
    aspect_sample.to_csv(args.aspect_out, index=False)

    print(f"Saved {args.retrieval_out}")
    print(f"Saved {args.aspect_out}")


if __name__ == "__main__":
    main()
