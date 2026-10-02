import json, random, os

random.seed(42)
src = "data/dev.json"
dst = "data/dev_probe.json"
k = 15

with open(src, "r", encoding="utf-8") as f:
    data = json.load(f)

keys = sorted(list(data.keys()))
sample = [keys[i] for i in range(0, len(keys), max(1, len(keys)//k))][:k]
probe = {q: data[q] for q in sample}

os.makedirs("data", exist_ok=True)
with open(dst, "w", encoding="utf-8") as f:
    json.dump(probe, f, ensure_ascii=False, indent=2)

print(f"Saved probe of {len(probe)} questions to {dst}")
