import os
import json
import yaml
import csv
import numpy as np
import pandas as pd
from tqdm import tqdm
from whoosh.index import open_dir
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, util

# Load YAML configuration file
def load_config(config_path: str):
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# Main pipeline execution
def run_pipeline(config_path: str, api_key: str = "test"):
    cfg = load_config(config_path)
    print(f"Loaded configuration: {config_path}")

    # Load or build index
    index_dir = cfg.get("index_dir", "index_data")
    try:
        _ = open_dir(index_dir)
        print("Index loaded successfully from:", index_dir)
    except Exception:
        print("No Whoosh index found — using fallback documents.")
    docs = [
        "Climate change affects global health and migration patterns.",
        "Healthcare systems in the United States are widely debated.",
        "Immigration has both cultural and economic impacts.",
        "Video games can improve problem-solving and reduce stress.",
        "Environmental policy discussions are gaining public attention."
    ]
    bm25 = BM25Okapi([d.split() for d in docs])

    # Load dataset (test.json preferred)
    test_path = "data/test.json"
    dev_path = "data/dev_groundtruth.json"
    dataset_path = test_path if os.path.exists(test_path) else dev_path
    print(f"Using dataset: {dataset_path}")

    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Detect structure of the dataset (list or dictionary)
    if isinstance(data, list):
        try:
            questions = [x["question"].strip() for x in data if "question" in x]
            qid_map = {x["question"].strip(): x.get("id", x["question"].strip()) for x in data}
        except Exception:
            questions = [str(x).strip() for x in data]
            qid_map = {q: q for q in questions}
    elif isinstance(data, dict):
        questions = [k.strip() for k in data.keys()]
        qid_map = {k.strip(): k.strip() for k in data.keys()}
    else:
        raise ValueError("Unknown dataset format. Must be list or dict.")

    print(f"Total questions loaded: {len(questions)}")

    # Load model and prepare embeddings
    model_name = cfg.get("model", "all-MiniLM-L6-v2")
    alpha = float(cfg.get("alpha", 0.8))
    model = SentenceTransformer(model_name)
    doc_emb = model.encode(docs, convert_to_tensor=True)

    # Generate predictions for each question
    results = []
    for qtext in tqdm(questions, desc="Generating predictions"):
        bm25_scores = bm25.get_scores(qtext.split())
        q_emb = model.encode(qtext, convert_to_tensor=True)
        sem_scores = util.cos_sim(q_emb, doc_emb)[0].cpu().numpy()

        combined = alpha * sem_scores + (1 - alpha) * bm25_scores
        top_docs = np.argsort(combined)[::-1][:3]
        supports = [f"DOC_{i}" for i in top_docs]

        options = ["Agree", "Disagree", "Neutral"]
        base = np.abs(np.tanh(combined[top_docs][:3]))
        probs = base / base.sum()

        results.append({
            "question": qtext,
            "distribution": json.dumps(dict(zip(options, probs.tolist())), ensure_ascii=False),
            "supports": json.dumps(supports, ensure_ascii=False)
        })

    # Save Kaggle submission file
    os.makedirs("outputs", exist_ok=True)
    csv_path = "outputs/submission.csv"

    # Preserve original question order from test.json
    with open(dataset_path, "r", encoding="utf-8") as jf:
        test_data = json.load(jf)
        if isinstance(test_data, dict):
            test_questions = list(test_data.keys())
        else:
            test_questions = [x["question"] for x in test_data]

    result_map = {r["question"]: r for r in results}

    # Write output as Kaggle submission CSV
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL, escapechar='\\')
        writer.writerow(["question", "distribution", "supports"])
        for q in test_questions:
            if q in result_map:
                r = result_map[q]
                dist = json.dumps(json.loads(r["distribution"]), ensure_ascii=False)
                supp = json.dumps(json.loads(r["supports"]), ensure_ascii=False)
                writer.writerow([q, dist, supp])
            else:
                writer.writerow([q, "{}", "[]"])

    print(f"Kaggle-ready CSV created: {csv_path}")

    # Validate CSV before upload
    df = pd.read_csv(csv_path)
    print(f"Rows in submission: {len(df)}")
    mismatches = [q for q in df["question"] if q not in test_questions]
    if mismatches:
        print(f"Warning: Mismatch found for {len(mismatches)} questions, check quoting.")
    else:
        print("All question texts match test.json exactly. Ready for Kaggle upload.")

    print("\nPreview:")
    print(df.head(3))

# Command line entry point
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Hybrid Retrieval MAS Survey Runner")
    parser.add_argument("--config", type=str, required=True)
    parser.add_argument("--api_key", type=str, default="test")
    args = parser.parse_args()
    run_pipeline(args.config, args.api_key)
# mas_survey/run.py
"""
Minimal placeholder for the MAS runner (two arguments only).

CLI:
    python -m mas_survey.run --config config.yaml --api_key <YOUR_KEY>
"""

import argparse


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="(placeholder) Run MAS pipeline")
    p.add_argument("--config", type=str, default="config.yaml",
                   help="Path to config.yaml (default: config.yaml)")
    p.add_argument("--api_key", type=str, default=None,
                   help="API key (accepted but unused in placeholder).")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    print(f"[mas_survey.run] config={args.config}  api_key={'<provided>' if args.api_key else '<none>'}")
    print("[mas_survey.run] TODO: implement pipeline and write artifacts/submission_js.csv")


if __name__ == "__main__":
    main()

