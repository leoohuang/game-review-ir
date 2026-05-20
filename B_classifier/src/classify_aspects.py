from groq import Groq
import pandas as pd
import json
import os
import time

# Setup
client = Groq(api_key=os.environ["GROQ_API_KEY"])

ASPECTS = ["combat", "story", "graphics", "price", "controls"]
 
# ── PROMPT VARIANT A: Zero-shot ──────────────────────────────────────────────
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
 
Examples of valid output: ["combat"] or ["graphics", "story"] or ["price", "controls"]
 
Review:
{review_text}
 
Output:"""
 
# ── PROMPT VARIANT B: Few-shot ───────────────────────────────────────────────
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
 
# ── Single review classifier ─────────────────────────────────────────────────
def classify_review(review_text, use_few_shot=False):
    prompt = make_few_shot_prompt(review_text) if use_few_shot else make_zero_shot_prompt(review_text)
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        labels = json.loads(raw)
        return [l for l in labels if l in ASPECTS]
    except Exception as e:
        print(f"  ERROR: {e}")
        return []
 
# ── TEST on 5 reviews ────────────────────────────────────────────────────────
if __name__ == "__main__":
    df = pd.read_json("game-review-ir/A_retrieval/results/retrieval_results.json")
 
    print("=" * 60)
    print("TESTING ZERO-SHOT on 5 reviews")
    print("=" * 60)
 
    for i, row in df.head(5).iterrows():
        print(f"\nReview {i+1}")
        print(f"  Game   : {row['game']}")
        print(f"  Aspect : {row['aspect']}  <- TRUE aspect from query")
        print(f"  Review : {row['review_text'][:120]}...")
        result = classify_review(row["review_text"], use_few_shot=False)
        print(f"  LLM said (zero-shot) : {result}")
        time.sleep(2)
 
    print("\n" + "=" * 60)
    print("TESTING FEW-SHOT on same 5 reviews")
    print("=" * 60)
 
    for i, row in df.head(5).iterrows():
        print(f"\nReview {i+1}")
        print(f"  Aspect : {row['aspect']}  <- TRUE aspect")
        print(f"  Review : {row['review_text'][:120]}...")
        result = classify_review(row["review_text"], use_few_shot=True)
        print(f"  LLM said (few-shot)  : {result}")
        time.sleep(2)
 
    print("\nDone. Check if labels make sense before running full pipeline.")