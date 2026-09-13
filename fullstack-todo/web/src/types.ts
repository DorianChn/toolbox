export type TaskStatus = 'active' | 'done';

export interface Task {
  id: string;
  title: string;
  notes: string;
  status: TaskStatus;
  createdAt: string;
  updatedAt: string;
}

export interface TaskStats {
  total: number;
  active: number;
  done: number;
}

export type Filter = 'all' | TaskStatus;
