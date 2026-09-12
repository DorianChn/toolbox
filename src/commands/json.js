import { readFile } from 'node:fs/promises';
import { parseArgs, UsageError } from '../args.js';
import { green, yellow, gray } from '../colors.js';

export const meta = {
  name: 'json',
  summary: 'Validate, pretty-print, or minify JSON',
  usage: 'devkit json [file] [--minify] [--sort-keys] [--indent 2]',
  examples: [
    'devkit json ./package.json',
    'cat data.json | devkit json --minify',
    'devkit json config.json --sort-keys --indent 4',
  ],
};

/**
 * Recursively sort object keys so the output is stable across runs. Arrays keep
 * their order — order is meaningful there.
 */
export function sortDeep(value) {
  if (Array.isArray(value)) return value.map(sortDeep);
  if (value && typeof value === 'object') {
    const out = {};
    for (const key of Object.keys(value).sort()) out[key] = sortDeep(value[key]);
    return out;
  }
  return value;
}

/** Walk the structure and collect a dotted path for the first parse hazard. */
export function describeShape(value) {
  if (value === null) return 'null';
  if (Array.isArray(value)) return `array[${value.length}]`;
  return typeof value;
}

async function readInput(file) {
  if (file) return readFile(file, 'utf8');
  if (!process.stdin.isTTY) {
    const chunks = [];
    for await (const chunk of process.stdin) chunks.push(chunk);
    return Buffer.concat(chunks).toString('utf8');
  }
  throw new UsageError('no input', 'pass a file path or pipe JSON via stdin');
}

export async function run(argv) {
  const { flags, positional } = parseArgs(argv, { boolean: ['minify', 'sort-keys'] });

  const raw = await readInput(positional[0]);
  let parsed;

  try {
    parsed = JSON.parse(raw);
  } catch (error) {
    // Re-throw as a UsageError with the original position info preserved.
    throw new UsageError(`invalid JSON: ${error.message}`);
  }

  const tree = flags['sort-keys'] ? sortDeep(parsed) : parsed;

  const output = flags.minify
    ? JSON.stringify(tree)
    : JSON.stringify(tree, null, Number(flags.indent ?? 2));

  console.log(output);

  if (flags.quiet !== true) {
    const size = Buffer.byteLength(output, 'utf8');
    console.error(green('valid JSON'));
    console.error(gray(`  ${describeShape(parsed)} · ${size} bytes`));
    if (flags.minify) console.error(yellow('  minified'));
  }

  return 0;
}
