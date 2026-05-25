"""Fetch English Steam reviews for selected games via Steam Store Reviews API.

Output:
- data/raw/steam_api_reviews.csv
- data/processed/clean_reviews.csv
- data/processed/clean_reviews.jsonl
"""
import argparse
import time
from pathlib import Path

import pandas as pd
import requests
import yaml
from tqdm import tqdm

from utils import clean_text, ensure_dirs, save_jsonl

API_URL = "https://store.steampowered.com/appreviews/{app_id}"

import re

def is_mostly_english(text, threshold=0.7):
    english_chars = re.findall(r'[A-Za-z]', str(text))
    total_chars = re.findall(r'\S', str(text))

    if len(total_chars) == 0:
        return False

    ratio = len(english_chars) / len(total_chars)

    return ratio >= threshold

def load_config(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def fetch_game_reviews(game_name, app_id, target_n, language="english", review_type="all", purchase_type="all", filter_="recent", sleep_seconds=0.8):
    records = []
    cursor = "*"
    seen_ids = set()
    pbar = tqdm(total=target_n, desc=f"Fetching {game_name}")

    while len(records) < target_n:
        params = {
            "json": 1,
            "filter": filter_,
            "language": language,
            "review_type": review_type,
            "purchase_type": purchase_type,
            "num_per_page": 100,
            "cursor": cursor,
        }
        try:
            resp = requests.get(API_URL.format(app_id=app_id), params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"[WARN] Request failed for {game_name}: {e}. Sleeping and retrying...")
            time.sleep(max(3, sleep_seconds * 3))
            continue

        reviews = data.get("reviews", [])
        if not reviews:
            print(f"[WARN] No more reviews returned for {game_name}. Collected {len(records)}.")
            break

        before = len(records)
        for item in reviews:
            rec_id = item.get("recommendationid")
            if rec_id in seen_ids:
                continue
            seen_ids.add(rec_id)
            text = clean_text(item.get("review", ""))
            if len(text.split()) < 20:
                continue
            author = item.get("author", {}) or {}
            records.append({
                "review_id": f"{app_id}_{rec_id}",
                "steam_recommendation_id": rec_id,
                "app_id": app_id,
                "game": game_name,
                "review_text": text,
                "language": language,
                "voted_up": item.get("voted_up"),
                "votes_up": item.get("votes_up"),
                "votes_funny": item.get("votes_funny"),
                "weighted_vote_score": item.get("weighted_vote_score"),
                "timestamp_created": item.get("timestamp_created"),
                "timestamp_updated": item.get("timestamp_updated"),
                "playtime_forever": author.get("playtime_forever"),
                "playtime_at_review": author.get("playtime_at_review"),
            })
            if len(records) >= target_n:
                break

        pbar.update(len(records) - before)
        new_cursor = data.get("cursor")
        if not new_cursor or new_cursor == cursor:
            print(f"[WARN] Cursor did not advance for {game_name}. Stopping.")
            break
        cursor = new_cursor
        time.sleep(sleep_seconds)

    pbar.close()
    return records[:target_n]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/games.yaml")
    parser.add_argument("--out-raw", default="data/raw/steam_api_reviews.csv")
    parser.add_argument("--out-clean", default="data/processed/clean_reviews.csv")
    parser.add_argument("--out-jsonl", default="data/processed/clean_reviews.jsonl")
    args = parser.parse_args()

    ensure_dirs()
    cfg = load_config(args.config)
    all_records = []
    for game in cfg["games"]:
        all_records.extend(fetch_game_reviews(
            game_name=game["name"],
            app_id=game["app_id"],
            target_n=int(cfg.get("reviews_per_game", 2500)),
            language=cfg.get("language", "english"),
            review_type=cfg.get("review_type", "all"),
            purchase_type=cfg.get("purchase_type", "all"),
            filter_=cfg.get("filter", "recent"),
            sleep_seconds=float(cfg.get("sleep_seconds", 0.8)),
        ))

    df = pd.DataFrame(all_records)
    if df.empty:
        raise RuntimeError("No reviews collected. Check internet connection or Steam API availability.")

    df = df.drop_duplicates(subset=["review_id"]).copy()
    df["review_text"] = df["review_text"].map(clean_text)
    df["word_count"] = df["review_text"].str.split().str.len()
    df = df[df["word_count"] >= 20].copy()
    df = df[df["review_text"].apply(is_mostly_english)].copy()

    Path(args.out_raw).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out_raw, index=False)
    df.to_csv(args.out_clean, index=False)

    keep_cols = ["review_id", "app_id", "game", "review_text", "language", "word_count"]
    save_jsonl(df[keep_cols].to_dict(orient="records"), args.out_jsonl)

    print("\nSaved:")
    print(f"- {args.out_raw} ({len(df)} rows)")
    print(f"- {args.out_clean}")
    print(f"- {args.out_jsonl}")
    print("\nCounts by game:")
    print(df.groupby("game").size())


if __name__ == "__main__":
    main()
