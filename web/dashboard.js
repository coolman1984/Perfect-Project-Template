/**
 * One-page chart rendering (Constitution Parts 26.2, 26.10).
 *
 * NO TRUSTED MATHS HERE. Values arrive from the local API already calculated
 * and already rounded. This module selects a chart type, binds pre-aggregated
 * series, and renders. Adding a sum, rate or ratio here is a rule 6 violation
 * that the dashboard-vs-SQL equality test is designed to catch.
 *
 * Chart selection follows the Part 26.2 map. Forbidden: 3D charts, multi-slice
 * pies, decorative gradients, and any chart without a decision question as its
 * title (Part 11.4).
 *
 * ECharts is loaded from web/vendor/ as a pinned local asset. A CDN reference
 * fails architecture verification (Part 23.8).
 *
 * Accessibility: every chart needs a text alternative and an accessible summary
 * that carries the same meaning as the picture (Part 22.9).
 */

export function renderChart(containerId, chartSpec) {
  throw new Error(
    'Not implemented. Bind chartSpec.series to a locally bundled ECharts ' +
    'instance, set the accessible summary, and animate between old and new ' +
    'states so the user can follow the change (Part 22.11).'
  );
}

export function disposeChart(containerId) {
  throw new Error('Not implemented. Dispose instances on filter reset to avoid leaks.');
}
