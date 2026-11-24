# Veo shot prompt template

One shot = one prompt = one 8-second clip. Order matters: subject first, then action, scene, camera, style.

```text
[SHOT TYPE + CAMERA] Medium shot, slow push-in at eye level.
[CHARACTER BLOCK — pasted verbatim from characters/style-sheet.md]
[ACTION — one clear action for 8 seconds] Pip walks to the window and looks up as the sun rises.
[SETTING — specific, simple] A cozy small bedroom with a round window, plants on the sill, dawn light.
[STYLE BLOCK — pasted verbatim]
[AUDIO] Ambient: soft morning birdsong. No dialogue, no music.
Avoid: text, captions, subtitles, logos, watermarks, realistic humans, flicker.
```

Rules
- ONE action per shot. Two actions in 8 s look rushed.
- No on-screen text in Veo — titles and captions are added later by HyperFrames/FFmpeg.
- "No dialogue" always: the voiceover is added in the edit. Ambient sound is fine (assemble.py replaces clip audio with the mix).
- Name the camera move: static, slow push-in, slow pull-back, pan left/right, orbit, low-angle, top-down.
- Abstract ideas → a visual metaphor with the hero (e.g. "memory" = Pip sorting glowing cards into shelves).
- Continuity: if shot N+1 continues shot N, repeat the setting sentence exactly.
- Keep the whole prompt under ~150 words.

Example (copy-ready)

```text
Wide establishing shot, slow pull-back, slightly high angle.
Pip, a small friendly robot-explorer about 1 meter tall, rounded white ceramic body, large round head with a glossy black visor face showing two soft cyan (#4FD1FF) oval eyes, short stubby arms, orange (#FF8A3D) scarf, small antenna with a glowing cyan tip, smooth rounded proportions, no mouth, no text or logos on the body.
Pip stands at the center of a giant glowing brain made of soft neon pathways that pulse gently.
A dark cosmic void with floating light particles.
Stylized 3D animated feature-film look, soft global illumination, warm key light from the left with cool rim light, gentle subsurface scattering, shallow depth of field, 35mm lens, saturated but soft palette of navy (#1B1F3A), purple (#3A2C6B), warm orange (#FFB347) and cyan (#4FD1FF), clean uncluttered sets, smooth subtle motion, cinematic 16:9.
Ambient: low soft hum. No dialogue, no music.
Avoid: text, captions, subtitles, logos, watermarks, realistic humans, flicker.
```
