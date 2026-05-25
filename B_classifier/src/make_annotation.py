import pandas as pd

df = pd.read_csv("outputs/classified_reviews.csv")

# Pick 40 reviews per aspect = 200 total, balanced
aspects = ["combat", "story", "graphics", "price", "controls"]
samples = []

for aspect in aspects:
    subset = df[df["aspect"] == aspect].head(40)
    samples.append(subset)

annotation = pd.concat(samples, ignore_index=True)

# Keep only columns needed
annotation = annotation[["review_id", "game", "aspect", "review_text", "llm_zeroshot", "llm_fewshot"]]

# Add blank column for your human labels
annotation["human_label_B"] = ""

annotation.to_csv("outputs/annotation_task.csv", index=False)
print(f"Saved {len(annotation)} rows to outputs/annotation_task.csv")
print("\nAspect distribution:")
print(annotation["aspect"].value_counts())
print("\nNow open outputs/annotation_task.csv in Excel")
print("Fill in the human_label_B column for each review")
print("Use: combat, story, graphics, price, controls")
print("Multiple aspects: graphics,story")
print("Nothing clear: leave empty")