import { renderChart, disposeChart } from './dashboard.js';

const API = {
  async request(path, options = {}) {
    const response = await fetch(path, {
      ...options,
      credentials: 'same-origin',
      headers: {
        'Accept': 'application/json',
        ...(options.headers || {}),
        ...(window.__launchSecret
          ? { 'X-Launch-Secret': window.__launchSecret }
          : {}),
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
  projects() { return this.request('/api/projects'); },
  project(id) { return this.request(`/api/projects/${encodeURIComponent(id)}`); },
  dashboard() { return this.request('/api/dashboard'); },
  history() { return this.request('/api/history'); },
  run(id) { return this.request(`/api/runs/${encodeURIComponent(id)}`); },
  events(id, since) {
    return this.request(
      `/api/runs/${encodeURIComponent(id)}/events?since=${since}`);
  },
  projectUpload(projectId, sourceId, file) {
    return this.request(
      `/api/project-uploads?project_id=${encodeURIComponent(projectId)}`
        + `&source_id=${encodeURIComponent(sourceId)}`,
      {
        method: 'POST',
        body: file,
        headers: {
          'Content-Type': 'application/octet-stream',
          'X-File-Name': encodeURIComponent(file.name),
        },
      },
    );
  },
  startProjectRun(projectId, uploads) {
    return this.request('/api/project-runs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project_id: projectId, uploads }),
    });
  },
};

class AppError extends Error {
  constructor(payload, status = 0) {
    super(
      payload.what_went_wrong || payload.message || 'Something went wrong.');
    this.status = status;
    this.supportCode = payload.support_code || payload.status || 'UNKNOWN';
    this.dataIsSafe = payload.is_my_data_safe !== false;
    this.nextAction = payload.next_action || '';
    this.supportDetail = payload.support_detail || '';
  }
}

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
      this.source = new EventSource(
        `/api/runs/${encodeURIComponent(this.runId)}/events`);
      this.source.onmessage = (message) => this.handle(JSON.parse(message.data));
      this.source.onerror = () => {
        this.source.close();
        this.source = null;
        this.startPolling();
      };
      return;
    }
    this.startPolling();
  }
  startPolling() {
    if (this.pollTimer) return;
    this.pollTimer = setInterval(async () => {
      try {
        (await API.events(this.runId, this.lastSequence))
          .forEach((event) => this.handle(event));
      } catch (_) {
        // Durable events are retried on the next poll.
      }
    }, 1000);
  }
  handle(event) {
    if (event.sequence <= this.lastSequence) return;
    this.lastSequence = event.sequence;
    this.onEvent(event);
    if (['COMPLETE', 'FAILED', 'CANCELLED'].includes(event.stage)) this.stop();
  }
  stop() {
    if (this.source) this.source.close();
    if (this.pollTimer) clearInterval(this.pollTimer);
    this.source = null;
    this.pollTimer = null;
  }
}

const UI = {
  renderHeader(pack) {
    document.getElementById('report-title').textContent = pack.report.title;
    document.getElementById('report-period').textContent = pack.report.period;
    const badge = document.getElementById('quality-badge');
    badge.dataset.status = pack.quality.status;
    document.getElementById('quality-text').textContent = pack.quality.status;
    badge.querySelector('.badge-icon').textContent = {
      PASS: '✓', WARNING: '!', BLOCK: '✕', FAIL: '✕',
    }[pack.quality.status] || '•';
    document.getElementById('freshness').textContent =
      `Data date ${pack.freshness.data_date}`;
    document.getElementById('demo-watermark').hidden = !pack.demo_data;
    document.getElementById('unapproved-watermark').hidden =
      !pack.unapproved_definitions;
    document.getElementById('partial-warning').hidden =
      !pack.freshness.is_partial;
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
      value.textContent = kpi.value === null ? '—' : kpi.display;
      const unit = document.createElement('p');
      unit.className = 'kpi-unit';
      unit.textContent = `${kpi.unit}${kpi.period ? ` · ${kpi.period}` : ''}`;
      card.append(label, value, unit);
      return card;
    }));
  },
  renderCharts(charts) {
    const grid = document.getElementById('chart-grid');
    grid.querySelectorAll('.chart').forEach((node) => disposeChart(node.id));
    grid.replaceChildren();
    charts.forEach((spec, index) => {
      const figure = document.createElement('figure');
      figure.className = `panel ${index === 0 ? 'span-8' : 'span-6'}`;
      const title = document.createElement('figcaption');
      title.className = 'panel-title';
      title.textContent = spec.title;
      const chart = document.createElement('div');
      chart.className = 'chart';
      chart.id = `chart-${spec.id}`;
      chart.setAttribute('role', 'img');
      const summary = document.createElement('p');
      summary.className = 'chart-summary visually-hidden';
      summary.textContent = spec.accessible_summary || '';
      figure.append(title, chart, summary);
      grid.append(figure);
      renderChart(chart.id, spec);
    });
  },
  renderInsights(insights) {
    const body = document.getElementById('insight-focus-body');
    body.replaceChildren();
    insights.forEach((insight) => {
      const item = document.createElement('p');
      item.className = 'insight-item';
      item.textContent = insight.text;
      body.append(item);
    });
    document.getElementById('insight-focus').hidden = insights.length === 0;
  },
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
  renderDashboard(pack) {
    this.renderHeader(pack);
    this.renderKpis(pack.kpis || []);
    this.renderCharts(pack.charts || []);
    this.renderInsights(pack.insights || []);
  },
};

const state = {
  projects: [],
  project: null,
  selectedFiles: [],
  bySource: new Map(),
  unmatched: [],
};

function globMatches(pattern, fileName) {
  const escaped = pattern
    .replace(/[.+^${}()|[\]\\]/g, '\\$&')
    .replaceAll('**', '.*')
    .replaceAll('*', '[^/]*')
    .replaceAll('?', '.');
  return new RegExp(`^${escaped}$`, 'i').test(fileName);
}

function availableSources() {
  return state.project ? state.project.sources : [];
}

function autoAssign(files) {
  state.selectedFiles = Array.from(files || []);
  state.bySource = new Map();
  state.unmatched = [];
  for (const file of state.selectedFiles) {
    const matches = availableSources().filter((source) =>
      source.file_patterns.some((pattern) => globMatches(pattern, file.name)));
    const unclaimed = matches.filter(
      (source) => !state.bySource.has(source.source_id));
    if (unclaimed.length === 1) {
      state.bySource.set(unclaimed[0].source_id, file);
    } else {
      state.unmatched.push(file);
    }
  }
  renderReadiness();
}

function assignManually(file, sourceId) {
  for (const [existingSource, existingFile] of state.bySource.entries()) {
    if (existingFile === file) state.bySource.delete(existingSource);
  }
  if (sourceId) {
    const displaced = state.bySource.get(sourceId);
    if (displaced && displaced !== file && !state.unmatched.includes(displaced)) {
      state.unmatched.push(displaced);
    }
    state.bySource.set(sourceId, file);
    state.unmatched = state.unmatched.filter((candidate) => candidate !== file);
  }
  renderReadiness();
}

function isReady() {
  if (!state.project) return false;
  return state.project.sources
    .filter((source) => source.required)
    .every((source) => state.bySource.has(source.source_id));
}

function renderReadiness() {
  const readiness = document.getElementById('source-readiness');
  const fileList = document.getElementById('file-list');
  const unmatchedPanel = document.getElementById('unmatched-files');
  const processButton = document.getElementById('process-button');
  readiness.replaceChildren();
  fileList.replaceChildren();
  unmatchedPanel.replaceChildren();

  if (!state.project) {
    processButton.disabled = true;
    unmatchedPanel.hidden = true;
    return;
  }

  const heading = document.createElement('h3');
  heading.textContent = 'Required source readiness';
  readiness.append(heading);
  const grid = document.createElement('div');
  grid.className = 'source-grid';
  for (const source of state.project.sources) {
    const card = document.createElement('article');
    card.className = 'source-card';
    const name = document.createElement('strong');
    name.textContent = `${source.source_id} · ${source.role}`;
    const meaning = document.createElement('p');
    meaning.textContent = source.grain;
    const expected = document.createElement('p');
    expected.className = 'source-pattern';
    expected.textContent = `Expected: ${source.file_patterns.join(', ')}`;
    const assigned = document.createElement('p');
    const file = state.bySource.get(source.source_id);
    assigned.className = file ? 'source-ready' : 'source-missing';
    assigned.textContent = file
      ? `✓ ${file.name}`
      : (source.required ? 'Required file missing' : 'Optional file not added');
    card.append(name, meaning, expected, assigned);
    grid.append(card);
    if (file) {
      const li = document.createElement('li');
      li.textContent = `${source.source_id}: ${file.name} · ${(file.size / 1048576).toFixed(1)} MB`;
      fileList.append(li);
    }
  }
  readiness.append(grid);

  if (state.unmatched.length) {
    unmatchedPanel.hidden = false;
    const title = document.createElement('strong');
    title.textContent = 'Files needing a source role';
    unmatchedPanel.append(title);
    state.unmatched.forEach((file) => {
      const row = document.createElement('div');
      row.className = 'unmatched-row';
      const label = document.createElement('span');
      label.textContent = file.name;
      const select = document.createElement('select');
      select.setAttribute('aria-label', `Choose the business source role for ${file.name}`);
      const empty = document.createElement('option');
      empty.value = '';
      empty.textContent = 'Choose source role';
      select.append(empty);
      availableSources().forEach((source) => {
        const option = document.createElement('option');
        option.value = source.source_id;
        option.textContent = `${source.source_id} · ${source.role}`;
        select.append(option);
      });
      select.addEventListener('change', () => assignManually(file, select.value));
      row.append(label, select);
      unmatchedPanel.append(row);
    });
  } else {
    unmatchedPanel.hidden = true;
  }

  processButton.disabled = !isReady();
}

async function selectProject(projectId) {
  state.project = projectId ? await API.project(projectId) : null;
  state.selectedFiles = [];
  state.bySource = new Map();
  state.unmatched = [];
  document.getElementById('file-input').value = '';
  renderReadiness();
}

function wireOperations() {
  const input = document.getElementById('file-input');
  const dropzone = document.getElementById('dropzone');
  const button = document.getElementById('process-button');
  const select = document.getElementById('project-select');

  const choose = (files) => autoAssign(files);
  dropzone.addEventListener('click', () => input.click());
  dropzone.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      input.click();
    }
  });
  dropzone.addEventListener('dragover', (event) => event.preventDefault());
  dropzone.addEventListener('drop', (event) => {
    event.preventDefault();
    choose(event.dataTransfer.files);
  });
  input.addEventListener('change', () => choose(input.files));
  select.addEventListener('change', async () => {
    try {
      await selectProject(select.value);
    } catch (error) {
      UI.renderError(error instanceof AppError ? error : new AppError({}));
    }
  });

  button.addEventListener('click', async () => {
    if (!state.project || !isReady()) return;
    button.disabled = true;
    const progress = document.getElementById('progress');
    const message = document.getElementById('progress-message');
    const fill = document.getElementById('progress-fill');
    progress.hidden = false;
    fill.style.width = '5%';
    try {
      const uploads = {};
      const entries = Array.from(state.bySource.entries());
      for (let index = 0; index < entries.length; index += 1) {
        const [sourceId, file] = entries[index];
        message.textContent = `Copying ${sourceId}: ${file.name} into the local intake area…`;
        const uploaded = await API.projectUpload(
          state.project.project_id, sourceId, file);
        uploads[sourceId] = uploaded.upload_id;
        fill.style.width = `${Math.max(10, Math.round(((index + 1) / entries.length) * 35))}%`;
      }
      message.textContent = 'All required sources are ready. Starting the project update…';
      const started = await API.startProjectRun(
        state.project.project_id, uploads);
      const stream = new ProgressStream(started.run_id, async (event) => {
        const source = event.source_id ? ` · ${event.source_id}` : '';
        message.textContent = `${event.stage.replaceAll('_', ' ')}${source}`;
        if (event.stage === 'SOURCE_OPENED') fill.style.width = '45%';
        if (event.stage === 'VALIDATING_PROJECT') fill.style.width = '65%';
        if (event.stage === 'COMPLETE') {
          fill.style.width = '100%';
          UI.renderDashboard(await API.dashboard());
          button.disabled = false;
        }
        if (event.stage === 'FAILED') {
          fill.style.width = '100%';
          UI.renderError(new AppError({
            what_went_wrong: 'The project update failed.',
            next_action: 'Open support details. Your previous trusted dashboard was not replaced.',
            support_code: 'RUN_FAILED',
          }));
          button.disabled = false;
        }
      });
      stream.start();
    } catch (error) {
      UI.renderError(
        error instanceof AppError ? error : new AppError({}));
      button.disabled = !isReady();
    }
  });
}

async function boot() {
  wireOperations();
  try {
    await API.health();
    state.projects = await API.projects();
    const select = document.getElementById('project-select');
    state.projects.forEach((project) => {
      const option = document.createElement('option');
      option.value = project.project_id;
      option.textContent = `${project.project_id}${project.demo ? ' · DEMO' : ''}`;
      select.append(option);
    });
    if (state.projects.length === 1) {
      select.value = state.projects[0].project_id;
      await selectProject(select.value);
    }
    try {
      UI.renderDashboard(await API.dashboard());
    } catch (error) {
      if (!(error instanceof AppError) || error.status !== 404) throw error;
    }
  } catch (error) {
    UI.renderError(error instanceof AppError ? error : new AppError({}));
  }
}

document.addEventListener('DOMContentLoaded', boot);
export { API, AppError, ProgressStream, UI, globMatches };
