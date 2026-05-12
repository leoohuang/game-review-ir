# Game Review IR

## Member Division

| Member | Primary Role | Specific Tasks |
| --- | --- | --- |
| Member A | Data & Corpus | Download and preprocess the Steam reviews dataset; filter non-English reviews, short reviews, and HTML tags; build the BM25 index; construct the 50-query set |
| Member B | LLM Aspect Classifier | Design the prompt; implement the batch classification pipeline; validate on the 200-review annotated subset; compute Cohen's kappa; conduct error analysis |
| Member C | Evaluation Metrics | Implement document-level and aspect-level nDCG@10; run the comparison experiment over 50 queries; conduct significance testing; produce the core results tables |
| Member D | Demo & Paper | Develop the Streamlit demo with side-by-side comparison view; lead paper writing and presentation slides; integrate outputs from all modules |
