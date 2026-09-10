# Wiring GitHub Actions to the class VM — runbook

Goal: every push to `main` publishes this site on the shared class VM at a
unique URL, automatically. No DB, no runtime — static files + nginx.

## What is already in place (in this repo)

- `.github/workflows/deploy-vm.yml` — the CI/CD pipeline. It is **dormant**:
  until the VM secrets exist it skips cleanly instead of failing, so the
  Actions tab stays green while we wait for the professor.
- `deploy/VM-SETUP.md` — the nginx + users layout for the shared VM
  (30 students, one vhost + one directory each).

## One-time setup, once the professor provides the VM

1. **Generate a deploy key pair** (on your laptop; a separate key from your
   personal one, used only by GitHub Actions):

   ```
   ssh-keygen -t ed25519 -a 200 -f ~/vm-deploy-key -C "deploy@github-actions"
   ```

2. **Give the professor the public key** (`~/vm-deploy-key.pub`) to append to
   `~/.ssh/authorized_keys` for your VM user (they create the user, e.g.
   `devyanshgupta`, and your nginx vhost — see VM-SETUP.md).

3. **Pin the host key** (prevents MITM; never skip unknown-host prompts in CI):

   ```
   ssh-keyscan -p 22 <VM_HOST>          # paste output into VM_KNOWN_HOSTS
   ```

4. **Add 5 repository secrets** — GitHub repo → Settings → Secrets and
   variables → Actions → New repository secret:

   | Secret           | Value                                        |
   |------------------|----------------------------------------------|
   | `VM_HOST`        | VM IP or hostname                            |
   | `VM_PORT`        | `22` (or whatever SSH port is exposed)       |
   | `VM_USER`        | your VM username (NOT root)                  |
   | `VM_SSH_KEY`     | full private key (single line, `-----BEGIN…END-----`) |
   | `VM_KNOWN_HOSTS` | output of step 3                             |
   | `VM_WEBROOT`     | `/var/www/students/<your-name>` (optional; default `$HOME/webroot`) |

5. **Push any commit to main** (or run the workflow manually via
   Actions → "Deploy to class VM" → Run workflow). The workflow:

   - rsyncs the site to `~/site/` on the VM (only your user can write there)
   - moves it into `~/webroot/releases/<timestamp>/`
   - atomically flips the `current` symlink (visitors never see a half-copied site)
   - garbage-collects all but the last 5 releases (rollback = re-point symlink)

6. **Verify**: open your URL — `http://<VM_HOST>/devyanshgupta/` (path mode) or
   `http://<your-name>.<class-domain>/` (subdomain mode). Then `git commit
   --allow-empty -m "deploy test" && git push` and watch the workflow go green
   and the change appear on the VM URL within ~1 minute.

## Why this design (and what the docs say)

- **rsync over SSH is the right primitive for static-to-VM deploys**:
  the `ubuntu-24.04` GitHub runner image ships rsync 3.2.7 and openssh-client
  preinstalled (runner-images README), so no extra install step is needed.
  `rsync -az --delete` gives incremental, mirrored, reproducible content.
- **Key auth, never passwords**: appleboy/scp-action's own security notes:
  "Prefer SSH key authentication over passwords", "Store all sensitive values
  (host, username, password, key) in GitHub Secrets", "Restrict write
  permissions on the target server directory", "Avoid using root as the SSH
  user", "Enable host key fingerprint verification". We follow all five.
- **ED25519 keys** (ssh-action docs) — no legacy `ssh-rsa` config needed.
- **Atomic publish via symlink flip** — nginx `try_files`/root reads the
  directory that `current` points to; `mv -T` swaps the symlink in one
  syscall, so a deploy can never expose a partially-copied tree.
- **Secrets hygiene**: all five secrets are repo secrets, encrypted at rest;
  the workflow never echoes them. Logs show only the result line.
- **Coexistence with Azure**: the existing SWA workflow stays — this adds a
  second, independent pipeline. Both run on push; disable either by disabling
  its workflow in the Actions tab.

## Sharing the VM fairly (30 students) — see deploy/VM-SETUP.md

- One Linux user + one directory + one nginx vhost per student; nobody gets
  root; students can only write their own directory.
- Unique URL per student: path mode (`/devyanshgupta/`) needs zero DNS setup;
  subdomain mode needs one wildcard DNS record `*.class.example.com` → VM IP.
- `Cache-Control: no-cache` on HTML so deploys appear instantly; 7-day cache
  for hashed static assets.
- Rollback: `ln -sfn ~/webroot/releases/<older> ~/webroot/current` on the VM.

## Residual uncertainty (honest limits)

- We don't know yet what the professor allows: whether students get their own
  Linux user, which ports/domains are exposed, and whether SSH inbound is
  open to GitHub's runner IP ranges (they are published at
  https://api.github.com/meta under `actions` if IP allowlisting is needed).
- If the professor only gives an FTP/SFTP account or a folder path, the same
  pipeline adapts: swap the rsync step for the matching action (e.g. an SFTP
  deploy action); everything else stays.
- If the VM sits behind a college proxy/firewall, `ssh-action` supports
  connecting through a jump host (proxy_host/proxy_key) if one is provided.
