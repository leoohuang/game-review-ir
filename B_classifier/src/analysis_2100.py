import pandas as pd
import ast
from collections import Counter

INPUT_FILE = "outputs/final_2100_predictions.csv"

df = pd.read_csv(INPUT_FILE)

# =========================
# SAFE PARSE
# =========================

def parse_labels(x):

    try:
        return ast.literal_eval(str(x))
    except:
        return []

df["predicted_aspects"] = df["predicted_aspects"].apply(parse_labels)

# =========================
# COUNT ASPECTS
# =========================

counter = Counter()

for labels in df["predicted_aspects"]:

    for label in labels:
        counter[label] += 1

print("\n==============================")
print("ASPECT DISTRIBUTION")
print("==============================\n")

for aspect, count in counter.most_common():

    percent = round((count / len(df)) * 100, 2)

    print(f"{aspect}: {count} reviews ({percent}%)")

# =========================
# PER GAME
# =========================

if "game" in df.columns:

    print("\n==============================")
    print("PER-GAME DISTRIBUTION")
    print("==============================\n")

    games = df["game"].unique()

    for game in games:

        print(f"\n--- {game} ---")

        subset = df[df["game"] == game]

        game_counter = Counter()

        for labels in subset["predicted_aspects"]:

            for label in labels:
                game_counter[label] += 1

        for aspect, count in game_counter.most_common():

            print(f"{aspect}: {count}")

# =========================
# MULTI-LABEL STATS
# =========================

multi_count = 0

for labels in df["predicted_aspects"]:

    if len(labels) > 1:
        multi_count += 1

print("\n==============================")
print("MULTI-LABEL STATISTICS")
print("==============================\n")

print(f"Reviews with multiple aspects: {multi_count}")
print(f"Percentage: {round((multi_count/len(df))*100, 2)}%")