import pandas as pd
import ast
from sklearn.metrics import cohen_kappa_score

df = pd.read_csv("outputs/classified_reviews.csv")

ASPECTS = ["combat", "story", "graphics", "price", "controls"]

# ── Parse LLM label strings into actual lists ─────────────────────────────────
def parse_labels(val):
    try:
        if pd.isna(val) or str(val).strip() == '[]' or str(val).strip() == '':
            return []
        result = ast.literal_eval(str(val))
        return [l for l in result if l in ASPECTS]
    except:
        return []

df["zero_parsed"] = df["llm_zeroshot"].apply(parse_labels)
df["few_parsed"]  = df["llm_fewshot"].apply(parse_labels)

# ── For each aspect: ground truth = 1 if query aspect matches, LLM = 1 if aspect in prediction
print("=" * 65)
print(f"{'ASPECT':<12} {'KAPPA (zero-shot)':>18} {'KAPPA (few-shot)':>18} {'N':>6}")
print("=" * 65)

results = []

for aspect in ASPECTS:
    # Ground truth: 1 if this row's query was about this aspect
    ground_truth = (df["aspect"] == aspect).astype(int).tolist()

    # LLM zero-shot: 1 if LLM predicted this aspect
    zero_pred = df["zero_parsed"].apply(lambda x: 1 if aspect in x else 0).tolist()
    few_pred  = df["few_parsed"].apply(lambda x: 1 if aspect in x else 0).tolist()

    k_zero = cohen_kappa_score(ground_truth, zero_pred)
    k_few  = cohen_kappa_score(ground_truth, few_pred)

    print(f"{aspect:<12} {k_zero:>18.3f} {k_few:>18.3f} {len(df):>6}")
    results.append({"aspect": aspect, "kappa_zeroshot": round(k_zero,3), "kappa_fewshot": round(k_few,3)})

print("=" * 65)

# Overall kappa (all aspects combined)
all_gt   = []
all_zero = []
all_few  = []

for aspect in ASPECTS:
    all_gt   += (df["aspect"] == aspect).astype(int).tolist()
    all_zero += df["zero_parsed"].apply(lambda x: 1 if aspect in x else 0).tolist()
    all_few  += df["few_parsed"].apply(lambda x: 1 if aspect in x else 0).tolist()

overall_zero = cohen_kappa_score(all_gt, all_zero)
overall_few  = cohen_kappa_score(all_gt, all_few)
print(f"{'OVERALL':<12} {overall_zero:>18.3f} {overall_few:>18.3f}")
print("=" * 65)

print("\nKappa interpretation:")
print("  < 0.20 = slight agreement")
print("  0.21–0.40 = fair agreement")
print("  0.41–0.60 = moderate agreement")
print("  0.61–0.80 = substantial agreement")
print("  > 0.80 = almost perfect agreement")

# Save results
results_df = pd.DataFrame(results)
results_df.loc[len(results_df)] = {"aspect": "OVERALL", "kappa_zeroshot": round(overall_zero,3), "kappa_fewshot": round(overall_few,3)}
results_df.to_csv("outputs/kappa_results.csv", index=False)
print("\nSaved to outputs/kappa_results.csv")