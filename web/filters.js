/**
 * One typed filter state for the whole page (Constitution Parts 22.6, 26.14).
 *
 * "All filters are applied through one typed filter-state object. No component
 * keeps a private contradictory copy." Every visual reads from here and every
 * change bumps filter_state_version, so a stale component is detectable rather
 * than silently wrong.
 *
 * Three filter scopes must stay distinguishable (Part 22.6):
 *   global      affects every compatible visual
 *   section     affects one clearly bounded analysis region
 *   cross       created by selecting a chart mark; shows a removable chip
 *
 * Comparison state defines the baseline. It never hides current values.
 *
 * The operator may change the VIEW — comparison, filter, approved scenario.
 * They may never change trusted source records or metric formulas. A data
 * correction uses a corrected source file, an approved configuration change,
 * or a governed exception workflow with audit history. Never add
 * spreadsheet-like silent editing to trusted data (Part 22.6).
 */

export class FilterState {
  constructor() {
    this.version = 0;
    this.global = new Map();
    this.section = new Map();
    this.cross = new Map();
    this.comparison = 'previous';
    this.listeners = new Set();
  }

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  set(scope, key, value) {
    const target = this[scope];
    if (!target) throw new Error(`unknown filter scope: ${scope}`);
    if (value === null || value === undefined) target.delete(key);
    else target.set(key, value);
    this.commit();
  }

  setComparison(mode) {
    this.comparison = mode;
    this.commit();
  }

  /** Return to the AUTHORED approved default, not to an empty state. */
  reset(defaults = {}) {
    this.global = new Map(Object.entries(defaults.global || {}));
    this.section.clear();
    this.cross.clear();
    this.comparison = defaults.comparison || 'previous';
    this.commit();
  }

  commit() {
    this.version += 1;
    const snapshot = this.snapshot();
    this.listeners.forEach((listener) => listener(snapshot));
  }

  snapshot() {
    return {
      filter_state_version: this.version,
      global: Object.fromEntries(this.global),
      section: Object.fromEntries(this.section),
      cross: Object.fromEntries(this.cross),
      comparison: this.comparison,
    };
  }

  /**
   * Only approved dimension keys and periods may persist to the URL or local
   * storage — never a raw row value or a secret (Part 22.2). Clear invalid
   * stored values after a schema or version change (Part 26.14).
   */
  toUrlParams(approvedKeys) {
    const params = new URLSearchParams();
    for (const [key, value] of this.global) {
      if (approvedKeys.includes(key)) params.set(key, String(value));
    }
    params.set('compare', this.comparison);
    return params;
  }
}

/**
 * Part 26.14 post-change verification. Run after every filter or comparison
 * change; a failure means a component is showing stale or unreconciled data.
 */
export function verifyReconciliation({ components, kpis, evidenceTables, paretoTotal, filteredTotal }) {
  const problems = [];
  const stale = components.filter((c) => c.filter_state_version !== components[0].filter_state_version);
  if (stale.length) problems.push(`components on a stale filter version: ${stale.length}`);
  if (paretoTotal !== filteredTotal) problems.push('Pareto bars do not reconcile to the filtered total');
  kpis.forEach((kpi) => {
    const evidence = evidenceTables[kpi.id];
    if (evidence && evidence.total !== kpi.value) {
      problems.push(`KPI ${kpi.id} does not match its evidence table`);
    }
  });
  return problems;
}
