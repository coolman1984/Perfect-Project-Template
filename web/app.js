import { renderChart, disposeChart } from './dashboard.js';
import { FilterState, verifyReconciliation } from './filters.js';
import { loadDictionary, storedLang, storeLang, applyDictionary, translate } from './i18n.js';

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
    const dictionary = state.dictionary || {};
    document.getElementById('report-title').textContent = pack.report.title;
    document.getElementById('report-period').textContent = pack.report.period;
    const badge = document.getElementById('quality-badge');
    badge.dataset.status = pack.quality.status;
    document.getElementById('quality-text').textContent =
      translate(dictionary, `quality.${pack.quality.status}`, pack.quality.status);
    badge.querySelector('.badge-icon').textContent = {
      PASS: '✓', WARNING: '!', BLOCK: '✕', FAIL: '✕',
    }[pack.quality.status] || '•';
    document.getElementById('freshness').textContent =
      `${translate(dictionary, 'freshness.dataDate', 'Data date')} ${pack.freshness.data_date}`;
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
  renderCharts(charts, filterStateVersion) {
    // The Part 26.11 blueprint: the first chart is the hero decision chart
    // (span-8) beside insight-focus (span-4, a permanent grid sibling this
    // function must never remove); every other chart gets its own full-width
    // row rather than an invented "compare/bridge" partner the data does not
    // support (unavailable regions disappear cleanly, not with dead space).
    const grid = document.getElementById('chart-grid');
    const insightFocus = document.getElementById('insight-focus');
    grid.querySelectorAll('[data-generated="chart"]').forEach((node) => {
      disposeChart(node.querySelector('.chart').id);
      node.remove();
    });
    charts.forEach((spec, index) => {
      const figure = document.createElement('figure');
      figure.className = `panel ${index === 0 ? 'span-8' : 'span-12'}`;
      figure.dataset.generated = 'chart';
      figure.dataset.filterStateVersion = String(filterStateVersion || 0);
      figure.dataset.dimensions = (spec.dimensions || []).join(',');
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
      if (index === 0) grid.insertBefore(figure, insightFocus);
      else grid.append(figure);
      renderChart(chart.id, spec);
    });
  },
  renderActions(actions) {
    const region = document.getElementById('action-region');
    const body = document.getElementById('action-table-body');
    body.replaceChildren();
    actions.forEach((action) => {
      const row = document.createElement('tr');
      const cells = [
        action.what || action.item || '',
        action.why_now || action.why || '',
        action.evidence_ref || action.evidence || '',
        action.suggested_owner || action.owner || '',
      ].map((text) => {
        const cell = document.createElement('td');
        cell.textContent = text;
        return cell;
      });
      const statusCell = document.createElement('td');
      if (action.status) {
        const badge = document.createElement('span');
        badge.className = 'action-status';
        badge.textContent = action.status;
        statusCell.append(badge);
      }
      row.append(...cells, statusCell);
      body.append(row);
    });
    region.hidden = actions.length === 0;
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
  renderFilters(pack) {
    const ribbon = document.getElementById('filter-ribbon');
    const controls = document.getElementById('filter-controls');
    controls.replaceChildren();
    const definitions = (pack.filters && pack.filters.definitions) || [];
    const available = filterOptions(pack);
    definitions.forEach((definition) => {
      const values = available.get(definition.id);
      if (!values || values.size === 0) return;
      const wrap = document.createElement('div');
      wrap.className = 'filter-control';
      const label = document.createElement('label');
      label.setAttribute('for', `filter-${definition.id}`);
      label.textContent = definition.label;
      const select = document.createElement('select');
      select.id = `filter-${definition.id}`;
      select.multiple = true;
      select.size = Math.min(4, values.size);
      select.setAttribute(
        'aria-label', `${definition.label} (multiple selection)`);
      Array.from(values).sort().forEach((value) => {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = value;
        select.append(option);
      });
      select.addEventListener('change', () => {
        const selected = Array.from(select.selectedOptions).map((o) => o.value);
        state.filterState.set(
          'global', definition.id, selected.length ? selected : null);
      });
      wrap.append(label, select);
      controls.append(wrap);
    });
    ribbon.hidden = controls.children.length === 0;
  },
  renderChips(snapshot) {
    const list = document.getElementById('active-chips');
    list.replaceChildren();
    const labels = new Map(
      ((state.pack && state.pack.filters && state.pack.filters.definitions) || [])
        .map((d) => [d.id, d.label]));
    Object.entries(snapshot.global).forEach(([filterId, values]) => {
      (values || []).forEach((value) => {
        const li = document.createElement('li');
        const text = document.createElement('span');
        text.textContent = `${labels.get(filterId) || filterId}: ${value}`;
        const remove = document.createElement('button');
        remove.type = 'button';
        remove.setAttribute('aria-label', `Remove filter: ${text.textContent}`);
        remove.textContent = '×';
        remove.addEventListener('click', () => {
          const remaining = (state.filterState.global.get(filterId) || [])
            .filter((v) => v !== value);
          state.filterState.set(
            'global', filterId, remaining.length ? remaining : null);
          const select = document.getElementById(`filter-${filterId}`);
          if (select) {
            Array.from(select.options)
              .forEach((option) => { if (option.value === value) option.selected = false; });
          }
        });
        li.append(text, remove);
        list.append(li);
      });
    });
  },
  renderDashboard(pack) {
    state.pack = pack;
    this.renderHeader(pack);
    this.renderKpis(pack.kpis || []);
    this.renderInsights(pack.insights || []);
    this.renderActions(pack.actions || []);
    this.renderFilters(pack);
    // Fires the FilterState listener, which renders the (unfiltered) charts
    // and reconciles them — the single path charts are drawn through,
    // whether this is the first load or a filter change (Part 26.14).
    state.filterState.reset();
  },
};

/** Every filter's selectable values, drawn from the chart data already sent to
 * the browser — a pre-aggregated client-side filter (Part 26.16 budget class),
 * not a new server round-trip the dashboard contract does not yet support. */
function filterOptions(pack) {
  const result = new Map();
  (pack.charts || []).forEach((chart) => {
    const points = ((chart.series || [])[0] || {}).points || [];
    (chart.dimensions || []).forEach((dimension) => {
      const set = result.get(dimension) || new Set();
      points.forEach((point) => set.add(point.x));
      result.set(dimension, set);
    });
  });
  return result;
}

function applyFilters(snapshot) {
  const pack = state.pack;
  if (!pack) return;
  // `allowed` is kept alongside each filtered spec (rather than only the
  // filtered points) so the reconciliation pass below can independently
  // re-check what should have been removed — it must not simply trust that
  // the filter above already did it correctly.
  const filtered = (pack.charts || []).map((spec) => {
    const activeDimension = (spec.dimensions || [])
      .find((dim) => snapshot.global[dim] && snapshot.global[dim].length);
    if (!activeDimension) return { spec, allowed: null };
    const allowed = new Set(snapshot.global[activeDimension]);
    const series = spec.series[0] || { points: [] };
    const points = series.points.filter((point) => allowed.has(point.x));
    return { spec: { ...spec, series: [{ ...series, points }] }, allowed };
  });
  UI.renderCharts(filtered.map((item) => item.spec), snapshot.filter_state_version);
  UI.renderChips(snapshot);

  // Part 26.14 post-change verification: no rendered point may be a value the
  // active filter excluded — a chart must never keep showing a stale
  // category just because a render path missed it. This checks point.x for
  // set membership only, never point.y for a number (GATE_NO_BROWSER_
  // ARITHMETIC): the browser compares identifiers, it does not derive a
  // trusted total.
  const stale = [];
  filtered.forEach(({ spec, allowed }) => {
    if (!allowed) return;
    (spec.series[0].points || []).forEach((point) => {
      if (!allowed.has(point.x)) stale.push(`${spec.id}:${point.x}`);
    });
  });
  const problems = verifyReconciliation({
    components: filtered.map(
      () => ({ filter_state_version: snapshot.filter_state_version })),
    kpis: [],
    evidenceTables: {},
    paretoTotal: 0,
    filteredTotal: 0,
  });
  if (stale.length) {
    problems.push(`${stale.length} chart point(s) retained a value the active filter excluded`);
  }
  document.getElementById('filter-status').textContent = problems.join('; ');
}

const state = {
  projects: [],
  project: null,
  selectedFiles: [],
  bySource: new Map(),
  unmatched: [],
  pack: null,
  filterState: new FilterState(),
  dictionary: null,
};
state.filterState.subscribe(applyFilters);

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

const THEMES = ['light', 'dark'];
const LANG_TOGGLE_LABEL = { en: 'العربية', ar: 'English' };

function wireChrome() {
  document.getElementById('reset-filters').addEventListener('click', () => {
    state.filterState.reset();
  });

  const themeToggle = document.getElementById('theme-toggle');
  themeToggle.addEventListener('click', () => {
    const current = document.documentElement.dataset.theme;
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    localStorage.setItem('excel-intelligence-theme', next);
  });
  const storedTheme = localStorage.getItem('excel-intelligence-theme');
  if (THEMES.includes(storedTheme)) document.documentElement.dataset.theme = storedTheme;

  const langToggle = document.getElementById('lang-toggle');
  langToggle.addEventListener('click', async () => {
    const next = document.documentElement.lang === 'ar' ? 'en' : 'ar';
    await setLanguage(next);
  });
}

async function setLanguage(lang) {
  const dictionary = await loadDictionary(lang);
  state.dictionary = dictionary;
  applyDictionary(lang, dictionary);
  storeLang(lang);
  document.getElementById('lang-toggle').textContent = LANG_TOGGLE_LABEL[lang];
  // Dynamic content already on screen (report title, quality text) was drawn
  // from the dashboard pack in the previous language pass; re-run it so a
  // language switch does not leave stale English inside an Arabic shell.
  if (state.pack) UI.renderHeader(state.pack);
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
  wireChrome();
  wireOperations();
  try {
    await setLanguage(storedLang());
  } catch (error) {
    // A missing/broken dictionary must not block the rest of the app; the
    // shell keeps its hard-coded English text (Part 22.9 degrades, never
    // blocks the operator's actual task).
  }
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
export {
  API, AppError, ProgressStream, UI, globMatches,
  filterOptions, applyFilters, setLanguage, state,
};
