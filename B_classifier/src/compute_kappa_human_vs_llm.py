import pandas as pd
import ast
import math
from sklearn.metrics import cohen_kappa_score

# =========================
# CONFIG
# =========================

INPUT_FILE = "outputs/berget_classified.csv"

ASPECTS = [
    "combat",
    "story",
    "graphics",
    "price",
    "controls",
    "other"
]

MODELS = [
    "llama_zeroshot",
    "llama_fewshot",
    "mistral_zeroshot",
    "mistral_fewshot"
]

# =========================
# LOAD DATA
# =========================

df = pd.read_csv(INPUT_FILE)

print("\nLoaded rows:", len(df))

# =========================
# ROBUST LABEL PARSER
# =========================

def safe_parse(x):

    if pd.isna(x):
        return []

    text = str(x).lower()

    found = []

    for aspect in ASPECTS:
        if aspect in text:
            found.append(aspect)

    return sorted(list(set(found)))


# =========================
# PARSE ALL COLUMNS
# =========================

df["human_label"] = df["human_label"].apply(safe_parse)

for model in MODELS:
    df[model] = df[model].apply(safe_parse)

# =========================
# DEBUG SAMPLE
# =========================

print("\n===== SAMPLE PREDICTIONS =====\n")

sample_cols = [
    "human_label",
    "llama_zeroshot",
    "llama_fewshot",
    "mistral_zeroshot",
    "mistral_fewshot"
]

print(df[sample_cols].head())

# =========================
# SAFE KAPPA
# =========================

def compute_safe_kappa(y_true, y_pred):

    try:

        # avoid single-label crash
        if len(set(y_true)) <= 1 and len(set(y_pred)) <= 1:
            return 0.0

        kappa = cohen_kappa_score(y_true, y_pred)

        if math.isnan(kappa):
            return 0.0

        return round(kappa, 3)

    except:
        return 0.0

# =========================
# COMPUTE PER-ASPECT KAPPA
# =========================

results = []

print("\n================================================")
print("LLM vs HUMAN KAPPA")
print("================================================\n")

for aspect in ASPECTS:

    print(f"--- {aspect.upper()} ---")

    human_binary = df["human_label"].apply(
        lambda x: 1 if aspect in x else 0
    )

    for model in MODELS:

        pred_binary = df[model].apply(
            lambda x: 1 if aspect in x else 0
        )

        kappa = compute_safe_kappa(
            human_binary.tolist(),
            pred_binary.tolist()
        )

        print(f"{model}: {kappa}")

        results.append({
            "aspect": aspect,
            "model": model,
            "kappa": kappa
        })

    print()

# =========================
# OVERALL KAPPA
# =========================

print("================================================")
print("OVERALL MODEL KAPPA")
print("================================================\n")

overall_results = []

for model in MODELS:

    all_human = []
    all_pred = []

    for aspect in ASPECTS:

        human_binary = df["human_label"].apply(
            lambda x: 1 if aspect in x else 0
        )

        pred_binary = df[model].apply(
            lambda x: 1 if aspect in x else 0
        )

        all_human.extend(human_binary.tolist())
        all_pred.extend(pred_binary.tolist())

    overall_kappa = compute_safe_kappa(
        all_human,
        all_pred
    )

    overall_results.append({
        "model": model,
        "overall_kappa": overall_kappa
    })

    print(f"{model}: {overall_kappa}")

# =========================
# SAVE RESULTS
# =========================

results_df = pd.DataFrame(results)

overall_df = pd.DataFrame(overall_results)

results_df.to_csv(
    "outputs/llm_kappa_per_aspect.csv",
    index=False
)

overall_df.to_csv(
    "outputs/llm_kappa_overall.csv",
    index=False
)

print("\nSaved:")
print("- outputs/llm_kappa_per_aspect.csv")
print("- outputs/llm_kappa_overall.csv")

print("\nKappa guide:")
print("<0.2 slight")
print("0.2-0.4 fair")
print("0.4-0.6 moderate")
print("0.6-0.8 substantial")
print(">0.8 almost perfect")