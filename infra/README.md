# Infrastructure

Render is the default PaaS target for the rewrite. The active infrastructure entrypoints are:

- `docker-compose.yml` for local verification
- `render.yaml` for Render Blueprint-style provisioning

## Local pgAdmin

`pgAdmin 4` is available as an optional local-only Docker Compose service. It is not part of the default stack and is not referenced by `render.yaml`.

Start the default local stack:

```powershell
docker compose up --build
```

Start the local stack with pgAdmin:

```powershell
docker compose --profile pgadmin up --build
```

Open pgAdmin in the browser at `http://localhost:5050` by default, or `http://localhost:${PGADMIN_PORT}` if you override the port in your local `.env`.

Default local pgAdmin credentials come from `.env` / `.env.example`:

- Email: `PGADMIN_DEFAULT_EMAIL`
- Password: `PGADMIN_DEFAULT_PASSWORD`

The preloaded pgAdmin server points at the Docker Compose PostgreSQL service named `postgres`, so it connects to the local database container rather than any remote or Render-managed database.

This directory is reserved for future platform-specific assets such as observability, backup, and environment runbooks.
