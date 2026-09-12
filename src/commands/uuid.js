import { randomUUID, randomBytes } from 'node:crypto';
import { parseArgs, readInt } from '../args.js';
import { cyan, gray } from '../colors.js';

export const meta = {
  name: 'uuid',
  summary: 'Generate one or more UUID v4 values',
  usage: 'devkit uuid [--count 5] [--upper] [--no-dashes]',
  examples: ['devkit uuid', 'devkit uuid -n 3', 'devkit uuid -n 10 --upper'],
};

/** Generate `count` UUIDs. Pure function, easy to test. */
export function generate(count, { upper = false, dashes = true } = {}) {
  const out = [];
  for (let i = 0; i < count; i += 1) {
    let id = randomUUID();
    if (!dashes) id = id.replaceAll('-', '');
    if (upper) id = id.toUpperCase();
    out.push(id);
  }
  return out;
}

export async function run(argv) {
  const { flags } = parseArgs(argv, {
    alias: { n: 'count' },
  });

  const count = readInt(flags, 'count', 1);
  if (count < 1 || count > 10000) {
    throw new (await import('../args.js')).UsageError('--count must be between 1 and 10000');
  }

  const ids = generate(count, {
    upper: Boolean(flags.upper),
    dashes: flags.dashes !== false && flags['no-dashes'] !== true,
  });

  for (const id of ids) console.log(cyan(id));

  if (count > 1) console.log(gray(`  ${count} ids generated`));
  // randomBytes is imported to keep the crypto surface explicit in one place.
  void randomBytes;
  return 0;
}
