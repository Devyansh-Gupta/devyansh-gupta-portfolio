# Plan: Devyansh Gupta — Portfolio Website (Azure)

Status: reviewed-plan (ulw-plan). Research dossier below feeds every decision.
Date: 2026-08-28 · Owner: Hermes · Executor: Hermes (direct build, user-approved scope)

## 1. Requirements (from user)
- Portfolio site from CV (Devyansh_Gupta_Resume_DevOps_Intern.pdf) + provided photo.
- "As creative as possible"; animation library welcome (user suggested anime.js, open to best option).
- Plain HTML/CSS/JS — no framework build step.
- Contact form with real email delivery.
- Host on Azure.
- Resume download button backed by an Azure Blob Storage pre-signed (SAS) link.

## 2. Research dossier (decision-grounding, retrieved 2026-08-28)

### 2.1 Animation library — DECISION: anime.js v4.1.2 (MIT), vendored locally
Evidence (practitioner comparisons, 2026):
- anime.js v4: ~13–17 kB, modular rewrite, MIT. Ships timelines, SVG draw/morph, ScrollObserver (`onScroll`), `TextSplitter`, `stagger`, physics springs. Concurrent perf on par with GSAP since v4 (ics.media production comparison).
- GSAP: deepest scroll engine (ScrollTrigger), now MIT (Webflow, Nov 2024), but ~31 kB+ and its value is scrub/pin choreography — overkill here.
- Motion: React-first; vanilla build adds little over anime.js for a no-framework site.
User named anime.js; evidence supports it as the right-weight choice. Pinned copy vendored at `vendor/anime.esm.js` (v4.1.2, 285 KB unminified ESM, exports verified: animate, createTimeline, onScroll, stagger, text.split, svg, utils). No CDN dependency at runtime.
Residual uncertainty: none material — v4 API verified against the pinned file itself (strongest source).

### 2.2 Hosting — DECISION: Azure Static Web Apps (SWA), GitHub Actions deploy
Official docs (learn.microsoft.com/azure/static-web-apps/*):
- SWA hosts static HTML/CSS/JS on a global CDN, free tier available, auto CI/CD from GitHub via `Azure/static-web-apps-deploy` action; PR staging environments included.
- `staticwebapp.config.json` controls routes/headers (routes.json deprecated).
- Managed functions = built-in serverless API at `/api/*` (HTTP triggers only, Node 18/20), deployed in the same workflow via `api_location`.
Rejected alternatives:
- App Service (cost, overkill for static), Blob static website hosting (no serverless API → can't do email or SAS minting), Container Apps (overkill).

### 2.3 Email — DECISION: SWA managed function `/api/contact` + nodemailer SMTP (Gmail app password)
Evidence:
- Official pattern: SWA "Add an API" doc shows managed HTTP functions (`@azure/functions` v4 programming model, `app.http(...)`).
- Azure Communication Services Email is the native option but requires an Email Communication Service resource + verified custom domain (DNS TXT/DKIM) — heavy setup for a personal inbox; kept as documented upgrade path.
- Practitioner sources (azurelessons.com 2026, cloudshift.nl) confirm: Functions has no built-in SMTP; nodemailer + provider SMTP is the standard lightweight route; never send from a user-facing page directly.
- Security: rate-limit by IP + honeypot field + input validation in the function; secrets in SWA app settings, never in repo.
Residual uncertainty: Gmail SMTP from Azure consumption IPs can occasionally be throttled; fallback documented (Brevo/SendGrid SMTP, same code path).

### 2.4 Resume download — DECISION: private blob + server-minted short-lived SAS via `/api/resume`
Official docs (learn.microsoft.com storage-sas-overview, create-user-delegation-sas):
- Microsoft recommends user delegation SAS (Entra-signed) over account-key SAS; least privilege (read-only, single blob); short expiry; HTTPS only.
- CRITICAL CONSTRAINT (verified, official + GitHub issue #466/#88): SWA **managed functions do NOT support managed identity**. So a user-delegation SAS (needs Entra token via MI) is not available in managed functions without bring-your-own-Functions.
- Chosen design: private container `resume` → blob `Devyansh_Gupta_Resume_DevOps_Intern.pdf` → `/api/resume` mints a **service SAS** (account-key-signed) scoped to that one blob, read-only, ~10-minute expiry, and 302-redirects the visitor. Account key lives only in SWA app settings. This satisfies "pre-signed link from Blob Storage" with least privilege and short lifetime per official best practices.
- Documented upgrade path: bring-your-own Function App with managed identity → user-delegation SAS (no key anywhere).
Rejected: public container (no SAS as requested; no revocability), long-lived static SAS in HTML (leak risk — explicitly warned against in official best practices).

## 3. Architecture
```
GitHub repo Devyansh-Gupta/devyansh-gupta-portfolio
├── index.html            single-page site (semantic, a11y)
├── css/styles.css        design system + layout
├── js/main.js            anime.js choreography
├── vendor/anime.esm.js   pinned anime.js v4.1.2 (MIT)
├── assets/               photo.webp/jpg, og-image, favicon
├── staticwebapp.config.json  routes/headers/platform
└── api/                  managed functions (Node 20, @azure/functions v4)
    ├── src/functions/contact.js   POST /api/contact → nodemailer SMTP
    ├── src/functions/resume.js    GET  /api/resume  → 302 to blob+SAS
    ├── package.json, host.json
Azure: resource group rg-portfolio · SWA swa-devyansh-portfolio ·
       storage stdevyanshportfolio (private container 'resume')
```

## 4. Design concept — "The DevOps Terminal"
Creative direction: DevOps identity expressed as a living terminal. Dark ops-room theme (deep navy-black, terminal green + amber accents, mono display type for headings, humanist sans for body). Signature moments:
1. Hero: typed `whoami` terminal boot sequence (anime.js TextSplitter + timer), name reveal, animated pipeline diagram (build→test→deploy nodes pulsing in sequence).
2. Photo: duotone-treated portrait with scanline/glitch hover, terminal-window chrome frame.
3. Scroll: `onScroll`-driven section reveals, staggered skill chips, timeline draw-on for experience/education.
4. Projects: cards with SVG line-draw icons; Abhyas/PolyBot/MEDBridge/InsightForge from CV.
5. Contact: form posting to `/api/contact`, animated success state.
6. Resume button: hero + nav + contact → `/api/resume` (SAS redirect).
Accessibility: prefers-reduced-motion honored (animations skipped), semantic landmarks, focus styles, contrast-checked palette.

## 5. Acceptance criteria (testable)
A1. `index.html` renders locally with zero console errors; all CV sections present (summary, skills, education, certs, experience, projects, publications, contact).
A2. Animations run via vendored anime.js v4 (no CDN); hero type-on + scroll reveals verified in preview pane.
A3. `prefers-reduced-motion: reduce` disables motion (verified by emulation).
A4. `POST /api/contact` validates input, rejects honeypot, sends mail via SMTP, returns JSON; secrets only in env/app settings.
A5. `GET /api/resume` returns 302 → `https://<acct>.blob.core.windows.net/resume/<blob>?<sas>` with read-only, ≤15-min expiry; blob container is private (direct URL without SAS → 404/403).
A6. Deployed to Azure SWA via GitHub Actions; production URL serves the site; `/api/resume` and `/api/contact` respond live.
A7. Lighthouse-style sanity: no broken assets, meta/OG tags present, mobile layout intact at 390px.

## 6. Verification commands
- Local: `npx serve .` (or `python -m http.server`) + preview pane walkthrough; `node --check js/main.js`; API smoke: `curl -X POST localhost:7071/api/contact` via `swa start` or functions core tools.
- Live: `curl -sI https://<swa-url>/` (200), `curl -sI https://<swa-url>/api/resume` (302 + Location with `sig=`), `curl -s -o /dev/null -w '%{http_code}' "<direct-blob-url>"` (403/404).

## 7. Risk register
| Risk | Mitigation |
|---|---|
| Gmail SMTP throttled from Azure IPs | Same-code fallback to Brevo/SendGrid SMTP; ACS Email upgrade path documented |
| Account key in app settings | Least-privilege SAS (one blob, read, 10 min); key never in repo; upgrade path to user-delegation SAS via BYO function |
| az CLI not installed on this box | Install via winget/pip during deploy phase; user `az login` device-code flow |
| anime.js v4 API drift | Vendored pinned copy; API verified against that exact file |
| SWA free-tier API limits | Contact form volume trivial; rate limit in function |

## 8. Rejected options (with reasons)
- GSAP: heavier, its differentiators (scrub/pin) not needed; user leaned anime.js.
- Blob static-website hosting: no `/api` → can't mint SAS or send email server-side.
- Public blob container: violates the explicit "pre-signed link" requirement.
- ACS Email day-1: custom-domain DNS verification overhead; kept as upgrade path.
- Client-side email services (smtpjs/Formspree): secrets in browser / third-party dependency; user asked for Azure-native.

## 9. Handoff
Executor: Hermes direct build (single-owner, bounded scope — user requested build+deploy in this session). No separate engine needed.
