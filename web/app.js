import { renderChart, disposeChart } from './dashboard.js';

const API = {
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
      const payload = await response.json().catch(() => ({}));
      throw new AppError(payload, response.status);
    }
    const type = response.headers.get('content-type') || '';
    return type.includes('application/json') ? response.json() : response;
  },
  health() { return this.request('/api/health'); },
  reports() { return this.request('/api/reports'); },
  dashboard() { return this.request('/api/dashboard'); },
  history() { return this.request('/api/history'); },
  run(id) { return this.request(`/api/runs/${encodeURIComponent(id)}`); },
  events(id, since) { return this.request(`/api/runs/${encodeURIComponent(id)}/events?since=${since}`); },
  upload(reportId, file) {
    return this.request(`/api/uploads?report_id=${encodeURIComponent(reportId)}`, {
      method: 'POST', body: file,
      headers: { 'Content-Type': 'application/octet-stream', 'X-File-Name': encodeURIComponent(file.name) },
    });
  },
  startRun(reportId, uploadId) {
    return this.request('/api/runs', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ report_id: reportId, upload_id: uploadId }),
    });
  },
};

class AppError extends Error {
  constructor(payload, status = 0) {
    super(payload.what_went_wrong || payload.message || 'Something went wrong.');
    this.status = status;
    this.supportCode = payload.support_code || payload.status || 'UNKNOWN';
    this.dataIsSafe = payload.is_my_data_safe !== false;
    this.nextAction = payload.next_action || '';
    this.supportDetail = payload.support_detail || '';
  }
}

class ProgressStream {
  constructor(runId, onEvent) { this.runId = runId; this.onEvent = onEvent; this.lastSequence = -1; this.source = null; this.pollTimer = null; }
  start() {
    if (typeof EventSource !== 'undefined') {
      this.source = new EventSource(`/api/runs/${encodeURIComponent(this.runId)}/events`);
      this.source.onmessage = (message) => this.handle(JSON.parse(message.data));
      this.source.onerror = () => { this.source.close(); this.source = null; this.startPolling(); };
      return;
    }
    this.startPolling();
  }
  startPolling() {
    if (this.pollTimer) return;
    this.pollTimer = setInterval(async () => {
      try { (await API.events(this.runId, this.lastSequence)).forEach((event) => this.handle(event)); } catch (_) { /* next poll retries */ }
    }, 1000);
  }
  handle(event) {
    if (event.sequence <= this.lastSequence) return;
    this.lastSequence = event.sequence; this.onEvent(event);
    if (['COMPLETE', 'FAILED', 'CANCELLED'].includes(event.stage)) this.stop();
  }
  stop() { if (this.source) this.source.close(); if (this.pollTimer) clearInterval(this.pollTimer); this.source = null; this.pollTimer = null; }
}

const UI = {
  renderHeader(pack) {
    document.getElementById('report-title').textContent = pack.report.title;
    document.getElementById('report-period').textContent = pack.report.period;
    const badge = document.getElementById('quality-badge'); badge.dataset.status = pack.quality.status;
    document.getElementById('quality-text').textContent = pack.quality.status;
    badge.querySelector('.badge-icon').textContent = { PASS: '✓', WARNING: '!', FAIL: '✕' }[pack.quality.status] || '•';
    document.getElementById('freshness').textContent = `Data date ${pack.freshness.data_date}`;
    document.getElementById('demo-watermark').hidden = !pack.demo_data;
    document.getElementById('unapproved-watermark').hidden = !pack.unapproved_definitions;
    document.getElementById('partial-warning').hidden = !pack.freshness.is_partial;
  },
  renderKpis(kpis) {
    const strip = document.getElementById('kpi-strip');
    strip.replaceChildren(...kpis.map((kpi) => {
      const card = document.createElement('article'); card.className = 'kpi-card';
      const label = document.createElement('h3'); label.textContent = kpi.label;
      const value = document.createElement('p'); value.className = 'kpi-value'; value.textContent = kpi.value === null ? '—' : kpi.display;
      const unit = document.createElement('p'); unit.className = 'kpi-unit'; unit.textContent = `${kpi.unit}${kpi.period ? ` · ${kpi.period}` : ''}`;
      card.append(label, value, unit); return card;
    }));
  },
  renderCharts(charts) {
    const grid = document.getElementById('chart-grid');
    grid.querySelectorAll('.chart').forEach((node) => disposeChart(node.id));
    grid.replaceChildren();
    charts.forEach((spec, index) => {
      const figure = document.createElement('figure'); figure.className = `panel ${index === 0 ? 'span-8' : 'span-6'}`;
      const title = document.createElement('figcaption'); title.className = 'panel-title'; title.textContent = spec.title;
      const chart = document.createElement('div'); chart.className = 'chart'; chart.id = `chart-${spec.id}`; chart.setAttribute('role', 'img');
      const summary = document.createElement('p'); summary.className = 'chart-summary visually-hidden'; summary.textContent = spec.accessible_summary || '';
      figure.append(title, chart, summary); grid.append(figure); renderChart(chart.id, spec);
    });
  },
  renderInsights(insights) {
    const body = document.getElementById('insight-focus-body'); body.replaceChildren();
    insights.forEach((insight) => { const item = document.createElement('p'); item.className = 'insight-item'; item.textContent = insight.text; body.append(item); });
    document.getElementById('insight-focus').hidden = insights.length === 0;
  },
  renderError(error) {
    const panel = document.getElementById('support-details'); panel.replaceChildren();
    const heading = document.createElement('p'); heading.textContent = error.message;
    const safety = document.createElement('p'); safety.textContent = error.dataIsSafe ? 'Your previous dashboard and history are unchanged and still correct.' : 'Support attention is required.';
    const action = document.createElement('p'); action.textContent = error.nextAction;
    const code = document.createElement('code'); code.textContent = error.supportCode;
    panel.append(heading, safety, action, code);
  },
  renderDashboard(pack) { this.renderHeader(pack); this.renderKpis(pack.kpis || []); this.renderCharts(pack.charts || []); this.renderInsights(pack.insights || []); },
};

let selectedFile = null;
let reports = [];

function wireOperations() {
  const input = document.getElementById('file-input');
  const dropzone = document.getElementById('dropzone');
  const button = document.getElementById('process-button');
  const list = document.getElementById('file-list');
  const select = document.getElementById('report-select');
  const choose = (files) => {
    selectedFile = files && files[0] ? files[0] : null;
    list.replaceChildren();
    if (selectedFile) { const li = document.createElement('li'); li.textContent = `${selectedFile.name} · ${(selectedFile.size / 1048576).toFixed(1)} MB`; list.append(li); }
    button.disabled = !selectedFile || !select.value;
  };
  dropzone.addEventListener('click', () => input.click());
  dropzone.addEventListener('keydown', (event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); input.click(); } });
  dropzone.addEventListener('dragover', (event) => event.preventDefault());
  dropzone.addEventListener('drop', (event) => { event.preventDefault(); choose(event.dataTransfer.files); });
  input.addEventListener('change', () => choose(input.files));
  select.addEventListener('change', () => { button.disabled = !selectedFile || !select.value; });
  button.addEventListener('click', async () => {
    if (!selectedFile || !select.value) return;
    button.disabled = true;
    const progress = document.getElementById('progress'); const message = document.getElementById('progress-message'); progress.hidden = false;
    try {
      message.textContent = 'Copying the selected file into the local intake area…';
      const uploaded = await API.upload(select.value, selectedFile);
      message.textContent = 'Starting the configured automation…';
      const started = await API.startRun(select.value, uploaded.upload_id);
      const stream = new ProgressStream(started.run_id, async (event) => {
        message.textContent = event.stage.replaceAll('_', ' ');
        if (event.stage === 'COMPLETE') { UI.renderDashboard(await API.dashboard()); button.disabled = false; }
        if (event.stage === 'FAILED') { UI.renderError(new AppError({ what_went_wrong: 'The new update failed.', next_action: 'Open support details. Your previous dashboard was not replaced.', support_code: 'RUN_FAILED' })); button.disabled = false; }
      });
      stream.start();
    } catch (error) { UI.renderError(error instanceof AppError ? error : new AppError({})); button.disabled = false; }
  });
}

async function boot() {
  wireOperations();
  try {
    await API.health();
    reports = await API.reports();
    const select = document.getElementById('report-select');
    reports.forEach((report) => { const option = document.createElement('option'); option.value = report.report_id; option.textContent = report.report_id; select.append(option); });
    if (reports.length === 1) select.value = reports[0].report_id;
    try { UI.renderDashboard(await API.dashboard()); } catch (error) { if (!(error instanceof AppError) || error.status !== 404) throw error; }
  } catch (error) { UI.renderError(error instanceof AppError ? error : new AppError({})); }
}

document.addEventListener('DOMContentLoaded', boot);
export { API, AppError, ProgressStream, UI };
