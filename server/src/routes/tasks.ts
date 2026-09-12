import { Router } from 'express';
import { z } from 'zod';
import { asyncHandler } from '../http.js';
import { ValidationError } from '../errors.js';
import { taskStore } from '../store.js';

const statusSchema = z.enum(['active', 'done']);

const createSchema = z.object({
  title: z.string().trim().min(1, 'title is required').max(200, 'title is too long'),
  notes: z.string().trim().max(2000, 'notes are too long').default(''),
});

const updateSchema = z
  .object({
    title: z.string().trim().min(1, 'title cannot be empty').max(200).optional(),
    notes: z.string().trim().max(2000).optional(),
    status: statusSchema.optional(),
  })
  .refine((value) => Object.keys(value).length > 0, {
    message: 'provide at least one field to update',
  });

const listQuerySchema = z.object({
  status: statusSchema.optional(),
  q: z.string().trim().max(200).optional(),
});

export const tasksRouter = Router();

/** GET /api/tasks?status=active|done&q=search */
tasksRouter.get(
  '/',
  asyncHandler(async (req, res) => {
    const parsed = listQuerySchema.safeParse(req.query);
    if (!parsed.success) {
      throw new ValidationError('Invalid query parameters', parsed.error.issues);
    }

    const [tasks, stats] = await Promise.all([
      taskStore.list({ status: parsed.data.status, query: parsed.data.q }),
      taskStore.stats(),
    ]);

    res.json({ tasks, stats });
  }),
);

/** GET /api/tasks/stats */
tasksRouter.get(
  '/stats',
  asyncHandler(async (_req, res) => {
    res.json(await taskStore.stats());
  }),
);

/** POST /api/tasks */
tasksRouter.post(
  '/',
  asyncHandler(async (req, res) => {
    const parsed = createSchema.safeParse(req.body);
    if (!parsed.success) {
      throw new ValidationError('Invalid task payload', parsed.error.issues);
    }

    const task = await taskStore.create(parsed.data);
    res.status(201).json({ task });
  }),
);

/** PATCH /api/tasks/:id */
tasksRouter.patch(
  '/:id',
  asyncHandler(async (req, res) => {
    const id = req.params.id;
    if (!id) throw new ValidationError('Missing task id');

    const parsed = updateSchema.safeParse(req.body);
    if (!parsed.success) {
      throw new ValidationError('Invalid task patch', parsed.error.issues);
    }

    const task = await taskStore.update(id, parsed.data);
    res.json({ task });
  }),
);

/** DELETE /api/tasks/:id */
tasksRouter.delete(
  '/:id',
  asyncHandler(async (req, res) => {
    const id = req.params.id;
    if (!id) throw new ValidationError('Missing task id');

    await taskStore.remove(id);
    res.status(204).end();
  }),
);

/** DELETE /api/tasks  -> clears every completed task */
tasksRouter.delete(
  '/',
  asyncHandler(async (_req, res) => {
    const removed = await taskStore.clearCompleted();
    res.json({ removed });
  }),
);
