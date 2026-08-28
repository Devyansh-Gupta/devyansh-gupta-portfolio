# Devyansh Gupta — Portfolio

Personal portfolio site. Plain HTML/CSS/JS, animated with [anime.js v4](https://animejs.com) (vendored, MIT), hosted on **Azure Static Web Apps** with managed Azure Functions for the contact form and resume download.

## Architecture

```
index.html · css/ · js/ · vendor/anime.esm.js   static front end
api/                                             managed functions (Node 20)
  src/functions/contact.js   POST /api/contact → SMTP email (nodemailer)
  src/functions/resume.js    GET  /api/resume  → 302 to Blob Storage + short-lived SAS
staticwebapp.config.json     routes, headers, apiRuntime
```

### Resume download (security model)
The resume PDF lives in a **private** blob container. `/api/resume` mints a
read-only, single-blob, HTTPS-only service SAS valid ~10 minutes and redirects
the visitor — per Microsoft's SAS best practices (least privilege, short
lifetime, no key in the browser).

## Required app settings (SWA → Configuration)

| Setting | Purpose |
|---|---|
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_SECURE` | SMTP relay (e.g. smtp.gmail.com / 587) |
| `SMTP_USER` / `SMTP_PASS` | SMTP credentials (Gmail **app password**) |
| `CONTACT_TO` | inbox that receives form messages |
| `STORAGE_ACCOUNT` / `STORAGE_KEY` | storage account holding the resume blob |
| `RESUME_CONTAINER` / `RESUME_BLOB` | e.g. `resume` / `Devyansh_Gupta_Resume_DevOps_Intern.pdf` |
| `RESUME_SAS_MINUTES` | optional, default 10 |

## Local development

```bash
# front end only (resume button falls back to /assets copy)
npx serve .

# with API (needs Azure Functions Core Tools + api/local.settings.json)
cd api && npm install && npm start
```

## Deployment
Push to `main` → GitHub Actions (auto-created by Azure Static Web Apps) builds and deploys.
