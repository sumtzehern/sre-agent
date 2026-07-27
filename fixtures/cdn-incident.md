# Incident: Query parameters dropped across CDN redirect chain

> Sanitized fixture for the Apodex verified-RCA demo. Config snippets below are
> **representative, not verbatim** captures of any real customer's configuration —
> the schema shape mirrors real Akamai Property Manager / Tencent EdgeOne rule
> syntax, but field values are illustrative.

## Incident description

Since the CDN migration cutover from Akamai to Tencent EdgeOne, marketing and
product analytics teams report that `?utm_campaign=` and `?session=` query
parameters are silently dropped when a specific route (`/promo/*`) issues its
302 redirect to the canonical landing page. This breaks two things downstream:

1. **Campaign attribution** — analytics can no longer tie inbound clicks to the
   originating `utm_campaign`, because the redirected request arrives with no
   query string at all.
2. **Session continuity** — a `session` token minted by an upstream service is
   lost across the redirect hop, forcing an unwanted re-auth / new session for
   affected users.

The route worked correctly on Akamai before cutover (query params *did*
survive the redirect there in production), so the assumption going in is that
something changed in how the redirect behaves post-migration — not that query
preservation was ever intentionally configured to be dropped.

## Evidence

### EVIDENCE-1 — Akamai Property Manager rule (pre-migration, `/promo/*`)

Source: Property Manager rule tree, rule "Promo Redirect", `redirect` behavior,
as captured from the last-known-good pre-cutover version:

```json
{
  "name": "redirect",
  "options": {
    "destinationProtocol": "SAME",
    "destinationHostname": "OTHER",
    "destinationHostnameOther": "www.example.com",
    "destinationPath": "AS_IS",
    "destinationQueryString": "APPEND",
    "responseCode": 302,
    "mobileDefaultChoice": "DEFAULT"
  }
}
```

Note: `destinationQueryString: "APPEND"` is Akamai's explicit opt-in to carry
the original request's query string onto the redirect target. This is not the
Property Manager default — it was intentionally set at some point (unclear
when/by whom) on the legacy config.

### EVIDENCE-2 — Tencent EdgeOne rule engine config (post-migration, same route)

Source: EdgeOne rule engine, rule "promo-redirect", matching condition
`request.url.path` starts with `/promo/`, action type `URLRedirect`:

```json
{
  "ruleName": "promo-redirect",
  "conditions": [
    { "type": "url.path", "operator": "starts_with", "value": "/promo/" }
  ],
  "actions": [
    {
      "type": "URLRedirect",
      "parameters": {
        "statusCode": 302,
        "targetUrl": "https://www.example.com${uri}",
        "keepQueryString": false
      }
    }
  ]
}
```

Note: EdgeOne's `URLRedirect` action requires an explicit
`"keepQueryString": true` (or an equivalent `${queryString}` placeholder
appended to `targetUrl`) to carry the original query string forward. Here it
is explicitly `false`, and `targetUrl` has no query-string placeholder.

## What a well-grounded RCA should conclude

The Akamai rule (EVIDENCE-1) explicitly opted in to query-string preservation
(`destinationQueryString: "APPEND"`) — that behavior was **not** captured when
the redirect rule was translated to EdgeOne's rule-engine schema. The migrated
EdgeOne rule (EVIDENCE-2) uses the platform's default drop-behavior
(`keepQueryString: false`), which is a **different default** between the two
platforms' redirect primitives, not a regression in EdgeOne itself. Root cause:
a **migration parity gap** — an explicit, non-default setting on the source
platform was not carried over as an equivalent explicit setting on the
destination platform, because the two platforms' query-preservation flags are
not analogous in name or default value.
