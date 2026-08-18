/** Reusable presentation-only chart renderer. Business maths never lives here. */
const instances = new Map();

function pointsOf(spec) {
  const series = (spec.series && spec.series[0]) || { points: [] };
  return series.points || [];
}

function fallback(container, spec) {
  container.replaceChildren();
  container.dataset.renderer = 'accessible-fallback';
  const table = document.createElement('table');
  table.className = 'chart-fallback-table';
  const caption = document.createElement('caption');
  caption.textContent = spec.accessible_summary || spec.title || 'Chart data';
  const body = document.createElement('tbody');
  pointsOf(spec).forEach((point) => {
    const row = document.createElement('tr');
    const label = document.createElement('th');
    label.scope = 'row'; label.textContent = point.x;
    const value = document.createElement('td');
    value.textContent = point.y === null ? '—' : `${point.y}${spec.unit ? ` ${spec.unit}` : ''}`;
    row.append(label, value); body.append(row);
  });
  table.append(caption, body); container.append(table);
}

export function renderChart(containerId, chartSpec) {
  const container = document.getElementById(containerId);
  if (!container) return;
  disposeChart(containerId);
  container.setAttribute('aria-label', chartSpec.accessible_summary || chartSpec.title || 'Chart');
  if (!window.echarts) {
    // Development/diagnostic fallback only. Release verification requires the
    // pinned local web/vendor/echarts.min.js asset and must fail closed if absent.
    fallback(container, chartSpec); return;
  }
  container.dataset.renderer = 'echarts';
  const chart = window.echarts.init(container);
  const points = pointsOf(chartSpec);
  const categories = points.map((point) => point.x);
  const values = points.map((point) => point.y);
  const isLine = chartSpec.type === 'line';
  const series = [{ name: (chartSpec.series[0] || {}).name || chartSpec.title, type: isLine ? 'line' : 'bar', data: values, emphasis: { focus: 'series' } }];
  if (chartSpec.type === 'pareto' && points.some((point) => point.cumulative_pct !== undefined)) {
    series.push({ name: 'Cumulative %', type: 'line', yAxisIndex: 1, data: points.map((point) => point.cumulative_pct) });
  }
  chart.setOption({
    animationDuration: 250,
    tooltip: { trigger: 'axis' },
    legend: { show: series.length > 1 },
    grid: { left: 54, right: series.length > 1 ? 56 : 24, top: 28, bottom: 46, containLabel: true },
    xAxis: { type: 'category', data: categories, axisLabel: { hideOverlap: true } },
    yAxis: series.length > 1 ? [{ type: 'value', name: chartSpec.unit || '' }, { type: 'value', name: '%', min: 0, max: 100 }] : { type: 'value', name: chartSpec.unit || '' },
    series,
  });
  instances.set(containerId, chart);
}

export function disposeChart(containerId) {
  const chart = instances.get(containerId);
  if (chart) { chart.dispose(); instances.delete(containerId); }
}
