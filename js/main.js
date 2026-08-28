/* ═══════════════════════════════════════════════════════════
   DEVYANSH GUPTA — PORTFOLIO · animation engine
   anime.js v4.1.2 (vendored, MIT) — no CDN, no framework
   ═══════════════════════════════════════════════════════════ */
import {
  animate, createTimeline, createTimer, onScroll, stagger, text, utils,
} from '../vendor/anime.esm.js';

const REDUCED = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if (REDUCED) document.documentElement.classList.add('no-motion');

/* ══════════════════════════════════════════════════════════
   RESUME LINK — paste your Azure Blob Storage pre-signed
   (SAS) URL between the quotes below, e.g.:
   "https://<account>.blob.core.windows.net/resume/Devyansh_Gupta_Resume_DevOps_Intern.pdf?sv=2022-11-02&ss=b&srt=o&sp=r&se=...&sig=..."
   While it's empty, buttons try /api/resume (server-side SAS)
   and fall back to the bundled PDF copy.
   ══════════════════════════════════════════════════════════ */
const RESUME_URL = "";

/* ────────────────────────────────────────────────────────────
   0. Small utilities
   ──────────────────────────────────────────────────────────── */
const $  = (s, c = document) => c.querySelector(s);
const $$ = (s, c = document) => [...c.querySelectorAll(s)];

$('#year').textContent = new Date().getFullYear();

/* nav scrolled state + active section highlight */
const nav = $('#nav');
const navLinks = $$('.nav-links a');
const sections = navLinks
  .map(a => $(a.getAttribute('href')))
  .filter(Boolean);

function syncNav() {
  nav.classList.toggle('scrolled', window.scrollY > 24);
  let current = null;
  for (const sec of sections) {
    if (sec.getBoundingClientRect().top <= window.innerHeight * 0.4) current = sec.id;
  }
  navLinks.forEach(a => a.classList.toggle('active', a.getAttribute('href') === `#${current}`));
}
window.addEventListener('scroll', syncNav, { passive: true });
syncNav();

/* mobile menu */
const burger = $('#navBurger');
const navLinksEl = $('#navLinks');
burger.addEventListener('click', () => {
  const open = navLinksEl.classList.toggle('open');
  burger.setAttribute('aria-expanded', String(open));
});
navLinksEl.addEventListener('click', e => {
  if (e.target.tagName === 'A') {
    navLinksEl.classList.remove('open');
    burger.setAttribute('aria-expanded', 'false');
  }
});

/* project-card cursor glow */
$$('.project-card').forEach(card => {
  card.addEventListener('pointermove', e => {
    const r = card.getBoundingClientRect();
    card.style.setProperty('--mx', `${e.clientX - r.left}px`);
    card.style.setProperty('--my', `${e.clientY - r.top}px`);
  });
});

/* ────────────────────────────────────────────────────────────
   1. Hero terminal boot sequence
   ──────────────────────────────────────────────────────────── */
const TERM_LINES = [
  { prompt: true, cmd: 'ssh devyansh@bengaluru --role devops-intern' },
  { out: 'Establishing secure connection… <span class="t-ok">OK</span>', delay: 350 },
  { out: 'Authenticating with public key… <span class="t-ok">OK</span>', delay: 300 },
  { prompt: true, cmd: 'cat profile.json', delay: 250 },
  { out: '{' },
  { out: '  <span class="t-info">"name"</span>: <span class="t-ok">"Devyansh Gupta"</span>,' },
  { out: '  <span class="t-info">"focus"</span>: [<span class="t-ok">"cloud"</span>, <span class="t-ok">"ci/cd"</span>, <span class="t-ok">"storage"</span>, <span class="t-ok">"backend"</span>],' },
  { out: '  <span class="t-info">"aws"</span>: <span class="t-ok">"Academy Solutions Architect"</span>,' },
  { out: '  <span class="t-info">"published"</span>: <span class="t-warn">true</span>,  <span class="t-info">// Q1 journal, cloud forensics</span>' },
  { out: '}' },
  { prompt: true, cmd: './deploy --career devops-internship', delay: 350 },
  { out: '<span class="t-ok">▸ pipeline ready — awaiting your offer ✦</span>', delay: 500 },
];

function runTerminal() {
  const body = $('#terminalBody');
  if (REDUCED) {
    // render everything instantly, no typing
    body.innerHTML = TERM_LINES.map(l =>
      l.prompt
        ? `<div class="t-line"><span class="t-prompt">$ </span><span class="t-cmd">${l.cmd}</span></div>`
        : `<div class="t-line t-out">${l.out}</div>`
    ).join('');
    return;
  }

  let i = 0;
  const typeLine = () => {
    if (i >= TERM_LINES.length) {
      body.insertAdjacentHTML('beforeend',
        '<div class="t-line"><span class="t-prompt">$ </span><span class="t-caret"></span></div>');
      return;
    }
    const line = TERM_LINES[i++];
    const div = document.createElement('div');
    div.className = 't-line';

    if (line.prompt) {
      div.innerHTML = '<span class="t-prompt">$ </span><span class="t-cmd"></span><span class="t-caret"></span>';
      body.appendChild(div);
      const cmdEl = div.querySelector('.t-cmd');
      let c = 0;
      const typer = createTimer({
        duration: line.cmd.length * 34,
        onUpdate: self => {
          const n = Math.floor((self.progress / 100) * line.cmd.length);
          if (n !== c) { c = n; cmdEl.textContent = line.cmd.slice(0, n); }
        },
        onComplete: () => {
          div.querySelector('.t-caret')?.remove();
          setTimeout(typeLine, 220);
        },
      });
      void typer;
    } else {
      div.classList.add('t-out');
      body.appendChild(div);
      const target = line.out;
      // fade/slide the output line in, then reveal its html
      div.style.opacity = '0';
      animate(div, { opacity: [0, 1], translateY: [4, 0], duration: 180, ease: 'outQuad' });
      div.innerHTML = target;
      setTimeout(typeLine, line.delay ?? 120);
    }
    body.scrollTop = body.scrollHeight;
  };
  setTimeout(typeLine, 500);
}

/* ────────────────────────────────────────────────────────────
   2. Hero entrance choreography
   ──────────────────────────────────────────────────────────── */
function heroEntrance() {
  if (REDUCED) return;

  // name: split into chars and cascade in.
  // NOTE: background-clip:text does NOT survive the split — anime.js wraps
  // each char in an inline-block span, so the parent gradient stops painting
  // and the inherited transparent fill makes the text invisible. We repaint
  // the gradient per-char below (and CSS has a solid-color fallback).
  const nameEl = $('#heroName');
  let chars;
  try {
    const splitter = text.split(nameEl, { chars: true });
    chars = splitter.chars;
  } catch {
    chars = [];
  }

  if (chars.length) {
    // recreate the CSS gradient (fg → green, 55%→90%) across the chars
    const from = [230, 237, 243]; // --fg
    const to = [63, 220, 139];    // --green
    chars.forEach((ch, i) => {
      const t = chars.length > 1 ? i / (chars.length - 1) : 1;
      const tt = Math.min(1, Math.max(0, (t - 0.55) / 0.35));
      const c = from.map((f, k) => Math.round(f + (to[k] - f) * tt));
      const col = `rgb(${c[0]}, ${c[1]}, ${c[2]})`;
      ch.style.color = col;
      ch.style.webkitTextFillColor = col;
    });
    animate(chars, {
      opacity: [0, 1],
      translateY: ['1.1em', 0],
      rotateX: [90, 0],
      duration: 700,
      ease: 'outExpo',
      delay: stagger(28),
    });
  } else {
    // split unavailable — fade the whole name in, gradient intact
    animate(nameEl, { opacity: [0, 1], translateY: [20, 0], duration: 800, ease: 'outExpo' });
  }

  createTimeline({ defaults: { ease: 'outQuad' } })
    .add('.hero-kicker',   { opacity: [0, 1], translateY: [12, 0], duration: 500 }, 200)
    .add('.hero-role',     { opacity: [0, 1], translateY: [16, 0], duration: 600 }, '-=300')
    .add('.hero-cta .btn', { opacity: [0, 1], translateY: [16, 0], duration: 500, delay: stagger(90) }, '-=350')
    .add('.hero-meta li',  { opacity: [0, 1], translateX: [-10, 0], duration: 400, delay: stagger(80) }, '-=300')
    .add('#heroTerminal',  { opacity: [0, 1], translateY: [24, 0], scale: [0.98, 1], duration: 700, ease: 'outExpo' }, 100)
    .add('.pipeline',      { opacity: [0, 1], translateY: [20, 0], duration: 600 }, '-=400')
    .add('.stats .stat',   { opacity: [0, 1], translateY: [14, 0], duration: 450, delay: stagger(70) }, '-=350');
}

/* ────────────────────────────────────────────────────────────
   3. CI/CD pipeline — endless pulse travelling through nodes
   ──────────────────────────────────────────────────────────── */
function pipelineLoop() {
  const nodes = $$('.pipe-node');
  const pulses = $$('.pipe-pulse');
  if (REDUCED) { nodes.forEach(n => n.classList.add('lit')); return; }

  const STEP = 900;
  let step = 0;
  createTimer({
    duration: Infinity,
    onUpdate: () => {},
  });
  const advance = () => {
    const idx = step % nodes.length;
    nodes.forEach((n, i) => n.classList.toggle('lit', i === idx));
    if (idx > 0) {
      animate(pulses[idx - 1], { translateX: ['0%', '430%'], duration: STEP * 0.8, ease: 'inOutQuad' });
    } else {
      pulses.forEach(p => { utils.set(p, { translateX: '0%' }); });
    }
    step++;
    setTimeout(advance, STEP);
  };
  advance();
}

/* ────────────────────────────────────────────────────────────
   4. Stats count-up (fires once when visible)
   ──────────────────────────────────────────────────────────── */
function statsCountUp() {
  const counters = $$('[data-count]');
  if (REDUCED) {
    counters.forEach(el => { el.textContent = el.dataset.count; });
    return;
  }
  let fired = false;
  onScroll({
    target: '#stats',
    onEnter: () => {
      if (fired) return; fired = true;
      counters.forEach(el => {
        const target = parseFloat(el.dataset.count);
        const decimals = parseInt(el.dataset.decimals || '0', 10);
        const obj = { v: 0 };
        animate(obj, {
          v: target,
          duration: 1600,
          ease: 'outExpo',
          modifier: v => { el.textContent = v.toFixed(decimals); return v; },
        });
      });
    },
  });
}

/* ────────────────────────────────────────────────────────────
   5. Marquee — infinite tech ticker
   ──────────────────────────────────────────────────────────── */
function marquee() {
  const track = $('#marqueeTrack');
  // duplicate content for seamless loop
  track.innerHTML += track.innerHTML;
  if (REDUCED) return;
  const half = track.scrollWidth / 2;
  const state = { x: 0 };
  animate(state, {
    x: -half,
    duration: half * 18,          // ~18ms per px → steady crawl
    ease: 'linear',
    loop: true,
    modifier: v => { track.style.transform = `translateX(${v}px)`; return v; },
  });
}

/* ────────────────────────────────────────────────────────────
   6. Scroll reveals — every [data-reveal] element
   ──────────────────────────────────────────────────────────── */
function scrollReveals() {
  const els = $$('[data-reveal]');
  if (REDUCED) { els.forEach(el => { el.style.opacity = ''; el.style.transform = ''; }); return; }

  els.forEach(el => {
    onScroll({
      target: el,
      enter: 'bottom bottom-=10%',
      once: true,
      onEnter: () => {
        animate(el, {
          opacity: [0, 1],
          translateY: [26, 0],
          duration: 750,
          ease: 'outExpo',
        });
      },
    });
  });
}

/* ────────────────────────────────────────────────────────────
   7. Timeline line draw-on as you scroll experience
   ──────────────────────────────────────────────────────────── */
function timelineDraw() {
  const tl = $('#timeline');
  if (!tl || REDUCED) return;
  onScroll({
    target: tl,
    enter: 'top bottom',
    leave: 'bottom center',
    sync: true,
    onScroll: self => {
      tl.style.setProperty('--tl-progress', String(Math.min(1, self.progress / 100)));
    },
  });
}

/* ────────────────────────────────────────────────────────────
   8. Photo scanline sweep
   ──────────────────────────────────────────────────────────── */
function photoScan() {
  const scan = $('.photo-scan');
  if (!scan || REDUCED) return;
  animate(scan, {
    top: ['-30%', '110%'],
    duration: 3400,
    ease: 'inOutSine',
    loop: true,
    alternate: true,
  });
}

/* ────────────────────────────────────────────────────────────
   9. Contact form → /api/contact
   ──────────────────────────────────────────────────────────── */
function contactForm() {
  const form = $('#contactForm');
  const status = $('#formStatus');
  const submitBtn = $('#cfSubmit');
  if (!form) return;

  form.addEventListener('submit', async e => {
    e.preventDefault();
    status.className = 'form-status';
    status.textContent = '';

    const name = $('#cf-name').value.trim();
    const email = $('#cf-email').value.trim();
    const message = $('#cf-message').value.trim();
    const honeypot = $('#cf-company').value;

    // client-side validation
    let bad = null;
    if (!name) bad = '#cf-name';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) bad = '#cf-email';
    else if (message.length < 10) bad = '#cf-message';
    $$('.form-row input, .form-row textarea', form).forEach(i => i.classList.remove('invalid'));
    if (bad) {
      $(bad).classList.add('invalid');
      $(bad).focus();
      status.classList.add('err');
      status.textContent = '✗ please fill every field (message ≥ 10 chars, valid email).';
      return;
    }

    submitBtn.disabled = true;
    submitBtn.querySelector('.btn-label').textContent = 'transmitting…';

    try {
      const res = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, message, company: honeypot }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);

      status.classList.add('ok');
      status.textContent = '✓ message delivered — I\'ll reply within 24h.';
      form.reset();
      if (!REDUCED) {
        animate(status, { scale: [1.06, 1], duration: 400, ease: 'outBack' });
      }
    } catch (err) {
      status.classList.add('err');
      status.textContent = `✗ transmission failed (${err.message}). email me directly: devyanshgupta04@gmail.com`;
    } finally {
      submitBtn.disabled = false;
      submitBtn.querySelector('.btn-label').textContent = 'send --message';
    }
  });
}

/* ────────────────────────────────────────────────────────────
   10. Resume buttons
       Priority: RESUME_URL (your pasted SAS link) → /api/resume
       (server-minted SAS) → bundled PDF fallback.
   ──────────────────────────────────────────────────────────── */
function resumeButtons() {
  $$('[data-resume]').forEach(btn => {
    // 1) explicit SAS link pasted in main.js
    if (RESUME_URL) {
      btn.setAttribute('href', RESUME_URL);
      btn.setAttribute('target', '_blank');
      btn.setAttribute('rel', 'noopener');
      return;
    }
    // 2) try the API; 3) fall back to bundled copy
    btn.addEventListener('click', async e => {
      try {
        const res = await fetch('/api/resume', { method: 'HEAD', redirect: 'manual' });
        if (res.ok || res.type === 'opaqueredirect' || res.status === 302) return; // let it navigate
        throw new Error(res.status);
      } catch {
        e.preventDefault();
        const a = document.createElement('a');
        a.href = '/assets/Devyansh_Gupta_Resume_DevOps_Intern.pdf';
        a.download = 'Devyansh_Gupta_Resume_DevOps_Intern.pdf';
        document.body.appendChild(a);
        a.click();
        a.remove();
      }
    });
  });
}

/* ────────────────────────────────────────────────────────────
   boot
   ──────────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  runTerminal();
  heroEntrance();
  pipelineLoop();
  statsCountUp();
  marquee();
  scrollReveals();
  timelineDraw();
  photoScan();
  contactForm();
  resumeButtons();
});
