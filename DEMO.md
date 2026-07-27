# Demo: Verified RCA Agent (Apodex)

A working proof that Apodex's verification-centric reasoning — grounded in evidence,
not memory, with every step traceable to a source — holds up on a real infra debugging
task: a CDN redirect silently dropping query parameters after an Akamai→Tencent EdgeOne
migration.

## Two ways to run it

1. **Standalone CLI** (`scripts/rca_demo.py`) — fastest way to show the reasoning chain
   live, including Apodex's `thinking` trace as it investigates:
   ```bash
   cd sre-agent
   pip install -r requirements.txt   # or: .venv/bin/pip install -r requirements.txt
   # APODEX_API_KEY is already in sre-agent/.env
   python3 scripts/rca_demo.py                 # grounded RCA only
   python3 scripts/rca_demo.py --compare        # + ungrounded comparison and grounding score
   ```
2. **Deployed chat UI** (`agents/chat/index.py` + `src/`) — the same evidence-grounded
   agent, in the product surface, with the reasoning chain rendered in a dedicated
   right-hand panel. Click the "Load CDN incident" preset chip to paste the fixture in
   one click.

Both read the same fixture: `fixtures/cdn-incident.md`.

## Demo narration (say this while it runs)

"Here's a real bug pattern from a CDN migration: after moving a redirect rule from
Akamai to Tencent EdgeOne, marketing campaign tags and session tokens started getting
silently dropped on a promo redirect — nothing crashed, nothing errored, it just quietly
broke attribution and login continuity. I'm giving Apodex the incident description plus
the two raw config snippets — the old Akamai rule and the new EdgeOne rule — and asking
it to investigate like an SRE would: form a hypothesis, check it against a specific
piece of evidence, and only conclude once it's actually looked. This is the hard case
for a bare LLM, because both platforms *sound* like they handle query strings, and
Akamai's `destinationQueryString: APPEND` and EdgeOne's `keepQueryString: false` aren't
obviously related unless you actually read both configs side by side — a model relying
on memorized platform docs will confidently guess at defaults instead of checking. Watch
every conclusion cite an EVIDENCE-ID; that's the auditable trail Apodex's pitch is built
on, not a chat transcript you have to take on faith."

## Punchline metric

From a live `--compare` run against the real Apodex API:

- **Grounded (Apodex, evidence-provided): 9/13 claims grounded (69%)** — the remaining
  ungrounded claims were reasonable inferences (impact framing), not fabricated config
  behavior.
- **Naive (bare LLM, no evidence provided): 6/22 claims grounded (27%)** — critically,
  the naive answer *fabricated specific EdgeOne default behavior* ("Query String...
  default to enable") by pattern-matching on vaguely-remembered docs, then built its
  entire root-cause narrative on that fabricated default.

**The number to say out loud: roughly 2.5x more of the grounded run's claims are
verifiably tied to real evidence than the ungrounded run — and the ungrounded run's
core root-cause claim is a plausible-sounding fabrication.** That gap, not just "a nicer
answer," is what Apodex's verification layer is selling.

## Notes
- Full Apodex API reference used to build this: `../apodex/apodex/apodex.md`.
- The reasoning-chain JSON contract (hypothesis → evidence_checked → conclusion →
  confidence) is enforced entirely via prompting — Apodex doesn't support
  `response_format`/structured output or custom tool calling.
