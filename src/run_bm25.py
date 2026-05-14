"""Run BM25 retrieval for each configured query within each game corpus."""
import argparse
from pathlib import Path

import pandas as pd
from rank_bm25 import BM25Okapi
from tqdm import tqdm

from utils import tokenize, ensure_dirs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", default="data/processed/clean_reviews.csv")
    parser.add_argument("--queries", default="config/queries.csv")
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--out-csv", default="results/retrieval_results.csv")
    parser.add_argument("--out-json", default="results/retrieval_results.json")
    args = parser.parse_args()

    ensure_dirs()
    corpus = pd.read_csv(args.corpus)
    queries = pd.read_csv(args.queries)

    required_corpus = {"review_id", "game", "review_text"}
    required_queries = {"query_id", "aspect", "query"}
    if not required_corpus.issubset(corpus.columns):
        raise ValueError(f"Corpus missing columns: {required_corpus - set(corpus.columns)}")
    if not required_queries.issubset(queries.columns):
        raise ValueError(f"Queries missing columns: {required_queries - set(queries.columns)}")

    results = []
    for game, gdf in tqdm(list(corpus.groupby("game")), desc="Games"):
        docs = gdf["review_text"].fillna("").tolist()
        tokenized_docs = [tokenize(d) for d in docs]
        bm25 = BM25Okapi(tokenized_docs)

        for _, q in queries.iterrows():
            q_tokens = tokenize(q["query"])
            scores = bm25.get_scores(q_tokens)
            top_indices = scores.argsort()[::-1][: args.top_k]
            for rank, idx in enumerate(top_indices, start=1):
                row = gdf.iloc[int(idx)]
                results.append({
                    "query_id": q["query_id"],
                    "aspect": q["aspect"],
                    "query": q["query"],
                    "game": game,
                    "rank": rank,
                    "review_id": row["review_id"],
                    "app_id": row.get("app_id", ""),
                    "bm25_score": float(scores[int(idx)]),
                    "review_text": row["review_text"],
                })

    out = pd.DataFrame(results)
    Path(args.out_csv).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out_csv, index=False)
    out.to_json(args.out_json, orient="records", indent=2, force_ascii=False)
    print(f"Saved {len(out)} retrieval rows to {args.out_csv} and {args.out_json}")


if __name__ == "__main__":
    main()
