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

ASPECTS = [
    "combat",
    "story",
    "graphics",
    "price",
    "controls",
    "other"
]

LLAMA = "meta-llama/Llama-3.3-70B-Instruct"
MISTRAL = "mistralai/Mistral-Small-3.2-24B-Instruct-2506"

INPUT_FILE = "annotations/final_gold.csv"
OUTPUT_FILE = "outputs/berget_classified.csv"

SAVE_EVERY = 5
WAIT_TIME = 1

# =========================
# PROMPTS
# =========================

def make_zero_shot_prompt(review_text):

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


def make_few_shot_prompt(review_text):

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

Multiple labels are allowed.

Examples:

Review:
"The bosses are difficult and combat feels amazing."
Output:
["combat"]

Review:
"Beautiful world with incredible atmosphere and visuals."
Output:
["graphics"]

Review:
"The story and characters are unforgettable."
Output:
["story"]

Review:
"Driving feels clunky and movement is unresponsive."
Output:
["controls"]

Review:
"Worth every dollar especially during sales."
Output:
["price"]

Review:
"This game changed my life."
Output:
["other"]

Review:
"The combat is smooth and the world looks incredible."
Output:
["combat", "graphics"]

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

def classify_with_retry(
    review_text,
    model,
    use_few_shot=False,
    max_retries=5
):

    prompt = (
        make_few_shot_prompt(review_text)
        if use_few_shot
        else make_zero_shot_prompt(review_text)
    )

    for attempt in range(max_retries):

        try:

            response = client.chat.completions.create(
                model=model,
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
    # FIXED REVIEW COLUMN
    # ---------------------

    review_col = "review_text"

    if review_col not in df.columns:

        raise Exception(
            f"'review_text' column not found.\nColumns are: {list(df.columns)}"
        )

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
    print("Auto-saving enabled.\n")

    # ---------------------
    # STORAGE
    # ---------------------

    llama_zero = []
    llama_few = []
    mistral_zero = []
    mistral_few = []

    # ---------------------
    # RUN PIPELINE
    # ---------------------

    for i, row in remaining.iterrows():

        review = str(row[review_col])

        print(f"\n[{start_from+i+1}/{total}] Processing review...")

        # -----------------
        # LLAMA ZERO
        # -----------------

        lz = classify_with_retry(
            review,
            LLAMA,
            use_few_shot=False
        )

        time.sleep(WAIT_TIME)

        # -----------------
        # LLAMA FEW
        # -----------------

        lf = classify_with_retry(
            review,
            LLAMA,
            use_few_shot=True
        )

        time.sleep(WAIT_TIME)

        # -----------------
        # MISTRAL ZERO
        # -----------------

        mz = classify_with_retry(
            review,
            MISTRAL,
            use_few_shot=False
        )

        time.sleep(WAIT_TIME)

        # -----------------
        # MISTRAL FEW
        # -----------------

        mf = classify_with_retry(
            review,
            MISTRAL,
            use_few_shot=True
        )

        time.sleep(WAIT_TIME)

        # -----------------
        # DEBUG
        # -----------------

        print("Llama-ZS:", lz)
        print("Llama-FS:", lf)
        print("Mistral-ZS:", mz)
        print("Mistral-FS:", mf)

        # -----------------
        # STORE
        # -----------------

        llama_zero.append(lz)
        llama_few.append(lf)
        mistral_zero.append(mz)
        mistral_few.append(mf)

        # -----------------
        # SAVE CHECKPOINT
        # -----------------

        if (i + 1) % SAVE_EVERY == 0:

            partial = remaining.iloc[:i+1].copy()

            partial["llama_zeroshot"] = llama_zero
            partial["llama_fewshot"] = llama_few
            partial["mistral_zeroshot"] = mistral_zero
            partial["mistral_fewshot"] = mistral_few

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

    final["llama_zeroshot"] = llama_zero
    final["llama_fewshot"] = llama_few
    final["mistral_zeroshot"] = mistral_zero
    final["mistral_fewshot"] = mistral_few

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