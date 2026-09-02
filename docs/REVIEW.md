# Release review

## Automated verification

`python3 scripts/verify_release.py` checks the published response counts, closed/open overlap, source-audit totals and principal attribution claims directly from the aggregate files.

## Independent editorial review

On 2 September 2026, a separate model reviewer, `google/gemini-3.7-flash` via OpenRouter, compared the publication draft with the frozen evidence pack.

Verdict: conditional pass.

Accepted changes:

- Labelled the top-50 retrieved-firm source check as exploratory.
- Softened language claiming what the 3 manual-review cases could prove.
- Kept the opening product reference generic to avoid implying that the controlled API condition reproduced a specific native product.

Rejected changes:

- The reviewer described an April 2026 domain-registration date as impossible. The benchmark ran in September 2026, so the date was chronologically possible and the objection was rejected. The underlying observation remains a dated diligence signal, not proof of legitimacy or illegitimacy.
- Suggestions that weakened the distinction between measured attribution loss and causal influence were not adopted.

## Remaining gate

Native-product observations remain pending and must be reported separately from the controlled common-retriever benchmark. They are not required to reproduce the API baseline and must not be backfilled from API responses.
