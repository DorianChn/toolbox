import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { Readable } from 'node:stream';

import { hashText, hashStream } from '../src/commands/hash.js';
import { generate } from '../src/commands/uuid.js';
import { sortDeep, describeShape } from '../src/commands/json.js';
import { encode, decode } from '../src/commands/b64.js';
import { generatePassword, generatePin, entropyBits } from '../src/commands/pass.js';
import { interpret, describe } from '../src/commands/ts.js';
import { parseArgs, readInt, UsageError } from '../src/args.js';

test('hashText matches node crypto', () => {
  const expected = createHash('sha256').update('hello', 'utf8').digest('hex');
  assert.equal(hashText('hello'), expected);
});

test('hashText supports alternate algorithms', () => {
  assert.equal(hashText('abc', 'md5'), '900150983cd24fb0d6963f7d28e17f72');
});

test('hashStream hashes a readable stream', async () => {
  const stream = Readable.from(['hello', ' ', 'world']);
  const digest = await hashStream(stream);
  assert.equal(digest, createHash('sha256').update('hello world').digest('hex'));
});

test('generate returns the requested number of unique uuids', () => {
  const ids = generate(50);
  assert.equal(ids.length, 50);
  assert.equal(new Set(ids).size, 50);
  for (const id of ids) {
    assert.match(id, /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/);
  }
});

test('generate honours upper and no-dashes options', () => {
  const [id] = generate(1, { upper: true, dashes: false });
  assert.equal(id.length, 32);
  assert.equal(id, id.toUpperCase());
});

test('sortDeep sorts nested object keys but preserves arrays', () => {
  const input = { b: 1, a: { d: 2, c: [3, { z: 1, y: 2 }] } };
  const output = sortDeep(input);
  assert.deepEqual(Object.keys(output), ['a', 'b']);
  assert.deepEqual(Object.keys(output.a), ['c', 'd']);
  assert.deepEqual(output.a.c[1], { y: 2, z: 1 });
});

test('describeShape reports container kinds', () => {
  assert.equal(describeShape([1, 2, 3]), 'array[3]');
  assert.equal(describeShape(null), 'null');
  assert.equal(describeShape('x'), 'string');
});

test('base64 round-trips utf8 text', () => {
  const original = '你好, devkit 🚀';
  assert.equal(decode(encode(original)), original);
});

test('base64 url-safe output has no padding or unsafe chars', () => {
  const encoded = encode('subjects?_d=1', { urlSafe: true });
  assert.doesNotMatch(encoded, /[+/=]/);
  assert.equal(decode(encoded, { urlSafe: true }), 'subjects?_d=1');
});

test('generatePassword respects length and excludes ambiguous chars', () => {
  const password = generatePassword(40);
  assert.equal(password.length, 40);
  assert.doesNotMatch(password, /[lIO01]/);
});

test('generatePassword excludes symbols unless asked', () => {
  const plain = generatePassword(64);
  const withSymbols = generatePassword(64, { symbols: true });
  assert.doesNotMatch(plain, /[!@#$%^&*]/);
  assert.equal(withSymbols.length, 64);
});

test('generatePin is all digits', () => {
  const pin = generatePin(6);
  assert.equal(pin.length, 6);
  assert.match(pin, /^\d{6}$/);
});

test('entropyBits grows with length', () => {
  assert.ok(entropyBits(60, 32) > entropyBits(60, 16));
});

test('interpret parses seconds and milliseconds timestamps', () => {
  const seconds = interpret('1735689600');
  const millis = interpret('1735689600000');
  assert.equal(seconds.getTime(), millis.getTime());
  assert.equal(seconds.toISOString(), '2025-01-01T00:00:00.000Z');
});

test('interpret parses ISO strings and rejects garbage', () => {
  assert.equal(interpret('2025-01-01T00:00:00Z').getTime(), 1735689600000);
  assert.equal(interpret('not a date'), null);
});

test('describe exposes unix and ms consistently', () => {
  const info = describe(new Date(1735689600000));
  assert.equal(info.unix, 1735689600);
  assert.equal(info.ms, 1735689600000);
});

test('parseArgs handles equals, space, boolean, and negation forms', () => {
  const { flags, positional } = parseArgs(
    ['--length=20', '--symbols', '--no-dashes', 'hello', 'world'],
    { boolean: ['symbols'] },
  );
  assert.equal(flags.length, '20');
  assert.equal(flags.symbols, true);
  assert.equal(flags.dashes, false);
  assert.deepEqual(positional, ['hello', 'world']);
});

test('parseArgs resolves short aliases', () => {
  const { flags } = parseArgs(['-n', '5'], { alias: { n: 'count' } });
  assert.equal(flags.count, '5');
});

test('parseArgs stops flag parsing after --', () => {
  const { positional } = parseArgs(['--', '--not-a-flag']);
  assert.deepEqual(positional, ['--not-a-flag']);
});

test('readInt falls back and throws on bad input', () => {
  assert.equal(readInt({}, 'count', 7), 7);
  assert.equal(readInt({ count: '12' }, 'count', 1), 12);
  assert.throws(() => readInt({ count: 'abc' }, 'count', 1), UsageError);
});
