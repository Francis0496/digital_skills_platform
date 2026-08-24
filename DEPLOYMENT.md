# Production Deployment

## Required environment

- Python 3.10 or newer
- `FLASK_CONFIG=production`
- `SECRET_KEY` containing at least 32 unpredictable characters
- `DATABASE_URL` for the production database (SQLite is suitable only for a
  single-process, low-traffic deployment)

Do not commit the real `.env` file.

## Build and release

```text
python -m venv .venv
python -m pip install -r requirements.txt
npm install
npm run build:css
flask --app wsgi:app db upgrade
flask --app wsgi:app seed-roles
```

The compiled `app/static/css/tailwind.css` is committed as a release asset, so
a runtime host does not need Node.js when the build has already run in CI.

## Start

```text
waitress-serve --call app:create_app
```

The included `Procfile` uses the same command. Terminate TLS at the platform
load balancer or reverse proxy, forward HTTPS requests to Waitress, and preserve
the original host and protocol headers.

Use `GET /health` as the readiness check. It returns HTTP 200 with
`{"status":"ok"}` only while the configured database responds.

## Release verification

```text
npm run build:css
python -m pytest
python -m pip check
```

After deployment, confirm `/health`, registration, login, course enrolment,
opportunity application, and administrator access over HTTPS. Verify narrow
mobile and desktop layouts with keyboard-only navigation.
