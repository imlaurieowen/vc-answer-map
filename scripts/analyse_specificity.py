#!/usr/bin/env python3
import csv
import json
import statistics
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

from analyse_results import canonical_firm, write_csv

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "analysis" / "specificity"
OUTPUT.mkdir(parents=True, exist_ok=True)

CATEGORY_BASELINE = {
    "climate_hardware": "discovery_climate_hardware",
    "defence_technology": "discovery_eu_defence",
    "university_spinout": "discovery_eu_spinout",
    "developer_infrastructure": "discovery_dev_infra",
    "capital_efficient_saas": "discovery_capital_efficient_saas",
}


def load_jsonl(path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def baseline_pools():
    rows = [r for r in csv.DictReader((ROOT / "analysis" / "firms-by-prompt.csv").open()) if r["prompt_type"] == "discovery"]
    counts = defaultdict(dict)
    breadth = defaultdict(set)
    for row in rows:
        firm = row["firm"]
        prompt_id = row["prompt_id"]
        counts[firm][prompt_id] = int(row["response_inclusions"])
        breadth[firm].add(prompt_id)
    prestige = {firm for firm, prompts in breadth.items() if len(prompts) >= 4}
    target = {}
    for category, prompt_id in CATEGORY_BASELINE.items():
        target[category] = {
            firm for firm, prompt_counts in counts.items()
            if firm not in prestige
            and prompt_counts.get(prompt_id, 0) >= 10
            and prompt_counts.get(prompt_id, 0) == max(prompt_counts.values())
        }
    return prestige, target


def flatten(responses, condition):
    rows = []
    for response in responses:
        for rank, rec in enumerate(response.get("parsed", {}).get("recommendations", []), 1):
            rows.append({
                "condition": condition,
                "model": response["model"],
                "prompt_id": response["prompt_id"],
                "category": response.get("category", ""),
                "specificity_level": int(response.get("specificity_level") or 0),
                "run": int(response["run"]),
                "rank": rank,
                "firm": canonical_firm(rec.get("firm")),
                "reason": (rec.get("reason") or "").strip(),
                "source_url": (rec.get("source_url") or "").strip(),
            })
    return rows


def main():
    responses_by_condition = {
        "closed_book": load_jsonl(ROOT / "results-specificity-closed.jsonl"),
        "open_book": load_jsonl(ROOT / "results-specificity-open.jsonl"),
    }
    responses = [r for values in responses_by_condition.values() for r in values]
    rows = [row for condition, values in responses_by_condition.items() for row in flatten(values, condition)]
    if rows:
        write_csv(OUTPUT / "recommendations.csv", list(rows[0]), rows)

    prestige, target = baseline_pools()
    pool_rows = ([{"pool": "prestige", "category": "", "firm": firm} for firm in sorted(prestige)] +
                 [{"pool": "target_association", "category": category, "firm": firm}
                  for category in sorted(target) for firm in sorted(target[category])])
    write_csv(OUTPUT / "predefined-pools.csv", ["pool", "category", "firm"], pool_rows)

    metrics = []
    for condition in responses_by_condition:
        for level in (1, 2, 3):
            selected = [r for r in rows if r["condition"] == condition and r["specificity_level"] == level and r["firm"]]
            counts = Counter(r["firm"] for r in selected)
            total = len(selected)
            metrics.append({
                "condition": condition,
                "specificity_level": level,
                "recommendations": total,
                "unique_firms": len(counts),
                "top5_concentration": round(sum(n for _, n in counts.most_common(5)) / total, 4) if total else "",
                "prestige_leakage": round(sum(r["firm"] in prestige for r in selected) / total, 4) if total else "",
                "target_association_rate": round(sum(r["firm"] in target.get(r["category"], set()) for r in selected) / total, 4) if total else "",
            })
    write_csv(OUTPUT / "level-metrics.csv", list(metrics[0]), metrics)

    cell_sets = defaultdict(dict)
    for row in rows:
        if row["firm"]:
            cell_sets[(row["condition"], row["model"], row["prompt_id"])].setdefault(row["run"], set()).add(row["firm"])
    stability = []
    for (condition, model, prompt_id), run_sets in sorted(cell_sets.items()):
        if len(run_sets) < 2:
            mean_jaccard = ""
        else:
            values = []
            for left, right in combinations(run_sets.values(), 2):
                union = left | right
                values.append(len(left & right) / len(union) if union else 1.0)
            mean_jaccard = round(statistics.mean(values), 4)
        stability.append({
            "condition": condition,
            "model": model,
            "prompt_id": prompt_id,
            "runs_observed": len(run_sets),
            "mean_pairwise_jaccard": mean_jaccard,
            "distinct_firms": len(set().union(*run_sets.values())),
        })
    if stability:
        write_csv(OUTPUT / "cell-stability.csv", list(stability[0]), stability)

    summary = {
        "responses": {condition: len(values) for condition, values in responses_by_condition.items()},
        "recommendations": len(rows),
        "prestige_pool": sorted(prestige),
        "target_pool_sizes": {category: len(firms) for category, firms in target.items()},
    }
    (OUTPUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
