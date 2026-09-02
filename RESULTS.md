# September 2026 baseline

The baseline contains 2,000 primary responses across 8 model families and 20 founder questions.

- 800 closed-book responses tested model associations without live retrieval.
- 480 common-retriever responses gave every model family the same Exa search layer.
- 720 specificity responses tested 3 levels of legitimate founder detail.

This is a benchmark of model behaviour. It does not establish which venture firm is objectively best.

## Headline findings

### Funding discovery is plural

The 400 closed-book funding answers contained 1,952 firm-bearing recommendations and 323 distinct canonical firms. The 5 most-mentioned firms accounted for 13.1% of recommendations.

### Founder advice is concentrated

The 400 closed-book operating-problem answers contained 1,525 firm-bearing recommendations and 49 distinct canonical firms. Andreessen Horowitz, Y Combinator, Sequoia Capital, First Round Capital and Benchmark accounted for 71.0% of recommendations.

### Retrieval rewrites the shortlist

Across 160 matched model-prompt cells, the mean Jaccard overlap between closed-book and common-retriever firm sets was 13.1%. It was 5.1% for funding-discovery questions and 21.0% for operating-problem questions.

The modal first recommendation remained the same in 17.5% of cells overall and 8.8% of funding-discovery cells.

### A shared retriever can create apparent consensus

Several common-retriever prompt results converged across all 8 model families. This is exploratory evidence about one controlled retrieval layer, not evidence that all consumer AI products behave identically.

### Citations still require diligence

A model-supplied URL appeared on 99.8% of 2,268 common-retriever recommendations. In a manual audit of the 5 most retrieved firms for each funding question, 39 of 50 firm-prompt associations were verified, 8 were qualified and 3 required manual review. The audit status applies to the observed association and cited claims, not to the overall quality of a firm.

### Specificity removes broad prestige, but does not guarantee the expected specialist

In closed-book specificity tests, the share of recommendations going to the preregistered empirical prestige pool fell from 17.9% at level 1 to 1.5% at level 2 and 1.7% at level 3. With the common retriever it fell from 2.0% to 0%.

The share going to the preregistered category-target pool did not rise monotonically. More detailed prompts produced different, query-shaped shortlists rather than a simple transfer to the expected specialists.

### Ideas can survive while attribution weakens

“Default Alive or Default Dead” appeared 83 times. The correct individual was retained in 67.5% of mentions and the correct institution in 69.9%. “Do Things That Don't Scale” retained the correct individual in 90.5% of 63 mentions and the correct institution in 98.4%.

## Files

- `data/headline-metrics.json`: compact headline statistics
- `data/discovery-top-five.csv`: top 5 firms by funding prompt and condition
- `data/closed-v-open-cells.csv`: matched closed-book and common-retriever overlap
- `data/specificity-category-level.csv`: specificity metrics by category and level
- `data/attribution-summary.csv`: framework attribution results
- `data/retrieval-prompt-convergence.csv`: exploratory common-retriever convergence
- `data/retrieved-source-audit.csv`: reviewed top-50 funding source audit
- `figures/`: publication charts in SVG and PNG

See [METHODOLOGY.md](METHODOLOGY.md) and [LIMITATIONS.md](LIMITATIONS.md) before interpreting the tables.
