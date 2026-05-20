# Member B — LLM Aspect Classifier

## What this does
Classifies Steam game reviews by aspect (combat, story, graphics, price, controls)
using Llama 3(llama-3.1-8b-instant) via Groq API. Compares zero-shot vs few-shot prompting.

## Files
- src/classify_aspects.py — prompt design and single review classifier
- src/run_pipeline.py — batch pipeline for all 2100 reviews
- src/compute_kappa.py — Cohen's kappa results
- src/find_errors.py — error analysis

## Key Results
| Aspect   | Kappa (zero-shot) | Kappa (few-shot) |
|----------|-------------------|------------------|
| combat   | 0.297             | 0.313            |
| story    | 0.182             | 0.140            |
| graphics | 0.221             | 0.193            |
| price    | 0.429             | 0.333            |
| controls | 0.319             | 0.324            |
| OVERALL  | 0.281             | 0.250            |

Overall fair agreement. Zero-shot outperforms few-shot overall.
Error rate: 28.2% (593/2100 reviews misclassified).