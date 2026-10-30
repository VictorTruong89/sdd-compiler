#!/bin/bash
# Judge round 15's 3 false alarms false in ../work/compile-v3, with batch 1's exact notes (no model call).
set -eu
cd "$(dirname "$0")/../../work/compile-v3"
sddc --json conflicts judge CF-000148 --verdict false --note 'different subjects: PRD 83 is a deprecated command'"'"'s warning channel; PRD 145 is when a deprecated option warns (only when the user supplied it)'
sddc --json conflicts judge CF-000149 --verdict false --note 'different subjects: PRD 83 is a deprecated command'"'"'s warning channel; PRD 163 is when a deprecated argument warns (only when the user supplied it)'
sddc --json conflicts judge CF-000154 --verdict false --note 'different subjects: the Terminology callback row is about parameter callbacks; PRD 131 is about a callable default being invoked'
