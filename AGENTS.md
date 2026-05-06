# AGENTS.md instructions for transight-sftp

## Operating Defaults

- Before acting, check whether a project or personal skill applies.
- Prefer focused, production-ready edits over broad rewrites.
- Use `rg` for search and keep inspection commands narrow.
- For Python commands, prefer `.venv/bin/python`; use `python3` only when `.venv` does not exist.

## Evidence Discipline

- Keep raw evidence, normalized data, interpretation, and final reports in separate artifacts.
- Store raw evidence under `data/raw`, normalized records under `data/normalized`, and reports under `data/reports`.
- Preserve provenance, freshness, request parameters, timestamps, and unresolved status when they affect conclusions.
- If a decisive artifact is not found, say that before presenting weaker surrounding evidence.

## External Providers

- Before designing retries, batching, fallback order, or rollout for an external API, prove the exact provider path with a minimal smoke request.
- Distinguish credential presence, authorization, minimal request success, and operational limits.

## Long-Running Work

- Long-running collectors must write logs under `logs` and checkpoint or cursor state under `state/checkpoints`.
- Report process health, domain progress, latest error, current blocker, and next action.
- Do not restart from scratch when a checkpoint exists unless the user asks.

## Verification

- Before claiming completion, run the narrowest meaningful test or verification command.
- For browser behavior, use Playwright instead of guessing.
- For generated reports or classifications, verify that each conclusion traces back to raw evidence.
