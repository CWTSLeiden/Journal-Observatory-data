#!/bin/sh
set -e

if [ "$1" = "run" ] || [ -z "$1" ]; then
    # Set defaults
    export PYTHONPATH="${PYTHONPATH:-./src}"
    export APP_HOST="${APP_HOST:-0.0.0.0}"
    export APP_PORT="${APP_PORT:-5000}"

    if [ "${APP_ENVIRONMENT}" = "production" ]; then
        exec gunicorn --bind "${APP_HOST}:${APP_PORT}" api.application:api
    fi
    exec flask -A api.application:api --debug run --host "${APP_HOST}" --port "${APP_PORT}"
fi

exec "$@"
