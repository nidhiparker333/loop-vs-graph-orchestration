# Next session: run Condition B

Everything is prepared and committed. Condition B has not been run.

## One command

In PowerShell, from `C:\LoopAndGraphEngineering`, with the key set in that
session (`$env:ANTHROPIC_API_KEY = "sk-ant-..."`):

    .\.venv\Scripts\python.exe experiment\run_experiment.py --condition b --pass-total 12

Estimated ~$0.55 for the three runs, a few minutes. Writes to
`experiment\results\condition_b\`. Condition A is not touched.

Optional cheap check first:

    .\.venv\Scripts\python.exe experiment\run_experiment.py --condition b --pass-total 12 --smoke

## State

- Condition A: run, analysed, committed. Frozen. `experiment/FINDINGS.md`.
- Condition B: preregistered in `experiment/CONDITION_B_PREREGISTRATION.md`,
  committed before running. Code supports it via `--pass-total` / `--condition`.
- The ~39% break-even is scoped to Condition A with its five assumptions listed,
  including that the loop performed exactly one rewrite attempt per title.

## After the run

1. Compare `results/condition_b/comparison.md` against Condition A side by side.
2. Report both. Neither is the "real" one.
3. Iteration counts are an outcome, not a target. Condition B is a
   quality-threshold sensitivity test, not an attempt to make the loop iterate.
4. Then, if wanted: the LinkedIn post and the comparison visual. Neither has
   been started, by design.
