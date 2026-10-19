# SeedanceGemini

This repository owns the Seedance Gemini CLI manifest, native sensitive Token setting, workflow skill, commands and bilingual onboarding. The existing SeedanceMCP owns the server; reuse its hosted endpoint without duplicating/changing shared code. Do not add hooks, trust bypass, hidden fallbacks or automatic paid generation.

Run `python3 -m unittest discover -s tests`, `python3 scripts/package_extension.py --output /tmp/seedance-by-ace-data-cloud.tar.gz`, the official `gemini extensions validate` and isolated lifecycle smoke checks. Ordinary CI must use test discovery. Keep English/Chinese guidance aligned, preserve real screenshot sources and license, do not commit .env, keys or private user transcripts. Publish changes through the bot PR; do not merge automatically.

Text-to-video and first/last-frame or multimodal image-to-video. Use reference_image_urls/reference_audio_urls/reference_video_urls as actual arrays, not comma-separated strings. Validate duration/resolution/ratio against the current schema and selected model; do not add web search, extra audio/reference operations, edit or extend implicitly. Do not hardcode a model based on an outdated description.
