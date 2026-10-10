# [the-internet.herokuapp.com] /download page is slow to load, dominated by connection setup time

**Severity:** Low — page fully loads (HTTP 200, ~1.04s total) with no functional breakage; flagged because ~70% of the load time is spent in DNS/TCP/TLS setup before any content is requested, which is worth investigating even though it is not currently blocking use. Reporter should re-rate if the real-world experience is slower than this single capture, or if this is consistently reproducible.
**Reported:** 2026-10-10   **Reporter:** Not provided

## Environment
- Deployment environment: Prod (public site) — the-internet.herokuapp.com is a public QA practice site with a single environment; no Dev/QA/Staging distinction applies.
- URL / host: https://the-internet.herokuapp.com/download
- App/version/build: Not provided (third-party public demo app)
- OS / device: Windows 10/11, x64 (from User-Agent)
- Browser / runtime: Chrome 154.0.0.0 (from User-Agent; HAR capture tool was WebInspector 537.36)
- Other relevant config: Server responds with `Server: Heroku`, `Via: 2.0 heroku-router` — app is hosted on Heroku.

## Summary
Loading `/download` took about 1.04 seconds end-to-end, which the reporter experienced as "very slow." Per the attached HAR, the delay is concentrated in the initial HTML document request (~917 ms of the ~1044 ms total `onLoad`), and within that request the majority of time is network/connection setup (DNS lookup + TCP connect + TLS handshake) rather than server-side rendering or payload size.

## Steps to Reproduce
1. Navigate to `https://the-internet.herokuapp.com/download`.
2. Capture a HAR / network trace of the page load (as provided: `the-internet.herokuapp.com.har`).

**Reproducibility:** Unknown — only one HAR capture (one page load) was provided; not confirmed across repeated loads or from a different network/location.

## Expected Result
The page loads promptly, consistent with its lightweight content (a static HTML page plus a handful of small CSS/JS/image assets, ~1.1 MB total transferred across 10 requests).

## Actual Result
Total page load (`onLoad`): **1044.5 ms**. `DOMContentLoaded` (`onContentLoad`): **914.7 ms**.

The root HTML document request alone (`GET /download`, HTTP 200) took **916.95 ms**, broken down as:

| Phase | Time (ms) |
|---|---|
| Blocked (queued) | 9.19 |
| DNS lookup | 143.18 |
| Connect (TCP + TLS) | 555.16 (of which TLS/SSL handshake: 207.00) |
| Send | 0.64 |
| Wait (TTFB / server processing) | 205.88 |
| Receive | 2.90 |

So roughly **698 ms (76%)** of the document request was spent establishing the connection (DNS + TCP + TLS) before the server could even begin processing the request, and server processing itself added another ~206 ms.

All subsequent static assets (JS/CSS, reusing the now-open connection) loaded quickly, in 42–46 ms each — except one image, which took **245.72 ms**, of which **207.01 ms** was "wait" (server response time) despite being a small 7.6 KB PNG served over the already-established connection.

An Optimizely analytics beacon request (`log.optimizely.com`) also fired, taking 60.23 ms (status 0 — did not complete/return a response in the capture); this is third-party analytics and not part of the page's own content.

## Logs / Evidence
Key timing data extracted from the HAR (no credentials or personal data present; nothing redacted):

```
GET https://the-internet.herokuapp.com/download -> 200
total: 916.95 ms
  blocked: 9.19  dns: 143.18  connect: 555.16 (ssl: 207.00)  send: 0.64  wait: 205.88  receive: 2.90

GET https://the-internet.herokuapp.com/img/forkme_right_green_007200.png -> 200
total: 245.72 ms  (wait: 207.01)

Page timings: onContentLoad=914.73 ms, onLoad=1044.50 ms
Total requests: 10, total transferred: ~1,105,793 bytes
```

Response headers on the document request confirm Heroku hosting:
```
server: Heroku
via: 2.0 heroku-router
```

## Attachments
- `the-internet.herokuapp.com.har` — full network capture of the page load, provided by reporter.

## Additional Notes
- **Suspected cause (unconfirmed):** The DNS (143 ms) + TCP/TLS connect (555 ms) time for the first request, combined with an elevated "wait" time (206 ms) even on a later static image request over a warm connection, is consistent with a Heroku dyno that was idle/sleeping and slow to wake, and/or DNS resolver or network latency between the client and Heroku's edge. This is a hypothesis based on the timing pattern, not confirmed from server-side logs.
- **Regression info:** Not provided — no prior-version baseline HAR to compare against.
- **Other environments:** Not applicable (single public environment).
- **Workaround:** None needed; the page does load successfully, just with a ~1 second delay perceived as slow.
- **Suggested follow-up:** Capture 3–5 repeat HARs (including a "second load" with a warm connection) to confirm whether the DNS/connect/TLS cost is a one-time cold-start cost or happens on every load, which would materially change the severity assessment.
