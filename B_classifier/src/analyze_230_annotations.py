import pandas as pd
from collections import Counter

# Load dataset
df = pd.read_csv(
    "./game-review-ir/B_classifier/annotations/final_gold_230.csv"
)

print("=" * 40)
print("DATASET OVERVIEW")
print("=" * 40)

print("Total reviews:", len(df))
print("Unique review IDs:", df["review_id"].nunique())

# -------------------------
# Aspect distribution
# -------------------------

aspect_counter = Counter()

for labels in df["aspect_labels"].fillna(""):
    for label in str(labels).split(";"):
        label = label.strip().lower()

        if label:
            aspect_counter[label] += 1

print("\n" + "=" * 40)
print("ASPECT DISTRIBUTION")
print("=" * 40)

for aspect, count in aspect_counter.most_common():
    pct = count / len(df) * 100
    print(f"{aspect:10s}: {count:3d} reviews ({pct:.2f}%)")

# -------------------------
# Per-game distribution
# -------------------------

print("\n" + "=" * 40)
print("PER-GAME DISTRIBUTION")
print("=" * 40)

for game in sorted(df["game"].unique()):

    print(f"\n--- {game} ---")

    game_df = df[df["game"] == game]

    counter = Counter()

    for labels in game_df["aspect_labels"].fillna(""):
        for label in str(labels).split(";"):
            label = label.strip().lower()

            if label:
                counter[label] += 1

    for aspect, count in counter.most_common():
        print(f"{aspect}: {count}")

# -------------------------
# Multi-label statistics
# -------------------------

multi = 0

for labels in df["aspect_labels"].fillna(""):
    n = len([
        x.strip()
        for x in str(labels).split(";")
        if x.strip()
    ])

    if n > 1:
        multi += 1

print("\n" + "=" * 40)
print("MULTI-LABEL STATISTICS")
print("=" * 40)

print("Reviews with multiple aspects:", multi)
print(
    "Percentage:",
    round(100 * multi / len(df), 2),
    "%"
)

# -------------------------
# Save summary
# -------------------------

with open(
    "./game-review-ir/B_classifier/analysis/annotation_230_analysis.txt",
    "w",
    encoding="utf-8"
) as f:

    f.write(f"Total reviews: {len(df)}\n")
    f.write(
        f"Unique review IDs: {df['review_id'].nunique()}\n\n"
    )

    f.write("Aspect Distribution\n")
    f.write("-" * 30 + "\n")

    for aspect, count in aspect_counter.most_common():
        pct = count / len(df) * 100
        f.write(
            f"{aspect}: {count} ({pct:.2f}%)\n"
        )

    f.write("\n")
    f.write(
        f"Multi-label reviews: {multi}\n"
    )
    f.write(
        f"Percentage: {100 * multi / len(df):.2f}%\n"
    )

print("\nSaved:")
print(
    "./game-review-ir/B_classifier/analysis/annotation_230_analysis.txt"
)