/**
 * Reduced-motion-safe transitions (Constitution Part 22.11).
 *
 * Animate only state change, hierarchy, and cause/effect:
 *   - 160-240ms UI transitions, 250-450ms chart transitions
 *   - stage the first dashboard reveal ONCE, in reading order, within 700ms
 *   - on filter change, MORPH existing marks; do not replay entrance effects
 *   - never bounce, spin, flash, pulse continuously, or animate backgrounds
 *   - stop all non-essential motion under prefers-reduced-motion: reduce
 *   - keep progress animation tied to durable events — NEVER fake activity
 *   - maintain 60fps on the target PC; avoid layout shifts
 *
 * Never animate axes in a way that disguises a scale change (Part 26.13).
 */

export const prefersReducedMotion = () =>
  window.matchMedia('(prefers-reduced-motion: reduce)').matches;

export function transition(element, changes, durationMs = 180) {
  if (prefersReducedMotion()) {
    Object.assign(element.style, changes);
    return Promise.resolve();
  }
  throw new Error('Not implemented. Use opacity and transform where possible.');
}
