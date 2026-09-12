import { parseArgs } from '../args.js';
import { blue, gray, cyan } from '../colors.js';

export const meta = {
  name: 'ts',
  summary: 'Convert between Unix timestamps and ISO dates',
  usage: 'devkit ts [value] [--ms] [--from-unix] [--to-ms]',
  examples: [
    'devkit ts',
    'devkit ts 1735689600',
    'devkit ts 2026-01-01T00:00:00Z',
    'devkit ts 1735689600000 --ms',
  ],
};

/**
 * Format a Date into the handful of representations a developer usually needs
 * when eyeballing a log line or an API payload.
 */
export function describe(date) {
  const ms = date.getTime();
  return {
    iso: date.toISOString(),
    unix: Math.floor(ms / 1000),
    ms,
    utc: date.toUTCString(),
    local: date.toLocaleString(),
  };
}

/**
 * Decide whether a raw string is a unix timestamp or a date string.
 * Heuristic: all digits, and shorter than 8 chars is almost certainly not a
 * timestamp; 10 digits = seconds, 13 digits = milliseconds.
 */
export function interpret(input, { assumeMs = false } = {}) {
  const trimmed = String(input).trim();

  if (/^-?\d+$/.test(trimmed)) {
    const num = Number(trimmed);
    const isMs = assumeMs || trimmed.replace('-', '').length >= 12;
    return new Date(isMs ? num : num * 1000);
  }

  const parsed = new Date(trimmed);
  if (Number.isNaN(parsed.getTime())) return null;
  return parsed;
}

function print(date) {
  const info = describe(date);
  console.log(`${blue('ISO')}   ${info.iso}`);
  console.log(`${blue('Unix')}  ${cyan(info.unix)}`);
  console.log(`${blue('ms')}    ${info.ms}`);
  console.log(`${blue('UTC')}   ${info.utc}`);
  console.log(`${blue('Local')} ${info.local}`);
}

export async function run(argv) {
  const { flags, positional } = parseArgs(argv, {
    boolean: ['ms', 'quiet'],
  });

  if (positional.length === 0) {
    const now = new Date();
    console.error(gray('now'));
    print(now);
    return 0;
  }

  const date = interpret(positional[0], { assumeMs: Boolean(flags.ms) });
  if (!date) {
    const { UsageError } = await import('../args.js');
    throw new UsageError(`could not parse date "${positional[0]}"`);
  }

  print(date);

  if (flags['to-ms']) {
    console.log(gray(`  input treated as milliseconds`));
  }

  return 0;
}
