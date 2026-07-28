# Benchmark: Verified RCA Grounding (POC Results)

As a Solutions Architect I would pull together during a
customer POC: not a single cherry-picked transcript, but a repeatable command
anyone can re-run against their own Apodex key to reproduce the number.

## Methodology

- **Fixture:** `fixtures/cdn-incident.md` (CDN redirect query-string-drop incident,
  Akamai → Tencent EdgeOne migration, 2 evidence blocks).
- **Command:** `python3 scripts/rca_demo.py --compare --no-stream`
- **Model:** `apodex-1-0-deep-solve` (both the RCA agent and the grounding judge).
- **Grounding judge:** a separate Apodex call classifies each factual claim in an
  answer as `grounded` (supported by the evidence), `fabricated` (asserts specific
  config/system behavior not in the evidence), or `unclear`. See
  `JUDGE_SYSTEM_PROMPT` in `scripts/rca_demo.py`.
- **Two conditions per run:**
  - **Verified** — the RCA agent gets the incident *and* the evidence blocks.
  - **Naive** — a bare LLM call gets only the incident description, no evidence.

## Results

| Run | Verified: grounded/total (%) | Naive: grounded/total (%) |
|-----|-------------------------------|----------------------------|
| 1   | 10/13 (77%)                   | 2/20 (10%)                 |

**N = 1.** A second trial was attempted but hit a `402 Payment Required` from the
Apodex API (account/key out of credits) partway through the judging step — see
Caveats. The table above reflects the one complete trial obtained; treat it as
directional, not a statistically stable average.

## Headline number

**Verified answers were ~7.7x more likely to be judged grounded than naive
answers in this trial (77% vs. 10%).**

The naive run's failure mode is the interesting part for a customer conversation:
it didn't just answer vaguely, it **fabricated a specific, plausible-sounding
default** (claiming EdgeOne's `QueryString` "default[s] to enable" / carries the
query string by default) and built its entire root-cause narrative on that
invented default — a confident, wrong answer, not just an incomplete one.

## Caveats

- **N = 1** for this table — the second and third trials were blocked by an API
  credit exhaustion (`402 Payment Required`) before the benchmark could be
  extended. Re-run the command above (with a funded key) to add more rows and
  compute a real mean/min/max; the script and fixture require no changes.
- Grounding is judged by an LLM (Apodex itself), not a human rubric — treat the
  percentage as directional signal, not a certified metric.
- Single fixture, single incident type (CDN redirect / migration parity gap) —
  this does not demonstrate breadth across incident categories.
- See `DEMO.md` for the narrative walkthrough this benchmark is derived from.
