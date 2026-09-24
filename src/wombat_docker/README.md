# Mastodon Wombat Docker Blueprint

This directory contains the runtime entrypoint and processing services for the
mastodon validator workflow.

## Purpose

The validator reads paired files from the fresh directory, validates and loads
JSON data to PostgreSQL, then moves both files in a pair to success or failure.
The koala mode builds a compact summary file from the latest success payload.

## Components

1. mastodon_app.py
2. validator.py
3. koala.py
4. Dockerfile

## Runtime Modes

1. validator
2. koala

Use environment variable stuntbox to select mode.

## Validator Flow

1. Read fresh directory targets.
2. Group files by base name.
3. Process only complete .csv + .json pairs.
4. Move unpaired files to failure.
5. Validate JSON payload and schema/business rules.
6. Insert load-log and observation records.
7. Move valid pairs to success.

## Environment Variables

1. DB_CONN
2. PG_CONNECT_TIMEOUT (default 5)
3. PG_STATEMENT_TIMEOUT_MS (default 5000)
4. FRESH_DIR (default /var/wombat/fresh/mastodon)
5. SUCCESS_DIR (default /var/wombat/mastodon/success)
6. FAILURE_DIR (default /var/wombat/failure)
7. KOALA_DIR (default /var/wombat/mastodon/koala)
8. stuntbox (validator or koala)

## Local Test Run

Run tests from this directory:

```bash
source venv/bin/activate
python -m pytest -q test_mastodon_app.py test_validator.py
```

## Docker Run Pattern

Build from src:

```bash
docker build -f wombat_docker/Dockerfile -t wombat:latest .
```

Run validator mode:

```bash
docker run -e stuntbox=validator -v /var/wombat:/mnt/wombat --name wombat wombat:latest
```

Run koala mode:

```bash
docker run -e stuntbox=koala -v /var/wombat:/mnt/wombat --name wombat wombat:latest
```
