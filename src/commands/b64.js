import { parseArgs, UsageError } from '../args.js';
import { green, gray } from '../colors.js';

export const meta = {
  name: 'b64',
  summary: 'Base64 encode or decode text, files, or stdin',
  usage: 'devkit b64 [text] [--decode] [--url-safe] [--file <path>]',
  examples: [
    'devkit b64 "hello"',
    'devkit b64 "aGVsbG8=" --decode',
    'cat img.png | devkit b64 --url-safe',
  ],
};

export function encode(text, { urlSafe = false } = {}) {
  const out = Buffer.from(text, 'utf8').toString('base64');
  return urlSafe ? out.replaceAll('+', '-').replaceAll('/', '_').replace(/=+$/, '') : out;
}

export function decode(text, { urlSafe = false } = {}) {
  let normalized = text.trim();
  if (urlSafe) normalized = normalized.replaceAll('-', '+').replaceAll('_', '/');
  // Restore padding so Buffer's decoder accepts stripped input.
  while (normalized.length % 4 !== 0) normalized += '=';
  return Buffer.from(normalized, 'base64').toString('utf8');
}

async function readInput(flags, positional) {
  if (positional.length > 0) return { text: positional.join(' '), source: 'argument' };
  if (flags.file) {
    const { readFile } = await import('node:fs/promises');
    return { text: await readFile(String(flags.file), 'utf8'), source: flags.file };
  }
  if (!process.stdin.isTTY) {
    const chunks = [];
    for await (const chunk of process.stdin) chunks.push(chunk);
    return { text: Buffer.concat(chunks).toString('utf8').replace(/\n$/, ''), source: 'stdin' };
  }
  throw new UsageError('no input', 'pass text, use --file, or pipe something in');
}

export async function run(argv) {
  const { flags, positional } = parseArgs(argv, {
    boolean: ['decode', 'url-safe', 'quiet'],
  });

  const { text, source } = await readInput(flags, positional);
  const urlSafe = Boolean(flags['url-safe']);

  const result = flags.decode ? decode(text, { urlSafe }) : encode(text, { urlSafe });

  if (flags.quiet) {
    console.log(result);
    return 0;
  }

  console.log(green(result));
  console.log(gray(`  ${flags.decode ? 'decoded' : 'encoded'} from ${source}`));
  return 0;
}
