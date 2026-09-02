#!/usr/bin/env python3
import csv
import json
import re
import statistics
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "analysis"
OUTPUT.mkdir(exist_ok=True)

FIRM_ALIASES = {
    "a16z": "Andreessen Horowitz",
    "a16z andreessen horowitz": "Andreessen Horowitz",
    "a16z andreessen horowitz fintech": "Andreessen Horowitz",
    "andreessen horowitz": "Andreessen Horowitz",
    "andreessen horowitz a16z": "Andreessen Horowitz",
    "andreessen horowitz fintech": "Andreessen Horowitz",
    "andreesen horowitz": "Andreessen Horowitz",
    "sequoia": "Sequoia Capital",
    "sequoia capital": "Sequoia Capital",
    "y combinator": "Y Combinator",
    "yc": "Y Combinator",
    "first round": "First Round Capital",
    "first round capital": "First Round Capital",
    "usv": "Union Square Ventures",
    "union square ventures": "Union Square Ventures",
    "benchmark capital": "Benchmark",
    "benchmark": "Benchmark",
    "greylock": "Greylock Partners",
    "greylock partners": "Greylock Partners",
    "bessemer": "Bessemer Venture Partners",
    "bessemer venture partners": "Bessemer Venture Partners",
    "lowercarbon": "Lowercarbon Capital",
    "lowercarbon capital": "Lowercarbon Capital",
    "breakthrough energy": "Breakthrough Energy Ventures",
    "breakthrough energy ventures": "Breakthrough Energy Ventures",
    "nfx": "NFX",
    "nato innovation fund nif": "NATO Innovation Fund",
    "nato innovation fund": "NATO Innovation Fund",
    "the nato innovation fund": "NATO Innovation Fund",
    "index": "Index Ventures",
    "index ventures": "Index Ventures",
    "qed": "QED Investors",
    "qed investors": "QED Investors",
    "point nine": "Point Nine Capital",
    "point nine capital": "Point Nine Capital",
    "point nine capital point nine": "Point Nine Capital",
    "cambridge innovation capital cic": "Cambridge Innovation Capital",
    "cambridge innovation capital": "Cambridge Innovation Capital",
    "oxford science enterprises ose": "Oxford Science Enterprises",
    "oxford science enterprises": "Oxford Science Enterprises",
    "ip group plc": "IP Group",
    "ip group": "IP Group",
    "kompas vc": "KOMPAS VC",
    "ruya ventures": "Ruya Ventures",
    "treverge": "Treverge",
    "extantia": "Extantia Capital",
    "extantia capital": "Extantia Capital",
    "u2v": "U2V",
    "u2v university2ventures": "U2V",
    "university2ventures u2v": "U2V",
    "nordic science investments": "Nordic Science Investments",
    "nordic science investments nsi": "Nordic Science Investments",
    "encoded vc": "Encoded Ventures",
    "encoded ventures": "Encoded Ventures",
    "nyca": "Nyca Partners",
    "nyca partners": "Nyca Partners",
    "boldstart ventures": "Boldstart Ventures",
    "commit": ">commit",
    "digital undivided": "digitalundivided",
    "digitalundivided": "digitalundivided",
    "five four partners": "Five Four Partners",
    "fivefour partners": "Five Four Partners",
    "menlo ventures inception fund": "Menlo Ventures Inception Fund",
    "mass ventures": "MassVentures",
    "massventures": "MassVentures",
    "montis vc": "Montis VC",
    "pale blue dot": "Pale Blue Dot",
    "speedinvest": "Speedinvest",
    "inovo vc": "Inovo VC",
    "iconiq growth": "ICONIQ Growth",
    "albionvc deeptech hub": "AlbionVC Deeptech Hub",
    "saastr jason lemkin": "SaaStr / Jason Lemkin",
}

FRAMEWORK_ALIASES = {
    "do things that dont scale": "Do Things That Don't Scale",
    "default alive": "Default Alive or Default Dead",
    "default alive or default dead": "Default Alive or Default Dead",
    "default alive vs default dead": "Default Alive or Default Dead",
    "the burn multiple": "Burn Multiple",
    "burn multiple": "Burn Multiple",
    "cold start problem": "The Cold Start Problem",
    "the cold start problem": "The Cold Start Problem",
    "product market fit": "Product-Market Fit",
    "founder led sales": "Founder-Led Sales",
    "founder led sales playbook": "Founder-Led Sales",
    "make something people want": "Make Something People Want",
}

def key(value):
    value = (value or "").strip().lower().replace("&", " and ")
    value = re.sub(r"[’']", "", value)
    value = re.sub(r"[\-–—./(),:?]", " ", value)
    return re.sub(r"\s+", " ", value).strip()

def canonical_firm(value):
    raw = (value or "").strip()
    if not raw:
        return ""
    normal = key(raw)
    if normal in FIRM_ALIASES:
        return FIRM_ALIASES[normal]
    return re.sub(r"\s+", " ", raw).strip()

def canonical_framework(value):
    raw = (value or "").strip()
    if not raw:
        return ""
    normal = key(raw)
    return FRAMEWORK_ALIASES.get(normal, re.sub(r"\s+", " ", raw).strip())

def write_csv(path, fields, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def load_rows():
    rows = []
    for name in ("results-full.jsonl", "results-replicate.jsonl"):
        for line in (ROOT / name).read_text().splitlines():
            rows.append(json.loads(line))
    return rows

def main():
    responses = load_rows()
    flat = []
    for response in responses:
        for rank, rec in enumerate(response["parsed"].get("recommendations", []), 1):
            flat.append({
                "model": response["model"],
                "prompt_id": response["prompt_id"],
                "prompt_type": response["prompt_type"],
                "run": response["run"],
                "rank": rank,
                "firm_raw": (rec.get("firm") or "").strip(),
                "firm": canonical_firm(rec.get("firm")),
                "individual": (rec.get("individual") or "").strip(),
                "reason": (rec.get("reason") or "").strip(),
                "framework_raw": (rec.get("named_framework") or "").strip(),
                "framework": canonical_framework(rec.get("named_framework")),
                "source_title": (rec.get("source_title") or "").strip(),
                "source_url": (rec.get("source_url") or "").strip(),
                "confidence": rec.get("confidence", ""),
            })
    flat_fields = list(flat[0])
    write_csv(OUTPUT / "recommendations-normalised.csv", flat_fields, flat)

    total_responses = len(responses)
    firm_rows = []
    firms = sorted({r["firm"] for r in flat if r["firm"]})
    for firm in firms:
        mentions = [r for r in flat if r["firm"] == firm]
        response_keys = {(r["model"], r["prompt_id"], r["run"]) for r in mentions}
        firm_rows.append({
            "firm": firm,
            "mentions": len(mentions),
            "response_inclusions": len(response_keys),
            "response_mention_rate": round(len(response_keys) / total_responses, 4),
            "top_rank_count": sum(r["rank"] == 1 for r in mentions),
            "models": len({r["model"] for r in mentions}),
            "prompts": len({r["prompt_id"] for r in mentions}),
            "mean_rank": round(statistics.mean(r["rank"] for r in mentions), 3),
        })
    firm_rows.sort(key=lambda r: (-r["response_inclusions"], r["mean_rank"], r["firm"]))
    write_csv(OUTPUT / "firms-overall.csv", list(firm_rows[0]), firm_rows)

    by_prompt = []
    prompt_ids = sorted({r["prompt_id"] for r in responses})
    for prompt_id in prompt_ids:
        prompt_responses = [r for r in responses if r["prompt_id"] == prompt_id]
        eligible = len(prompt_responses)
        prompt_flat = [r for r in flat if r["prompt_id"] == prompt_id and r["firm"]]
        for firm in sorted({r["firm"] for r in prompt_flat}):
            mentions = [r for r in prompt_flat if r["firm"] == firm]
            response_keys = {(r["model"], r["run"]) for r in mentions}
            model_counts = Counter(r["model"] for r in mentions)
            by_prompt.append({
                "prompt_id": prompt_id,
                "prompt_type": prompt_responses[0]["prompt_type"],
                "firm": firm,
                "response_inclusions": len(response_keys),
                "eligible_responses": eligible,
                "mention_rate": round(len(response_keys) / eligible, 4),
                "models_ever": len(model_counts),
                "models_majority": sum(count >= 3 for count in model_counts.values()),
                "top_rank_count": sum(r["rank"] == 1 for r in mentions),
                "mean_rank": round(statistics.mean(r["rank"] for r in mentions), 3),
            })
    by_prompt.sort(key=lambda r: (r["prompt_id"], -r["response_inclusions"], r["mean_rank"], r["firm"]))
    write_csv(OUTPUT / "firms-by-prompt.csv", list(by_prompt[0]), by_prompt)

    response_sets = {}
    response_tops = {}
    for response in responses:
        rkey = (response["model"], response["prompt_id"], response["run"])
        recs = response["parsed"].get("recommendations", [])
        response_sets[rkey] = {canonical_firm(r.get("firm")) for r in recs if canonical_firm(r.get("firm"))}
        response_tops[rkey] = canonical_firm(recs[0].get("firm")) if recs else ""
    stability = []
    for model, prompt_id in sorted({(r["model"], r["prompt_id"]) for r in responses}):
        sets = [response_sets[(model, prompt_id, run)] for run in range(1, 6)]
        tops = [response_tops[(model, prompt_id, run)] for run in range(1, 6)]
        similarities = []
        for left, right in combinations(sets, 2):
            similarities.append(len(left & right) / len(left | right) if left | right else 1.0)
        top_counts = Counter(tops)
        stability.append({
            "model": model,
            "prompt_id": prompt_id,
            "mean_pairwise_jaccard": round(statistics.mean(similarities), 4),
            "top1_modal_firm": top_counts.most_common(1)[0][0],
            "top1_agreement": round(top_counts.most_common(1)[0][1] / 5, 2),
            "distinct_firms_across_runs": len(set().union(*sets)),
        })
    write_csv(OUTPUT / "cell-stability.csv", list(stability[0]), stability)

    model_rows = []
    for model in sorted({r["model"] for r in responses}):
        model_responses = [r for r in responses if r["model"] == model]
        model_flat = [r for r in flat if r["model"] == model and r["firm"]]
        model_stability = [r for r in stability if r["model"] == model]
        counts = Counter(r["firm"] for r in model_flat)
        total = sum(counts.values())
        model_rows.append({
            "model": model,
            "responses": len(model_responses),
            "firm_recommendations": total,
            "unique_firms": len(counts),
            "top5_mention_share": round(sum(n for _, n in counts.most_common(5)) / total, 4),
            "mean_cell_jaccard": round(statistics.mean(r["mean_pairwise_jaccard"] for r in model_stability), 4),
            "mean_top1_agreement": round(statistics.mean(r["top1_agreement"] for r in model_stability), 4),
        })
    write_csv(OUTPUT / "models.csv", list(model_rows[0]), model_rows)

    framework_rows = []
    for framework in sorted({r["framework"] for r in flat if r["framework"]}):
        mentions = [r for r in flat if r["framework"] == framework]
        framework_rows.append({
            "framework": framework,
            "mentions": len(mentions),
            "models": len({r["model"] for r in mentions}),
            "prompts": len({r["prompt_id"] for r in mentions}),
            "firms": " | ".join(name for name, _ in Counter(r["firm"] for r in mentions if r["firm"]).most_common(5)),
            "individuals": " | ".join(name for name, _ in Counter(r["individual"] for r in mentions if r["individual"]).most_common(5)),
        })
    framework_rows.sort(key=lambda r: (-r["mentions"], r["framework"]))
    write_csv(OUTPUT / "frameworks.csv", list(framework_rows[0]), framework_rows)

    verification = []
    grouped_prompt = defaultdict(list)
    for row in by_prompt:
        grouped_prompt[row["prompt_id"]].append(row)
    for prompt_id, prompt_rows in grouped_prompt.items():
        for position, row in enumerate(prompt_rows[:5], 1):
            verification.append({
                "verification_type": "firm_prompt_association",
                "priority": position,
                "prompt_id": prompt_id,
                "entity": row["firm"],
                "observed_count": row["response_inclusions"],
                "claim_to_check": "Current stage, geography, sector fit, portfolio evidence and accuracy of model-supplied reasons",
                "status": "unverified",
                "primary_source_url": "",
                "accessed_date": "",
                "notes": "",
            })
    for position, row in enumerate(framework_rows[:20], 1):
        verification.append({
            "verification_type": "framework_attribution",
            "priority": position,
            "prompt_id": "",
            "entity": row["framework"],
            "observed_count": row["mentions"],
            "claim_to_check": "Original author, firm affiliation at publication, original title and source",
            "status": "unverified",
            "primary_source_url": "",
            "accessed_date": "",
            "notes": "",
        })
    write_csv(OUTPUT / "verification-queue.csv", list(verification[0]), verification)

    summary = {
        "responses": len(responses),
        "recommendations": len(flat),
        "canonical_firms": len(firms),
        "framework_mentions": sum(bool(r["framework"]) for r in flat),
        "mean_cell_jaccard": round(statistics.mean(r["mean_pairwise_jaccard"] for r in stability), 4),
        "median_cell_jaccard": round(statistics.median(r["mean_pairwise_jaccard"] for r in stability), 4),
        "mean_top1_agreement": round(statistics.mean(r["top1_agreement"] for r in stability), 4),
        "stable_cells_jaccard_gte_0_6": sum(r["mean_pairwise_jaccard"] >= 0.6 for r in stability),
        "unstable_cells_jaccard_lt_0_4": sum(r["mean_pairwise_jaccard"] < 0.4 for r in stability),
    }
    (OUTPUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
