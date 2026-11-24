"""Make word-timed captions from a voiceover (free, runs locally).
Usage: python tools/captions.py audio/voiceover.wav audio/captions
Writes captions.srt (3-5 word chunks) and captions.json (every word with times)."""
import json, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel
src, out = sys.argv[1], sys.argv[2]
model = WhisperModel("small.en", device="cpu", compute_type="int8")
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
audio = np.frombuffer(pcm, dtype=np.float32)
segments, _ = model.transcribe(audio, word_timestamps=True, vad_filter=True)
words = [{"text": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)}
         for s in segments for w in s.words]
json.dump(words, open(out + ".json", "w"), indent=1)
def ts(t):
    h, r = divmod(t, 3600); m, s = divmod(r, 60)
    return f"{int(h):02}:{int(m):02}:{int(s):02},{int((s % 1) * 1000):03}"
chunks, cur = [], []
for w in words:
    cur.append(w)
    if len(cur) >= 4 or w["text"][-1:] in ".?!,":
        chunks.append(cur); cur = []
if cur: chunks.append(cur)
with open(out + ".srt", "w") as f:
    for i, c in enumerate(chunks, 1):
        f.write(f"{i}\n{ts(c[0]['start'])} --> {ts(c[-1]['end'])}\n{' '.join(w['text'] for w in c)}\n\n")
print(f"{len(words)} words, {len(chunks)} captions -> {out}.srt")
