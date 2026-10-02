import argparse
import subprocess
import sys
import os
import json

def main():
    parser = argparse.ArgumentParser(description="Run different MAS experiment variants.")
    parser.add_argument("--config", required=True, help="Path to config YAML file.")
    parser.add_argument("--name", required=True, help="Name of this variant (used for saving outputs).")
    args = parser.parse_args()

    print(f"\nRunning variant: {args.name}")
    print(f"Config path: {args.config}\n")

    # Ensure output directory exists
    os.makedirs("reports/ablation", exist_ok=True)

    # Save probe file path (used for mini dev set testing)
    probe_path = "data/dev_probe.json"
    if not os.path.exists(probe_path):
        print("Probe file not found! Run 'python scripts/make_probe.py' first.")
        return

    # Use sys.executable to ensure same Python environment (.venv)
    cmd = [
        sys.executable,
        "-m", "mas_survey.run",
        "--config", args.config,
        "--api_key", "test"
    ]

    print("Executing command:", " ".join(cmd))
    try:
        subprocess.check_call(cmd)
        print(f"\nSuccessfully ran variant: {args.name}")
    except subprocess.CalledProcessError as e:
        print(f"\nError while running variant '{args.name}': {e}")
        return

    # Check output
    output_csv = "outputs/submission.csv"
    if os.path.exists(output_csv):
        new_path = f"reports/ablation/{args.name}_submission.csv"
        os.rename(output_csv, new_path)
        print(f"Output saved to: {new_path}")
    else:
        print("No submission.csv found after execution.")

    # Optional: save a summary JSON for easy tracking
    summary = {
        "variant": args.name,
        "config": args.config,
        "status": "success",
    }
    with open(f"reports/ablation/{args.name}_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Summary written to: reports/ablation/{args.name}_summary.json")

if __name__ == "__main__":
    main()
