# fullstack-todo

A small but properly-structured full-stack task manager: **React + TypeScript + Vite** on the front, **Express + TypeScript** on the back, and a dependency-free JSON store for persistence.

It is meant to be a starting point you can actually read end to end — no magic, no native modules, no database to install.

```
┌─────────────────┐        ┌─────────────────┐        ┌──────────────────┐
│  React + Vite   │  /api  │  Express (TS)   │        │  JSON file store │
│  localhost:5173 │ ─────► │  localhost:4000 │ ─────► │  .data/tasks.json│
└─────────────────┘        └─────────────────┘        └──────────────────┘
```

## Quick start

Requires **Node 20.10+**.

```bash
npm install
npm run dev
```

- Web app: <http://localhost:5173>
- API: <http://localhost:4000/api/health>

The Vite dev server proxies `/api` to the Express server, so there is no CORS setup to worry about.

## Features

- Create, edit, complete, and delete tasks
- Filter by **all / active / done** and search across title and notes
- Live counters and a completion progress bar
- Clear all completed tasks in one click
- Optimistic UI: the list updates instantly and rolls back if the request fails
- Atomic writes, so two requests at the same time can never corrupt the data file
- Auto light/dark theme based on your OS preference

## Scripts

| Command              | What it does                                        |
| -------------------- | --------------------------------------------------- |
| `npm run dev`        | Runs the API and the web app together               |
| `npm run build`      | Type-checks and builds both packages                |
| `npm start`          | Starts the API (serves the built frontend if present) |
| `npm run typecheck`  | Type-checks both packages without emitting         |
| `npm test`           | Boots the API and runs an end-to-end smoke test     |

## API

Base path: `/api`

| Method   | Endpoint        | Body / query                        | Response                     |
| -------- | --------------- | ----------------------------------- | ---------------------------- |
| `GET`    | `/health`       | –                                   | `{ status, uptime }`         |
| `GET`    | `/tasks`        | `?status=active\|done&q=search`     | `{ tasks, stats }`           |
| `GET`    | `/tasks/stats`  | –                                   | `{ total, active, done }`    |
| `POST`   | `/tasks`        | `{ title, notes? }`                 | `201` → `{ task }`           |
| `PATCH`  | `/tasks/:id`    | `{ title?, notes?, status? }`       | `{ task }`                   |
| `DELETE` | `/tasks/:id`    | –                                   | `204`                        |
| `DELETE` | `/tasks`        | –                                   | `{ removed }` (clears done)  |

Errors come back as `{ "error": { "message": string, "details": unknown } }` with a matching status code.

```bash
curl -X POST localhost:4000/api/tasks \
  -H 'content-type: application/json' \
  -d '{"title":"Read the source","notes":"It is short"}'
```

## Project layout

```
.
├── server/                 # Express + TypeScript API
│   └── src
│       ├── app.ts          # middleware, routes, static hosting, error handler
│       ├── config.ts       # env-driven configuration
│       ├── store.ts        # JSON persistence (swap this for a real DB)
│       └── routes/tasks.ts # validation + route handlers
├── web/                    # React + Vite frontend
│   └── src
│       ├── App.tsx         # state, filters, optimistic updates
│       ├── api.ts          # typed fetch wrapper
│       └── components/     # TaskComposer, TaskItem
└── .github/workflows/ci.yml
```

## Configuration

Copy `server/.env.example` to `server/.env` to override the defaults:

| Variable       | Default                  | Purpose                                |
| -------------- | ------------------------ | -------------------------------------- |
| `PORT`         | `4000`                   | API port                               |
| `DATA_FILE`    | `.data/tasks.json`       | Where tasks are stored                 |
| `CORS_ORIGIN`  | `http://localhost:5173`  | Allowed browser origins (comma-separated) |

To point the frontend at a remote API, set `VITE_API_BASE` when building the web app.

## Production

```bash
npm run build
npm start        # serves the API and, if it exists, web/dist on one port
```

## License

[MIT](./LICENSE)
