from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
import time
import os
import re

# =========================
# LOAD API
# =========================

load_dotenv()

client = OpenAI(
    api_key=os.getenv("BERGET_API_KEY"),
    base_url="https://api.berget.ai/v1"
)

# =========================
# CONFIG
# =========================

MODEL = "meta-llama/Llama-3.3-70B-Instruct"

INPUT_FILE = "game-review-ir/A_retrieval/results/retrieval_results.csv"

OUTPUT_FILE = "outputs/final_2100_predictions.csv"

SAVE_EVERY = 20
WAIT_TIME = 1

ASPECTS = [
    "combat",
    "story",
    "graphics",
    "price",
    "controls",
    "other"
]

# =========================
# PROMPT
# =========================

def make_prompt(review_text):

    return f"""
You are an expert video game review classifier.

Classify which gameplay aspects are discussed in this Steam review.

Possible labels:
- combat = gameplay, weapons, bosses, fighting, builds, difficulty
- story = narrative, lore, dialogue, characters, endings
- graphics = visuals, atmosphere, FPS, performance, bugs, world design
- price = value, DLC, sale, worth buying
- controls = movement, responsiveness, driving, aiming, UI, camera
- other = emotional or vague opinions without clear aspect discussion

Important:
- Infer aspects naturally from context
- Multiple labels are allowed
- Reviews may imply aspects indirectly
- Return ONLY the labels
- Return output as a Python list

Examples:
["combat"]
["graphics", "story"]
["other"]

Review:
{review_text}

Output:
"""

# =========================
# PARSER
# =========================

def parse_labels(raw_text):

    raw_text = str(raw_text).lower()

    found = []

    for aspect in ASPECTS:

        pattern = rf"\b{aspect}\b"

        if re.search(pattern, raw_text):
            found.append(aspect)

    if not found:
        return ["other"]

    return sorted(list(set(found)))

# =========================
# API CALL
# =========================

def classify_review(review_text, max_retries=5):

    prompt = make_prompt(review_text)

    for attempt in range(max_retries):

        try:

            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=30,
                temperature=0
            )

            raw = response.choices[0].message.content.strip()

            return parse_labels(raw)

        except Exception as e:

            err = str(e)

            if "429" in err or "rate" in err.lower():

                wait_time = 30 * (attempt + 1)

                print(f"Rate limit hit. Waiting {wait_time}s...")

                time.sleep(wait_time)

            else:

                print(f"ERROR: {e}")

                return ["other"]

    return ["other"]

# =========================
# MAIN
# =========================

if __name__ == "__main__":

    # ---------------------
    # LOAD DATA
    # ---------------------

    df = pd.read_csv(INPUT_FILE)

    print("\nColumns:")
    print(df.columns)

    total = len(df)

    print(f"\nLoaded {total} reviews.")

    # ---------------------
    # FIND REVIEW COLUMN
    # ---------------------

    possible_review_cols = [
        col for col in df.columns
        if "review" in col.lower()
        and "id" not in col.lower()
    ]

    if not possible_review_cols:

        raise Exception(
            f"No review text column found.\nColumns: {list(df.columns)}"
        )

    review_col = possible_review_cols[0]

    print(f"Using review column: {review_col}")

    # ---------------------
    # RESUME SUPPORT
    # ---------------------

    start_from = 0
    done_df = pd.DataFrame()

    if os.path.exists(OUTPUT_FILE):

        done_df = pd.read_csv(OUTPUT_FILE)

        start_from = len(done_df)

        print(f"Resuming from row {start_from}")

    else:

        print("Starting fresh...")

    remaining = df.iloc[start_from:].reset_index(drop=True)

    print(f"Rows remaining: {len(remaining)}")

    # ---------------------
    # STORAGE
    # ---------------------

    predictions = []

    # ---------------------
    # RUN
    # ---------------------

    for i, row in remaining.iterrows():

        review = str(row[review_col])

        print(f"\n[{start_from+i+1}/{total}] Processing...")

        pred = classify_review(review)

        print("Prediction:", pred)

        predictions.append(pred)

        time.sleep(WAIT_TIME)

        # -----------------
        # SAVE CHECKPOINT
        # -----------------

        if (i + 1) % SAVE_EVERY == 0:

            partial = remaining.iloc[:i+1].copy()

            partial["predicted_aspects"] = predictions

            combined = pd.concat(
                [done_df, partial],
                ignore_index=True
            )

            combined.to_csv(
                OUTPUT_FILE,
                index=False
            )

            progress = start_from + i + 1

            print(f"\nSaved progress: {progress}/{total}")

    # ---------------------
    # FINAL SAVE
    # ---------------------

    final = remaining.copy()

    final["predicted_aspects"] = predictions

    combined = pd.concat(
        [done_df, final],
        ignore_index=True
    )

    combined.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nALL DONE!")
    print(f"Saved to: {OUTPUT_FILE}")