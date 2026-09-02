#!/usr/bin/env python3
"""Check that published aggregates support the headline release claims."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def rows(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="") as handle:
        return list(csv.DictReader(handle))


def close(actual: float, expected: float, tolerance: float = 0.0001) -> None:
    assert abs(actual - expected) <= tolerance, (actual, expected)


def main() -> None:
    metrics = json.loads((DATA / "headline-metrics.json").read_text())
    assert metrics["closed_book_responses"] == 800
    assert metrics["open_book_responses"] == 480
    assert metrics["specificity_responses"] == 720
    assert metrics["total_primary_responses"] == 2_000
    close(metrics["mean_closed_open_jaccard"], 0.1305)
    close(metrics["modal_top1_same_share"], 0.175)
    close(metrics["open_source_url_coverage"], 0.9982)

    cells = rows("closed-v-open-cells.csv")
    assert len(cells) == 160
    close(sum(float(row["set_jaccard"]) for row in cells) / len(cells), 0.1305)
    discovery = [row for row in cells if row["prompt_id"].startswith("discovery_")]
    close(sum(float(row["set_jaccard"]) for row in discovery) / len(discovery), 0.0509)
    close(sum(int(row["top1_same"]) for row in discovery) / len(discovery), 0.0875)

    audit = Counter(row["status"] for row in rows("retrieved-source-audit.csv"))
    assert audit == {"verified": 39, "qualified": 8, "needs_manual_review": 3}

    attribution = {row["framework"]: row for row in rows("attribution-summary.csv")}
    default_alive = attribution["Default Alive or Default Dead"]
    assert int(default_alive["mentions"]) == 83
    close(float(default_alive["individual_correct_rate"]), 0.6747)
    close(float(default_alive["firm_correct_rate"]), 0.6988)

    print("Release verification passed: counts, overlap, source audit and attribution.")


if __name__ == "__main__":
    main()
