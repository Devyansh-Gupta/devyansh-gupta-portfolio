// POST /api/contact — validate, honeypot-check, rate-limit, send via SMTP.
// Secrets come from SWA app settings (env vars), never from the repo.
const { app } = require('@azure/functions');
const nodemailer = require('nodemailer');

// ── tiny in-memory rate limiter: max 3 submissions / 10 min per IP ──
const WINDOW_MS = 10 * 60 * 1000;
const MAX_HITS = 3;
const hits = new Map();

function rateLimited(ip) {
  const now = Date.now();
  const arr = (hits.get(ip) || []).filter(t => now - t < WINDOW_MS);
  if (arr.length >= MAX_HITS) { hits.set(ip, arr); return true; }
  arr.push(now);
  hits.set(ip, arr);
  return false;
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

let transporterPromise = null;
function getTransporter() {
  if (!transporterPromise) {
    const { SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_SECURE } = process.env;
    if (!SMTP_HOST || !SMTP_USER || !SMTP_PASS) {
      throw new Error('SMTP is not configured on this deployment');
    }
    transporterPromise = nodemailer.createTransport({
      host: SMTP_HOST,
      port: Number(SMTP_PORT || 587),
      secure: SMTP_SECURE === 'true' || Number(SMTP_PORT || 587) === 465,
      auth: { user: SMTP_USER, pass: SMTP_PASS },
    });
  }
  return transporterPromise;
}

app.http('contact', {
  route: 'contact',
  methods: ['POST'],
  authLevel: 'anonymous',
  handler: async (request, context) => {
    const json = (status, body) => ({
      status,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    // parse body
    let data;
    try {
      data = typeof request.body === 'string' ? JSON.parse(request.body) : await request.json();
    } catch {
      return json(400, { error: 'invalid JSON body' });
    }

    const name = String(data.name || '').trim();
    const email = String(data.email || '').trim();
    const message = String(data.message || '').trim();
    const honeypot = String(data.company || '').trim();

    // honeypot: bots fill the hidden field — pretend success, send nothing
    if (honeypot) return json(200, { ok: true });

    // validation
    if (!name || name.length > 200) return json(400, { error: 'invalid name' });
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email) || email.length > 200) {
      return json(400, { error: 'invalid email' });
    }
    if (message.length < 10 || message.length > 5000) {
      return json(400, { error: 'message must be 10–5000 characters' });
    }

    // rate limit
    const ip =
      request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() ||
      request.headers.get('x-azure-clientip') || 'unknown';
    if (rateLimited(ip)) return json(429, { error: 'too many messages — try again later' });

    // send
    try {
      const transporter = getTransporter();
      const to = process.env.CONTACT_TO || process.env.SMTP_USER;
      await transporter.sendMail({
        from: `"Portfolio Contact Form" <${process.env.SMTP_USER}>`,
        replyTo: email,
        to,
        subject: `Portfolio message from ${name}`,
        text: `${name} <${email}> wrote:\n\n${message}`,
        html: `
          <div style="font-family:monospace;background:#0a0e14;color:#e6edf3;padding:24px;border-radius:10px;max-width:560px">
            <p style="color:#3fdc8b;margin:0 0 16px">$ ./new-message --from "${escapeHtml(name)}"</p>
            <p style="margin:0 0 6px"><strong>from:</strong> ${escapeHtml(name)} &lt;${escapeHtml(email)}&gt;</p>
            <hr style="border:none;border-top:1px solid #1d2635;margin:14px 0">
            <p style="white-space:pre-wrap;margin:0;line-height:1.6">${escapeHtml(message)}</p>
            <hr style="border:none;border-top:1px solid #1d2635;margin:14px 0">
            <p style="color:#566374;font-size:12px;margin:0">sent from devyansh-gupta portfolio contact form</p>
          </div>`,
      });
      context.log(`contact form message delivered from ${email}`);
      return json(200, { ok: true });
    } catch (err) {
      context.error('contact form send failed:', err.message);
      return json(502, { error: 'email service unavailable — please email devyanshgupta04@gmail.com directly' });
    }
  },
});
