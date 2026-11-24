# Storyboard JSON schema (`storyboards/<slug>.json`)

`tools/assemble.py` reads this file. Paths are relative to the studio folder.

```json
{
  "slug": "sleep-science",
  "title": "Why Your Brain Cleans Itself at Night",
  "fps": 30, "width": 1920, "height": 1080,
  "voiceover": "audio/sleep-science/voiceover.wav",
  "captions":  "audio/sleep-science/captions.srt",
  "music":     "audio/sleep-science/music.wav",
  "music_volume": 0.22,
  "intro": "graphics/sleep-science/intro.mp4",
  "outro": "graphics/sleep-science/outro.mp4",
  "overlays": [{"file": "graphics/sleep-science/section1.mov", "at": 30}],
  "sfx":      [{"file": "audio/sleep-science/sfx/whoosh.wav", "at": 29.6, "volume": 0.4}],
  "backend": "flow-veo-3.1-lite",
  "credits_per_shot": 10,
  "shots": [
    {
      "id": "s01",
      "duration": 8,
      "narration": "Did you know your brain cleans itself every night?",
      "visual": "Pip stands in a dark bedroom as a glowing brain hologram lights the room.",
      "camera": "slow push-in, eye level",
      "veo_prompt": "<full prompt from veo-prompt-template.md>",
      "clip":  "shots/sleep-science/s01.mp4",
      "image": "shots/sleep-science/s01.png",
      "status": "pending | generated | fallback",
      "credits_used": 0
    }
  ]
}
```

Rules
- `duration`s should add up to the voiceover length (assemble.py stretches the last shot if short).
- `at` times for overlays and sfx are measured from the start of shot 1 (the intro length is added automatically).
- Missing `clip` → uses `image` (Ken Burns move) → else a labelled placeholder. A finished video must have no placeholders.
