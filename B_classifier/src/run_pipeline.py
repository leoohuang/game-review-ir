import re
from groq import Groq
import pandas as pd
import json
import time
import os 

# ── paste your working key here ───────────────────────────────────────────────
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
 
A review can mention multiple aspects. Return ONLY a valid JSON list.
Only include aspects that are clearly discussed. If none apply, return [].
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
 
Return ONLY a valid JSON list. Multiple aspects allowed. If none apply, return [].
 
Examples:
Review: "The sword fighting feels incredible, every hit has weight and boss fights are brutal"
Output: ["combat"]
 
Review: "Stunning visuals but the story is weak and it costs way too much for what you get"
Output: ["graphics", "story", "price"]
 
Review: "Works great with a controller, very responsive inputs and clean UI"
Output: ["controls"]
 
Review: "The characters are amazing and the lore is deep, but framerates drop badly on PC"
Output: ["story", "graphics"]
 
Now classify this review:
Review:
{review_text}
 
Output:"""
 
def classify_with_retry(review_text, use_few_shot=False, max_retries=10):
    prompt = make_few_shot_prompt(review_text) if use_few_shot else make_zero_shot_prompt(review_text)
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0
            )
            raw = response.choices[0].message.content.strip()
            raw = raw.replace("```json", "").replace("```", "").strip()
            # Find the JSON list even if model adds extra text
            match = re.search(r'\[.*?\]', raw)
            if match:
                labels = json.loads(match.group())
                return [l for l in labels if l in ASPECTS]
            return []
        except Exception as e:
            err = str(e)
            if "rate_limit_exceeded" in err or "429" in err:
                # Extract exact wait time from error message
                wait = 120
                if "Please try again in" in err:
                    try:
                        part = err.split("Please try again in")[1].split(".")[0].strip()
                        mins = 0
                        secs = 0
                        if "m" in part:
                            mins = int(part.split("m")[0].strip())
                            secs_part = part.split("m")[1].replace("s","").strip()
                            secs = int(secs_part) if secs_part else 0
                        elif "s" in part:
                            secs = int(part.replace("s","").strip())
                        wait = mins * 60 + secs + 10
                    except:
                        wait = 120
                print(f"  Rate limit hit. Waiting {wait} seconds... (attempt {attempt+1}/{max_retries})")
                time.sleep(wait)
            else:
                print(f"  ERROR: {e}")
                return []
    return []
 
# ── MAIN PIPELINE ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    df = pd.read_json("game-review-ir/A_retrieval/results/retrieval_results.json")
    total = len(df)
    output_path = "outputs/classified_reviews.csv"
 
    # Resume from where we left off if file already exists
    start_from = 0
    done_df = pd.DataFrame()
 
    if os.path.exists(output_path):
        done_df = pd.read_csv(output_path)
        start_from = len(done_df)
        print(f"Resuming from row {start_from} (already done {start_from}/{total} rows)")
    else:
        print(f"Starting fresh pipeline on {total} reviews...")
 
    remaining = df.iloc[start_from:].reset_index(drop=True)
    print(f"Rows remaining: {len(remaining)}")
    print("Will auto-wait if rate limit hit. Safe to leave running overnight.\n")
 
    zeroshot_labels = []
    fewshot_labels  = []
 
    for i, row in remaining.iterrows():
        # Zero-shot
        z = classify_with_retry(row["review_text"], use_few_shot=False)
        zeroshot_labels.append(z)
        time.sleep(5)
 
        # Few-shot
        f = classify_with_retry(row["review_text"], use_few_shot=True)
        fewshot_labels.append(f)
        time.sleep(5)
 
        # Save progress every 10 rows
        if (i + 1) % 10 == 0:
            done_so_far = remaining.iloc[:i+1].copy()
            done_so_far["llm_zeroshot"] = zeroshot_labels
            done_so_far["llm_fewshot"]  = fewshot_labels
            combined = pd.concat([done_df, done_so_far], ignore_index=True)
            combined.to_csv(output_path, index=False)
            print(f"  Progress: {start_from + i+1}/{total} rows done ({round((start_from+i+1)/total*100)}%) — saved")
 
    # Final save
    final = remaining.copy()
    final["llm_zeroshot"] = zeroshot_labels
    final["llm_fewshot"]  = fewshot_labels
    combined = pd.concat([done_df, final], ignore_index=True)
    combined.to_csv(output_path, index=False)
 
    print(f"\nAll done! Saved to {output_path}")
    print(f"Total rows saved: {len(combined)}")
    print("\nSample output:")
    print(combined[["review_id", "aspect", "llm_zeroshot", "llm_fewshot"]].head(5).to_string())