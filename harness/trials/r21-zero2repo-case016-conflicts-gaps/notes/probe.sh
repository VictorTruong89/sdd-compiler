#!/bin/bash
# Round 21 (copied from round 20; one change: the image is r21-probe, python:3.13-slim with Node.js, built from
# work/probe-image/Dockerfile, because half the probes fire the Node hooks). Run the probes on one unpacked build,
# in a throwaway container with no network.
#   bash notes/probe.sh <app-dir> [C01 G01 ...]      -> one JSON line on stdout
set -eu
APP="$(cd "$1" && pwd)"; NOTES="$(cd "$(dirname "$0")" && pwd)"
docker run --rm --network none -e PYTHONDONTWRITEBYTECODE=1 -v "$APP":/app:ro -v "$NOTES":/probe:ro \
  r21-probe python3 -I /probe/probe.py /app "${@:2}"
