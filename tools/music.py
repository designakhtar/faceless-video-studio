"""Generate royalty-free background music locally with MusicGen-small (free).
Usage: python tools/music.py "calm uplifting lo-fi piano, soft drums" 30 audio/music.wav
Makes a loopable bed; FFmpeg loops/fades it to the full video length later."""
import sys
import numpy as np, soundfile as sf, torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration
prompt, seconds, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
proc = AutoProcessor.from_pretrained("facebook/musicgen-small")
model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
inputs = proc(text=[prompt], padding=True, return_tensors="pt")
tokens = int(seconds * model.config.audio_encoder.frame_rate)
with torch.no_grad():
    audio = model.generate(**inputs, do_sample=True, guidance_scale=3, max_new_tokens=tokens)
sr = model.config.audio_encoder.sampling_rate
sf.write(out, audio[0, 0].cpu().numpy().astype(np.float32), sr)
print(f"wrote {out} ({seconds}s @ {sr} Hz)")
