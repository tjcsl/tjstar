#!/bin/sh

# This assumes you've created a virtual environment and installed Gunicorn
# See the docs for instructions

cd /site

. "$HOME/.local/bin/env"

uv sync
uv run manage.py collectstatic --noinput
uv run manage.py migrate

uv run gunicorn tjstar.wsgi -b $HOST:$PORT -w 1
