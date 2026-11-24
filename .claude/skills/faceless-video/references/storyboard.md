# storyboards/<slug>.json

`studio.py new` creates it. One entry per shot, in order:

```json
{"id": "s01", "type": "veo", "duration": 8, "narration": "spoken words, shown as captions",
 "visual": "short note for the user", "camera": "Wide shot, slow push-in.", "hero": true,
 "action": "One visible action with a clear end state.", "setting": "One simple place and light.",
 "ambient": "soft street sounds", "veo_prompt": "", "clip": "shots/<slug>/s01.mp4",
 "status": "pending", "credits_used": 0}
```

- `duration` and captions are written by `join`, `veo_prompt` by `prompts`. Do not set them by hand.
- `hero: false` when the character is not in the shot.
- Graphic card: `"type": "graphic"`, `"clip": "graphics/<slug>/s03.mp4"`, plus narration. Captions are hidden on cards.
- `status` becomes `done` on import. `prompts` never changes a `done` shot.
- A clip is slowed at most 1.4x, so one 8 s clip covers about 11 s.
- Captions show `narration`. If the voice needs a different spelling, put that only in the voice prompt.
- Optional top level: `intro`, `outro`, `overlays`, `sfx` (see `tools/assemble.py`).
