import pandas as pd

for path in [
    "data/processed/clean_reviews.csv",
    "results/retrieval_results.csv",
    "annotation/retrieval_annotation_template.csv",
]:
    df = pd.read_csv(path)
    print("\n", path)
    print(df.shape)
    print(df.head(3))
