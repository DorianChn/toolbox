/**
 * Minimal argument parser.
 *
 * Supports the subset devkit actually needs:
 *   --flag            boolean true
 *   --no-flag         boolean false
 *   --key=value       string
 *   --key value       string
 *   -k value          short alias (only when a command declares it)
 *   positional...     collected into `_`
 *
 * Deliberately not a general-purpose parser; keeping it small means the whole
 * project stays dependency-free.
 */

function isNegativeNumber(token) {
  return /^-\d+(?:\.\d+)?$/.test(token);
}

/**
 * @param {string[]} argv
 * @param {{ boolean?: string[], alias?: Record<string, string> }} [options]
 */
export function parseArgs(argv, options = {}) {
  const booleanKeys = new Set(options.boolean ?? []);
  const alias = options.alias ?? {};

  const flags = {};
  const positional = [];

  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];

    if (token === '--') {
      positional.push(...argv.slice(i + 1));
      break;
    }

    if (token.startsWith('--')) {
      const body = token.slice(2);
      const eq = body.indexOf('=');

      if (eq !== -1) {
        flags[body.slice(0, eq)] = body.slice(eq + 1);
        continue;
      }

      if (body.startsWith('no-')) {
        flags[body.slice(3)] = false;
        continue;
      }

      if (booleanKeys.has(body)) {
        flags[body] = true;
        continue;
      }

      const next = argv[i + 1];
      if (next !== undefined && (!next.startsWith('-') || isNegativeNumber(next))) {
        flags[body] = next;
        i += 1;
      } else {
        flags[body] = true;
      }
      continue;
    }

    if (token.startsWith('-') && token.length > 1) {
      const short = token.slice(1);
      const long = alias[short] ?? short;

      if (booleanKeys.has(long)) {
        flags[long] = true;
        continue;
      }

      const next = argv[i + 1];
      if (next !== undefined && (!next.startsWith('-') || isNegativeNumber(next))) {
        flags[long] = next;
        i += 1;
      } else {
        flags[long] = true;
      }
      continue;
    }

    positional.push(token);
  }

  return { flags, positional, _: positional };
}

/**
 * Thrown for bad user input. The entry point formats these differently from
 * unexpected crashes.
 */
export class UsageError extends Error {
  constructor(message, hint) {
    super(message);
    this.name = 'UsageError';
    this.hint = hint;
  }
}

/**
 * Read a numeric flag with a default.
 */
export function readInt(flags, key, fallback) {
  const raw = flags[key];
  if (raw === undefined || raw === true) return fallback;
  const value = Number.parseInt(String(raw), 10);
  if (Number.isNaN(value)) {
    throw new UsageError(`--${key} expects a number, got "${raw}"`);
  }
  return value;
}
