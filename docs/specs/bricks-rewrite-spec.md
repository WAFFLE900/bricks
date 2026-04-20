# Bricks Rewrite Spec

## Summary

Bricks is being rebuilt from a mixed Flask/MySQL/Vue CLI codebase into a clean frontend/backend split:

- Frontend: Vue 3 + Vite + Pinia in `apps/web`
- Backend: FastAPI + SQLAlchemy 2 + Alembic in `apps/api`
- Database: PostgreSQL
- Local verification: Docker Compose
- PaaS target: Render

The rewrite is intentionally additive. Existing Flask and Vue CLI code stays in place as migration reference until the new stack fully replaces it.

## Current State Inventory

### Backend

- The current backend lives in `backend/backend`.
- `main.py` contains a large single-file Flask application with direct route definitions for auth, project, record, tag, and rollback flows.
- `app/modules/*` contains an unfinished Blueprint split with overlapping logic.
- Database credentials, JWT secret, Google OAuth credentials, and remote host/IPs are hardcoded in source.
- The current implementation uses a global SQLAlchemy session with request-unsafe lifecycle management.
- Existing tests are minimal and depend on the legacy import shape and, in practice, remote database assumptions.

### Frontend

- The current frontend is nested under `frontend/frontend/frontend`, with extra `package.json` files at `frontend/` and `frontend/frontend/`.
- `frontend/frontend/node_modules` is committed into the repository.
- The active app is built with Vue CLI and `vue-cli-service`, but the main application directory does not currently rebuild cleanly from a fresh environment.
- API calls are scattered through `views` and `components` and directly reference multiple hardcoded Google Cloud IP addresses.
- The app lacks a centralized API client, stable environment-variable handling, and a feature-oriented module layout.
- Vuex is used only as a light global store and does not provide a modern domain-oriented state boundary.

## Frontend Technology Decision

- Vue remains the frontend framework.
- Vue CLI is not the target architecture for the rewrite.
- The new frontend is implemented as a brand-new Vite app in `apps/web`.
- Pinia replaces Vuex as the default state-management layer.
- Axios remains acceptable for HTTP, but only behind `src/shared/api/client.ts` and feature service wrappers.
- The legacy Vue CLI app remains read-only migration reference until feature parity is reached.

## Decision Rationale

- Vue CLI is in maintenance mode and is no longer the recommended baseline for new Vue 3 projects.
- Vue officially recommends Vite-based scaffolding for new work.
- Bricks needs clean environment separation, local Docker verification, faster rebuilds, clearer module boundaries, and safer PaaS deployment. Vite aligns with those needs better than continuing on webpack/Vue CLI.

Reference material:

- <https://cli.vuejs.org/guide/index.html>
- <https://cli.vuejs.org/guide/cli-service>
- <https://v3-migration.vuejs.org/recommendations.html>
- <https://vite.dev/guide/>
- <https://vite.dev/guide/why.html>

## Migration Strategy

- Build a brand-new frontend in `apps/web`.
- Keep the current Vue CLI application as legacy frontend reference.
- Do not attempt an in-place webpack/Vue CLI modernization.
- Migrate by feature domain instead of file-by-file copying.
- Remove the legacy frontend only after the rewritten feature domains are running on the new API.

## Backend Target Architecture

- Use a single FastAPI application under `apps/api`.
- Manage backend dependencies and local execution with `uv`.
- Use SQLAlchemy 2 with synchronous sessions and PostgreSQL via `psycopg`.
- Use Alembic for schema migrations and initial PostgreSQL schema bootstrapping.
- Group routes by domain under `/api/v1`:
  - `/auth`
  - `/users`
  - `/projects`
  - `/project-types`
  - `/records`
  - `/tags`
  - `/search`
- Centralize settings, auth, CORS, database lifecycle, and error formatting.

## Frontend Target Architecture

`apps/web` follows this structure:

- `src/app`: app bootstrap, router, providers
- `src/features`: domain modules for auth, projects, and records
- `src/shared`: API client, config, types, UI primitives, utilities

Rules:

- Components must not hardcode API URLs.
- Components must not import `axios` directly.
- All browser-facing env variables use the Vite `VITE_` prefix.
- Auth bootstrap loads persisted tokens, fetches the current user, and guards protected routes.

## Legacy-to-New API Mapping

### Auth

- `POST /bricks_login` -> `POST /api/v1/auth/login`
- `POST /register` -> `POST /api/v1/auth/register`
- `POST /register/survey` -> `POST /api/v1/auth/survey`
- `POST /google_login` -> `GET /api/v1/auth/google/url` and future callback handling

### Projects

- `POST /project_index` -> `GET /api/v1/projects?status=active|ended|trash`
- `POST /add_project` -> `POST /api/v1/projects`
- `POST /set_project_end` -> `PATCH /api/v1/projects/{project_id}/state`
- `POST /to_trashcan` -> `PATCH /api/v1/projects/{project_id}/trash`
- `POST /trashcan_recover` -> `PATCH /api/v1/projects/{project_id}/trash`
- `POST /permanent_delete` -> `DELETE /api/v1/projects/{project_id}`
- `POST /edit_type` -> `POST /api/v1/project-types/rename`
- `POST /search` -> `GET /api/v1/search/projects`

### Records and Tags

- `POST /get_record_index` -> `GET /api/v1/projects/{project_id}/records`
- `POST /add_record` -> `POST /api/v1/projects/{project_id}/records`
- `POST /get_record` -> `GET /api/v1/projects/{project_id}/records/{record_id}`
- `POST /edit_record` -> `PATCH /api/v1/records/{record_id}`
- `POST /delete_record` -> `PATCH /api/v1/records/{record_id}/trash`
- `POST /recover_record` -> `PATCH /api/v1/records/{record_id}/trash`
- `POST /delete_record_permanent` -> `DELETE /api/v1/records/{record_id}`
- `POST /add_textBox` -> `POST /api/v1/records/{record_id}/text-boxes`
- `POST /edit_textBox` -> `PATCH /api/v1/text-boxes/{text_box_id}`
- `POST /add_tag` -> `POST /api/v1/tags`
- `POST /delete_tag` -> `DELETE /api/v1/text-boxes/{text_box_id}/tags/{tag_id}`

## Data Model Mapping

The legacy MySQL dump is the source of truth for initial PostgreSQL mapping.

Core tables that are already in the first rewrite slice:

- `users`
- `project`
- `project_sort`
- `record`
- `textBox`
- `tag`
- `tag_textBox`
- `search_history`

Deferred legacy tables that stay documented but are not part of the first migrated UI flow:

- `delete`
- `groups`
- `groups_member`
- `mention`
- `notification`
- `problem`

## Delivery Phases

1. Create spec and repo scaffolding.
2. Stand up the new FastAPI and Vite applications.
3. Add Docker Compose and Render configuration.
4. Migrate auth and survey flows.
5. Migrate project listing, creation, trash, and search flows.
6. Migrate record and textbox/tag flows.
7. Execute MySQL-to-PostgreSQL data import and cut over traffic.
8. Remove hardcoded secrets/IPs, legacy entrypoints, and the legacy frontend when parity is reached.

## Acceptance Criteria

### Backend

- `apps/api` starts locally with environment-based configuration only.
- Core route groups exist under `/api/v1`.
- Pytest covers auth, survey, projects, search, records, text boxes, and tags.
- No hardcoded production credentials or remote database hosts remain in the new backend.

### Frontend

- `apps/web` builds independently.
- API base URL is injected entirely through env variables.
- Feature pages do not directly call `axios`.
- Auth and project flow smoke tests exist.
- At least one end-to-end login-to-project workflow exists.

### Deployment

- `docker compose up --build` brings up PostgreSQL, API, and frontend.
- `render.yaml` defines the API web service, frontend static site, and PostgreSQL database.

## Notes

- The current repository root is not a Git root. This rewrite is implemented as filesystem structure plus executable services, without rewriting legacy history.
- The new stack is the forward path. Legacy code stays available only to support migration and verification.
