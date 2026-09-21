import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import type { Server } from 'node:http';
import type { AddressInfo } from 'node:net';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { after, before, it } from 'node:test';

const dataDir = await mkdtemp(path.join(tmpdir(), 'fullstack-todo-corrupt-test-'));
const dataFile = path.join(dataDir, 'tasks.json');
const original = '{"not": "a task list"}\n';
await writeFile(dataFile, original, 'utf8');
process.env.DATA_FILE = dataFile;

const { createApp } = await import('./app.js');

let server: Server;
let baseUrl: string;

before(async () => {
  server = createApp().listen(0);
  await new Promise<void>((resolve) => server.once('listening', () => resolve()));
  const address = server.address() as AddressInfo;
  baseUrl = `http://127.0.0.1:${address.port}`;
});

after(async () => {
  await new Promise<void>((resolve) => server.close(() => resolve()));
  await rm(dataDir, { recursive: true, force: true });
});

it('fails closed for invalid task data without overwriting the file', async () => {
  const response = await fetch(`${baseUrl}/api/tasks`);

  assert.equal(response.status, 500);
  assert.deepEqual(await response.json(), { error: { message: 'Internal server error' } });
  assert.equal(await readFile(dataFile, 'utf8'), original);
});
