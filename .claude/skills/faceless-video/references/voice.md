# Voice (Higgsfield connector)

Voice used so far: model `text2speech_v2`, variant `elevenlabs`, voice_type `preset`,
voice_id `e2a2d2e6-9ed2-59cd-82af-feaa27f8a678` ("Grady"). Reuse it so the channel sounds the same.

1. Load the Higgsfield tools with ToolSearch: estimate_audio_cost, balance, generate_audio, jobs_wait.
2. Quote every line, add them up, show the total and the balance, wait for a yes.
   Seen in Nov 2026: 0.30-0.45 credits for an 8-9 s line; a whole 94 s script was 2.85. Many short lines may cost
   more than one long script. If the balance is too low, offer a shorter script or the user's own recording
   (one file per shot).
3. Generate with the returned quote refs, one job per shot. Download to `audio/<slug>/vo/sNN.mp3`.
   If a submit times out, check the job before sending again.
4. Spell digits out in words. Mixed Bangla + English words worked.
5. The user listens. Redo only bad lines, each with a new quote and yes.
6. `py tools/studio.py join <slug>` evens out loudness and sets timing.

Clone another person's voice only with that person's permission.
