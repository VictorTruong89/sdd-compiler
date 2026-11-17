#!/bin/bash
# Round 28 case001: run notes/probe.py on one built tomli (a folder), in a container with no network.
#   bash notes/probe.sh <app dir>      -> JSON {item: side}
D="$(cd "$1" && pwd)"; N="$(cd "$(dirname "$0")" && pwd)"
docker run --rm --network none -v "$D":/app:ro -v "$N/probe.py":/probe.py:ro python:3.13-slim-bookworm python3 /probe.py /app
