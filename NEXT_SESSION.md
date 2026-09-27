# State and next steps

## Done

- **10-title pilot** — three runs. `experiment/FINDINGS.md` (kept unedited,
  marked superseded).
- **1,000-title run**, Condition A (`PASS_TOTAL = 9`) — one run, 4,495 calls,
  $7.49. `experiment/FINDINGS_SCALED.md`, raw data in
  `experiment/results/condition_scaled/`.

## Not run

**Condition B** — same everything, `PASS_TOTAL = 12` instead of 9, as a
quality-threshold sensitivity test. Preregistered in
`experiment/CONDITION_B_PREREGISTRATION.md`, written before any Condition B run.

On the 1,000-title dataset, with the key set in that PowerShell session:

    .\.venv\Scripts\python.exe experiment\run_experiment.py --dataset titles_1000.json --runs 1 --condition b --pass-total 12

Expect more than $7.49, since a stricter threshold means more revision rounds.
Writes to `experiment\results\condition_b\`. Nothing existing is touched. A run
checkpoints per title, so re-running the same command after a crash resumes
without re-paying.

## Open questions a reviewer or a later session might take up

1. **A second run at n=1,000** would give the run-to-run variance estimate the
   current result lacks. About $7.50.
2. **Varying the ambiguous share** (10 / 30 / 50%) would measure the token
   break-even curve directly instead of deriving it from two points. Note the
   per-title costs are already recorded per category, so much of this can be
   re-derived from saved data at no cost.
3. **The audit's `STRUCTURAL` allowlist** is a judgement call that materially
   moves the counts. Worth a sensitivity check — also free, it runs over saved
   results.
4. **Holding the prompts constant** between the two workflows would let the
   comparison say something causal about routing. The current design cannot.

## Free checks

These make no API calls:

    .\.venv\Scripts\python.exe experiment\test_run_state.py
    .\.venv\Scripts\python.exe experiment\generate_titles.py --report
    .\.venv\Scripts\python.exe experiment\audit.py experiment\results\condition_scaled\run_1
