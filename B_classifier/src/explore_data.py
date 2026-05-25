import pandas as pd

df = pd.read_json("game-review-ir/A_retrieval/results/retrieval_results.json")

print("=== COLUMNS ===")
print(df.columns.tolist())

print("\n=== SIZE ===")
print(f"{len(df)} rows total")

print("\n=== ASPECTS IN DATA ===")
print(df["aspect"].value_counts())

print("\n=== FIRST 3 REVIEWS ===")
for i, row in df.head(3).iterrows():
    print(f"\nAspect: {row['aspect']} | Game: {row['game']}")
    print(f"Query: {row['query']}")
    print(f"Review: {row['review_text'][:200]}")
    print("---")