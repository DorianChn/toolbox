import type { Task, TaskStats, TaskStatus } from './types';

/** Empty by default: Vite proxies /api to the Express server in dev, and in
 *  production both are served from the same origin. */
const BASE = import.meta.env.VITE_API_BASE ?? '';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE}${path}`, {
      ...init,
      headers: init?.body ? { 'content-type': 'application/json' } : undefined,
    });
  } catch {
    throw new Error('Cannot reach the API. Is the server running?');
  }

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = (await response.json()) as { error?: { message?: string } };
      if (body.error?.message) message = body.error.message;
    } catch {
      // keep the generic message
    }
    throw new Error(message);
  }

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export interface ListParams {
  status?: TaskStatus | 'all';
  query?: string;
}

export const api = {
  list({ status, query }: ListParams = {}): Promise<{ tasks: Task[]; stats: TaskStats }> {
    const params = new URLSearchParams();
    if (status && status !== 'all') params.set('status', status);
    if (query?.trim()) params.set('q', query.trim());
    const suffix = params.size > 0 ? `?${params.toString()}` : '';
    return request(`/api/tasks${suffix}`);
  },

  stats(): Promise<TaskStats> {
    return request('/api/tasks/stats');
  },

  create(input: { title: string; notes?: string }): Promise<{ task: Task }> {
    return request('/api/tasks', { method: 'POST', body: JSON.stringify(input) });
  },

  update(
    id: string,
    patch: { title?: string; notes?: string; status?: TaskStatus },
  ): Promise<{ task: Task }> {
    return request(`/api/tasks/${id}`, { method: 'PATCH', body: JSON.stringify(patch) });
  },

  remove(id: string): Promise<void> {
    return request(`/api/tasks/${id}`, { method: 'DELETE' });
  },

  clearCompleted(): Promise<{ removed: number }> {
    return request('/api/tasks', { method: 'DELETE' });
  },
};
