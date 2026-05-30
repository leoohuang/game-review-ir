# Member C — Evaluation Metrics

## Role

This module evaluates whether aspect-aware reranking improves Steam review retrieval quality over the BM25 baseline.

The project now uses **35 aspect queries**: 7 queries for each of graphics, story, combat, price, and controls.

## Systems Compared

| System | Ranking method |
|---|---|
| BM25 baseline | Uses the original ranking from `A_retrieval/results/retrieval_results.csv` |
| Aspect-aware rerank | Moves reviews whose LLM-predicted aspects contain the query aspect above non-matching reviews, then breaks ties by BM25 score |

## Metrics

The main metric is nDCG@10.

Two relevance views are supported:

| Relevance type | Meaning |
|---|---|
| `doc_relevance` | Optional human qrels field: whether the review is useful/relevant for the query overall |
| `aspect_relevance` | Whether the review discusses the requested aspect |

The final project plan does not require full human retrieval qrels. Instead, C evaluates binary aspect-level retrieval by using each query's aspect as the ground truth target and Member B's final LLM aspect labels as the document aspect signal.

Member B's final classifier was selected using the expanded 230-review gold set (`B_classifier/annotations/final_gold_230.csv`). The selected model is Llama 3.3 70B zero-shot with overall Human-vs-LLM Cohen's kappa `0.540`.

The script still supports optional human qrels if the team later decides to add retrieval-level judgments.

## Inputs

Default classifier output:

```text
B_classifier/outputs/final_2100_predictions.csv
```

Optional human qrels file:

```text
C_evaluation/data/retrieval_qrels.csv
```

Optional qrels columns:

```text
query_id,game,review_id,doc_relevance
query_id,game,review_id,aspect_relevance
```

At least one of `doc_relevance` or `aspect_relevance` is required when using `--qrels`.

Use binary labels:

| Label | Meaning |
|---|---|
| 0 | aspect absent / not relevant |
| 1 | aspect present / relevant |

## Run

Install dependencies from the repository root:

```bash
python3 -m pip install -r C_evaluation/requirements.txt
```

Run the final 35-query aspect evaluation:

```bash
python3 C_evaluation/src/evaluate_ndcg.py
```

Create a retrieval qrels annotation template:

```bash
python3 C_evaluation/src/make_qrels_template.py
```

Optional: run with human retrieval qrels if they are available:

```bash
python3 C_evaluation/src/evaluate_ndcg.py \
  --qrels C_evaluation/data/retrieval_qrels.csv
```

If the available human file is the 230-review aspect annotation CSV, convert it first:

```bash
python3 C_evaluation/src/convert_aspect_labels_to_qrels.py \
  --annotation B_classifier/annotations/final_gold_230.csv

python3 C_evaluation/src/evaluate_ndcg.py \
  --qrels C_evaluation/data/aspect_label_qrels.csv
```

This conversion only evaluates retrieved rows whose `review_id` appears in the aspect annotation file. It is useful as an annotated sanity check, while the main C result is the 35-query aspect evaluation above.

## Outputs

```text
C_evaluation/results/ranked_system_outputs.csv
C_evaluation/results/ndcg_by_query_game.csv
C_evaluation/results/overall_results.csv
C_evaluation/results/per_aspect_results.csv
C_evaluation/results/significance_tests.csv
C_evaluation/results/evaluation_summary.md
```

## Significance Testing

The script uses a two-sided paired sign-flip permutation test over query-game nDCG scores. Each query-game pair is one paired observation comparing BM25 with aspect-aware reranking.
