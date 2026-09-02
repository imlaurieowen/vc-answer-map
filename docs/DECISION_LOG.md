# Decision log

## 2026-09-01: pre-baseline design

- Defined the primary question as which venture firms models recommend for founder categories and operating problems.
- Selected 10 discovery prompts and 10 founder-problem prompts.
- Selected one model from each of eight developer families.
- Separated closed-book model behaviour from open-book retrieval.
- Chose a 160-response exploratory baseline followed by repeated confirmatory runs on selected prompts.
- Decided to publish methodology before results while keeping raw responses in local private storage.
- Recorded six competing hypotheses before complete baseline analysis.
- Completed a two-call private smoke test. No full baseline results were viewed.
- Smoke-test API cost was approximately $0.012.

Next action: freeze exact configuration, add reproducibility metadata to the private runner, tag `prebaseline-v0.1`, then launch the private baseline.

## 2026-09-01: execution amendment v0.1a

- Stopped the first full-run attempt after one usable response and 2 failed attempts on the next job.
- The failure was mechanical: a 1,200-token completion ceiling produced truncated JSON, followed by a response with no answer content.
- No complete-baseline analysis was performed and no prompt, hypothesis, model or scoring definition was changed.
- Preserved the partial attempt as an aborted private run.
- Raised the completion ceiling to 3,000 tokens for all models.
- Requested low reasoning effort where supported to protect the structured answer budget.
- Assigned a new run identifier and methodology tag so the aborted attempt cannot be mixed with the clean baseline.

Next action: run a 2-call v0.1a smoke test, then launch the clean baseline if both responses validate.

## 2026-09-01: provider compatibility amendment v0.1b

- Paused the v0.1a baseline after 19 valid responses because DeepSeek and Mistral repeatedly returned empty answer content.
- Ran a 2-call compatibility test using the same prompt and schema with reasoning disabled for those 2 models.
- DeepSeek and Mistral both returned valid structured answers. The compatibility test cost approximately $0.005.
- Kept all 8 model families.
- Froze model-specific reasoning configuration: low reasoning for 6 families and reasoning disabled for the tested DeepSeek and Mistral models.
- Preserved the incomplete v0.1a run in private storage and excluded it from the clean baseline.

Next action: tag `baseline-v0.1b` and launch a clean 160-response baseline.

## 2026-09-01: full-panel replication

- Completed the clean v0.1b baseline with 160 of 160 valid responses, 20 per model family and no permanent failures.
- Recorded 764 recommendations at a total API cost of $0.9866.
- Decided before firm-level analysis to run 4 additional repetitions of every model-prompt cell.
- The replication batch adds 640 planned responses and creates 5 total observations per cell.
- Chose complete-panel replication to measure stochastic stability without selecting prompts based on interesting initial results.
- Kept execution sequential to reduce provider rate-limit and concurrency effects.

Next action: freeze the replication configuration and launch runs 2–5 as a separate checkpointed dataset.

## 2026-09-02: open-book and specificity experiments

- Completed 800 closed-book responses with 5 observations in all 160 model-prompt cells.
- Observed sufficient first-position stability to stop general closed-book replication at 5 runs.
- Pre-registered a controlled open-book comparison using a common Exa retrieval layer across all model families.
- Planned 3 open-book observations per model-prompt cell, producing 480 responses.
- Separated this controlled retrieval benchmark from future tests of native consumer products.
- Added a specificity-ladder design to test when smaller or specialist firms enter recommendations.
- Preserved the remaining budget for retrieval and prompt-sensitivity evidence rather than further general repetition.

Next action: freeze the open-book execution configuration, run a 2-call search smoke test and launch the 480-response comparison if validation passes.

## 2026-09-02: interruption-safe execution

- Added a connectivity gate before every paid request.
- When OpenRouter is unreachable, the runner waits locally and does not consume a model-prompt attempt.
- Completed responses remain checkpointed and are skipped after restart.
- The detached macOS session can resume after temporary Wi-Fi loss or system wake.
- This operational change does not alter prompts, models, scoring or response conditions.

## 2026-09-02: specificity prompts frozen

- Froze 15 prompts across 5 categories and 3 levels of legitimate founder specificity.
- Categories: climate hardware, defence technology, university spinouts, developer infrastructure and capital-efficient SaaS.
- Level 1 names only the broad category.
- Level 2 adds stage, geography and a category constraint.
- Level 3 adds a subsector, company state and investor-relevant operating constraints.
- The experiment will measure unique-firm count, specialist inclusion, concentration and prestige leakage at each level.
- Before collecting specificity results, operationalised prestige leakage from baseline category breadth and separated a reproducible target-association proxy from primary-source-verified specialist status. This prevents post-result hand-selection of a prestige or specialist list.
- Reconciled the measures section with that operational definition: rationale quality remains a separate human-coded judgment rather than being folded into the prestige-leakage rate.

Next action: run the specificity ladder only after validating the controlled open-book comparison and its remaining budget.

## 2026-09-02: native-product spot check frozen

- Added a separate 16-observation descriptive check across ChatGPT, Claude, Gemini and Grok.
- Selected two discovery prompts and two founder-problem prompts from the already frozen panel.
- Required fresh chats and logging of visible product state, search behaviour, citations and errors.
- Prohibited pooling native-product observations with either controlled API condition.

## 2026-09-02: exploratory retrieval-convergence diagnostic

- Reviewed partial output from the controlled open-book condition while collection was still in progress.
- Observed that several model families were citing the same domains and surfacing the same clusters of niche firms under the shared retrieval layer.
- Added a post-hoc diagnostic for source-domain frequency, model-family coverage and cross-model recommendation overlap.
- Labelled this analysis exploratory because it was motivated by visible partial results.
- Made no change to prompts, models, collection settings or preregistered measures.
