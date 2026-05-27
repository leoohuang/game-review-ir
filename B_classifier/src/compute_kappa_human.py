import pandas as pd
from sklearn.metrics import cohen_kappa_score

df = pd.read_csv("annotations/aspect_annotation_30.csv", skiprows=1)
df.columns = ["review_id","game","review_text","annotator_A","annotator_B","annotator_C","annotator_D"]

ASPECTS = ["combat", "story", "graphics", "price", "controls"]

def parse(val):
    if pd.isna(val) or str(val).strip() == "":
        return []
    val = str(val).lower()
    val = val.replace(";", ",").replace("\n", "")
    return [a.strip() for a in val.split(",") if a.strip() in ASPECTS]

df["A"] = df["annotator_A"].apply(parse)
df["B"] = df["annotator_B"].apply(parse)
df["C"] = df["annotator_C"].apply(parse)
df["D"] = df["annotator_D"].apply(parse)

annotators = {"kaki": df["A"], "Tan": df["B"], "tianle": df["C"], "Tanjila": df["D"]}

print("=" * 60)
print("INTER-ANNOTATOR KAPPA (per aspect)")
print("=" * 60)

pairs = [("kaki","Tan"), ("kaki","tianle"), ("kaki","Tanjila"),
         ("Tan","tianle"), ("Tan","Tanjila"), ("tianle","Tanjila")]

for aspect in ASPECTS:
    print(f"\n--- {aspect.upper()} ---")
    for a1, a2 in pairs:
        v1 = annotators[a1].apply(lambda x: 1 if aspect in x else 0).tolist()
        v2 = annotators[a2].apply(lambda x: 1 if aspect in x else 0).tolist()
        try:
            k = cohen_kappa_score(v1, v2)
            print(f"  {a1} vs {a2}: {k:.3f}")
        except:
            print(f"  {a1} vs {a2}: N/A (no variation)")

print("\n" + "=" * 60)
print("OVERALL KAPPA (all aspects combined)")
print("=" * 60)

for a1, a2 in pairs:
    all_v1, all_v2 = [], []
    for aspect in ASPECTS:
        all_v1 += annotators[a1].apply(lambda x: 1 if aspect in x else 0).tolist()
        all_v2 += annotators[a2].apply(lambda x: 1 if aspect in x else 0).tolist()
    try:
        k = cohen_kappa_score(all_v1, all_v2)
        print(f"  {a1} vs {a2}: {k:.3f}")
    except:
        print(f"  {a1} vs {a2}: N/A")

print("\nKappa guide: <0.2 slight | 0.2-0.4 fair | 0.4-0.6 moderate | 0.6-0.8 substantial")