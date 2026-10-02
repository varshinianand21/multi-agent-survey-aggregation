import csv, json, math, sys

if len(sys.argv) < 2:
    print("Usage: python scripts/validate_csv.py <submission.csv>")
    sys.exit(1)

path = sys.argv[1]
OK = True

with open(path, encoding="utf-8") as f:
    rdr = csv.DictReader(f)
    for i, row in enumerate(rdr, 1):
        dist = json.loads(row["distribution"])
        s = sum(dist.values())
        if not math.isclose(s, 1.0, abs_tol=1e-6):
            print(f"[X] Row {i}: distribution sums to {s:.8f} != 1.0")
            OK = False
        sups = json.loads(row["supports"])
        if len(set(sups)) != 100:
            print(f"[X] Row {i}: supports contain {len(set(sups))} unique IDs (need 100)")
            OK = False

if OK:
    print(f"{path} PASSED validation.")
else:
    print("Validation failed.")
sys.exit(0 if OK else 1)
