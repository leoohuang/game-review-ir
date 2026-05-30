# Member B — LLM Aspect Classifier

## Overview

This module implements the LLM-based aspect classification component of the Game Review IR project.

The objective is to automatically identify gameplay-related aspects discussed in Steam reviews using prompt-based Large Language Models (LLMs). The resulting aspect labels are later used to support retrieval evaluation and aspect-aware analysis.

### Implemented Features

- Multi-label aspect classification
- Zero-shot prompting
- Few-shot prompting
- Multiple LLM backbones
- Human annotation and validation
- Inter-annotator agreement analysis
- Human-vs-LLM evaluation
- Large-scale inference over retrieved reviews

---

# Human Annotation

## Phase 1: Shared Annotation

A shared annotation set consisting of **30 reviews** was independently annotated by all four group members.

This dataset was used to:

- Refine annotation guidelines
- Resolve labeling ambiguities
- Compute inter-annotator agreement
- Validate LLM classification quality

## Phase 2: Extended Annotation

After establishing annotation guidelines, each annotator independently labeled **50 additional reviews**.

### Dataset Composition

| Source | Reviews |
|----------|----------|
| Shared Annotation Set | 30 |
| Annotator A | 50 |
| Annotator B | 50 |
| Annotator C | 50 |
| Annotator D | 50 |
| **Total Gold Dataset** | **230** |

Final dataset:

```text
annotations/final_gold_230.csv
```

---

# Aspect Taxonomy

| Aspect | Description |
|----------|----------|
| combat | Gameplay mechanics, bosses, fighting, weapons, builds, difficulty |
| story | Narrative, lore, dialogue, characters, endings |
| graphics | Visual quality, atmosphere, FPS, performance, bugs, world design |
| price | DLC, value, sales, worth buying |
| controls | Movement, responsiveness, driving, aiming, UI, camera |
| other | Emotional or vague opinions without explicit aspect discussion |

The task was implemented as a **multi-label classification problem** because a review may discuss multiple aspects simultaneously.

---

# Prompting Strategies

Two prompting strategies were evaluated.

## Zero-shot Prompting

The model receives:

- Aspect definitions
- Classification instructions
- Review text

No labeled examples are provided.

## Few-shot Prompting

The model receives:

- Aspect definitions
- Multiple labeled examples
- Review text

The goal is to determine whether demonstrations improve classification quality.

---

# Models Evaluated

The following models were evaluated through Berget AI:

| Model | Configuration |
|----------|----------|
| Llama 3.3 70B Instruct | Zero-shot |
| Llama 3.3 70B Instruct | Few-shot |
| Mistral Small 3.2 24B | Zero-shot |
| Mistral Small 3.2 24B | Few-shot |

---

# Evaluation Methodology

The four model configurations were evaluated against the 230-review gold-standard dataset.

### Metric

**Cohen's Kappa (κ)**

### Interpretation

| Kappa | Interpretation |
|----------|----------|
| < 0.20 | Slight |
| 0.20 – 0.40 | Fair |
| 0.40 – 0.60 | Moderate |
| 0.60 – 0.80 | Substantial |
| > 0.80 | Almost Perfect |

---

# Human vs LLM Evaluation Results

## Overall Model Performance

| Model | Overall Kappa |
|----------|----------|
| **Llama Zero-shot** | **0.540** |
| Llama Few-shot | 0.510 |
| Mistral Zero-shot | 0.473 |
| Mistral Few-shot | 0.399 |

### Best Model

**Llama 3.3 70B Zero-shot** achieved the highest agreement with human annotations:

```text
κ = 0.540
```

Therefore, Llama Zero-shot was selected as the final classification model used in downstream experiments.

---

## Per-Aspect Performance

| Aspect | Best Kappa |
|----------|----------|
| Story | 0.767 |
| Graphics | 0.613 |
| Controls | 0.572 |
| Price | 0.539 |
| Combat | 0.502 |
| Other | 0.215 |

### Observations

- Story was the easiest aspect to identify
- Graphics and controls showed consistent performance
- Combat and price achieved moderate agreement
- The "other" category remained difficult due to its subjective nature

---

# Large-Scale Inference

After model selection, the best-performing model (**Llama Zero-shot**) was applied to the full retrieval dataset.

### Dataset

- 2100 retrieved Steam reviews
- Six game domains:
  - Cyberpunk 2077
  - Elden Ring
  - Hades
  - Stardew Valley
  - Titanfall 2
  - Forza Horizon 5

### Output

```text
outputs/final_2100_predictions.csv
```

---

# Output Files

```text
outputs/berget_classified.csv
outputs/berget_classified_230.csv
outputs/llm_kappa_overall.csv
outputs/llm_kappa_per_aspect.csv
outputs/final_2100_predictions.csv
```

---
---

# Analysis Files

The following analysis files were generated during the evaluation process and should be consulted when writing the final report.

## analysis/annotation_230_analysis.txt

Contains statistics for the final 230-review gold-standard dataset, including:

- Total number of annotated reviews
- Aspect frequency distribution
- Per-game aspect distribution
- Multi-label annotation statistics
- Dataset composition summary

This file should be used when writing:

- Dataset Description
- Annotation Statistics
- Aspect Distribution Results

---

## analysis/human_kappa_results.txt

Contains inter-annotator agreement results computed on the shared 30-review annotation set.

Includes:

- Cohen's Kappa scores between annotators
- Human agreement analysis
- Annotation consistency observations

This file should be used when writing:

- Annotation Methodology
- Inter-Annotator Agreement Section

---

## analysis/human_vs_llm_kappa.txt

Contains the final Human vs LLM evaluation results on the 230-review gold-standard dataset.

Includes:

- Per-aspect Cohen's Kappa scores
- Overall model Kappa scores
- Comparison between:
  - Llama Zero-shot
  - Llama Few-shot
  - Mistral Zero-shot
  - Mistral Few-shot

This file should be used when writing:

- Experimental Results
- Model Evaluation
- Human vs LLM Comparison

---

## analysis/2100_data_analysis.txt

Contains statistics generated from the full classified retrieval dataset.

Includes:

- Aspect frequency across 2100 reviews
- Game-wise aspect trends
- Multi-label prediction analysis
- Large-scale dataset observations

This file should be used when writing:

- Large-Scale Analysis
- Discussion Section
- Retrieval Dataset Findings

---

# Main Scripts

```text
src/berget_30_annotation.py
src/compute_kappa_human.py
src/compute_kappa_human_vs_llm.py
src/run_full_2100_llama.py
src/analyze_230_annotations.py
src/merge_annotations.py
```

---

# Conclusion

The experiments demonstrate that prompt-based LLM classification can reliably identify gameplay-related aspects in Steam reviews.

Evaluation on a 230-review gold-standard dataset showed that:

- Llama 3.3 70B Zero-shot achieved the highest agreement with human annotators
- Multi-label classification is necessary for realistic game review analysis
- Prompt-based LLMs can effectively support downstream retrieval and ranking tasks
- Human annotation remains essential for evaluation and validation

The final classifier was successfully integrated into the overall retrieval pipeline and used to support aspect-aware retrieval analysis.