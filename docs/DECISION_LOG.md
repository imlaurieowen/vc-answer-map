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
