# Project context

VC Answer Map is a transparent, reproducible benchmark of which venture firms and investors appear in AI answers to founder-intent questions.

The project measures model behaviour. It does not establish actual firm quality, performance or founder experience.

## Research protocol

Read these before modifying the benchmark:

1. `METHODOLOGY.md`
2. `LIMITATIONS.md`
3. `CORRECTIONS.md`
4. The latest entry in `docs/DECISION_LOG.md`

The first complete baseline begins after the commit tagged `prebaseline-v0.1`. Subsequent work should:

- preserve frozen prompts, hypotheses, model selection and scoring definitions;
- record methodological amendments in `docs/DECISION_LOG.md`;
- assign a new version when a change affects comparability;
- preserve original files or Git history; and
- distinguish exploratory from confirmatory analysis.

## Public and private data

This public repository may contain methodology, prompt and model configuration, reproduction code, reviewed aggregate results, approved sanitised examples and public verification sources.

It must not contain credentials, raw private responses, unreviewed claims about firms or people, client documents, private source material, unnecessary personal information or absolute local paths.

Raw responses remain outside the repository in private storage. Scripts accept an external input path or environment variable.

## Research integrity

- Preserve exact prompts and raw observations.
- Keep model output separate from human coding.
- Record timestamps, model identifiers, provider metadata and search condition.
- Disable model fallbacks where the provider permits.
- Retain errors, refusals and missing responses.
- Do not discard inconvenient or null findings.
- Do not alter scoring because a favoured firm performs poorly.
- Report sample sizes and repetition counts beside every metric.
- Treat self-reported model confidence as uncalibrated.

## Factual verification

Model output proves only that a model produced the output. Before publishing a claim about a firm, investor, portfolio or framework:

1. Find a dated primary source.
2. Record the source URL and access date.
3. Check that the source directly supports the claim.
4. Mark the verification status.
5. Preserve corrections rather than silently rewriting history.

## Reproduction and release

- Read API keys only from environment variables.
- Never print, log, commit or transmit secrets.
- Use a hard cost ceiling for paid runs.
- Run a minimal smoke test before full execution.
- Record actual model identifiers, usage and cost.
- Keep runs resumable and idempotent.
- Validate structured outputs before analysis.
- Generate aggregate files from code rather than manual spreadsheet edits.
- Do not overwrite historical outputs.

No result is publication-ready until the run manifest is complete, parsing checks pass, relevant factual claims are reviewed, limitations accompany the result and private material is absent.

## Language

- Use UK spelling and digits.
- Avoid hype and false precision.
- Say `model recommendation`, `model association` or `observed inclusion`.
- Never present the benchmark as identifying the objectively best venture firms.
- Distinguish closed-book model behaviour from search-enabled retrieval.
- Use exact dates and model identifiers.
