# Issues

2026-10-18 — The literal handover check `pgrep -f run_queue.sh` matched its own shell command and
printed “a driver is already running”. A second process-specific check, `pgrep -af '[r]un_queue\.sh'`,
found no active driver. No driver was running and no model call was started.
2026-10-18 — The revised handover changed the instruction from waiting for the 2026-10-19 usage
reset to “Start now”. The owner asked on 2026-10-18 to start now; the required lock checks passed
with `no-driver-batch-1` and `no-driver-batch-2`.
2026-10-19 — The owner ran the earlier prompt version, so Copilot resumed the driver check but did not score or write up. Claude Code scored the 5 runs, read the notes and wrote `TRIAL.md` on 2026-10-19 (no model call).
