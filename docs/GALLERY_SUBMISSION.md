# Seedance gallery handoff

Candidate 0.1.0: `seedance-by-ace-data-cloud`, publisher AceDataCloud/SeedanceGemini.

Official mechanism: https://github.com/google-gemini/gemini-cli/blob/main/docs/extensions/releasing.md . Public repository + root manifest + `gemini-cli-extension` topic, daily validation/crawl. No email/issue needed; indexing is not guaranteed.

Prepared topics: `gemini-cli-extension`, `gemini-cli`, `seedance`, `ai-video`, `video-generation`, `mcp`, `agent-skills`, `acedata-cloud`. Use factual service keywords first and explicit Ace identity; no official-service endorsement. Manifest has no supported custom icon/category/keywords field; do not invent them. Gallery uses detected MCP/Skills/Commands and publisher avatar.

After human-reviewed authorized merge, verify root package on main, apply prepared topics and optionally publish version-matching release archive. Then test ordinary default install and, after daily crawl, actual official `Seedance` search → publisher card → install. Do not add the index topic while main is initialization-only.

This package is a Seedance tool extension. Official main-model provider choices remain Google/Gemini API Key/Vertex AI; maintainer scope and approved-feature/CLA gate are documented at https://github.com/google-gemini/gemini-cli/issues/1515#issuecomment-3145970081 and CONTRIBUTING.md. No default Ace provider or agreement acceptance is claimed.
