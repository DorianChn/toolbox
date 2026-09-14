import { parseArgs, UsageError } from '../args.js';
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
    'devkit ts 2025-01-01T00:00:00Z --to-ms',
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
export function interpret(input, { assumeMs = false, fromUnix = false } = {}) {
  const trimmed = String(input).trim();

  if (fromUnix && !/^-?\d+$/.test(trimmed)) return null;

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
    boolean: ['ms', 'from-unix', 'to-ms', 'quiet'],
  });

  if (positional.length === 0) {
    if (flags['from-unix']) {
      throw new UsageError('--from-unix requires a numeric timestamp');
    }
    const now = new Date();
    if (flags['to-ms']) {
      console.log(now.getTime());
      return 0;
    }
    console.error(gray('now'));
    print(now);
    return 0;
  }

  const date = interpret(positional[0], {
    assumeMs: Boolean(flags.ms),
    fromUnix: Boolean(flags['from-unix']),
  });
  if (!date) {
    throw new UsageError(`could not parse date "${positional[0]}"`);
  }

  if (flags['to-ms']) {
    console.log(date.getTime());
    return 0;
  }

  print(date);
  return 0;
}
