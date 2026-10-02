<<<<<<< HEAD
from whoosh import index
from whoosh.fields import Schema, TEXT, ID
import os
import yaml

def load_config(config_path):
    # Read configuration settings from the YAML file
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def main(config_path="config.yaml"):
    config = load_config(config_path)
    index_dir = config.get("index_dir", "index_data")

    # Create the index directory if it does not already exist
    os.makedirs(index_dir, exist_ok=True)

    # Define the structure of the index with document ID and text content
    schema = Schema(
        doc_id=ID(stored=True, unique=True),
        content=TEXT(stored=True)
    )

    # Build a new index if one is not already present
    if not index.exists_in(index_dir):
        ix = index.create_in(index_dir, schema)
        writer = ix.writer()

        # Add a few sample documents to initialize the index
        docs = [
            ("DOC1", "Climate change affects everyone globally."),
            ("DOC2", "Healthcare and education are key priorities."),
            ("DOC3", "Economic policies shape citizens' wellbeing.")
        ]
        for doc_id, text in docs:
            writer.add_document(doc_id=doc_id, content=text)
        writer.commit()
        print(f"Index created successfully at: {index_dir}")
    else:
        print("Index already exists.")
=======
# index/build.py
"""
Minimal placeholder for the index builder.

Keeps the CLI contract only (arguments parsing). No indexing logic.
Usage:
    python -m index.build --config config.yaml --api_key <YOUR_KEY>
"""

import argparse


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="(placeholder) Build indexes from documents.jsonl"
    )
    p.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to config.yaml (default: config.yaml)",
    )
    p.add_argument(
        "--api_key",
        type=str,
        default=None,
        help="Together (or other) API key; accepted but unused in placeholder.",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    # Placeholder: just acknowledge arguments.
    print(f"[index.build] config={args.config}  api_key={'<provided>' if args.api_key else '<none>'}")
    print("[index.build] TODO: implement indexing logic here.")

>>>>>>> c9908a585555510f53ae0fab18c93cdee943d944

if __name__ == "__main__":
    main()
