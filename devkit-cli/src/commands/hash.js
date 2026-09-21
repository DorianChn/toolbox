import { createHash } from 'node:crypto';
import { createReadStream } from 'node:fs';
import { parseArgs, UsageError } from '../args.js';
import { gray, green, bold } from '../colors.js';

export const meta = {
  name: 'hash',
  summary: 'Compute a checksum of text, a file, or stdin',
  usage: 'devkit hash [text] [--algo sha256|md5|sha1|sha512] [--file <path>]',
  examples: [
    'devkit hash "hello world"',
    'devkit hash --file ./dist/app.js',
    'echo -n "abc" | devkit hash',
  ],
};

const ALGOS = ['sha256', 'sha1', 'sha512', 'md5'];

/**
 * Hash a stream without buffering the whole thing into memory.
 *
 * `end` and `close` can both fire, and `digest()` may only be called once, so
 * the result is memoized behind a settled guard.
 */
export function hashStream(stream, algo = 'sha256') {
  return new Promise((resolve, reject) => {
    const digest = createHash(algo);
    let settled = false;
    let ended = false;

    const finish = () => {
      if (settled) return;
      settled = true;
      resolve(digest.digest('hex'));
    };

    const fail = (error) => {
      if (settled) return;
      settled = true;
      reject(error);
    };

    stream.on('error', fail);
    digest.on('error', fail);
    stream.on('data', (chunk) => digest.update(chunk));
    stream.on('end', () => {
      ended = true;
      finish();
    });
    stream.on('close', () => {
      if (!ended) fail(new Error('input stream closed before end'));
    });
  });
}

export function hashText(text, algo = 'sha256') {
  return createHash(algo).update(text, 'utf8').digest('hex');
}

async function readStdin() {
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  return Buffer.concat(chunks);
}

export async function run(argv) {
  const { flags, positional } = parseArgs(argv, { boolean: ['quiet'] });
  const algo = String(flags.algo ?? 'sha256').toLowerCase();

  if (!ALGOS.includes(algo)) {
    throw new UsageError(
      `unsupported algorithm "${algo}"`,
      `choose one of: ${ALGOS.join(', ')}`,
    );
  }

  let digest;

  if (flags.file) {
    digest = await hashStream(createReadStream(String(flags.file)), algo);
  } else if (positional.length > 0) {
    digest = hashText(positional.join(' '), algo);
  } else if (!process.stdin.isTTY) {
    const buffer = await readStdin();
    digest = hashText(buffer.toString('utf8').replace(/\n$/, ''), algo);
  } else {
    throw new UsageError(
      'nothing to hash',
      'pass text, use --file, or pipe something in',
    );
  }

  if (flags.quiet) {
    console.log(digest);
  } else {
    console.log(`${bold(algo)}  ${green(digest)}`);
    if (flags.file) console.log(gray(`  from ${flags.file}`));
  }

  return 0;
}
