import json
import csv
import os
import re

# Paths
GROUNDTRUTH_PATH = "data/dev_groundtruth.json"
SUMMARY_PATH = "reports/ablation/hybrid_alpha_0.8_summary.json"
OUTPUT_PATH = "outputs/submission.csv"

def clean_text(text):
    text = text.replace('"', "'").replace("\n", " ").replace("\r", " ")
    text = text.replace("//", "/")
    text = re.sub(r"\s+", " ", text.strip())
    return text

def main():
    print("Loading files...")
    with open(GROUNDTRUTH_PATH, "r", encoding="utf-8") as f:
        groundtruth = json.load(f)

    with open(SUMMARY_PATH, "r", encoding="utf-8") as f:
        results = json.load(f)

    print(f"Loaded {len(groundtruth)} groundtruth questions.")
    os.makedirs("outputs", exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["question", "distribution", "supports"])

        count = 0
        for q in groundtruth.keys():
            q_clean = clean_text(q)

            if q in results:
                dist = results[q]["distribution"]
                supp = results[q]["supports"]
            else:
                # Fallback if missing
                dist = {"Agree": 0.34, "Disagree": 0.33, "Neutral": 0.33}
                supp = ["DOC_0"]

            writer.writerow([
                q_clean,
                json.dumps(dist, ensure_ascii=False, separators=(",", ":")),
                json.dumps(supp, ensure_ascii=False, separators=(",", ":"))
            ])
            count += 1

    print(f"Final submission ready → {OUTPUT_PATH} ({count} questions)")

if __name__ == "__main__":
    main()
