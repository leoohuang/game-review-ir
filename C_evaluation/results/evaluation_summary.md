# Member C Evaluation Summary

Relevance source: `query_aspect_from_llm_predictions`

## Overall nDCG

| system | relevance_type | mean_ndcg | std_ndcg | groups |
| --- | --- | --- | --- | --- |
| aspect_aware_rerank | aspect | 0.9810 | 0.1370 | 210 |
| bm25 | aspect | 0.8756 | 0.2100 | 210 |

## Significance Tests

| relevance_type | baseline_system | candidate_system | mean_baseline | mean_candidate | mean_delta | paired_permutation_p | groups |
| --- | --- | --- | --- | --- | --- | --- | --- |
| aspect | bm25 | aspect_aware_rerank | 0.8756 | 0.9810 | 0.1053 | 0.0001 | 210 |
