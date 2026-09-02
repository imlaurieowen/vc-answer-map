#!/usr/bin/env python3
import csv
import json
import statistics
from itertools import combinations
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

from analyse_results import canonical_firm, write_csv

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "analysis" / "openbook"
OUTPUT.mkdir(parents=True, exist_ok=True)


def load_jsonl(path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def domain(url):
    host = urlparse(url or "").netloc.lower().split(":")[0]
    return host[4:] if host.startswith("www.") else host


def normalise_url(url):
    parsed = urlparse(url or "")
    host = parsed.netloc.lower().split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    path = parsed.path.rstrip("/") or "/"
    return host + path


def recommendation_rows(responses, condition):
    rows = []
    for response in responses:
        annotation_urls = {
            normalise_url(annotation.get("url_citation", {}).get("url", ""))
            for annotation in response.get("annotations", [])
            if annotation.get("type") == "url_citation"
        }
        for rank, rec in enumerate(response.get("parsed", {}).get("recommendations", []), 1):
            source_url = (rec.get("source_url") or "").strip()
            rows.append({
                "condition": condition,
                "model": response["model"],
                "prompt_id": response["prompt_id"],
                "prompt_type": response["prompt_type"],
                "run": response["run"],
                "rank": rank,
                "firm": canonical_firm(rec.get("firm")),
                "individual": (rec.get("individual") or "").strip(),
                "reason": (rec.get("reason") or "").strip(),
                "named_framework": (rec.get("named_framework") or "").strip(),
                "source_title": (rec.get("source_title") or "").strip(),
                "source_url": source_url,
                "source_domain": domain(source_url),
                "source_url_in_provider_annotations": int(bool(source_url) and normalise_url(source_url) in annotation_urls),
                "confidence": rec.get("confidence", ""),
            })
    return rows


def sets_by_cell(rows):
    result = defaultdict(set)
    for row in rows:
        if row["firm"]:
            result[(row["model"], row["prompt_id"])].add(row["firm"])
    return result


def top_by_cell(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["model"], row["prompt_id"])].append(row)
    result = {}
    for cell, cell_rows in grouped.items():
        counts = Counter(row["firm"] for row in cell_rows if row["firm"] and row["rank"] == 1)
        result[cell] = counts.most_common(1)[0][0] if counts else ""
    return result


def main():
    closed_responses = load_jsonl(ROOT / "results-full.jsonl") + load_jsonl(ROOT / "results-replicate.jsonl")
    open_responses = load_jsonl(ROOT / "results-openbook.jsonl")
    closed = recommendation_rows(closed_responses, "closed_book")
    opened = recommendation_rows(open_responses, "open_book")
    if opened:
        write_csv(OUTPUT / "recommendations-openbook.csv", list(opened[0]), opened)

    closed_sets = sets_by_cell(closed)
    open_sets = sets_by_cell(opened)
    closed_tops = top_by_cell(closed)
    open_tops = top_by_cell(opened)
    comparison = []
    for model, prompt_id in sorted(open_sets):
        left = closed_sets.get((model, prompt_id), set())
        right = open_sets[(model, prompt_id)]
        union = left | right
        comparison.append({
            "model": model,
            "prompt_id": prompt_id,
            "closed_unique_firms": len(left),
            "open_unique_firms": len(right),
            "shared_firms": len(left & right),
            "set_jaccard": round(len(left & right) / len(union), 4) if union else 1.0,
            "closed_modal_top1": closed_tops.get((model, prompt_id), ""),
            "open_modal_top1": open_tops.get((model, prompt_id), ""),
            "top1_same": int(closed_tops.get((model, prompt_id), "") == open_tops.get((model, prompt_id), "")),
        })
    if comparison:
        write_csv(OUTPUT / "closed-v-open-cells.csv", list(comparison[0]), comparison)

    model_rows = []
    for model in sorted({r["model"] for r in open_responses}):
        responses = [r for r in open_responses if r["model"] == model]
        recs = [r for r in opened if r["model"] == model]
        urls = [r["source_url"] for r in recs if r["source_url"]]
        annotation_supported = [r for r in recs if r["source_url_in_provider_annotations"]]
        domains = [r["source_domain"] for r in recs if r["source_domain"]]
        annotations = sum(len(r.get("annotations", [])) for r in responses)
        cells = [r for r in comparison if r["model"] == model]
        model_rows.append({
            "model": model,
            "responses": len(responses),
            "recommendations": len(recs),
            "recommendations_with_source_url": len(urls),
            "source_url_coverage": round(len(urls) / len(recs), 4) if recs else 0,
            "annotation_supported_url_rate": round(len(annotation_supported) / len(recs), 4) if recs else 0,
            "provider_annotations": annotations,
            "unique_source_domains": len(set(domains)),
            "top5_domain_share": round(sum(n for _, n in Counter(domains).most_common(5)) / len(domains), 4) if domains else 0,
            "mean_closed_open_jaccard": round(statistics.mean(r["set_jaccard"] for r in cells), 4) if cells else "",
            "modal_top1_same_share": round(statistics.mean(r["top1_same"] for r in cells), 4) if cells else "",
        })
    if model_rows:
        write_csv(OUTPUT / "models-openbook.csv", list(model_rows[0]), model_rows)

    source_rows = []
    for source_domain, count in Counter(r["source_domain"] for r in opened if r["source_domain"]).most_common():
        source_rows.append({
            "source_domain": source_domain,
            "recommendation_citations": count,
            "models": len({r["model"] for r in opened if r["source_domain"] == source_domain}),
            "prompts": len({r["prompt_id"] for r in opened if r["source_domain"] == source_domain}),
        })
    if source_rows:
        write_csv(OUTPUT / "source-domains.csv", list(source_rows[0]), source_rows)

    # Exploratory, post-hoc diagnostic registered after partial output was seen.
    # It describes convergence under the shared retrieval layer and is never
    # presented as a preregistered confirmatory measure.
    firm_convergence = []
    for (prompt_id, firm), recs in sorted(
        defaultdict(list, {
            key: [r for r in opened if (r["prompt_id"], r["firm"]) == key]
            for key in {(r["prompt_id"], r["firm"]) for r in opened if r["firm"]}
        }).items()
    ):
        firm_convergence.append({
            "prompt_id": prompt_id,
            "firm": firm,
            "recommendations": len(recs),
            "models": len({r["model"] for r in recs}),
            "runs": len({(r["model"], r["run"]) for r in recs}),
            "source_domains": len({r["source_domain"] for r in recs if r["source_domain"]}),
        })
    firm_convergence.sort(key=lambda r: (r["prompt_id"], -r["models"], -r["recommendations"], r["firm"]))
    if firm_convergence:
        write_csv(OUTPUT / "retrieval-firm-convergence.csv", list(firm_convergence[0]), firm_convergence)

    prompt_convergence = []
    for prompt_id in sorted({r["prompt_id"] for r in opened}):
        by_model = defaultdict(set)
        domains_by_model = defaultdict(set)
        for row in opened:
            if row["prompt_id"] != prompt_id:
                continue
            if row["firm"]:
                by_model[row["model"]].add(row["firm"])
            if row["source_domain"]:
                domains_by_model[row["model"]].add(row["source_domain"])
        firm_pairs = []
        domain_pairs = []
        for left, right in combinations(sorted(by_model), 2):
            union = by_model[left] | by_model[right]
            firm_pairs.append(len(by_model[left] & by_model[right]) / len(union) if union else 1.0)
            domain_union = domains_by_model[left] | domains_by_model[right]
            domain_pairs.append(len(domains_by_model[left] & domains_by_model[right]) / len(domain_union) if domain_union else 1.0)
        prompt_convergence.append({
            "prompt_id": prompt_id,
            "models_observed": len(by_model),
            "mean_pairwise_firm_jaccard": round(statistics.mean(firm_pairs), 4) if firm_pairs else "",
            "mean_pairwise_source_domain_jaccard": round(statistics.mean(domain_pairs), 4) if domain_pairs else "",
        })
    if prompt_convergence:
        write_csv(OUTPUT / "retrieval-prompt-convergence.csv", list(prompt_convergence[0]), prompt_convergence)

    summary = {
        "closed_responses": len(closed_responses),
        "open_responses": len(open_responses),
        "open_recommendations": len(opened),
        "open_recommendations_with_source_url": sum(bool(r["source_url"]) for r in opened),
        "open_recommendations_with_annotation_supported_url": sum(bool(r["source_url_in_provider_annotations"]) for r in opened),
        "provider_annotations": sum(len(r.get("annotations", [])) for r in open_responses),
        "cells_compared": len(comparison),
        "mean_closed_open_jaccard": round(statistics.mean(r["set_jaccard"] for r in comparison), 4) if comparison else None,
        "modal_top1_same_share": round(statistics.mean(r["top1_same"] for r in comparison), 4) if comparison else None,
        "exploratory_prompts_with_cross_model_convergence": len(prompt_convergence),
    }
    (OUTPUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
