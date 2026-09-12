import { existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import cors from 'cors';
import express, { type NextFunction, type Request, type Response } from 'express';
import { CORS_ORIGIN } from './config.js';
import { HttpError } from './errors.js';
import { tasksRouter } from './routes/tasks.js';

export function createApp(): express.Express {
  const app = express();

  app.use(cors({ origin: CORS_ORIGIN }));
  app.use(express.json({ limit: '64kb' }));

  app.get('/api/health', (_req, res) => {
    res.json({ status: 'ok', uptime: Number(process.uptime().toFixed(2)) });
  });

  app.use('/api/tasks', tasksRouter);

  app.use('/api', (_req, res) => {
    res.status(404).json({ error: { message: 'Unknown API route' } });
  });

  // In production the built frontend is served from the same origin, which keeps
  // deployment to a single process. Dev mode relies on Vite's proxy instead.
  const webDist = path.resolve(fileURLToPath(new URL('../../web/dist', import.meta.url)));
  if (existsSync(webDist)) {
    app.use(express.static(webDist));
    app.get(/.*/, (_req, res) => {
      res.sendFile(path.join(webDist, 'index.html'));
    });
  }

  app.use((err: unknown, _req: Request, res: Response, _next: NextFunction) => {
    if (err instanceof HttpError) {
      res.status(err.status).json({
        error: { message: err.message, details: err.details ?? null },
      });
      return;
    }

    console.error('[api] unhandled error:', err);
    res.status(500).json({ error: { message: 'Internal server error' } });
  });

  return app;
}
