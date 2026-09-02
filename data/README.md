# Data dictionary

These are reviewed aggregate outputs from the September 2026 pre-publication baseline. Raw model responses remain private because they contain unreviewed model-generated claims and provider material.

## Common fields

- `condition`: `closed_book` or `open_book`; open-book means the controlled common-retriever condition, not a native product browsing mode.
- `prompt_id`: stable identifier from `config/prompts.json`.
- `prompt_type`: funding `discovery` or founder operating `problem`.
- `canonical_firm`: manually normalised firm identity.
- `response_count`: number of responses in the relevant cell.
- `inclusion_count`: responses containing the firm at least once.
- `inclusion_share`: `inclusion_count / response_count`.
- `model_count`: distinct model families containing the firm.
- `top1_count`: responses placing the firm first.

## File notes

### `headline-metrics.json`

Top-level counts, concentration, overlap and source-audit status used in the public summary.

### `discovery-top-five.csv`

The top 5 canonical firms for each funding-discovery prompt under both conditions. Ties are resolved deterministically for display; small rank differences should not be over-interpreted.

### `closed-v-open-cells.csv`

One row per matched model-prompt cell. `jaccard` is intersection divided by union of the 2 firm sets. `same_top1` compares the first recommendation.

### `specificity-category-level.csv`

Aggregates the specificity panel by category, condition and detail level. Prestige and target pools were defined before the completed specificity analysis. They are diagnostic proxies, not quality labels.

### `attribution-summary.csv`

Counts detected mentions of named frameworks and whether the expected individual and institution were present. Detection and entity normalisation can miss paraphrases.

### `retrieval-prompt-convergence.csv`

Exploratory measures of cross-model convergence when all families received the same retrieved context. This analysis was registered after partial results were observed.

### `retrieved-source-audit.csv`

Manual review of the 5 most retrieved firms for each funding prompt. `verified`, `qualified` and `needs_manual_review` describe whether public sources supported the observed firm-prompt association and relevant claims at the access date. They are not judgements about investment quality or legitimacy.

## Reproducibility boundary

The scripts in `scripts/` reproduce analysis from the frozen private response corpus when given the expected input structure. They are published for transparency. The aggregate tables here are sufficient to inspect the published numerical claims without access to raw responses.

Run `python3 scripts/verify_release.py` to check the published response counts, overlap metrics, source-audit totals and principal attribution figures directly from these aggregate files.
