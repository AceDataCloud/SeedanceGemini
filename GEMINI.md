# Seedance by Ace Data Cloud

This independent Seedance extension loads service-specific tools and a `seedance-video` workflow skill. It is not endorsed by the service owner or Google and does not change Gemini CLI's main model/login.

Call only `seedance_list_models` for a reference-only first check. It returns documentation, not a generation or balance result.

Use the native password setting `Ace Data Cloud Seedance API Token` for credentials; never ask for a Key in chat or expose it. For the requested paid operation, check current price, model and parameters and stay within the user's authorized budget. Submit once, retain the task ID, query the same ID with `seedance_get_task` using parameter `task_id`, and do not regenerate to poll or retry. Task-query permission does not grant generation permission. Return only actual terminal media URLs; pending, connection and green CLI status are not final output or unique-billing evidence.

Text-to-video and first/last-frame or multimodal image-to-video. Use reference_image_urls/reference_audio_urls/reference_video_urls as actual arrays, not comma-separated strings. Validate duration/resolution/ratio against the current schema and selected model; do not add web search, extra audio/reference operations, edit or extend implicitly. Do not hardcode a model based on an outdated description.
