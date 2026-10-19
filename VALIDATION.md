# Seedance validation boundary

2026-10-18. Candidate 0.1.0, Gemini CLI 0.64.0. No paid model or media generation is part of the check.

Contract tests use `python3 -m unittest discover -s tests`. The official CLI validates the manifest/context. Native lifecycle tests install the package, enter the per-service native password in an isolated encrypted secret-store fallback, list extension/MCP/Skill, activate the check command, verify tool filtering and uninstall. Local fixture-only task checks exercise `seedance_get_task` using exact `task_id` without sending a real task query.

Live mode uses the real hosted endpoint for tool discovery and only the static reference tool seedance_list_models. The model is a deterministic localhost fixture. Remote CI installs the actual GitHub review commit with no Token and skips settings; it does not prove hosted access. No fabricated task ID is ever sent to a live service.

Results are recorded after execution. Main/release/gallery indexing and default-provider selection are separate gates; none is claimed by local or review-branch installation.

## Executed local lifecycle (2026-10-18)

Five package/schema/command/attribution checks and Skill validation passed. Official0.64.0 native install/password prompt/encrypted secret storage/extension list/MCP list/Skill activation/check command/uninstall passed. Local-only fixture queried the original test task with the exact task_id parameter and returned its result. This fixture ID was never sent to any real endpoint.

## Executed hosted check (2026-10-18)

Native install/password/encrypted storage/list/Skill/check-command/uninstall passed against the real hosted endpoint. Only the static seedance_list_models reference tool was called. Model responses were deterministic localhost fixtures, not paid inference. No media generated or fabricated task queried.
