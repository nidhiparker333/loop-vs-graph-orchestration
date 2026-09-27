# For reviewers

Two AI workflows compared on one narrow task. Please attack it.

## What it claims

1. On this dataset, the graph workflow used **+16.3% model calls and +5.8%
   tokens** versus the loop workflow, accepted **23 fewer** titles and sent
   **22 more** to human review.
2. A word-level groundedness check flagged **59 of 699** loop outputs and
   **30 of 677** graph outputs as containing a possible unsupported addition.
   On the 674 titles both workflows accepted, the split is **54 vs 29**.
3. **All 89 audit-flagged outputs passed the model rubric**, each scoring 2/2
   on "groundedness".
4. Token break-even for the graph on this dataset is **36% ambiguous inputs**;
   the dataset was 30%.

## What it does not claim

- **No causal claim about routing.** The two workflows differ in three ways at
  once — the routing step, 3 vs 5 prompts, and the wording of the rewrite
  instruction. This compares two complete workflows as built.
- **No fabrication rate.** The audit is a heuristic for possible unsupported
  additions, not a validated measure of factual error. Flags are not confirmed
  errors, and unsupported claims that add no new word go unflagged.
- **No claim that the rubric detects 0% of fabrications.** What is measured is
  narrower: on the 89 outputs the audit flagged, the rubric objected to none.
  Outputs the audit did not flag were never independently checked.
- **No cost model for human review.** No dollar figure is assumed for a review
  or for an unsupported claim reaching a catalog.
- Nothing about orchestration patterns in general, other tasks, or other models.

## Where to start

| File | |
|---|---|
| `experiment/FINDINGS_SCALED.md` | the 1,000-title result and its limits |
| `README.md` | overview, setup, what preregistration covers |
| `experiment/PREREGISTRATION.md` | prediction, committed before the pilot ran |
| `experiment/FINDINGS.md` | the earlier 10-title pilot, unedited |
| `experiment/shared.py` | the only place the API is called; prompts; thresholds |
| `experiment/loop_workflow.py` / `graph_workflow.py` | the two workflows |
| `experiment/audit.py` | the groundedness heuristic |
| `experiment/results/condition_scaled/` | every model call and token count, raw |

**Scope of preregistration:** `PREREGISTRATION.md` covers the 10-title pilot
only. The 1,000-title dataset and `audit.py` were built afterwards in response
to the pilot. The rubric, PASS rule and both workflows were unchanged between
them, but the scaled run is not a preregistered test of a prior hypothesis.
`git log --reverse` shows the ordering.

## Weaknesses already known — push here first

1. **Single run at n=1,000.** No run-to-run variance estimate.
2. **The ambiguous-input share (30%) is a design choice** sitting just below the
   measured 36% break-even. Pick 40% and the token conclusion reverses. Is
   reporting the break-even enough, or is the headline still misleading?
3. **The loop revised only 22 of 1,000 titles** (`avg_iterations = 1.02`). A
   thrashing loop — the case that motivates the question — is untested. Is the
   comparison meaningful without it?
4. **The audit is the author's own construction.** It forgives plurals,
   substrings and unit words, so it under-reports; and some flags are harmless
   (`Slate Grey` → `Slate Grey Finish`). Does the `STRUCTURAL` allowlist let
   real unsupported claims through? Adding it moved a 30-title sample's loop
   rate from 30.0% to 10.0% — a large swing from one judgement call.
5. **The dataset is synthetic and author-generated** (`generate_titles.py`). The
   `major_abbrev` style truncates words and both workflows expand them back; 20
   of the loop's 59 flags and 18 of the graph's 30 are that. Both the excluded
   and unexcluded numbers are reported — is the exclusion defensible?
6. **The two workflows differ in several ways at once**, so the comparison
   cannot attribute the result to routing. Is comparing whole workflows still
   useful, or does it make the result uninterpretable?
7. **Same model generates and evaluates.** Claim 3 is a finding about how
   unreliable that is, yet PASS and HUMAN_REVIEW counts still depend on it.
8. **MINOR/MAJOR ground-truth labels are the author's**; the classifier
   disagreed on 181 of 999. The argument that this does not affect cost — both
   routes take 3 calls — should be checked.
9. **The 21 graph over-routes to human review** are counted against the graph,
   but no cost is attached to a human review, so the accepted/review trade-off
   is reported without being resolved. Is presenting both columns sufficient?

## Reproducing

Local tests and dataset generation cost nothing:

```
python experiment/test_run_state.py
python experiment/generate_titles.py --report
python experiment/audit.py experiment/results/condition_scaled/run_1
```

The 1,000-title run needs an API key and costs about $7.50:

```
python experiment/run_experiment.py --dataset titles_1000.json --runs 1 --condition scaled
```

The generator is seeded and reproduces `titles_1000.json` byte for byte.

## Not yet run

`experiment/CONDITION_B_PREREGISTRATION.md` raises the pass threshold from 9/12
to 12/12 as a sensitivity test. Preregistered, unrun.
