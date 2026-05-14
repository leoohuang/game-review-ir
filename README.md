# IR Game Reviews — A Module: Steam API + BM25

This repository contains the **A role** pipeline for the IR project:

1. Fetch English Steam reviews from the Steam Store Reviews API
2. Clean and normalize the review corpus
3. Run BM25 retrieval for aspect-specific queries
4. Export retrieval results and annotation templates

## Games

The default configuration uses six games:

- Elden Ring Soulslike Open-World RPG
- Cyberpunk 2077 Open-World Action RPG
- Stardew Valley Farming Simulation
- Hades Roguelike Action Dungeon Crawler
- Titanfall 2 FPS
- Forza Horizon 5 Driving Simulation

You can edit `config/games.yaml` if the team changes the games or the number of reviews per game.

## Setup in VS Code

Open this folder in VS Code, then run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run the full pipeline

```bash
./run_pipeline.sh
```

On Windows, run the steps manually:

```powershell
python src/fetch_reviews.py --config config/games.yaml
python src/run_bm25.py --corpus data/processed/clean_reviews.csv --queries config/queries.csv --top-k 10
python src/make_annotation_files.py
```

## Test quickly with fewer reviews

For the first test, edit `config/games.yaml` and change:

```yaml
reviews_per_game: 2500
```

to:

```yaml
reviews_per_game: 50
```

Then run:

```bash
./run_pipeline.sh
```

If it works, change it back to 2000–3000.

## Outputs

### Clean corpus

```text
data/processed/clean_reviews.csv
data/processed/clean_reviews.jsonl
```

Important columns:

- `review_id`
- `app_id`
- `game`
- `review_text`
- `language`
- `word_count`

### BM25 retrieval results

```text
results/retrieval_results.csv
results/retrieval_results.json
```

Important columns:

- `query_id`
- `aspect`
- `query`
- `game`
- `rank`
- `review_id`
- `bm25_score`
- `review_text`

### Annotation templates

```text
annotation/retrieval_annotation_template.csv
annotation/aspect_annotation_sample.csv
```

These files are for teammates responsible for human annotation and evaluation.

## GitHub notes

Do commit:

- `src/`
- `config/`
- `README.md`
- `requirements.txt`
- `run_pipeline.sh`

Do **not** commit large generated data files:

- `data/raw/*`
- `data/processed/*`
- `results/*`
- `annotation/*`
- `logs/*`

These are already ignored by `.gitignore`.

## Common problems

### Steam API is slow or stops early

Reduce request speed by increasing `sleep_seconds` in `config/games.yaml`:

```yaml
sleep_seconds: 1.5
```

### Forza or another game returns fewer reviews than requested

That is acceptable. The script saves whatever it successfully collects.

