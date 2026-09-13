import { useCallback, useEffect, useState } from 'react';
import { api } from './api';
import { TaskComposer } from './components/TaskComposer';
import { TaskItem } from './components/TaskItem';
import type { Filter, Task, TaskStats, TaskStatus } from './types';

const EMPTY_STATS: TaskStats = { total: 0, active: 0, done: 0 };

const FILTERS: Array<{ key: Filter; label: string }> = [
  { key: 'all', label: 'All' },
  { key: 'active', label: 'Active' },
  { key: 'done', label: 'Done' },
];

function messageOf(error: unknown): string {
  return error instanceof Error ? error.message : 'Something went wrong';
}

export default function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [stats, setStats] = useState<TaskStats>(EMPTY_STATS);
  const [filter, setFilter] = useState<Filter>('all');
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (nextFilter: Filter, nextQuery: string) => {
    try {
      const result = await api.list({ status: nextFilter, query: nextQuery });
      setTasks(result.tasks);
      setStats(result.stats);
      setError(null);
    } catch (err) {
      setError(messageOf(err));
    } finally {
      setLoading(false);
    }
  }, []);

  // Debounced so typing in the search box does not hammer the API.
  useEffect(() => {
    const timer = setTimeout(() => void load(filter, query), query ? 250 : 0);
    return () => clearTimeout(timer);
  }, [filter, query, load]);

  const runMutation = useCallback(
    async (optimistic: Task[], action: () => Promise<void>) => {
      const snapshot = tasks;
      setTasks(optimistic);
      try {
        await action();
        setStats(await api.stats());
        setError(null);
      } catch (err) {
        setTasks(snapshot);
        setError(messageOf(err));
      }
    },
    [tasks],
  );

  const handleCreate = useCallback(
    async (title: string) => {
      try {
        const { task } = await api.create({ title });
        setTasks((prev) => (filter === 'done' ? prev : [task, ...prev]));
        setStats(await api.stats());
        setError(null);
      } catch (err) {
        setError(messageOf(err));
      }
    },
    [filter],
  );

  const handleToggle = useCallback(
    (task: Task) => {
      const nextStatus: TaskStatus = task.status === 'done' ? 'active' : 'done';
      const matches = (candidate: Task) => filter === 'all' || candidate.status === filter;
      const optimistic = tasks
        .map((item) => (item.id === task.id ? { ...item, status: nextStatus } : item))
        .filter(matches);

      void runMutation(optimistic, async () => {
        const { task: updated } = await api.update(task.id, { status: nextStatus });
        setTasks((prev) =>
          prev.map((item) => (item.id === task.id ? updated : item)).filter(matches),
        );
      });
    },
    [tasks, filter, runMutation],
  );

  const handleSave = useCallback(
    (task: Task, patch: { title: string; notes: string }) => {
      const optimistic = tasks.map((item) =>
        item.id === task.id ? { ...item, ...patch } : item,
      );

      void runMutation(optimistic, async () => {
        const { task: updated } = await api.update(task.id, patch);
        setTasks((prev) => prev.map((item) => (item.id === task.id ? updated : item)));
      });
    },
    [tasks, runMutation],
  );

  const handleDelete = useCallback(
    (task: Task) => {
      void runMutation(
        tasks.filter((item) => item.id !== task.id),
        () => api.remove(task.id),
      );
    },
    [tasks, runMutation],
  );

  const handleClearCompleted = useCallback(() => {
    void runMutation(
      tasks.filter((item) => item.status !== 'done'),
      async () => {
        await api.clearCompleted();
      },
    );
  }, [tasks, runMutation]);

  const progress = stats.total === 0 ? 0 : Math.round((stats.done / stats.total) * 100);

  return (
    <div className="page">
      <main className="card">
        <header className="card__header">
          <h1 className="card__title">fullstack-todo</h1>
          <p className="card__subtitle">
            React + TypeScript on the front, Express + TypeScript behind it.
          </p>

          <div className="stats">
            <span className="stat">
              <strong>{stats.total}</strong> total
            </span>
            <span className="stat">
              <strong>{stats.active}</strong> active
            </span>
            <span className="stat">
              <strong>{stats.done}</strong> done
            </span>
            <span className="stat stat--muted">{progress}%</span>
          </div>

          <div className="progress" role="presentation">
            <div className="progress__bar" style={{ width: `${progress}%` }} />
          </div>
        </header>

        <TaskComposer onCreate={handleCreate} />

        <div className="toolbar">
          <div className="segmented" role="group" aria-label="Filter tasks">
            {FILTERS.map(({ key, label }) => (
              <button
                key={key}
                type="button"
                className={`segmented__item${filter === key ? ' is-active' : ''}`}
                aria-pressed={filter === key}
                onClick={() => setFilter(key)}
              >
                {label}
              </button>
            ))}
          </div>

          <input
            className="toolbar__search"
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search tasks…"
            aria-label="Search tasks"
          />

          <button
            type="button"
            className="btn btn--ghost"
            onClick={handleClearCompleted}
            disabled={stats.done === 0}
          >
            Clear done
          </button>
        </div>

        {error ? (
          <p className="alert" role="alert">
            {error}
          </p>
        ) : null}

        {loading ? (
          <p className="placeholder">Loading tasks…</p>
        ) : tasks.length === 0 ? (
          <p className="placeholder">
            {query ? `No tasks match “${query}”.` : 'Nothing here yet — add your first task.'}
          </p>
        ) : (
          <ul className="task-list">
            {tasks.map((task) => (
              <TaskItem
                key={task.id}
                task={task}
                onToggle={handleToggle}
                onDelete={handleDelete}
                onSave={handleSave}
              />
            ))}
          </ul>
        )}
      </main>

      <footer className="footer">
        <span>Data lives in a JSON file on the server — restart safe, zero setup.</span>
      </footer>
    </div>
  );
}
