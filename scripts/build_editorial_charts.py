#!/usr/bin/env python3
"""Generate publication-ready SVG charts for the VC Answer Map essay."""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ANALYSIS = ROOT / "analysis"
OUT = ANALYSIS / "editorial" / "charts"
OUT.mkdir(parents=True, exist_ok=True)

BG, FG, MUTED, LIME, BLUE, GRID, WARN = "#111315", "#F4F0E6", "#A5A7A9", "#C7F36B", "#78A9FF", "#34383C", "#FFB86B"


def esc(value: object) -> str:
    return html.escape(str(value))


def save(name: str, width: int, height: int, body: str) -> None:
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="{BG}"/>
<style>
text {{ font-family: Inter, Arial, sans-serif; fill: {FG}; }}
.title {{ font-size: 34px; font-weight: 700; }} .sub {{ font-size: 17px; fill: {MUTED}; }}
.big {{ font-size: 76px; font-weight: 750; }} .label {{ font-size: 18px; }}
.small {{ font-size: 14px; fill: {MUTED}; }} .firm {{ font-size: 15px; font-weight: 650; }}
</style>{body}</svg>'''
    (OUT / name).write_text(svg)


def retrieval_rewrite() -> None:
    data = json.loads((ANALYSIS / "editorial" / "headline-metrics.json").read_text())
    body = [
        '<text x="60" y="68" class="title">Search rewrote the shortlist</text>',
        '<text x="60" y="104" class="sub">Controlled comparison across 8 model families and 20 identical prompts</text>',
        f'<text x="90" y="245" class="big" fill="{LIME}">{data["mean_closed_open_jaccard"]:.1%}</text>',
        '<text x="90" y="287" class="label">mean overlap between closed- and open-book firm sets</text>',
        f'<text x="715" y="245" class="big" fill="{BLUE}">{data["modal_top1_same_share"]:.1%}</text>',
        '<text x="715" y="287" class="label">kept the same modal first recommendation</text>',
        '<line x1="640" y1="150" x2="640" y2="325" stroke="#34383C" stroke-width="2"/>',
        '<text x="60" y="395" class="small">160 model-prompt cells. Open-book used the same Exa retrieval layer for every model family.</text>',
    ]
    save("search-rewrites-shortlist.svg", 1280, 450, "\n".join(body))


def specificity() -> None:
    rows = list(csv.DictReader((ANALYSIS / "specificity" / "level-metrics.csv").open()))
    width, height = 1280, 610
    x = {1: 340, 2: 670, 3: 1000}
    body = [
        '<text x="60" y="68" class="title">Specificity removes prestige faster than it finds the expected specialist</text>',
        '<text x="60" y="104" class="sub">Share of all firm recommendations at each legitimate founder-detail level</text>',
    ]
    panels = [("prestige_leakage", "Empirical prestige pool", 165), ("target_association_rate", "Frozen category-association pool", 365)]
    colours = {"closed_book": LIME, "open_book": BLUE}
    for metric, label, top in panels:
        body.append(f'<text x="60" y="{top+20}" class="label">{esc(label)}</text>')
        for level in (1, 2, 3):
            body.append(f'<text x="{x[level]-35}" y="{top+145}" class="small">Level {level}</text>')
        for condition in ("closed_book", "open_book"):
            vals = [r for r in rows if r["condition"] == condition]
            points = []
            for row in vals:
                level = int(row["specificity_level"])
                value = float(row[metric])
                y = top + 110 - value * 260
                points.append((x[level], y, value))
            body.append(f'<polyline points="{" ".join(f"{px},{py:.1f}" for px, py, _ in points)}" fill="none" stroke="{colours[condition]}" stroke-width="5"/>')
            for px, py, value in points:
                body += [f'<circle cx="{px}" cy="{py:.1f}" r="8" fill="{colours[condition]}"/>', f'<text x="{px+14}" y="{py+6:.1f}" class="firm">{value:.1%}</text>']
    body += [
        f'<rect x="820" y="558" width="18" height="5" fill="{LIME}"/><text x="848" y="566" class="small">Closed-book</text>',
        f'<rect x="990" y="558" width="18" height="5" fill="{BLUE}"/><text x="1018" y="566" class="small">Common retriever</text>',
        '<text x="60" y="566" class="small">Target association is a preregistered proxy, not a quality score.</text>',
    ]
    save("specificity-prestige-specialists.svg", width, height, "\n".join(body))


def source_audit() -> None:
    rows = list(csv.DictReader((ANALYSIS / "openbook" / "verification-reviewed.csv").open()))
    counts = {status: sum(r["status"] == status for r in rows) for status in ("verified", "qualified", "needs_manual_review", "unverified")}
    labels = [("Verified", counts["verified"], LIME), ("Qualified", counts["qualified"], BLUE), ("Manual review", counts["needs_manual_review"], WARN), ("Unverified", counts["unverified"], MUTED)]
    body = [
        '<text x="60" y="68" class="title">A citation is the beginning of diligence</text>',
        '<text x="60" y="104" class="sub">Human review of the top 5 retrieved firms for each of 10 discovery prompts</text>',
    ]
    for i, (label, value, colour) in enumerate(labels):
        y = 165 + i * 82
        body += [
            f'<text x="60" y="{y+31}" class="label">{label}</text>',
            f'<rect x="280" y="{y}" width="800" height="40" rx="4" fill="{GRID}"/>',
            f'<rect x="280" y="{y}" width="{800*value/50:.1f}" height="40" rx="4" fill="{colour}"/>',
            f'<text x="1105" y="{y+30}" class="firm">{value}/50</text>',
        ]
    body.append('<text x="60" y="535" class="small">Qualified means the entity is real but an important stage, vehicle or availability caveat affects founder fit.</text>')
    save("retrieved-source-audit.svg", 1280, 585, "\n".join(body))


def shortlist_table() -> None:
    rows = list(csv.DictReader((ANALYSIS / "editorial" / "discovery-top-five.csv").open()))
    names = {
        "discovery_capital_efficient_saas": "Capital-efficient SaaS", "discovery_climate_hardware": "Climate hardware",
        "discovery_consumer": "Consumer", "discovery_dev_infra": "Developer infrastructure", "discovery_enterprise_ai": "Enterprise AI",
        "discovery_eu_biotech": "European biotech", "discovery_eu_defence": "European defence", "discovery_eu_spinout": "University spinouts",
        "discovery_fintech_infra": "Fintech infrastructure", "discovery_preseed_technical": "Pre-Seed technical founder",
    }
    body = [
        '<text x="50" y="62" class="title">Memory and retrieval nominate different category owners</text>',
        '<text x="50" y="98" class="sub">Most frequently included firm in each discovery prompt</text>',
        f'<text x="400" y="142" class="label" fill="{LIME}">Closed-book leader</text>',
        f'<text x="850" y="142" class="label" fill="{BLUE}">Common-retriever leader</text>',
    ]
    for i, prompt in enumerate(names):
        y = 180 + i * 58
        closed = next(r for r in rows if r["prompt_id"] == prompt and r["condition"] == "closed_book" and r["rank_within_prompt"] == "1")
        opened = next(r for r in rows if r["prompt_id"] == prompt and r["condition"] == "open_book" and r["rank_within_prompt"] == "1")
        body += [
            f'<text x="50" y="{y}" class="small">{esc(names[prompt])}</text>',
            f'<text x="400" y="{y}" class="firm">{esc(closed["firm"])} · {float(closed["mention_rate"]):.0%}</text>',
            f'<text x="850" y="{y}" class="firm">{esc(opened["firm"])} · {float(opened["mention_rate"]):.0%}</text>',
            f'<line x1="50" y1="{y+18}" x2="1220" y2="{y+18}" stroke="{GRID}"/>',
        ]
    body.append('<text x="50" y="785" class="small">Rates use 40 closed-book and 24 open-book responses per prompt. Model behaviour, not firm quality.</text>')
    save("category-leaders-closed-open.svg", 1280, 825, "\n".join(body))


def main() -> None:
    retrieval_rewrite(); specificity(); source_audit(); shortlist_table()
    print("\n".join(str(path) for path in sorted(OUT.glob("*.svg"))))


if __name__ == "__main__":
    main()
