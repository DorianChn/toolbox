import { mkdir, readFile, rename, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { nanoid } from 'nanoid';
import { DATA_FILE } from './config.js';
import { NotFoundError } from './errors.js';
import type { CreateTaskInput, Task, TaskStats, TaskStatus, UpdateTaskInput } from './types.js';

export interface ListOptions {
  status?: TaskStatus;
  query?: string;
}

function isStoredTask(value: unknown): value is Task {
  if (!value || typeof value !== 'object') return false;
  const task = value as Record<string, unknown>;
  return (
    typeof task.id === 'string' &&
    typeof task.title === 'string' &&
    typeof task.notes === 'string' &&
    (task.status === 'active' || task.status === 'done') &&
    typeof task.createdAt === 'string' &&
    typeof task.updatedAt === 'string'
  );
}

/**
 * A tiny persistence layer backed by a single JSON file.
 *
 * It is intentionally free of native dependencies so the project runs anywhere
 * Node runs. Every mutation is serialised through an in-memory queue and written
 * atomically (temp file + rename), so concurrent requests can never corrupt the
 * store. Swapping this out for Postgres/Prisma later only means reimplementing
 * the handful of methods below.
 */
class TaskStore {
  private cache: Task[] | null = null;
  private queue: Promise<unknown> = Promise.resolve();

  /** Serialise work so read-modify-write cycles cannot interleave. */
  private run<T>(fn: () => Promise<T>): Promise<T> {
    const result = this.queue.then(fn, fn);
    this.queue = result.then(
      () => undefined,
      () => undefined,
    );
    return result;
  }

  private async read(): Promise<Task[]> {
    if (this.cache !== null) return this.cache;

    let raw: string;
    try {
      raw = await readFile(DATA_FILE, 'utf8');
    } catch (error) {
      const code = (error as NodeJS.ErrnoException).code;
      if (code === 'ENOENT') {
        this.cache = [];
        return this.cache;
      }
      throw new Error(`[store] could not read ${DATA_FILE} without risking data loss`, { cause: error });
    }

    let parsed: unknown;
    try {
      parsed = JSON.parse(raw);
    } catch (error) {
      throw new Error(`[store] invalid JSON in ${DATA_FILE}; refusing to overwrite it`, { cause: error });
    }

    if (!Array.isArray(parsed)) {
      throw new Error(`[store] invalid task data in ${DATA_FILE}; refusing to overwrite it`);
    }

    const tasks = parsed.filter(isStoredTask);
    if (tasks.length !== parsed.length) {
      throw new Error(`[store] invalid task data in ${DATA_FILE}; refusing to overwrite it`);
    }

    this.cache = tasks;
    return this.cache;
  }

  private async write(tasks: Task[]): Promise<void> {
    await mkdir(path.dirname(DATA_FILE), { recursive: true });
    const tmp = `${DATA_FILE}.${process.pid}.tmp`;
    await writeFile(tmp, `${JSON.stringify(tasks, null, 2)}\n`, 'utf8');
    await rename(tmp, DATA_FILE);
    this.cache = tasks;
  }

  list(options: ListOptions = {}): Promise<Task[]> {
    return this.run(async () => {
      const tasks = await this.read();
      const needle = options.query?.toLowerCase();

      return tasks
        .filter((task) => (options.status ? task.status === options.status : true))
        .filter((task) => {
          if (!needle) return true;
          return (
            task.title.toLowerCase().includes(needle) ||
            task.notes.toLowerCase().includes(needle)
          );
        })
        .sort((a, b) => b.createdAt.localeCompare(a.createdAt));
    });
  }

  stats(): Promise<TaskStats> {
    return this.run(async () => {
      const tasks = await this.read();
      const done = tasks.filter((task) => task.status === 'done').length;
      return { total: tasks.length, active: tasks.length - done, done };
    });
  }

  create(input: CreateTaskInput): Promise<Task> {
    return this.run(async () => {
      const tasks = await this.read();
      const now = new Date().toISOString();
      const task: Task = {
        id: nanoid(12),
        title: input.title,
        notes: input.notes ?? '',
        status: 'active',
        createdAt: now,
        updatedAt: now,
      };

      tasks.unshift(task);
      await this.write(tasks);
      return task;
    });
  }

  update(id: string, patch: UpdateTaskInput): Promise<Task> {
    return this.run(async () => {
      const tasks = await this.read();
      const index = tasks.findIndex((task) => task.id === id);
      const current = tasks[index];
      if (index === -1 || !current) {
        throw new NotFoundError(`Task ${id} does not exist`);
      }

      const updated: Task = {
        ...current,
        ...patch,
        id: current.id,
        createdAt: current.createdAt,
        updatedAt: new Date().toISOString(),
      };

      const next = [...tasks];
      next[index] = updated;
      await this.write(next);
      return updated;
    });
  }

  remove(id: string): Promise<void> {
    return this.run(async () => {
      const tasks = await this.read();
      const next = tasks.filter((task) => task.id !== id);
      if (next.length === tasks.length) {
        throw new NotFoundError(`Task ${id} does not exist`);
      }
      await this.write(next);
    });
  }

  clearCompleted(): Promise<number> {
    return this.run(async () => {
      const tasks = await this.read();
      const next = tasks.filter((task) => task.status !== 'done');
      const removed = tasks.length - next.length;
      if (removed > 0) {
        await this.write(next);
      }
      return removed;
    });
  }
}

export const taskStore = new TaskStore();
