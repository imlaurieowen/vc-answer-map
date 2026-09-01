# Working rules for VC Answer Map

These instructions apply to humans, Codex, Claude and other coding or research agents working in this repository.

## Mission

Build a transparent, reproducible benchmark of which venture firms and investors appear in AI answers to founder-intent questions.

The project measures model behaviour. Never convert model output into an unsupported claim about actual firm quality, performance or founder experience.

## Start here

Before changing anything, read:

1. `METHODOLOGY.md`
2. `LIMITATIONS.md`
3. `CORRECTIONS.md`
4. The latest entry in `docs/DECISION_LOG.md`

## Pre-registration boundary

The first complete baseline begins after the commit tagged `prebaseline-v0.1`.

After that point:

- Never silently edit frozen prompts, hypotheses, model selection or scoring definitions.
- Record a methodological amendment in `docs/DECISION_LOG.md`.
- Assign a new version when a change affects comparability.
- Preserve the original file or Git history.
- Label exploratory and confirmatory analysis separately.

## Public and private data

This is a public repository.

Allowed:

- Methodology
- Prompt and model configuration
- Reproduction code
- Reviewed aggregate results
- Approved sanitised examples
- Public verification sources

Prohibited:

- API keys, tokens and `.env` files
- Raw private model responses
- Unreviewed model claims about firms or people
- Client documents, calls, transcripts or private Refinery material
- Personal information that is unnecessary for the benchmark
- Absolute local paths in committed files

Raw responses live outside this repository in approved local private storage. Scripts should accept an external input path or an environment variable. Never copy private inputs into this repository for convenience.

## Credentials and cost

- Read API keys only from environment variables.
- Never print, log, commit or transmit secrets.
- Every paid runner must implement a hard cost ceiling.
- Run a minimal smoke test before a new full execution.
- Record actual model IDs, usage and cost.
- Stop on uncertain billing behaviour.

## Research integrity

- Preserve exact prompts and raw observations.
- Keep model output separate from human coding.
- Record timestamps, model IDs, provider metadata and search condition.
- Disable model fallbacks where the provider permits.
- Retain errors, refusals and missing responses.
- Do not discard inconvenient or null findings.
- Do not alter scoring because a favoured firm performs poorly.
- Report sample sizes and repetition counts beside every metric.
- Treat self-reported model confidence as uncalibrated.

## Factual verification

Model output only proves that a model produced the output.

Before publishing a claim about a firm, investor, portfolio or framework:

1. Find a dated primary source.
2. Record the source URL and access date.
3. Check that the source directly supports the claim.
4. Mark the verification status.
5. Preserve corrections rather than silently rewriting history.

## Language

- Use UK spelling.
- Use digits for numbers.
- Avoid hype and false precision.
- Say `model recommendation`, `model association` or `observed inclusion`.
- Never describe the benchmark as determining the objectively best venture firms.
- Distinguish closed-book model behaviour from search-enabled retrieval.
- Use exact dates and model identifiers.

## Code changes

- Prefer standard-library implementations where practical.
- Make runs resumable and idempotent.
- Validate structured outputs before analysis.
- Add tests for parsers, scoring and deduplication.
- Do not overwrite historical outputs.
- Generate aggregate files from code rather than manual spreadsheet edits.
- Keep dependencies minimal and documented.

## Publication gate

No result is publication-ready until:

- The run manifest is complete
- Parsing checks pass
- Relevant factual claims are verified
- At least one second reviewer checks the interpretation
- Limitations accompany the result
- Private data and credentials are absent

## Agent handoff

At the end of a substantive session, append a dated entry to `docs/DECISION_LOG.md` containing:

- Work completed
- Methodological decisions
- Files changed
- Tests run
- Costs incurred
- Open risks
- Exact next action
