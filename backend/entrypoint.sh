#!/bin/sh
# Runs pending migrations before the app starts, so a deploy never boots
# against a schema the code doesn't expect. Safe to run on every container
# start — alembic upgrade head is a no-op when the schema is already current.
set -e

alembic upgrade head
exec "$@"
