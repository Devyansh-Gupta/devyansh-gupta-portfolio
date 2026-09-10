# Class VM — shared hosting layout for 30 students
# One nginx server per student. Each student owns exactly one directory
# under /var/www/<usn-or-name>/ and one vhost file. Nobody needs root after
# initial setup; deploys land in the student's home and are published by
# symlink flip (see deploy-vm.yml).

## Directory layout (created once by the professor/admin)

/var/www/students/
  devyanshgupta/          <- this site's web root (symlink target: ~/webroot/current)
  <student2>/
  ...

/home/devyanshgupta/
  site/                   <- rsync landing zone (overwritten each deploy)
  webroot/
    releases/<timestamp>/  <- immutable published copies (last 5 kept)
    current -> releases/<latest>   <- what nginx serves (atomic flip)

## nginx per-student vhost (path / subdomain variants)

Two options for the unique URL — both are one small file per student:

### Option A — path-based (no DNS needed, works with just an IP)
# /etc/nginx/sites-available/students-devyanshgupta.conf
server {
    listen 80;
    server_name _;                      # or the VM's hostname
    # everything under /devyanshgupta/ maps to my web root
    location /devyanshgupta/ {
        alias /var/www/students/devyanshgupta/;
        index index.html;
        try_files $uri $uri/ =404;
        add_header Cache-Control "no-cache" always;   # always fresh after a deploy
    }
}

### Option B — subdomain-based (needs a wildcard DNS A record *.classVMdomain
### pointing at the VM; prettier URLs, one vhost file per student)
# /etc/nginx/sites-available/devyanshgupta.class.example.conf
server {
    listen 80;
    server_name devyanshgupta.class.example.com;
    root /var/www/students/devyanshgupta;
    index index.html;
    location / {
        try_files $uri $uri/ =404;
        add_header Cache-Control "no-cache" always;
    }
}

Enable either with:
    sudo ln -s /etc/nginx/sites-available/<file> /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl reload nginx

## Per-student SSH access (professor runs once per student)

sudo useradd -m -s /bin/bash devyanshgupta
sudo mkdir -p /var/www/students/devyanshgupta
sudo chown devyanshgupta:www-data /var/www/students/devyanshgupta   # student can publish
# the student's ~/webroot/current symlink must point INTO their published dir;
# simplest: professor makes /var/www/students/devyanshgupta a symlink to
# /home/devyanshgupta/webroot/current — nginx follows symlinks by default.

Then the student (or admin) appends their deploy public key:
  ssh-ed25519 AAAA... deploy@github-actions  # from GitHub Actions, per student key

## Caching headers (optional, add inside the server/location block)

Static assets should cache, HTML should not, so deploys show instantly:
    location ~* \.(css|js|webp|jpg|png|svg|pdf)$ {
        expires 7d;
        add_header Cache-Control "public";
    }
    location = /index.html { add_header Cache-Control "no-cache" always; }
