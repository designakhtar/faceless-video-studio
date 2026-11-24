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
import json, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(cmd, cwd=None):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=cwd)
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
    sb = json.load(open(p(sb_path), encoding="utf-8"))
    slug, fps = sb["slug"], sb.get("fps", 30)
    W, H = sb.get("width", 1920), sb.get("height", 1080)
    enc = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-r", str(fps), "-an"]
    fit = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
           f"setsar=1,fps={fps}")
    tmp = tempfile.mkdtemp(prefix=f"assemble-{slug}-")
    # Bundled fonts are used directly, so they need not be installed.
    shutil.copytree(p("assets/fonts"), os.path.join(tmp, "fonts"))
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
            # Clip a bit short for its slot? Slow it down (up to 1.4x) before holding the last frame.
            stretch = min(max(d / max(dur(p(s["clip"])), 0.1), 1.0), 1.4)
            run(["ffmpeg", "-y", "-i", p(s["clip"]), "-vf",
                 f"setpts={stretch:.3f}*PTS,{fit},tpad=stop_mode=clone:stop_duration={d}",
                 "-t", str(d), *enc, out])
            report.append(f"{s['id']}: clip" + (f" (slowed {stretch:.2f}x)" if stretch > 1.01 else ""))
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
            arial = "C:/Windows/Fonts/arial.ttf"  # Windows FFmpeg has no default font
            font = ""
            if os.name == "nt" and os.path.exists(arial):
                shutil.copy(arial, os.path.join(tmp, "label.ttf"))
                font = "fontfile=label.ttf:"
            run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=0x1b1f3a:s={W}x{H}:r={fps}",
                 "-vf", f"drawtext={font}text='{label}':fontcolor=white:fontsize=64:"
                 "x=(w-tw)/2:y=(h-th)/2", "-t", str(d), *enc, out], cwd=tmp)
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
    open(lst, "w", encoding="utf-8").write("".join(f"file '{f}'\n" for f in norm))
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
        # Convert to ASS so we can use complex text shaping (needed for Bangla, Hindi, Arabic...).
        ass = os.path.join(tmp, "captions.ass")
        run(["ffmpeg", "-y", "-itsoffset", str(intro_len), "-i", p(sb["captions"]), ass])
        font, size = sb.get("caption_font", "DejaVu Sans"), sb.get("caption_size", 22)
        lines = open(ass, encoding="utf-8").read().splitlines()
        for i, ln in enumerate(lines):
            if ln.startswith("Style: Default,"):
                # Name,Font,Size,Primary,Secondary,Outline,Back,Bold,Italic,Underline,StrikeOut,
                # ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
                lines[i] = (f"Style: Default,{font},{size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,"
                            "-1,0,0,0,100,100,0,0,1,3,1,2,20,20,20,1")
        open(ass, "w", encoding="utf-8").write("\n".join(lines) + "\n")
        # Bare names + cwd=tmp: a Windows drive colon would break the filter string.
        vf.append(f"[{last}]ass=captions.ass:fontsdir=fonts:shaping=complex[vout]")
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
         "-c:a", "aac", "-b:a", "192k", "-t", str(video_len), "-movflags", "+faststart", final], cwd=tmp)

    print("\n".join(report))
    print(f"FINAL: {final}  ({dur(final):.1f}s, {os.path.getsize(final)/1e6:.1f} MB)")


if __name__ == "__main__":
    main(sys.argv[1])
