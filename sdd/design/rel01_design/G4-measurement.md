# G4 — Effectiveness measurement

> **Status:** PLACEHOLDER — two steps (rel01 D22): an **outline reviewed before coding**, the detailed
> experiment designed after G1 and G2 produce a spec graph
> **Tier:** design, non-authoritative

## Starting material (not decisions)

- [`../../../docs/lectures/lecture-tiered-md-vs-graph.html`](../../../docs/lectures/lecture-tiered-md-vs-graph.html)
  Parts 6–10: arms (flat / tiered / graph views / graph + queries), metrics for reading and
  generation, Claude Code instrumentation surfaces, failure catalogue, experiment design.
  ⚠ Written before rel01 D26. Its "graph + queries" arm assumes query tooling F4 provides, which is in
  rel01; its hook-based instrumentation is not.

## Outline to review before coding (rel01 D22)

1. What "effective" means for rel01, as measurable outcomes.
2. The metrics, chosen from lecture Part 7.
3. **Instrumentation the code must emit**, so the experiment is possible later without re-engineering.
   Already specified and enough to start: run records (F1 CT-1.3), judgment records with usage and cost
   (F3 CT-3.2), retrieval counts (F5 CT-5.3), conflict counts (F6 CT-6.2), and F5's exhaustive mode for
   measuring what ranking misses.
   ⚠ rel01 has **no hooks**, so the lecture's hook-based read logs are not available. An experiment
   that needs "which specs did the agent read" must get it from the agent's own transcript or telemetry,
   not from this compiler.

## To design once a graph exists

1. What "effective" means for rel01, stated as measurable outcomes.
2. The smallest experiment that can run on rel01's actual output.
3. Instrumentation for the agent side of a comparison: headless JSON, transcripts and telemetry
   (Claude Code hooks only if the live-editing release brings them back).
