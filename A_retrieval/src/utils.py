import re
import json
from pathlib import Path
from bs4 import BeautifulSoup


def ensure_dirs():
    for d in ["data/raw", "data/processed", "results", "annotation", "logs"]:
        Path(d).mkdir(parents=True, exist_ok=True)


def clean_text(text: str) -> str:
    if text is None:
        return ""
    text = BeautifulSoup(str(text), "html.parser").get_text(" ")
    text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str):
    text = clean_text(text).lower()
    return re.findall(r"[a-z0-9']+", text)


def save_jsonl(records, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
