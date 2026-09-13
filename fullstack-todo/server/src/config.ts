import path from 'node:path';

const DEFAULT_DATA_FILE = path.join('.data', 'tasks.json');

export const PORT = Number.parseInt(process.env.PORT ?? '4000', 10);

export const DATA_FILE = path.resolve(process.env.DATA_FILE ?? DEFAULT_DATA_FILE);

export const CORS_ORIGIN = (process.env.CORS_ORIGIN ?? 'http://localhost:5173')
  .split(',')
  .map((origin) => origin.trim())
  .filter(Boolean);
