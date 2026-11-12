# Devyansh Gupta — Portfolio

Personal portfolio site. Plain HTML/CSS/JS, animated with [anime.js v4](https://animejs.com) (vendored, MIT), with a managed Azure Function for the contact form.

## Architecture

```
index.html · css/ · js/ · vendor/anime.esm.js   static front end
assets/Devyansh_Gupta_Resume_DevOps_Intern.pdf  resume, served with the site
api/                                            managed functions (Node 20)
  src/functions/contact.js   POST /api/contact → SMTP email (nodemailer)
staticwebapp.config.json     routes, headers, apiRuntime
```

### Contact form

Form submissions try the managed function first (`POST /api/contact` —
validates, honeypot-checks, rate-limits, then emails via SMTP); if that is
not configured or fails, they fall back to [formsubmit.co](https://formsubmit.co)
to the same inbox. Either way the message lands straight in your email —
no database involved.

The fallback is activated once: the first submission triggers a
"Activate Form" email to the recipient inbox — click that link and all
future submissions deliver immediately.

### Resume download

The resume buttons link directly to the PDF bundled with the site
(`/assets/Devyansh_Gupta_Resume_DevOps_Intern.pdf`) with a `download`
attribute — no API, no storage account, no redirects. To update the resume,
replace that file and commit.

## Required app settings (SWA → Configuration)

| Setting | Purpose |
|---|---|
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_SECURE` | SMTP relay (e.g. smtp.gmail.com / 587) |
| `SMTP_USER` / `SMTP_PASS` | SMTP credentials (Gmail **app password**) |
| `CONTACT_TO` | inbox that receives form messages |

## Local development

```bash
# front end only
npx serve .

# with API (needs Azure Functions Core Tools + api/local.settings.json)
cd api && npm install && npm start
```

<!-- BACKUP-SETUP -->
## Local setup / restore

This repository is a **backup copy** made before a machine reformat.

| | |
|---|---|
| Original location on disk | `C:\Users\Admin\Documents\Projects\Devyansh-portfolio` |
| Original remote | `https://github.com/Devyansh-Gupta/devyansh-gupta-portfolio.git` |
| Backup remote (this repo) | `https://github.com/Devyansh-Gupta/devyansh-gupta-portfolio` |

### Prerequisites

- Git

### Setup
No dependency manifest was detected in this folder. The files are archived as-is - open them directly, or see the notes below.

### What is *not* in this backup

These are regenerable and were deliberately excluded (see `.gitignore`):

`node_modules/`  `.venv/`  `dist/`  `build/`  `target/`  `.next/`  `__pycache__/`  `.tools/`  `.pytest_cache/`

Run the setup steps above to recreate them.
