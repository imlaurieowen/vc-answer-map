# VC firm answer audit

This guide helps a venture firm test how accurately AI systems describe it. It uses the same distinctions as VC Answer Map and can be run without changing the benchmark.

## 1. Write the ground truth first

Create one dated record covering:

- Current investment stage
- Initial cheque range
- Lead or follow preference
- Active geographies
- Sectors and business models
- Current fund status
- Named partners and their areas of work
- Portfolio evidence for each claimed focus
- Canonical sources for named frameworks

Link every claim to a stable primary page. Record the date because mandates, teams and fund status change.

## 2. Test founder discovery

Use the exact discovery prompts in [`config/prompts.json`](../config/prompts.json). Add separate prompts that match the firm's genuine mandate and the language founders use.

For each answer, record:

- Whether the firm appears
- Its position
- The reason given
- Whether the reason is specific to the founder's situation
- Whether stage, geography and sector claims are current
- The cited source
- Confusion with a similarly named firm

An appearance measures model association at that moment. Investment fit still requires human judgment.

## 3. Test founder problems

Use the founder-problem prompts in [`config/prompts.json`](../config/prompts.json). Focus on problems where the firm has published original, useful work.

Record whether the system:

- Retrieves the idea
- Names the framework accurately
- Credits the correct individual and firm
- Links to the original source
- Preserves important qualifications
- Recommends advice that remains current

## 4. Compare memory and retrieval

Run fresh chats with search disabled where the product permits it, then repeat with live search enabled. Keep the conditions separate.

Closed-book inclusion indicates accumulated model association. Search-enabled inclusion also depends on the retriever, current index, citations and source quality. A change between the 2 conditions helps locate the visibility gap.

## 5. Audit the retrieved sources

Open every citation used to justify the firm. Check:

- The page supports the exact claim
- The page is current and clearly dated
- Team and portfolio evidence are identifiable
- Fund status is explicit
- Claims agree across the site
- Old and current versions of the firm are distinguishable
- Third-party evidence supports material claims

Record contradictions, placeholder copy and unsupported portfolio claims. Search visibility is never a substitute for verification.

## 6. Build a correction queue

Classify each observed claim:

- `verified`: supported by current primary evidence
- `qualified`: directionally supported, with an important limitation
- `unverified`: insufficient evidence found
- `needs manual review`: conflicting or potentially consequential evidence

Fix factual ambiguity before working on broader visibility. Useful fixes include one canonical mandate page, redirects from old material, named authors, original publication dates and explicit updates when a thesis changes.

## 7. Repeat on a schedule

Keep the prompt, product state, model label, search state and date with every observation. Re-run after a model change, website migration, fund launch, team change or major publication.

Use the benchmark's longitudinal rules for comparisons across time. Public benchmark results can themselves enter retrieval systems, so pre-publication and post-publication observations belong in separate periods.
