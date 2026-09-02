#!/usr/bin/env python3
"""Build publication-oriented aggregate tables from reviewed VC Answer Map outputs."""

from __future__ import annotations

import csv
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ANALYSIS = ROOT / "analysis"
OUT = ANALYSIS / "editorial"
OUT.mkdir(parents=True, exist_ok=True)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(name: str, rows: list[dict]) -> None:
    if not rows:
        return
    with (OUT / name).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def response_key(row: dict[str, str]) -> tuple[str, str, str]:
    return row["model"], row["prompt_id"], row["run"]


def rank_firms(rows: list[dict[str, str]], condition: str) -> list[dict]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row.get("firm"):
            grouped[(row["prompt_id"], row["firm"])].append(row)
    output = []
    for (prompt_id, firm), mentions in grouped.items():
        inclusions = len({response_key(row) for row in mentions})
        output.append({
            "condition": condition,
            "prompt_id": prompt_id,
            "prompt_type": mentions[0].get("prompt_type", "discovery"),
            "firm": firm,
            "response_inclusions": inclusions,
            "eligible_responses": 40 if condition == "closed_book" else 24,
            "mention_rate": round(inclusions / (40 if condition == "closed_book" else 24), 4),
            "models": len({row["model"] for row in mentions}),
            "top_rank_count": sum(row["rank"] == "1" for row in mentions),
        })
    output.sort(key=lambda r: (r["condition"], r["prompt_id"], -r["response_inclusions"], -r["models"], r["firm"]))
    ranks = Counter()
    for row in output:
        key = (row["condition"], row["prompt_id"])
        ranks[key] += 1
        row["rank_within_prompt"] = ranks[key]
    return output


def specificity_tables(rows: list[dict[str, str]], prestige: set[str], targets: dict[str, set[str]]) -> tuple[list[dict], list[dict]]:
    groups: dict[tuple[str, str, int], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[(row["condition"], row["category"], int(row["specificity_level"]))].append(row)

    summaries = []
    firm_rows = []
    for (condition, category, level), group in sorted(groups.items()):
        recs = [r for r in group if r.get("firm")]
        by_firm: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in recs:
            by_firm[row["firm"]].append(row)
        ranked = sorted(by_firm.items(), key=lambda item: (-len({response_key(r) for r in item[1]}), item[0]))
        top5 = ranked[:5]
        summaries.append({
            "condition": condition,
            "category": category,
            "specificity_level": level,
            "recommendations": len(recs),
            "unique_firms": len(by_firm),
            "prestige_share": round(sum(r["firm"] in prestige for r in recs) / len(recs), 4),
            "target_share": round(sum(r["firm"] in targets.get(category, set()) for r in recs) / len(recs), 4),
            "top_firms": " | ".join(f"{firm} ({len({response_key(r) for r in rs})}/24)" for firm, rs in top5),
            "top5_inclusion_share": round(sum(len({response_key(r) for r in rs}) for _, rs in top5) / (24 * 5), 4),
        })
        for position, (firm, firm_mentions) in enumerate(ranked, 1):
            firm_rows.append({
                "condition": condition,
                "category": category,
                "specificity_level": level,
                "rank": position,
                "firm": firm,
                "response_inclusions": len({response_key(r) for r in firm_mentions}),
                "models": len({r["model"] for r in firm_mentions}),
                "is_prestige": int(firm in prestige),
                "is_target_association": int(firm in targets.get(category, set())),
            })
    return summaries, firm_rows


def main() -> None:
    closed = read_csv(ANALYSIS / "recommendations-normalised.csv")
    opened = read_csv(ANALYSIS / "openbook" / "recommendations-openbook.csv")
    specificity = read_csv(ANALYSIS / "specificity" / "recommendations.csv")
    pools = read_csv(ANALYSIS / "specificity" / "predefined-pools.csv")
    prestige = {r["firm"] for r in pools if r["pool"] == "prestige"}
    targets: dict[str, set[str]] = defaultdict(set)
    for row in pools:
        if row["pool"] == "target_association":
            targets[row["category"]].add(row["firm"])

    prompt_rankings = rank_firms(closed, "closed_book") + rank_firms(opened, "open_book")
    write_csv("prompt-firm-rankings.csv", prompt_rankings)

    discovery_leaders = [r for r in prompt_rankings if r["prompt_type"] == "discovery" and r["rank_within_prompt"] <= 5]
    write_csv("discovery-top-five.csv", discovery_leaders)

    spec_summary, spec_firms = specificity_tables(specificity, prestige, targets)
    write_csv("specificity-category-level.csv", spec_summary)
    write_csv("specificity-firm-rankings.csv", spec_firms)

    quality = read_csv(ANALYSIS / "openbook" / "verification-reviewed.csv")
    write_csv("retrieved-source-audit.csv", quality)

    status_counts = Counter(r["status"] for r in quality)
    open_summary = json.loads((ANALYSIS / "openbook" / "summary.json").read_text())
    base_summary = json.loads((ANALYSIS / "summary.json").read_text())
    spec_level = read_csv(ANALYSIS / "specificity" / "level-metrics.csv")
    attribution = read_csv(ANALYSIS / "attribution-summary.csv")
    convergence = read_csv(ANALYSIS / "openbook" / "retrieval-prompt-convergence.csv")
    closed_open_cells = read_csv(ANALYSIS / "openbook" / "closed-v-open-cells.csv")

    type_metrics = {}
    for prompt_type in ("discovery", "problem"):
        type_closed = [r for r in closed if r["prompt_type"] == prompt_type and r["firm"]]
        counts = Counter(r["firm"] for r in type_closed)
        cells = [r for r in closed_open_cells if r["prompt_id"].startswith(prompt_type + "_")]
        type_metrics[prompt_type] = {
            "closed_recommendations": len(type_closed),
            "closed_unique_firms": len(counts),
            "closed_top5_share": round(sum(n for _, n in counts.most_common(5)) / len(type_closed), 4),
            "closed_top5_firms": [firm for firm, _ in counts.most_common(5)],
            "mean_closed_open_jaccard": round(statistics.mean(float(r["set_jaccard"]) for r in cells), 4),
            "modal_top1_same_share": round(statistics.mean(int(r["top1_same"]) for r in cells), 4),
        }

    headlines = {
        "closed_book_responses": base_summary["responses"],
        "open_book_responses": open_summary["open_responses"],
        "specificity_responses": 720,
        "total_primary_responses": base_summary["responses"] + open_summary["open_responses"] + 720,
        "mean_closed_open_jaccard": open_summary["mean_closed_open_jaccard"],
        "modal_top1_same_share": open_summary["modal_top1_same_share"],
        "open_source_url_coverage": round(open_summary["open_recommendations_with_source_url"] / open_summary["open_recommendations"], 4),
        "retrieved_source_audit": dict(status_counts),
        "by_prompt_type": type_metrics,
    }
    (OUT / "headline-metrics.json").write_text(json.dumps(headlines, indent=2) + "\n")

    lines = [
        "# VC Answer Map editorial evidence pack",
        "",
        "Generated from completed, validated experiment outputs. Model recommendations measure model behaviour, not investment quality.",
        "",
        "## Dataset",
        "",
        f"- {headlines['total_primary_responses']:,} primary responses: {headlines['closed_book_responses']} closed-book baseline, {headlines['open_book_responses']} controlled open-book, and 720 specificity responses.",
        f"- Closed/open mean firm-set Jaccard: {headlines['mean_closed_open_jaccard']:.1%}.",
        f"- Same modal top recommendation after retrieval: {headlines['modal_top1_same_share']:.1%} of model-prompt cells.",
        f"- Open-book source URL coverage: {headlines['open_source_url_coverage']:.1%}.",
        f"- Discovery answers used {type_metrics['discovery']['closed_unique_firms']} firms; their top 5 captured {type_metrics['discovery']['closed_top5_share']:.1%} of firm-bearing recommendations.",
        f"- Founder-problem answers used {type_metrics['problem']['closed_unique_firms']} firms; their top 5 captured {type_metrics['problem']['closed_top5_share']:.1%}.",
        f"- Retrieval changed discovery most: {type_metrics['discovery']['mean_closed_open_jaccard']:.1%} mean firm overlap and the same modal top firm in {type_metrics['discovery']['modal_top1_same_share']:.1%} of cells.",
        f"- Founder-problem answers retained {type_metrics['problem']['mean_closed_open_jaccard']:.1%} mean firm overlap and the same modal top firm in {type_metrics['problem']['modal_top1_same_share']:.1%} of cells.",
        "",
        "## Specificity ladder",
        "",
        "| Condition | Level | Firms | Top-5 concentration | Prestige leakage | Target association |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in spec_level:
        lines.append(f"| {row['condition']} | {row['specificity_level']} | {row['unique_firms']} | {float(row['top5_concentration']):.1%} | {float(row['prestige_leakage']):.1%} | {float(row['target_association_rate']):.1%} |")
    lines += [
        "",
        "The preregistered target-association proxy falls with specificity in both conditions. Do not describe specificity as automatically surfacing verified specialists. The strongest supported result is that legitimate founder detail almost eliminates the empirically defined prestige pool, while the replacement set is narrower and search-layer dependent.",
        "",
        "## Retrieved-source audit",
        "",
        f"- Verified: {status_counts['verified']}/50",
        f"- Qualified: {status_counts['qualified']}/50",
        f"- Needs manual review: {status_counts['needs_manual_review']}/50",
        f"- Unverified: {status_counts['unverified']}/50",
        "",
        f"The {status_counts['needs_manual_review']} manual-review cases must be described as unverified warning signs, never as proven fabrication.",
        "",
        "## Attribution examples",
        "",
        "| Framework | Mentions | Correct person | Correct firm |",
        "|---|---:|---:|---:|",
    ]
    for row in attribution:
        if row["individual_correct_rate"]:
            lines.append(f"| {row['framework']} | {row['mentions']} | {float(row['individual_correct_rate']):.1%} | {float(row['firm_correct_rate']):.1%} |")
    lines += [
        "",
        "## Exploratory retrieval convergence",
        "",
        "Every prompt showed cross-model convergence under the shared retriever. This is post-hoc evidence and must remain labelled exploratory.",
        "",
        "Highest cross-model firm convergence examples are in `prompt-firm-rankings.csv`; source convergence is in the preregistered analysis outputs.",
        "",
        "## Editorial guardrails",
        "",
        "- Say observed, recommended, retrieved or associated. Never say a firm is objectively best.",
        "- Keep common-retriever results separate from native product behaviour.",
        "- Label retrieval convergence and source-quality audit exploratory.",
        "- Link claims about firms to the reviewed source ledger.",
        "- Treat specificity's failure to increase the frozen target pool as a real result, not a metric to rewrite.",
    ]
    (OUT / "EVIDENCE-PACK.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({"output": str(OUT), "files": len(list(OUT.iterdir())), "headlines": headlines}, indent=2))


if __name__ == "__main__":
    main()
