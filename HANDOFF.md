# Handoff — creative-promo (for the Claude Code session on Akhtar's Windows PC)

The cloud session could not reach this PC, so the 3D shots are generated here.
Talk to the user in simple Bangla. Follow `.claude/skills/faceless-video/SKILL.md`.

## Already done (do NOT redo or re-spend)
- Script APPROVED: `scripts/creative-promo.md`
- Style sheet (hero "Pixo"): `characters/style-sheet.md`
- Storyboard + timings + Veo prompts: `storyboards/creative-promo.json` (11 shots, 96 s)
  and copy-ready prompts in `storyboards/creative-promo-prompts.md`
- Graphic cards (free): `graphics/creative-promo/s03.mp4`, `s09.mp4`, `s11.mp4`
- Bangla voiceover (Higgsfield/ElevenLabs, 2.85 credits spent): `audio/creative-promo/voiceover.wav`
- Bangla captions (hand-timed, hidden during cards): `audio/creative-promo/captions.srt`
- Music (free, MusicGen): `audio/creative-promo/music.wav`
- Timing preview with placeholders: `final/creative-promo-PREVIEW.mp4`

## Remaining
1. Setup on Windows (one time):
   - Need: Node.js 18+, Python 3.10+, FFmpeg (`winget install Gyan.FFmpeg`), Google Chrome.
   - `npm install` in the studio root and in `.tools/google-flow-mcp`
     (set `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1`).
   - Copy `.tools/google-flow-mcp/config/flow.config.example.json` → `flow.config.json`;
     set `expectedAccount` (ask the user for their Google AI Pro email), keep the Windows Chrome path.
   - The `google-flow` MCP server is registered in `.mcp.json`; restart Claude Code so it loads and approve it.
   - Python tools are NOT needed for this step (voice, captions, music are done).
2. Start Chrome: `powershell -NoProfile -ExecutionPolicy Bypass -File .tools/google-flow-mcp/scripts/ensure-flow-chrome.ps1`
   User signs in to Google, then clicks "Sign in to Flow" once. Then `flow_connect`.
3. Generate the 8 Veo shots (type "veo" in the storyboard: s01 s02 s04 s05 s06 s07 s08 s10):
   - User already approved option A (~80 Flow credits total). Do ONE test shot first (s02, shows Pixo),
     show a frame to the user, and only continue after they say OK.
   - `flow_generate_video` with the shot's `veo_prompt`, `model:"lite"`, `duration:"8s"`, `ratio:"16:9"`,
     `project_name:"creative-promo"`, `auto_confirm:true`. Save as `shots/creative-promo/<id>.mp4`.
   - Update each shot's `status` and `credits_used` in the storyboard JSON.
4. Assemble: `python tools/assemble.py storyboards/creative-promo.json` → `final/creative-promo.mp4`.
   Captions need the Hind Siliguri font installed in Windows (install `assets/fonts/*.ttf`).
   Short clips are slowed up to 1.4x automatically (s04 and s07 have ~10.5–11 s slots).
5. QA 4 frames, write `final/creative-promo-report.md`, commit and push.

## Open item
Ask the user to listen at 1:20 of the preview: the phone number (+880 1819 831512) may be mis-read by the AI voice.
If wrong, regenerate only that line (quote the Higgsfield cost first) and splice it in.
