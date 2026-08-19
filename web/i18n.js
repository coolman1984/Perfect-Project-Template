/**
 * Local UI translation (Constitution Part 22.9).
 *
 * Arabic and English share one data contract; only the dictionaries here
 * differ. Switching language sets BOTH `lang` and `dir` on the document root —
 * mirroring text with `direction: rtl` alone is not translation, and the
 * standalone report's `dir="auto"` is not available here because the local
 * app has interactive controls whose layout must actually flip.
 */

const SUPPORTED = ['en', 'ar'];
const STORAGE_KEY = 'excel-intelligence-lang';
const cache = new Map();

export async function loadDictionary(lang) {
  if (cache.has(lang)) return cache.get(lang);
  const response = await fetch(`i18n/${lang}.json`);
  if (!response.ok) throw new Error(`missing i18n dictionary: ${lang}`);
  const dictionary = await response.json();
  cache.set(lang, dictionary);
  return dictionary;
}

export function storedLang() {
  const stored = localStorage.getItem(STORAGE_KEY);
  return SUPPORTED.includes(stored) ? stored : 'en';
}

export function storeLang(lang) {
  localStorage.setItem(STORAGE_KEY, lang);
}

/** Apply a dictionary to every `[data-i18n]` node and set document direction. */
export function applyDictionary(lang, dictionary) {
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
  document.querySelectorAll('[data-i18n]').forEach((node) => {
    const key = node.getAttribute('data-i18n');
    const text = dictionary[key];
    if (text === undefined) return;
    if (node.hasAttribute('data-i18n-attr')) {
      node.setAttribute(node.getAttribute('data-i18n-attr'), text);
    } else {
      node.textContent = text;
    }
  });
}

export function translate(dictionary, key, fallback = key) {
  return dictionary[key] !== undefined ? dictionary[key] : fallback;
}

export { SUPPORTED };
