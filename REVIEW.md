# For reviewers

Two AI workflows compared on one narrow task. Please attack it.

## What it claims

1. On this dataset, the graph workflow used **+16.3% model calls and +5.8%
   tokens** versus the loop workflow, accepted **23 fewer** titles and sent
   **22 more** to human review.
2. A word-level groundedness check flagged **59 of 699** loop outputs and
   **30 of 677** graph outputs as containing a possible unsupported addition.
   On the 674 titles both workflows accepted, the split is **54 vs 29**.
3. Over **every candidate the evaluator scored**, restricted to those it judged
   workable: the evaluator gave full groundedness marks to **83%** of the loop's
   71 flagged candidates and **75%** of the graph's 40. It also objected on
   candidates the check passed (10 loop, 7 graph; 16 and 7 across all scored
   candidates), so the disagreement is not one-directional.
4. Token break-even for the graph on this dataset is **36% ambiguous inputs**;
   the dataset was 30%.

## What it does not claim

- **No causal claim about routing.** The two workflows differ in three ways at
  once — the routing step, 3 vs 5 prompts, and the wording of the rewrite
  instruction. This compares two complete workflows as built.
- **No fabrication rate.** The audit is a heuristic for possible unsupported
  additions, not a validated measure of factual error. Flags are not confirmed
  errors, and unsupported claims that add no new word go unflagged.
- **No claim that the rubric detects 0% of fabrications.** Neither instrument is
  ground truth for the other and both miss things. An earlier version led with
  "all 89 flagged outputs passed with groundedness 2" — accurate, but it
  follows directly from the PASS rule, which requires `groundedness == 2`. That
  is now stated as such and replaced with the all-candidates measurement.
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
4. **The audit is the author's own construction, and it was tuned on data from
   the population it is applied to.** The `STRUCTURAL` allowlist was chosen by
   looking at 30-title dry runs drawn from this same dataset — not a held-out
   sample. Adding it moved that sample's loop rate from 30.0% to 10.0%, so the
   tuning moved the numbers materially. `titles_1000.json` was then edited after
   those dry runs (commit `cf05f15`), so the tuning set and the final dataset
   are not identical. Does the allowlist let real unsupported claims through?
5. **The audit ignores tokens under 3 characters**, so a changed two-digit
   number (`9W` → `12W`, quantity 4 → 6) is invisible to it. Verified against
   the saved run: no output introduced a number absent from its input, so it
   did not fire here — but it is a real gap for any future run.
6. **The dataset is synthetic and author-generated** (`generate_titles.py`). The
   `major_abbrev` style truncates words and both workflows expand them back; 20
   of the loop's 59 flags and 18 of the graph's 30 are that. Both the excluded
   and unexcluded numbers are reported — is the exclusion defensible?
7. **The two workflows differ in several ways at once**, so the comparison
   cannot attribute the result to routing. Is comparing whole workflows still
   useful, or does it make the result uninterpretable?
8. **Same model generates and evaluates.** Claim 3 is a finding about how
   unreliable that is, yet PASS and HUMAN_REVIEW counts still depend on it.
9. **MINOR/MAJOR ground-truth labels are the author's**; the classifier
   disagreed on 181 of 999. The argument that this does not affect cost — both
   routes take 3 calls — should be checked.
10. **The 21 graph over-routes to human review** are counted against the graph,
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
