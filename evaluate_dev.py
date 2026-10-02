import os
import json
import numpy as np
from scipy.spatial.distance import jensenshannon

# Function: Safely evaluate folder with shape alignment
def evaluate_folder(gt_path, folder_path):
    with open(gt_path, "r", encoding="utf-8") as f:
        gt = json.load(f)

    print("\n================ Evaluation ================")
    final_results = []

    for file in sorted(os.listdir(folder_path)):
        if not file.endswith("_summary.json"):
            continue
        path = os.path.join(folder_path, file)
        with open(path, "r", encoding="utf-8") as f:
            preds = json.load(f)

        # Try text alignment if IDs differ
        if not set(preds.keys()).intersection(gt.keys()):
            print(f"No matching IDs in {file}, attempting text alignment...")
            aligned = {}
            for p_text, p_val in preds.items():
                for g_text in gt.keys():
                    if g_text.strip().lower() == p_text.strip().lower():
                        aligned[g_text] = p_val
                        break
            preds = aligned

        js_scores, map_scores = [], []

        # Handle different option lengths
        for q, g_data in gt.items():
            if q not in preds:
                continue

            # Extract groundtruth and predicted distributions
            g = np.array(list(g_data["distribution"].values()), dtype=float)
            p = np.array(list(preds[q]["distribution"].values()), dtype=float)

            # Handle mismatched lengths (e.g. 3 vs 5)
            if len(p) != len(g):
                # If prediction has 3 values but groundtruth has 5, expand via interpolation
                if len(p) < len(g):
                    pad = len(g) - len(p)
                    p = np.pad(p, (0, pad), mode="constant")
                elif len(g) < len(p):
                    pad = len(p) - len(g)
                    g = np.pad(g, (0, pad), mode="constant")

            # Normalize both
            p = np.clip(p, 1e-9, None)
            g = np.clip(g, 1e-9, None)
            p /= p.sum()
            g /= g.sum()

            # JS similarity (1 - distance)
            js = 1 - jensenshannon(p, g)
            js_scores.append(js)

            # MAP (mean absolute product for overlap)
            map_val = np.mean(np.minimum(p, g))
            map_scores.append(map_val)

        # Compute average metrics
        js_mean = np.mean(js_scores) if js_scores else 0
        map_mean = np.mean(map_scores) if map_scores else 0
        print(f"{file[:-13]}  JS = {js_mean:.4f}   MAP = {map_mean:.4f}")
        final_results.append((file[:-13], js_mean, map_mean))

    print("\n============== Final Comparison ==============")
    print(f"{'Variant':<20}{'JS Similarity':<15}{'MAP Score'}")
    print("-" * 45)
    for v, js, mp in final_results:
        print(f"{v:<20}{js:<15.4f}{mp:.4f}")
    print("==============================================")

# CLI Entry
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate all model variants")
    parser.add_argument("--gt", type=str, required=True)
    parser.add_argument("--folder", type=str, required=True)
    args = parser.parse_args()
    evaluate_folder(args.gt, args.folder)
