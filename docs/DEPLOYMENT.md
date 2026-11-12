# Production deployment

## Scope and verification

The production configuration uses **Django + PostgreSQL + Gunicorn + WhiteNoise**
behind a trusted HTTPS reverse proxy. The local classroom setup continues to use
SQLite and needs none of this infrastructure.

The supplied configuration, dependencies, Django deployment checks and static
collection were validated. Docker/PostgreSQL services and external SMTP were not
available in the build environment; validate those integrations in staging.
No live deployment, security audit or load certification is claimed.
Apply the instructor algorithms before using this print shop for live work.
The untouched student starter deliberately has incorrect queue ordering and
flat workflow storage; those are assignment targets, not production defaults
to keep.

## Configure

1. Copy `.env.example` to `.env` and replace every example/placeholder.
2. Generate a secret with `python -c "import secrets; print(secrets.token_urlsafe(64))"`.
   Set a different long random PostgreSQL password. Keep `.env` private.
3. Set actual `DJANGO_ALLOWED_HOSTS` and HTTPS CSRF origins. Wildcard hosts and
   missing/example secrets are rejected by production settings.
4. Configure a real SMTP account if password-reset delivery is required.
   Local console email is for development only. Invitations are manually shared
   links; they do not pretend to have sent email.
5. Put a trusted HTTPS reverse proxy in front of `127.0.0.1:8000` on the host.
   `deploy/nginx.conf.example` demonstrates routing/header/rate-limit setup;
   supply your own valid certificates and domain.
6. Set `DJANGO_TRUST_PROXY=1` only after that proxy replaces forwarded-protocol
   headers and untrusted clients cannot reach the application port directly.

The compose mapping binds the application to host loopback, not all network
interfaces. PostgreSQL has no published host port. HTTPS is enforced in Django;
secure session/CSRF cookies, HSTS, explicit hosts and CSRF trusted origins are
configured. Use a staging hostname before enabling HSTS for a real domain.

## Build and initialize

From the project directory, with Docker Engine and Compose installed:

```bash
docker compose build
docker compose up -d db
docker compose run --rm web python manage.py migrate --noinput
docker compose run --rm web python manage.py check --deploy --fail-level WARNING
docker compose run --rm web python manage.py createsuperuser
docker compose up -d web
```

`production_start.py` performs deployment checks and `collectstatic` **inside
that running container**, then replaces itself with Gunicorn. Static collection
is not lost in an earlier disposable container. Migrations are a deliberate
single initialization/release step rather than simultaneous worker startup work.
The image runs under an unprivileged UID. No credentials are built into it.

Normal users register at `/accounts/register/`; the initial workspace owner can
invite teammates. The separate superuser is for staff administration only.
Do not distribute a pre-made shared administrator account/password.

## Validate staging

- Run the application and both goal suites against an isolated staging database
  using completed instructor algorithms. Use a database role allowed to create
  Django's temporary test database, never a live customer database.
- Open the real HTTPS hostname and confirm hashed CSS/JS/favicon are served.
- Verify sign-in/out, reset email delivery and the complete one-time reset flow.
- Use separate owner/agent/viewer accounts and two workspaces. Verify forbidden
  writes, foreign object IDs, removed access and email-bound invitation expiry.
- Submit two queue pages opened at the same time; a stale expected-next value
  must not start another request. Exercise actual PostgreSQL row contention.
- Repeat edits from two tabs and confirm the stale form is rejected.
- Check backup restoration, logs, database outage behavior and `/health/`.

`/health/` performs a simple database query and returns 503 when unavailable.
It does not expose secrets. Run it through HTTPS. `manage.py check --deploy`
checks configuration; it is not a substitute for these infrastructure checks.

## Operations

Run `manage.py maintain_desk` daily for expired sessions and old throttle records.
Use an external scheduler; no unconfigured background worker is represented as
running. Monitor application/proxy logs and database capacity. Choose your own
alerting, retention, recovery objectives and supported user volume.

PostgreSQL data is stored in the named `postgres_data` volume. Back it up using
PostgreSQL-aware tooling; never treat copying a live volume as a consistent
backup. A simple logical backup example is:

```bash
docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > printpilot-backup.sql
```

Keep backups/private configuration protected and rehearse restoration into an
isolated database. Local SQLite development backups should be taken with the
server stopped. Keep source and database schema migrations versioned together.

For a release: back up, build the new image, apply included migrations once,
start the new web service, check health and exercise key actions. A rollback
must account for database migration compatibility, not just an older image.
Dependency versions are pinned at build time; plan regular security updates.
