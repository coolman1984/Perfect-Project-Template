/**
 * Application shell: navigation, API access, events, accessibility.
 * Constitution Parts 22.2, 22.4, 25.5.
 *
 * Boundaries this file must respect:
 *   - Every server call goes through the loopback API. The browser never
 *     touches Excel COM, DuckDB or the filesystem (Part 0.9).
 *   - No trusted arithmetic. Values arrive pre-calculated and pre-rounded;
 *     this file formats and displays them (rule 6).
 *   - No remote request of any kind. No CDN, font, icon or telemetry
 *     (Part 23.6). The browser verification step fails the build on one.
 *   - Durable state lives on the server. A refresh reconnects by run_id and
 *     event sequence; the renderer is never the source of truth
 *     (Part 25.5.1 rule 6).
 */

const API = {
  /**
   * Same-origin fetch against the loopback API.
   *
   * The per-launch secret is injected by the bootstrap handshake and kept in
   * memory only — never in a URL, a log or browser history (Part 43).
   */
  async request(path, options = {}) {
    const response = await fetch(path, {
      ...options,
      credentials: 'same-origin',
      headers: {
        'Accept': 'application/json',
        ...(options.headers || {}),
        ...(window.__launchSecret ? { 'X-Launch-Secret': window.__launchSecret } : {}),
      },
    });
    if (!response.ok) {
      // Never surface a raw stack trace as the primary message (Part 22.8).
      const payload = await response.json().catch(() => ({}));
      throw new AppError(payload);
    }
    return response.json();
  },

  health()          { return this.request('/api/health'); },
  reports()         { return this.request('/api/reports'); },
  dashboard()       { return this.request('/api/dashboard'); },
  history()         { return this.request('/api/history'); },
  run(id)           { return this.request(`/api/runs/${encodeURIComponent(id)}`); },
  events(id, since) { return this.request(`/api/runs/${encodeURIComponent(id)}/events?since=${since}`); },
};

/** Carries a registry error code and its four-part operator screen (Part 22.8). */
class AppError extends Error {
  constructor(payload) {
    super(payload.what_went_wrong || 'Something went wrong.');
    this.supportCode = payload.support_code || 'UNKNOWN';
    this.dataIsSafe = payload.is_my_data_safe !== false;
    this.nextAction = payload.next_action || '';
    this.supportDetail = payload.support_detail || '';
  }
}

/**
 * Durable progress stream (Part 22.4).
 *
 * Server-sent events are preferred. Polling by (run_id, last sequence) is a
 * DELIVERY fallback for a verified renderer limitation — it is not permission
 * to remove the server.
 */
class ProgressStream {
  constructor(runId, onEvent) {
    this.runId = runId;
    this.onEvent = onEvent;
    this.lastSequence = -1;
    this.source = null;
    this.pollTimer = null;
  }

  start() {
    if (typeof EventSource !== 'undefined') {
      this.source = new EventSource(`/api/runs/${encodeURIComponent(this.runId)}/events`);
      this.source.onmessage = (message) => this.handle(JSON.parse(message.data));
      this.source.onerror = () => { this.source.close(); this.startPolling(); };
      return;
    }
    this.startPolling();
  }

  startPolling() {
    this.pollTimer = setInterval(async () => {
      const batch = await API.events(this.runId, this.lastSequence);
      batch.forEach((event) => this.handle(event));
    }, 1000);
  }

  /** Events are ordered and replayable, so out-of-order arrivals are dropped. */
  handle(event) {
    if (event.sequence <= this.lastSequence) return;
    this.lastSequence = event.sequence;
    this.onEvent(event);
  }

  stop() {
    if (this.source) this.source.close();
    if (this.pollTimer) clearInterval(this.pollTimer);
  }
}

const UI = {
  /** Quality and freshness are never hidden (Part 26.11). */
  renderHeader(pack) {
    document.getElementById('report-title').textContent = pack.report.title;
    document.getElementById('report-period').textContent = pack.report.period;

    const badge = document.getElementById('quality-badge');
    badge.dataset.status = pack.quality.status;
    document.getElementById('quality-text').textContent = pack.quality.status;
    // Icon plus text, so meaning survives greyscale printing (Part 11.4).
    badge.querySelector('.badge-icon').textContent =
      { PASS: '✓', WARNING: '!', FAIL: '✕' }[pack.quality.status] || '•';

    document.getElementById('freshness').textContent = `Data date ${pack.freshness.data_date}`;
    document.getElementById('demo-watermark').hidden = !pack.demo_data;
    document.getElementById('unapproved-watermark').hidden = !pack.unapproved_definitions;
    document.getElementById('partial-warning').hidden = !pack.freshness.is_partial;
  },

  renderKpis(kpis) {
    const strip = document.getElementById('kpi-strip');
    strip.replaceChildren(...kpis.map((kpi) => {
      const card = document.createElement('article');
      card.className = 'kpi-card';

      const label = document.createElement('h3');
      label.textContent = kpi.label;

      const value = document.createElement('p');
      value.className = 'kpi-value';
      // A null value is shown as an em dash, never as a false zero (Part 26.5).
      value.textContent = kpi.value === null ? '—' : kpi.display;

      const unit = document.createElement('p');
      unit.className = 'kpi-unit';
      unit.textContent = `${kpi.unit}${kpi.period ? ` · ${kpi.period}` : ''}`;

      card.append(label, value, unit);

      if (kpi.comparison) {
        const comparison = document.createElement('p');
        comparison.className = 'kpi-comparison';
        comparison.dataset.direction = UI.directionOf(kpi);
        // The comparison base is visible beside the KPI, not hidden in a
        // tooltip (Part 22.6).
        comparison.textContent =
          `${kpi.comparison.change_percent}% vs ${kpi.comparison.base}`;
        card.append(comparison);
      }
      return card;
    }));
  },

  directionOf(kpi) {
    const change = kpi.comparison && kpi.comparison.change_absolute;
    if (!change) return 'flat';
    if (kpi.direction === 'neutral') return 'flat';
    const improving = kpi.direction === 'up_good' ? change > 0 : change < 0;
    return improving ? 'good' : 'bad';
  },

  /** The four-part error screen. Technical detail stays collapsed (Part 22.8). */
  renderError(error) {
    const panel = document.getElementById('support-details');
    panel.replaceChildren();
    const heading = document.createElement('p');
    heading.textContent = error.message;
    const safety = document.createElement('p');
    safety.textContent = error.dataIsSafe
      ? 'Your previous dashboard and history are unchanged and still correct.'
      : 'Support attention is required.';
    const action = document.createElement('p');
    action.textContent = error.nextAction;
    const code = document.createElement('code');
    code.textContent = error.supportCode;
    panel.append(heading, safety, action, code);
  },
};

async function boot() {
  try {
    await API.health();
    const pack = await API.dashboard();
    UI.renderHeader(pack);
    UI.renderKpis(pack.kpis);
    // Charts, filters, story and motion are wired by their own modules.
  } catch (error) {
    // Golden operating rule: never a blank page. Show the last truth, with its
    // date, or a plain-language explanation (Part 12.6).
    UI.renderError(error instanceof AppError ? error : new AppError({}));
  }
}

document.addEventListener('DOMContentLoaded', boot);

export { API, AppError, ProgressStream, UI };
