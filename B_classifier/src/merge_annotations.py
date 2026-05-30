import pandas as pd

BASE = "./game-review-ir/B_classifier/annotations"

# ----------------------------------
# Load shared 30-review gold set
# ----------------------------------
gold = pd.read_csv(f"{BASE}/final_gold.csv")

gold = gold[
    ["review_id", "game", "review_text", "human_label"]
].copy()

gold = gold.rename(
    columns={"human_label": "aspect_labels"}
)

# ----------------------------------
# Load individual annotator files
# ----------------------------------
dfs = []

for fname in [
    "annotator_A.csv",
    "annotator_B.csv",
    "annotator_C.csv",
    "annotator_D.csv"
]:
    try:
        df = pd.read_csv(f"{BASE}/{fname}")
    except:
        df = pd.read_csv(
            f"{BASE}/{fname}",
            encoding="latin1"
        )

    df = df[
        ["review_id", "game", "review_text", "aspect_labels"]
    ].copy()

    dfs.append(df)

# ----------------------------------
# Merge all annotations
# ----------------------------------
final_df = pd.concat(
    [gold] + dfs,
    ignore_index=True
)

# Remove duplicates if any
final_df = final_df.drop_duplicates(
    subset=["review_id"]
)

print("Total reviews:", len(final_df))

# Save
final_df.to_csv(
    f"{BASE}/final_gold_230.csv",
    index=False
)

print("Saved:")
print(f"{BASE}/final_gold_230.csv")


# ------- Quick check of the merged file ---------
import pandas as pd

df = pd.read_csv(
    "./game-review-ir/B_classifier/annotations/final_gold_230.csv"
)

print(df.shape)
print(df.head())