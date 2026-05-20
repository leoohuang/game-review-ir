import pandas as pd
import ast

df = pd.read_csv("outputs/classified_reviews.csv")

ASPECTS = ["combat", "story", "graphics", "price", "controls"]

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

# ── Find cases where LLM missed the true aspect ───────────────────────────────
errors = []

for _, row in df.iterrows():
    true_aspect = row["aspect"]
    zero_hit = true_aspect in row["zero_parsed"]
    few_hit  = true_aspect in row["few_parsed"]

    if not zero_hit or not few_hit:
        errors.append({
            "review_id":    row["review_id"],
            "game":         row["game"],
            "true_aspect":  true_aspect,
            "llm_zeroshot": row["zero_parsed"],
            "llm_fewshot":  row["few_parsed"],
            "zero_correct": zero_hit,
            "few_correct":  few_hit,
            "review_text":  row["review_text"][:300]
        })

errors_df = pd.DataFrame(errors)
errors_df.to_csv("outputs/error_cases.csv", index=False)
print(f"Total error cases: {len(errors_df)} out of {len(df)} rows")
print(f"Error rate: {round(len(errors_df)/len(df)*100, 1)}%")

# ── Show 3 interesting examples per aspect ────────────────────────────────────
print("\n" + "=" * 70)
print("SAMPLE ERROR CASES BY ASPECT")
print("=" * 70)

for aspect in ASPECTS:
    subset = errors_df[errors_df["true_aspect"] == aspect].head(3)
    print(f"\n--- {aspect.upper()} ({len(errors_df[errors_df['true_aspect']==aspect])} errors) ---")
    for _, row in subset.iterrows():
        print(f"  Game: {row['game']}")
        print(f"  LLM zero-shot: {row['llm_zeroshot']} | few-shot: {row['llm_fewshot']}")
        print(f"  Review: {row['review_text'][:150]}...")
        print()

print("Saved to outputs/error_cases.csv")