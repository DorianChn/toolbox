import assert from 'node:assert/strict';
import { mkdtemp, rm } from 'node:fs/promises';
import type { Server } from 'node:http';
import type { AddressInfo } from 'node:net';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { after, before, describe, it } from 'node:test';

// Point the store at a throwaway directory *before* the modules that read config.
const dataDir = await mkdtemp(path.join(tmpdir(), 'fullstack-todo-test-'));
process.env.DATA_FILE = path.join(dataDir, 'tasks.json');

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

async function api(pathname: string, init?: RequestInit): Promise<Response> {
  return fetch(`${baseUrl}${pathname}`, init);
}

describe('API', () => {
  it('reports health', async () => {
    const res = await api('/api/health');
    assert.equal(res.status, 200);
    const body = (await res.json()) as { status: string };
    assert.equal(body.status, 'ok');
  });

  it('creates, updates and deletes a task', async () => {
    const created = await api('/api/tasks', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ title: 'Write the README', notes: 'Keep it short' }),
    });
    assert.equal(created.status, 201);
    const { task } = (await created.json()) as { task: { id: string; title: string } };
    assert.equal(task.title, 'Write the README');

    const patched = await api(`/api/tasks/${task.id}`, {
      method: 'PATCH',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ status: 'done' }),
    });
    assert.equal(patched.status, 200);

    const listed = await api('/api/tasks?status=done');
    const listedBody = (await listed.json()) as { tasks: Array<{ id: string }> };
    assert.equal(listedBody.tasks.length, 1);
    assert.equal(listedBody.tasks[0]?.id, task.id);

    const deleted = await api(`/api/tasks/${task.id}`, { method: 'DELETE' });
    assert.equal(deleted.status, 204);

    const missing = await api(`/api/tasks/${task.id}`, { method: 'DELETE' });
    assert.equal(missing.status, 404);
  });

  it('rejects an empty title', async () => {
    const res = await api('/api/tasks', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ title: '   ' }),
    });
    assert.equal(res.status, 400);
  });

  it('clears completed tasks and reports stats', async () => {
    for (const title of ['a', 'b']) {
      const res = await api('/api/tasks', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ title }),
      });
      const { task } = (await res.json()) as { task: { id: string } };
      await api(`/api/tasks/${task.id}`, {
        method: 'PATCH',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ status: 'done' }),
      });
    }

    const cleared = await api('/api/tasks', { method: 'DELETE' });
    const clearedBody = (await cleared.json()) as { removed: number };
    assert.equal(clearedBody.removed, 2);

    const stats = await api('/api/tasks/stats');
    const statsBody = (await stats.json()) as { total: number; done: number };
    assert.equal(statsBody.done, 0);
  });
});
