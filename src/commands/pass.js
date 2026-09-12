import { randomInt, randomBytes } from 'node:crypto';
import { parseArgs, readInt, UsageError } from '../args.js';
import { yellow, gray, bold } from '../colors.js';

export const meta = {
  name: 'pass',
  summary: 'Generate a strong random password',
  usage: 'devkit pass [--length 20] [--symbols] [--count 3] [--pin]',
  examples: [
    'devkit pass',
    'devkit pass --length 32 --symbols',
    'devkit pass --pin --length 6',
  ],
};

const LOWER = 'abcdefghijkmnopqrstuvwxyz'; // no l
const UPPER = 'ABCDEFGHJKLMNPQRSTUVWXYZ'; // no I, O
const DIGITS = '23456789'; // no 0, 1
const SYMBOLS = '!@#$%^&*()-_=+[]{};:,.?';

/**
 * Build a password from an explicit alphabet. Ambiguous characters (l/1/I/O/0)
 * are excluded by default so passwords survive being read aloud or retyped.
 */
export function generatePassword(length = 20, { symbols = false } = {}) {
  const alphabet = LOWER + UPPER + DIGITS + (symbols ? SYMBOLS : '');
  let out = '';

  // Rejection sampling keeps the distribution uniform; modulo bias is real but
  // tiny here, and this loop is cheap.
  while (out.length < length) {
    const byte = randomBytes(1)[0];
    const limit = 256 - (256 % alphabet.length);
    if (byte >= limit) continue;
    out += alphabet[byte % alphabet.length];
  }

  return out;
}

export function generatePin(length = 6) {
  let out = '';
  for (let i = 0; i < length; i += 1) out += randomInt(0, 10).toString();
  return out;
}

/** Rough entropy estimate in bits, based on alphabet size * length. */
export function entropyBits(alphabetSize, length) {
  return Math.round(length * Math.log2(alphabetSize));
}

/**
 * Size of the alphabet actually used.
 *
 * Derived from the constants rather than hardcoded, so adding or removing a
 * character can never leave the entropy estimate quietly lying.
 */
export function alphabetSize({ symbols = false } = {}) {
  return (LOWER + UPPER + DIGITS + (symbols ? SYMBOLS : '')).length;
}

export async function run(argv) {
  const { flags } = parseArgs(argv, { alias: { n: 'count', l: 'length' } });

  const length = readInt(flags, 'length', 20);
  const count = readInt(flags, 'count', 1);

  if (length < 4) throw new UsageError('--length must be at least 4');
  if (count < 1 || count > 100) {
    throw new UsageError('--count must be between 1 and 100');
  }

  const symbols = Boolean(flags.symbols);

  for (let i = 0; i < count; i += 1) {
    const value = flags.pin
      ? generatePin(length)
      : generatePassword(length, { symbols });
    process.stdout.write(`${yellow(value)}\n`);
  }

  if (count === 1 && !flags.pin) {
    const bits = entropyBits(alphabetSize({ symbols }), length);
    console.error(gray(`  ${bold(length)} chars · ~${bits} bits of entropy`));
  }

  return 0;
}
