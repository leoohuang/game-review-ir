"""Evaluate BM25 and aspect-aware reranking with nDCG@10.

The script can run in two modes:
1. Official mode: pass a qrels CSV with human ``doc_relevance`` and/or
   ``aspect_relevance`` labels.
2. Query-aspect mode: omit qrels and derive aspect relevance by checking
   whether the LLM-predicted review aspects contain the current query aspect.

The project plan no longer requires full retrieval qrels. Query-aspect mode is
therefore the default experiment used for the 35-query comparison.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


KEY_COLUMNS = ["query_id", "game", "review_id"]
DEFAULT_INPUT = "B_classifier/outputs/final_2100_predictions.csv"
DEFAULT_OUTPUT_DIR = "C_evaluation/results"


def parse_labels(value: object) -> set[str]:
    """Parse labels stored as Python-list strings or semicolon strings."""
    if pd.isna(value):
        return set()

    text = str(value).strip()
    if not text:
        return set()

    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, str):
            return {parsed.strip().lower()} if parsed.strip() else set()
        if isinstance(parsed, Iterable):
            return {str(item).strip().lower() for item in parsed if str(item).strip()}
    except (ValueError, SyntaxError):
        pass

    return {part.strip().lower() for part in text.replace(",", ";").split(";") if part.strip()}


def dcg(relevances: Iterable[float]) -> float:
    return sum((2**rel - 1) / math.log2(idx + 2) for idx, rel in enumerate(relevances))


def ndcg_at_k(relevances: Iterable[float], k: int = 10) -> float:
    values = list(relevances)[:k]
    if not values:
        return 0.0

    ideal = sorted(values, reverse=True)
    ideal_dcg = dcg(ideal)
    if ideal_dcg == 0:
        return 0.0
    return dcg(values) / ideal_dcg


def load_predictions(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"query_id", "aspect", "game", "rank", "review_id", "bm25_score", "predicted_aspects"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Input is missing required columns: {sorted(missing)}")

    df = df.copy()
    df["aspect"] = df["aspect"].astype(str).str.lower()
    df["predicted_label_set"] = df["predicted_aspects"].apply(parse_labels)
    df["aspect_match"] = df.apply(lambda row: row["aspect"] in row["predicted_label_set"], axis=1)
    return df


def attach_relevance(df: pd.DataFrame, qrels_path: str | None) -> tuple[pd.DataFrame, str]:
    df = df.copy()

    if qrels_path:
        qrels = pd.read_csv(qrels_path)
        missing_keys = set(KEY_COLUMNS) - set(qrels.columns)
        if missing_keys:
            raise ValueError(f"Qrels file is missing key columns: {sorted(missing_keys)}")

        relevance_cols = [col for col in ["doc_relevance", "aspect_relevance"] if col in qrels.columns]
        if not relevance_cols:
            raise ValueError("Qrels file must contain doc_relevance and/or aspect_relevance.")

        qrels = qrels[KEY_COLUMNS + relevance_cols].copy()
        merged = df.merge(qrels, on=KEY_COLUMNS, how="left")
        judged_mask = merged[relevance_cols].notna().any(axis=1)
        dropped = int((~judged_mask).sum())
        if dropped:
            print(f"Dropped {dropped} unjudged rows that were not present in qrels.")
        merged = merged[judged_mask].copy()
        for col in relevance_cols:
            merged[col] = pd.to_numeric(merged[col], errors="coerce").fillna(0)
        return merged, "human_qrels"

    # Query-aspect relevance for the final project setup:
    # a retrieved review is relevant when the best LLM classifier says it contains
    # the aspect requested by the query.
    df["aspect_relevance"] = np.where(df["aspect_match"], 2, 0)
    return df, "query_aspect_from_llm_predictions"


def add_system_ranks(df: pd.DataFrame) -> pd.DataFrame:
    bm25 = df.copy()
    bm25["system"] = "bm25"
    bm25["system_rank"] = bm25["rank"].astype(int)

    reranked = df.sort_values(
        ["query_id", "game", "aspect_match", "bm25_score"],
        ascending=[True, True, False, False],
    ).copy()
    reranked["system"] = "aspect_aware_rerank"
    reranked["system_rank"] = reranked.groupby(["query_id", "game"]).cumcount() + 1

    return pd.concat([bm25, reranked], ignore_index=True)


def compute_group_metrics(ranked: pd.DataFrame, k: int) -> pd.DataFrame:
    rows = []
    relevance_cols = [col for col in ["doc_relevance", "aspect_relevance"] if col in ranked.columns]

    group_cols = ["system", "query_id", "game", "aspect"]
    for keys, group in ranked.groupby(group_cols, sort=True):
        group = group.sort_values("system_rank")
        base = dict(zip(group_cols, keys))
        for rel_col in relevance_cols:
            rows.append(
                {
                    **base,
                    "metric": f"ndcg@{k}",
                    "relevance_type": rel_col.replace("_relevance", ""),
                    "score": ndcg_at_k(group[rel_col].tolist(), k=k),
                }
            )

    return pd.DataFrame(rows)


def paired_permutation_pvalue(baseline: np.ndarray, candidate: np.ndarray, seed: int = 42) -> float:
    """Two-sided paired sign-flip permutation test for mean difference."""
    diff = candidate - baseline
    diff = diff[~np.isnan(diff)]
    if len(diff) == 0:
        return float("nan")

    observed = abs(float(np.mean(diff)))
    if observed == 0:
        return 1.0

    rng = np.random.default_rng(seed)
    n = len(diff)
    if n <= 20:
        signs = np.array(np.meshgrid(*[[-1, 1]] * n)).T.reshape(-1, n)
    else:
        signs = rng.choice([-1, 1], size=(10000, n))

    sampled = np.abs((signs * diff).mean(axis=1))
    return float((np.sum(sampled >= observed) + 1) / (len(sampled) + 1))


def summarize_metrics(group_metrics: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    overall = (
        group_metrics.groupby(["system", "relevance_type"], as_index=False)
        .agg(mean_ndcg=("score", "mean"), std_ndcg=("score", "std"), groups=("score", "size"))
        .sort_values(["relevance_type", "system"])
    )

    by_aspect = (
        group_metrics.groupby(["aspect", "system", "relevance_type"], as_index=False)
        .agg(mean_ndcg=("score", "mean"), std_ndcg=("score", "std"), groups=("score", "size"))
        .sort_values(["relevance_type", "aspect", "system"])
    )

    pivot_keys = ["query_id", "game", "aspect", "relevance_type"]
    wide = group_metrics.pivot_table(index=pivot_keys, columns="system", values="score", aggfunc="mean").reset_index()

    significance_rows = []
    for rel_type, subset in wide.groupby("relevance_type"):
        if {"bm25", "aspect_aware_rerank"}.issubset(subset.columns):
            baseline = subset["bm25"].to_numpy(dtype=float)
            candidate = subset["aspect_aware_rerank"].to_numpy(dtype=float)
            significance_rows.append(
                {
                    "relevance_type": rel_type,
                    "baseline_system": "bm25",
                    "candidate_system": "aspect_aware_rerank",
                    "mean_baseline": float(np.nanmean(baseline)),
                    "mean_candidate": float(np.nanmean(candidate)),
                    "mean_delta": float(np.nanmean(candidate - baseline)),
                    "paired_permutation_p": paired_permutation_pvalue(baseline, candidate),
                    "groups": int(len(subset)),
                }
            )

    significance = pd.DataFrame(significance_rows)
    return overall, by_aspect, significance


def write_outputs(
    ranked: pd.DataFrame,
    group_metrics: pd.DataFrame,
    overall: pd.DataFrame,
    by_aspect: pd.DataFrame,
    significance: pd.DataFrame,
    output_dir: str,
    relevance_source: str,
) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    ranked.drop(columns=["predicted_label_set"], errors="ignore").to_csv(out / "ranked_system_outputs.csv", index=False)
    group_metrics.to_csv(out / "ndcg_by_query_game.csv", index=False)
    overall.to_csv(out / "overall_results.csv", index=False)
    by_aspect.to_csv(out / "per_aspect_results.csv", index=False)
    significance.to_csv(out / "significance_tests.csv", index=False)

    with (out / "evaluation_summary.md").open("w", encoding="utf-8") as f:
        f.write("# Member C Evaluation Summary\n\n")
        f.write(f"Relevance source: `{relevance_source}`\n\n")
        f.write("## Overall nDCG\n\n")
        f.write(frame_to_markdown(overall))
        f.write("\n\n## Significance Tests\n\n")
        f.write(frame_to_markdown(significance))
        f.write("\n")


def frame_to_markdown(df: pd.DataFrame) -> str:
    """Render a small DataFrame as a GitHub-style Markdown table."""
    if df.empty:
        return "_No rows._"

    display = df.copy()
    for col in display.select_dtypes(include=[float]).columns:
        display[col] = display[col].map(lambda value: f"{value:.4f}")

    headers = [str(col) for col in display.columns]
    rows = [[str(value) for value in row] for row in display.to_numpy()]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=DEFAULT_INPUT, help="B classifier output CSV.")
    parser.add_argument("--qrels", default=None, help="Optional human qrels CSV.")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--k", type=int, default=10)
    args = parser.parse_args()

    predictions = load_predictions(args.input)
    judged, relevance_source = attach_relevance(predictions, args.qrels)
    ranked = add_system_ranks(judged)
    group_metrics = compute_group_metrics(ranked, k=args.k)
    overall, by_aspect, significance = summarize_metrics(group_metrics)

    write_outputs(ranked, group_metrics, overall, by_aspect, significance, args.output_dir, relevance_source)

    print(f"Relevance source: {relevance_source}")
    print(f"Evaluated {group_metrics[['query_id', 'game']].drop_duplicates().shape[0]} query-game groups.")
    print(f"Saved evaluation tables to {args.output_dir}")


if __name__ == "__main__":
    main()
