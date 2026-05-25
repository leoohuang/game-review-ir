from groq import Groq
import pandas as pd
import json
import re
import time
import os

client = Groq(api_key=os.environ["GROQ_API_KEY"])

ASPECTS = ["combat", "story", "graphics", "price", "controls"]

def make_zero_shot_prompt(review_text):
    return f"""You are classifying Steam game reviews by which aspects they discuss.

The five aspects are:
- combat: fighting mechanics, difficulty, enemy AI, hit feel, boss fights
- story: narrative, characters, lore, writing, plot
- graphics: visuals, art style, performance, resolution, frame rate
- price: cost, value for money, DLC, sales, worth buying
- controls: input responsiveness, controller support, UI, keybindings

Return ONLY a valid JSON list. If none apply return [].
Examples: ["combat"] or ["graphics", "story"] or ["price", "controls"]

Review:
{review_text}
Output:"""

def make_few_shot_prompt(review_text):
    return f"""You are classifying Steam game reviews by which aspects they discuss.

The five aspects are:
- combat: fighting mechanics, difficulty, enemy AI, hit feel, boss fights
- story: narrative, characters, lore, writing, plot
- graphics: visuals, art style, performance, resolution, frame rate
- price: cost, value for money, DLC, sales, worth buying
- controls: input responsiveness, controller support, UI, keybindings

Return ONLY a valid JSON list. Multiple aspects allowed. If none apply return [].

Examples:
Review: "The sword fighting feels incredible, every hit has weight"
Output: ["combat"]
Review: "Stunning visuals but the story is weak and overpriced"
Output: ["graphics", "story", "price"]

Now classify:
Review:
{review_text}
Output:"""

def classify_with_retry(review_text, use_few_shot=False, max_retries=10):
    prompt = make_few_shot_prompt(review_text) if use_few_shot else make_zero_shot_prompt(review_text)
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0
            )
            raw = response.choices[0].message.content.strip()
            raw = raw.replace("```json", "").replace("```", "").strip()
            match = re.search(r'\[.*?\]', raw)
            if match:
                labels = json.loads(match.group())
                return [l for l in labels if l in ASPECTS]
            return []
        except Exception as e:
            err = str(e)
            if "429" in err or "rate_limit" in err:
                wait = 120
                if "Please try again in" in err:
                    try:
                        part = err.split("Please try again in")[1].split(".")[0].strip()
                        mins, secs = 0, 0
                        if "m" in part:
                            mins = int(part.split("m")[0].strip())
                            sp = part.split("m")[1].replace("s","").strip()
                            secs = int(sp) if sp else 0
                        elif "s" in part:
                            secs = int(part.replace("s","").strip())
                        wait = mins * 60 + secs + 30
                    except:
                        wait = 120
                print(f"  Rate limit. Waiting {wait}s... (attempt {attempt+1}/{max_retries})")
                time.sleep(wait)
            else:
                print(f"  ERROR: {e}")
                return []
    return []

if __name__ == "__main__":
    df = pd.read_csv("outputs/classified_reviews.csv")
    output_path = "outputs/classified_reviews.csv"

    # Find empty rows
    empty_zero = df['llm_zeroshot'].apply(lambda x: str(x).strip() == '[]' or str(x).strip() == '' or pd.isna(x))
    empty_few  = df['llm_fewshot'].apply(lambda x: str(x).strip() == '[]' or str(x).strip() == '' or pd.isna(x))

    zero_indices = df[empty_zero].index.tolist()
    few_indices  = df[empty_few].index.tolist()

    print(f"Empty zero-shot rows to fill: {len(zero_indices)}")
    print(f"Empty few-shot rows to fill:  {len(few_indices)}")
    print(f"Total API calls needed: {len(zero_indices) + len(few_indices)}")

    # Fill zero-shot empty rows
    print("\nFilling zero-shot empty rows...")
    for count, idx in enumerate(zero_indices):
        result = classify_with_retry(df.loc[idx, "review_text"], use_few_shot=False)
        df.at[idx, "llm_zeroshot"] = str(result)
        time.sleep(15)
        if (count + 1) % 10 == 0:
            df.to_csv(output_path, index=False)
            print(f"  Zero-shot: {count+1}/{len(zero_indices)} filled — saved")

    # Fill few-shot empty rows
    print("\nFilling few-shot empty rows...")
    for count, idx in enumerate(few_indices):
        result = classify_with_retry(df.loc[idx, "review_text"], use_few_shot=True)
        df.at[idx, "llm_fewshot"] = str(result)
        time.sleep(15)
        if (count + 1) % 10 == 0:
            df.to_csv(output_path, index=False)
            print(f"  Few-shot: {count+1}/{len(few_indices)} filled — saved")

    # Final save
    df.to_csv(output_path, index=False)
    print(f"\nAll empty rows filled!")

    # Verify
    still_empty_z = df['llm_zeroshot'].apply(lambda x: str(x).strip() == '[]').sum()
    still_empty_f = df['llm_fewshot'].apply(lambda x: str(x).strip() == '[]').sum()
    print(f"Remaining empty zero-shot: {still_empty_z}")
    print(f"Remaining empty few-shot:  {still_empty_f}")