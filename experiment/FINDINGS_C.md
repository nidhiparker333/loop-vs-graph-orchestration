# Findings — Condition C, prompts held constant

One run, 1,000 titles, `claude-sonnet-5`, thinking disabled, `PASS_TOTAL = 12`,
4-attempt cap. 7,206 model calls, **$13.34**, ~18 minutes. Raw data in
`results/condition_c/`.

Predictions were committed in `CONDITION_C_PREREGISTRATION.md` (`aec4b8b`)
before any API call and are scored below unedited.

## What makes this different from Condition A

Condition A could not attribute its result to routing: its arms differed in the
classifier, the prompt count and the rewrite wording at once. Here **both arms
send the same prompt text**. `REWRITE` and `EVALUATE` come from `shared.py`
unchanged; both use one `FIX` template built from the same per-criterion
instructions. For any evaluation with exactly one failed criterion the two arms
emit **byte-identical prompts** — asserted in `test_run_state.py`.

One variable is manipulated:

- **Loop** — fix every failed criterion at once, re-evaluate.
- **Graph** — route to the highest-priority failed criterion, fix only that,
  re-evaluate.

Same model, evaluator, thresholds, cap, human-review exit, and no pre-classifier
in either arm.

## Headline

| | loop | graph | |
|---|---|---|---|
| Model calls | 3,575 | 3,631 | +1.6% |
| Total tokens | 1,920,960 | 1,942,684 | +1.1% |
| Cost | $6.62 | $6.72 | +$0.10 |
| PASS | **500** | 477 | −23 |
| HUMAN_REVIEW | 303 | 303 | 0 |
| FAIL_CAP | 194 | **218** | +24 |
| Errored | 3 | 2 | |
| Mean iterations | 1.76 | 1.79 | |
| Audit-flagged final outputs | 61 of 694 (8.8%) | 50 of 695 (7.2%) | |

With the prompts held constant, **the two control flows are nearly the same
price.** The +1.6% call gap here is a tenth of Condition A's +16.3%, which
suggests most of that earlier gap came from the classifier call and the extra
prompts rather than from branching.

## Prediction scoring

### 1. The strict threshold makes the loop actually loop — at least 1.5 attempts per title

**CONFIRMED.** Loop mean **1.76** attempts (graph 1.79). Condition A's loop
managed 1.02 at the 9/12 bar; 12/12 changed that decisively.

The distribution is strikingly bimodal:

| attempts | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| loop | 685 | 70 | 36 | 206 |
| graph | 683 | 66 | 24 | 225 |

Titles either clear 12/12 on the first try or grind to the cap. Very little in
between. That shape is itself a finding: the repair rounds rarely rescue a title
that failed once — of the 312 loop titles that needed a second attempt, only 110
ever reached PASS.

### 2. The graph uses more model calls and more total tokens

**CONFIRMED**, but barely. Calls +56 (+1.6%), tokens +21,724 (+1.1%), cost
+$0.10. The direction is right; the magnitude is small enough that it would not
survive as a practical argument.

### 3. The graph reaches PASS on more titles and hits the attempt cap less often

**REFUTED, on both halves.** The graph did the opposite of each.

| | loop | graph |
|---|---|---|
| PASS | **500** | 477 |
| FAIL_CAP | 194 | **218** |

Paired, on the titles both arms attempted:

- **PASS**: 75 loop-only vs 52 graph-only discordant pairs, exact McNemar
  **p = 0.0505** — right at the threshold, so the PASS gap is suggestive rather
  than established.
- **FAIL_CAP**: 50 loop-only vs 74 graph-only, **p = 0.0384** — the graph
  genuinely hits the cap more.

The mechanism is the manipulated variable doing exactly what it should: fixing
one criterion per round costs rounds, and with only four attempts a title
failing two or three criteria can run out of budget before the graph reaches
them all. Repairing everything at once is simply faster at clearing a strict bar.

### 4. The graph's final outputs are audit-flagged less often

**MIXED.** The unpaired rates match the prediction — loop 8.8% (61 of 694),
graph 7.2% (50 of 695) — but the paired test does not support a real difference.

On the 425 titles **both** arms passed, where the comparison is like-for-like:

| | loop | graph |
|---|---|---|
| Audit-flagged | 31 (7.3%) | 29 (6.8%) |
| Discordant | 8 loop-only | 6 graph-only |

Exact McNemar **p = 0.791**. Indistinguishable.

The unpaired gap is confounded: the two arms passed different sets of titles, so
their "produced" populations are not comparable. Once that is controlled for, the
difference disappears. Direction predicted correctly, effect not established.

### 5. HUMAN_REVIEW counts differ by 10 or fewer

**CONFIRMED, exactly.** 303 in both arms — a difference of zero, and 298 of them
are the *same titles*. The shared exit behaves identically, which is what it was
designed to do.

Ambiguous inputs caught: loop 295 of 300, graph 298 of 300.

## Graph node visits

**Executed** is how many times a node actually ran. **Planned** also counts the
node a title was routed to when it hit the attempt cap — that routing decision
was recorded but never executed, so the planned column overstates the busiest
node. The executed column is the real one.

| node | executed | planned |
|---|---|---|
| `fix_consistency` | **601** | 790 |
| `fix_attribute_preservation` | 72 | 75 |
| `fix_groundedness` | 54 | 64 |
| `fix_searchability` | 53 | 66 |
| `fix_product_clarity` | 5 | 6 |
| `fix_readability` | 4 | 6 |
| `done` | — | 477 |
| `human_review` | — | 303 |

**789 fix-node runs executed**, of which **601 were consistency — 76%.**
(Cross-checked: each executed fix appends one version, and the graph arm's
versions-minus-one summed over all titles is exactly 789.)

The graph is, in practice, almost a single-purpose consistency fixer.
`fix_readability` ran 4 times despite readability being a common failure — it
sits last in priority, so something else almost always outranks it.

This matters for interpreting the whole condition: a routing policy whose top
branch absorbs 76% of executed repairs is barely routing. The graph and the loop behave
similarly here partly because the graph rarely has a meaningful choice to make.

## Audit, over every scored candidate

Not just final outputs — every `(version, evaluation)` pair the evaluator scored.

| | loop workable | loop all | graph workable | graph all |
|---|---|---|---|---|
| Candidates | 1,454 | 1,757 | 1,484 | 1,787 |
| Flagged | 134 | 177 | 116 | 166 |
| ...evaluator still scored groundedness 2 | 100 | 117 | 84 | 101 |
| **Flagged candidates the evaluator passed** | **75%** | 66% | **72%** | 61% |
| Not flagged, evaluator scored below 2 | 26 | 32 | 32 | 35 |

Condition A's central finding reproduces at a stricter threshold and with
matched prompts: the evaluator gives full groundedness marks to roughly
three-quarters of what a word-level check flags, and objects to things the check
misses. Neither instrument is ground truth for the other. Raising the bar from
9/12 to 12/12 did not close the gap.

## What this condition establishes

**Control flow alone is close to free here, and it does not buy quality.** With
prompts held constant, one-repair-at-a-time cost 1.6% more calls, passed 23
fewer titles, hit the cap 24 more times, and produced outputs the audit could
not distinguish from the loop's.

**Most of Condition A's cost gap was not branching.** +16.3% calls there versus
+1.6% here, with the classifier and the specialised prompts removed. The earlier
headline was mostly measuring the extra classifier call, not the routing.

**The strict threshold is what made the loop loop** — and it also revealed that
iteration rarely rescues a failing title. 685 of 1,000 passed or escalated on
the first attempt; 206 ground to the cap. The middle is nearly empty.

## Limits

1. **One run.** No run-to-run variance estimate. The paired tests establish a
   difference within this run only, and the PASS result sits at p = 0.0505.
2. **The routing policy barely routes.** 76% of executed repairs went to one node.
   A dataset with a flatter failure distribution would test branching harder;
   this one mostly tested "fix consistency, one way or the other".
3. **The priority order is a design choice.** A different order is a different
   graph. Groundedness-first was chosen on principle, and groundedness turned
   out to fail rarely, so the choice had little effect.
4. **Same synthetic dataset** as Conditions A and B, with the same designed 30%
   ambiguous share and author-generated construction.
5. **Same model generates and evaluates**, and section "Audit, over every scored
   candidate" is direct evidence that the evaluator is unreliable on the
   criterion it is being trusted for. PASS and FAIL_CAP counts inherit that.
6. **`PASS_TOTAL = 12` is strict by construction.** Results do not transfer to
   the 9/12 bar Condition A used — 194 and 218 FAIL_CAP against Condition A's
   zero is the size of that difference.
7. **5 titles errored** (3 loop, 2 graph) after exhausting JSON parse retries,
   and are excluded from rates. `t0895` errored in both arms.
8. **The audit's known blind spots carry over**: flags are possible unsupported
   additions rather than confirmed errors, tokens under three characters are
   skipped, and the `STRUCTURAL` allowlist was tuned on dry runs from this
   dataset.

## Scorecard

| # | Prediction | Result |
|---|---|---|
| 1 | Loop averages ≥ 1.5 attempts | **Confirmed** — 1.76 |
| 2 | Graph uses more calls and tokens | **Confirmed** — +1.6% calls, +1.1% tokens |
| 3 | Graph passes more, caps less | **Refuted** — passes 23 fewer, caps 24 more |
| 4 | Graph's outputs flagged less often | **Mixed** — 7.2% vs 8.8% unpaired, but paired p = 0.791 |
| 5 | HUMAN_REVIEW within 10 | **Confirmed** — identical at 303 |
