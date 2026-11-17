#!/bin/bash
# Run the side probes on one unpacked build, in a throwaway container with no network.
#   bash notes/probe.sh <app-dir>      -> one JSON line on stdout
set -eu
APP="$(cd "$1" && pwd)"; NOTES="$(cd "$(dirname "$0")" && pwd)"
docker run --rm --network none -e PYTHONDONTWRITEBYTECODE=1 -v "$APP":/app:ro -v "$NOTES":/probe:ro \
  python:3.13-slim python3 -I /probe/probe.py /app
