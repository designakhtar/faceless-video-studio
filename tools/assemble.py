"""Assemble a finished video from a storyboard JSON (FFmpeg only, free).

Usage:  python3 tools/assemble.py storyboards/<slug>.json

Storyboard fields used (paths are relative to the studio folder):
  slug, fps (30), width (1920), height (1080)
  voiceover   audio/<slug>/voiceover.wav      (required)
  music       audio/<slug>/music.wav          (optional, looped + ducked under voice)
  sfx         [{"file": "...", "at": 12.5, "volume": 0.6}]   (optional)
  captions    audio/<slug>/captions.srt       (optional, burned in)
  intro       graphics/<slug>/intro.mp4       (optional title card before shot 1)
  outro       graphics/<slug>/outro.mp4       (optional end card)
  overlays    [{"file": "graphics/<slug>/x.mov", "at": 30}]  (optional alpha .mov/.webm on top)
  shots       [{"id": "s01", "duration": 8, "clip": "shots/<slug>/s01.mp4",
                "image": "shots/<slug>/s01.png"}]
For each shot: uses the clip if present; else Ken-Burns-animates the image; else a
labelled placeholder (so a missing shot never breaks the build). Shots shorter than
their slot hold the last frame; longer ones are trimmed.
Output: final/<slug>.mp4 (H.264 + AAC, loudness -14 LUFS for YouTube).
"""
import json, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"FFmpeg failed:\n{' '.join(cmd)}\n{r.stderr[-2000:]}")


def dur(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    return float(out.strip() or 0)


def p(rel):
    return rel if os.path.isabs(rel) else os.path.join(ROOT, rel)


def exists(rel):
    return bool(rel) and os.path.exists(p(rel))


def main(sb_path):
    sb = json.load(open(p(sb_path)))
    slug, fps = sb["slug"], sb.get("fps", 30)
    W, H = sb.get("width", 1920), sb.get("height", 1080)
    enc = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-r", str(fps), "-an"]
    fit = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
           f"setsar=1,fps={fps}")
    tmp = tempfile.mkdtemp(prefix=f"assemble-{slug}-")
    voice = p(sb["voiceover"])
    voice_len = dur(voice)

    # Make the shots cover the whole voiceover: stretch the last shot if needed.
    shots = sb["shots"]
    total = sum(s["duration"] for s in shots)
    if voice_len > total:
        shots[-1]["duration"] += round(voice_len - total + 0.5, 2)

    parts, report = [], []
    if exists(sb.get("intro")):
        parts.append(p(sb["intro"]))
    intro_len = dur(parts[0]) if parts else 0.0

    for i, s in enumerate(shots):
        d, out = s["duration"], os.path.join(tmp, f"shot{i:03}.mp4")
        if exists(s.get("clip")):
            run(["ffmpeg", "-y", "-i", p(s["clip"]), "-vf",
                 f"{fit},tpad=stop_mode=clone:stop_duration={d}", "-t", str(d), *enc, out])
            report.append(f"{s['id']}: clip")
        elif exists(s.get("image")):
            frames = int(d * fps)
            run(["ffmpeg", "-y", "-loop", "1", "-i", p(s["image"]), "-vf",
                 f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
                 f"zoompan=z='min(1+0.0008*on,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                 f":d={frames}:s={W}x{H}:fps={fps},setsar=1",
                 "-frames:v", str(frames), *enc, out])
            report.append(f"{s['id']}: image (Ken Burns)")
        else:
            label = f"MISSING SHOT {s['id']}".replace(":", "")
            run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=0x1b1f3a:s={W}x{H}:r={fps}",
                 "-vf", f"drawtext=text='{label}':fontcolor=white:fontsize=64:"
                 "x=(w-tw)/2:y=(h-th)/2", "-t", str(d), *enc, out])
            report.append(f"{s['id']}: PLACEHOLDER (no clip or image found)")
        parts.append(out)

    if exists(sb.get("outro")):
        parts.append(p(sb["outro"]))

    # Normalise intro/outro too, then join everything.
    norm = []
    for i, f in enumerate(parts):
        if f.startswith(tmp):
            norm.append(f)
            continue
        out = os.path.join(tmp, f"card{i:03}.mp4")
        run(["ffmpeg", "-y", "-i", f, "-vf", fit, *enc, out])
        norm.append(out)
    lst = os.path.join(tmp, "list.txt")
    open(lst, "w").write("".join(f"file '{f}'\n" for f in norm))
    body = os.path.join(tmp, "body.mp4")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", body])
    video_len = dur(body)

    # Video filters: alpha overlays, then burned-in captions (shifted by intro length).
    inputs, vf, last = ["-i", body], [], "0:v"
    for k, ov in enumerate(sb.get("overlays", [])):
        if not exists(ov.get("file")):
            continue
        inputs += ["-itsoffset", str(ov["at"] + intro_len), "-i", p(ov["file"])]
        idx = len([x for x in inputs if x == "-i"]) - 1
        vf.append(f"[{last}][{idx}:v]overlay=eof_action=pass[ov{k}]")
        last = f"ov{k}"
    if exists(sb.get("captions")):
        srt = os.path.join(tmp, "captions.srt")
        run(["ffmpeg", "-y", "-itsoffset", str(intro_len), "-i", p(sb["captions"]), srt])
        style = ("FontName=DejaVu Sans,FontSize=22,Bold=1,PrimaryColour=&H00FFFFFF,"
                 "OutlineColour=&H00000000,BorderStyle=1,Outline=3,Shadow=1,"
                 "Alignment=2,MarginV=60")
        vf.append(f"[{last}]subtitles='{srt}':force_style='{style}'[vout]")
        last = "vout"

    # Audio: voice (delayed by intro) + looped music ducked under voice + sound effects.
    n = len([x for x in inputs if x == "-i"])
    inputs += ["-i", voice]
    vi, af = n, []
    delay = int(intro_len * 1000)
    af.append(f"[{vi}:a]aresample=48000,adelay={delay}|{delay},apad,"
              f"atrim=0:{video_len},asplit=2[voice][key]")
    mix = ["[voice]"]
    if exists(sb.get("music")):
        inputs += ["-stream_loop", "-1", "-i", p(sb["music"])]
        mi = vi + 1
        fade_at = max(video_len - 3, 0)
        af.append(f"[{mi}:a]aresample=48000,atrim=0:{video_len},volume={sb.get('music_volume', 0.22)},"
                  f"afade=t=in:d=2,afade=t=out:st={fade_at}:d=3[mus]")
        af.append("[mus][key]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[duck]")
        mix.append("[duck]")
    else:
        af.append("[key]anullsink")
    for j, fx in enumerate(sb.get("sfx", [])):
        if not exists(fx.get("file")):
            continue
        inputs += ["-i", p(fx["file"])]
        xi = len([x for x in inputs if x == "-i"]) - 1
        ms = int((fx["at"] + intro_len) * 1000)
        af.append(f"[{xi}:a]aresample=48000,volume={fx.get('volume', 0.6)},adelay={ms}|{ms}[fx{j}]")
        mix.append(f"[fx{j}]")
    af.append(f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0:duration=first,"
              "loudnorm=I=-14:TP=-1.5:LRA=11[aout]")

    os.makedirs(p("final"), exist_ok=True)
    final = p(f"final/{slug}.mp4")
    run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(vf + af),
         "-map", f"[{last}]" if vf else "0:v", "-map", "[aout]",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-t", str(video_len), "-movflags", "+faststart", final])

    print("\n".join(report))
    print(f"FINAL: {final}  ({dur(final):.1f}s, {os.path.getsize(final)/1e6:.1f} MB)")


if __name__ == "__main__":
    main(sys.argv[1])
