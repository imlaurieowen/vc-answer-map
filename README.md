# VC Answer Map

An open benchmark of which venture capital firms AI models recommend for specific founders, investment categories and operating problems.

The project asks a narrow question:

> When a founder describes what they are building or the problem they have, which venture firms does an AI model reach for, and why?

VC Answer Map measures model associations. It does not rank investment performance, founder experience or objective firm quality.

## What the benchmark tests

- Which firms are associated with particular sectors, stages, geographies and investment philosophies
- Which firms or investors are associated with useful founder advice
- Whether the association exists in model knowledge without live search
- Whether live retrieval produces a different answer
- Whether models provide specific evidence or generic prestige language
- Whether named ideas remain correctly attributed to their originators
- How stable the results are across model families and repeated runs

## Status

`v0.2-baseline-candidate`

The 2,000-response pre-publication baseline is complete. Reviewed aggregate results and publication figures are available in this repository. The independent second review is documented; native-product spot checks remain a clearly separated release gate.

## Read first

- [METHODOLOGY.md](METHODOLOGY.md): full research protocol
- [RESULTS.md](RESULTS.md): September 2026 baseline findings
- [data/README.md](data/README.md): field definitions and reproducibility boundary
- [docs/REVIEW.md](docs/REVIEW.md): automated and independent review record
- [AGENTS.md](AGENTS.md): rules for humans and coding agents working in this repository
- [LIMITATIONS.md](LIMITATIONS.md): what the study can and cannot establish
- [CORRECTIONS.md](CORRECTIONS.md): how firms can submit factual corrections
- [docs/FIRM_SELF_AUDIT.md](docs/FIRM_SELF_AUDIT.md): a practical accuracy and visibility audit for venture firms

## Repository boundary

This public repository contains reproducible methods, prompts, code and approved aggregate outputs. Credentials, unreviewed raw responses, private analysis and source material remain in local private storage.

## Licence

Code is licensed under MIT. Written methodology and published datasets are licensed under CC BY 4.0 unless a file states otherwise.
