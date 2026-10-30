"""Print gaps.tsv rows for the given inputs, in full: python3 -I show_gaps.py R22_DIR INPUT..."""
import csv
import sys
for r in csv.DictReader(open(sys.argv[1] + "/gap/gaps.tsv"), delimiter="\t"):
    if r["input"] in sys.argv[2:]:
        print(f"[{r['id']}] sh={r['share']} {r['located']} | {r['scope']}\n  Q: {r['quote']}\n  C: {r['change']}")
