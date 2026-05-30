import pandas as pd

files = [
    "./game-review-ir/B_classifier/annotations/final_gold.csv",
    "./game-review-ir/B_classifier/annotations/annotator_A.csv",
    "./game-review-ir/B_classifier/annotations/annotator_B.csv",
    "./game-review-ir/B_classifier/annotations/annotator_C.csv",
    "./game-review-ir/B_classifier/annotations/annotator_D.csv"
]

for f in files:
    try:
        df = pd.read_csv(f)
    except:
        df = pd.read_csv(f, encoding="latin1")

    print("=" * 50)
    print(f)
    print(df.columns.tolist())
    print()