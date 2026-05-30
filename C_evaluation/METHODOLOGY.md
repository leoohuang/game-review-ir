# Member C Methodology

## Goal

Member C evaluates whether using Member B's aspect predictions can improve retrieval quality over the original BM25 rankings from Member A.

The final experiment uses:

- 35 aspect queries
- 6 games
- top-10 retrieved reviews per query-game pair
- 210 query-game groups
- 2100 retrieved rows

## Input Chain

### Member A Output

`A_retrieval/results/retrieval_results.csv`

This file contains the BM25 top-10 results for each query-game pair. Important columns include:

- `query_id`
- `aspect`
- `query`
- `game`
- `rank`
- `review_id`
- `bm25_score`
- `review_text`

### Member B Output

`B_classifier/outputs/final_2100_predictions.csv`

This file keeps the retrieval columns and adds:

- `predicted_aspects`

These predicted aspects are the document-side aspect signal used by Member C.

Member B's classifier selection was updated after evaluating four LLM
configurations against the 230-review gold-standard annotation set in
`B_classifier/annotations/final_gold_230.csv`. The best configuration was
Llama 3.3 70B zero-shot with overall Cohen's kappa `0.540`; this is the
classifier used to produce `final_2100_predictions.csv`.

## Systems Compared

### BM25 Baseline

The baseline uses the original `rank` from Member A.

### Aspect-Aware Rerank

The reranked system promotes documents whose `predicted_aspects` contain the target query `aspect`.

Sorting rule:

1. aspect match first
2. higher BM25 score second

## Relevance Definition

The revised project plan does not use full human retrieval relevance annotation or three-level relevance grading.

For aspect-level evaluation, a retrieved review is considered relevant if:

```text
query aspect is in predicted_aspects
```

The binary relevance value is:

| Condition | aspect_relevance |
| --- | ---: |
| query aspect appears in predicted aspects | 1 |
| query aspect does not appear in predicted aspects | 0 |

## Metric

The main metric is aspect-level nDCG@10.

For each query-game group:

1. collect the top-10 ranked rows from each system
2. compute DCG@10 from `aspect_relevance`
3. compute ideal DCG@10 by sorting the same relevance labels
4. divide DCG@10 by ideal DCG@10

## Significance Test

The significance test compares BM25 and aspect-aware reranking over paired query-game nDCG@10 scores.

The script uses a two-sided paired sign-flip permutation test.

## Final Results

| System | Aspect nDCG@10 |
| --- | ---: |
| BM25 baseline | 0.8756 |
| Aspect-aware rerank | 0.9810 |

| Comparison | Mean delta | p-value |
| --- | ---: | ---: |
| Aspect-aware rerank minus BM25 | 0.1053 | 0.0001 |

The result suggests that incorporating LLM-predicted aspect labels improves aspect-focused retrieval quality.

Because the relevance signal is derived from LLM-predicted aspect labels rather
than full human retrieval judgments, these scores should be interpreted as
aspect-consistency evaluation. The expanded 230-review validation increases
confidence in the classifier signal, but residual classification noise remains,
especially for the broad `other` category.
