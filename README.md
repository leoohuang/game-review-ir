# Game Review IR

## Project Pipeline

The project is organized as a four-part IR pipeline:

1. **Member A — Retrieval corpus and BM25**: collect Steam reviews, clean the text, define 35 aspect queries, and retrieve top-10 reviews for each query-game pair.
2. **Member B — Aspect classification**: classify each retrieved review into gameplay aspects using the best LLM setup, producing aspect labels for all 2100 retrieved rows.
3. **Member C — Evaluation metrics**: compare the original BM25 ranking with an aspect-aware reranking that promotes reviews whose predicted aspects match the query aspect. The main metric is aspect-level nDCG@10 over 35 queries and 6 games.
4. **Member D — Demo and paper**: integrate the pipeline outputs into the demo, paper, and presentation.

## Member Division

| Member | Primary Role | Specific Tasks |
| --- | --- | --- |
| Member A | Data & Corpus | Download and preprocess the Steam reviews dataset; filter non-English reviews, short reviews, and HTML tags; build the BM25 index; construct the 35-query set |
| Member B | LLM Aspect Classifier | Design the prompt; implement the batch classification pipeline; validate on the 230-review gold-standard subset; compute Cohen's kappa; conduct error analysis |
| Member C | Evaluation Metrics | Implement aspect-level nDCG@10; run the comparison experiment over 35 queries; conduct significance testing; produce the core results tables |
| Member D | Demo & Paper | Develop the Streamlit demo with side-by-side comparison view; lead paper writing and presentation slides; integrate outputs from all modules |

## Current Member C Results

Member C's final setup uses `B_classifier/outputs/final_2100_predictions.csv` as input. A retrieved review is treated as aspect-relevant when its LLM-predicted aspect labels contain the target aspect of the query. The aspect classifier was selected after Member B's 230-review Human-vs-LLM evaluation; the best configuration is Llama 3.3 70B zero-shot with overall Cohen's kappa `0.540`.

| System | Aspect nDCG@10 |
| --- | ---: |
| BM25 baseline | 0.8756 |
| Aspect-aware rerank | 0.9810 |

The paired permutation test over 210 query-game groups gives `p = 0.0001`, indicating a statistically significant improvement for aspect-aware reranking.

Detailed result tables are in `C_evaluation/results/`.
