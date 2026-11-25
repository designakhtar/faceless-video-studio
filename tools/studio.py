"""Faceless Video Studio helper. Needs only Python and FFmpeg; never spends credits.

  py tools/studio.py check                      is this computer ready?
  py tools/studio.py new <slug>                 make folders and a starter storyboard
  py tools/studio.py prompts <slug>             build and lint every Veo prompt
  py tools/studio.py join <slug>                join per-shot voice files; sets shot lengths + captions
  py tools/studio.py import <slug> s01="Name*"  copy Flow downloads into shots/<slug>/
  py tools/studio.py sheet <slug>               contact sheet of all clips
  py tools/studio.py preview <slug>             small 720p copy of the final video
  py tools/studio.py status [slug]              what is done, what is left
"""
import json, math, os, re, shutil, subprocess, sys, time, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOWNLOADS = Path.home() / "Downloads"
sys.stdout.reconfigure(encoding="utf-8")


def ff(*cmd):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        sys.exit(f"FFmpeg failed: {' '.join(map(str, cmd))}\n{r.stderr[-1200:]}")
    return r


def dur(path):
    return float(ff("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path).stdout)


def sb_path(slug):
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug):
        sys.exit("The slug must be lower-case words joined by hyphens, e.g. eid-offer")
    return ROOT / "storyboards" / f"{slug}.json"


def load(slug):
    if not sb_path(slug).exists():
        sys.exit(f"No storyboard: {sb_path(slug)}")
    return json.loads(sb_path(slug).read_text(encoding="utf-8"))


def save(slug, sb):
    sb_path(slug).write_text(json.dumps(sb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


def cmd_check():
    ok = True
    for label, good in [
        ("FFmpeg", shutil.which("ffmpeg") and shutil.which("ffprobe")),
        ("Node.js", shutil.which("node")),
        ("HyperFrames (npm install)", (ROOT / "node_modules/hyperframes").exists()),
        ("Bangla font", any((ROOT / "assets/fonts").glob("HindSiliguri*.ttf"))),
        ("Style sheet", (ROOT / "characters/style-sheet.md").exists()),
        ("Music bed", (ROOT / "assets/music/default.wav").exists()),
        ("Downloads folder", DOWNLOADS.exists()),
    ]:
        print(("OK      " if good else "MISSING ") + label)
        ok = ok and bool(good)
    print("READY" if ok else "NOT READY")
    print("Not testable here: Claude in Chrome + Flow sign-in, Higgsfield connector.")
    sys.exit(0 if ok else 1)


def cmd_new(slug):
    if sb_path(slug).exists():
        sys.exit(f"{slug} already exists; pick another slug.")
    for d in ("shots", "graphics", "audio"):
        (ROOT / d / slug / ("vo" if d == "audio" else "")).mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / "assets/music/default.wav", ROOT / "audio" / slug / "music.wav")
    save(slug, {
        "slug": slug, "title": "", "fps": 30, "width": 1920, "height": 1080,
        "voiceover": f"audio/{slug}/voiceover.wav", "captions": f"audio/{slug}/captions.srt",
        "music": f"audio/{slug}/music.wav", "music_volume": 0.2, "sfx": [],
        "caption_font": "Hind Siliguri", "caption_size": 20, "credits_per_shot": 10,
        "shots": [{"id": "s01", "type": "veo", "duration": 8, "narration": "", "visual": "",
                   "camera": "", "hero": True, "action": "", "setting": "", "ambient": "",
                   "veo_prompt": "", "clip": f"shots/{slug}/s01.mp4", "status": "pending", "credits_used": 0}]})
    print(f"Created storyboards/{slug}.json and folders")


def sheet_path(slug=None):
    """A video can have its own sheet at characters/<slug>.md; otherwise the channel sheet."""
    own = ROOT / "characters" / f"{slug}.md"
    return own if slug and own.exists() else ROOT / "characters/style-sheet.md"


def block(name, slug=None):
    text = sheet_path(slug).read_text(encoding="utf-8")
    m = re.search(rf"^## {re.escape(name)}\s*\n(.+?)(?=^## |\Z)", text, re.S | re.M)
    if not m:
        sys.exit(f"'## {name}' is missing from {sheet_path(slug).name}")
    return " ".join(m.group(1).split())


def lint(prompt, hero_name):
    """Codes, names and sizes in a prompt get drawn as text in the video."""
    bad = []
    if re.search(r"#[0-9A-Fa-f]{3,8}\b", prompt):
        bad.append("hex colour code")
    if hero_name and re.search(rf"\b{re.escape(hero_name)}\b", prompt, re.I):
        bad.append(f"hero name '{hero_name}'")
    if re.search(r"\b\d+\s*(cm|centimet|met(er|re)|mm)", prompt, re.I):
        bad.append("a size in numbers")
    if "\n" in prompt:
        bad.append("line break")
    if len(prompt.split()) > 190:
        bad.append(f"too long ({len(prompt.split())} words)")
    return bad


def cmd_prompts(slug):
    sb = load(slug)
    sheet = sheet_path(slug).read_text(encoding="utf-8")
    m = re.search(r"^- Name:\s*(\S+)", sheet, re.M)
    hero_name = m.group(1) if m else ""
    hero, style, avoid = block("VEO CHARACTER BLOCK", slug), block("VEO STYLE BLOCK", slug), block("VEO AVOID", slug)
    problems, out = 0, [f"# Veo prompts: {slug}", ""]
    for s in sb["shots"]:
        if s.get("type") != "veo":
            continue
        missing = [k for k in ("camera", "action", "setting") if not s.get(k)]
        if missing:
            if s.get("veo_prompt"):
                print(f"{s['id']}: old-style prompt kept as is")
            else:
                print(f"{s['id']}: MISSING {', '.join(missing)}"); problems += 1
                continue
        elif s.get("status") == "done":
            print(f"{s['id']}: already generated, prompt left unchanged")
        else:
            bits = [s["camera"], hero if s.get("hero", True) else "", s["action"], s["setting"], style,
                    f"Ambient: {s.get('ambient') or 'soft room tone'}", "No dialogue, no music", avoid]
            s["veo_prompt"] = " ".join(" ".join(b.split()).rstrip(".") + "." for b in bits if b)
        if s.get("status") != "done":
            bad = lint(s["veo_prompt"], hero_name)
            problems += bool(bad)
            print(f"{s['id']}: " + ("FIX " + ", ".join(bad) if bad else "ok"))
        out += [f"## {s['id']}", "```text", s["veo_prompt"], "```", ""]
    save(slug, sb)
    (ROOT / "storyboards" / f"{slug}-prompts.md").write_text("\n".join(out), encoding="utf-8", newline="\n")
    todo = [s for s in sb["shots"] if s.get("type") == "veo" and s.get("status") != "done"]
    print(f"{len(todo)} shots to generate x {sb.get('credits_per_shot', 10)} = "
          f"{len(todo) * sb.get('credits_per_shot', 10)} Flow credits (estimate; Flow's own figure decides)")
    sys.exit(1 if problems else 0)


def silences(path):
    err = ff("ffmpeg", "-hide_banner", "-i", path, "-af", "silencedetect=noise=-35dB:d=0.15", "-f", "null", "-").stderr
    a = [float(x) for x in re.findall(r"silence_start: ([-\d.]+)", err)]
    b = [float(x) for x in re.findall(r"silence_end: ([-\d.]+)", err)]
    return [(x, y) for x, y in zip(a, b) if x > 0.05]


def phrases(text):
    parts = [p.strip() for p in re.findall(r"[^।.?!,:;—]+[।.?!,:;—]*", text) if p.strip()]
    out = []
    for p in parts:  # join tiny pieces so a caption never flashes by
        if out and len(out[-1]) < 14 and out[-1][-1] not in "।?!":
            out[-1] += " " + p
        else:
            out.append(p)
    return out


def align(weights, sil, total):
    """Choose one pause for each boundary between texts, closest to its expected place."""
    n, need = len(sil), len(weights) - 1
    if need <= 0:
        return []
    if n < need:
        return None
    spoken_before = [a - sum(y - x for x, y in sil[:i]) for i, (a, _) in enumerate(sil)]
    spoken_total = total - sum(y - x for x, y in sil)
    cum, acc = [], 0.0
    for w in weights[:-1]:
        acc += w
        cum.append(acc / sum(weights) * spoken_total)
    INF = math.inf
    cost, back = [[INF] * n for _ in range(need)], [[-1] * n for _ in range(need)]
    for k in range(need):
        best, arg = (0.0, -1) if k == 0 else (INF, -1)
        for i in range(n):
            if k and i and cost[k - 1][i - 1] < best:
                best, arg = cost[k - 1][i - 1], i - 1
            if k and not i:
                continue
            gap = sil[i][1] - sil[i][0]
            cost[k][i] = best + (spoken_before[i] - cum[k]) ** 2 - 2.0 * min(gap, 1.0)
            back[k][i] = arg
    i = min(range(n), key=lambda j: cost[-1][j])
    picks = []
    for k in range(need - 1, -1, -1):
        picks.append(i)
        i = back[k][i]
    return [sil[j] for j in reversed(picks)]


def weight(text):
    """Rough speaking length: letters and vowel signs, digits read one by one, pauses at stops."""
    w = 0.0
    for ch in text:
        if ch.isdigit():
            w += 4
        elif ch == "্":  # hasanta joins two consonants
            w -= 0.5
        elif ch.isalpha() or unicodedata.category(ch) in ("Mn", "Mc"):
            w += 1
    return max(w, 1.0)


def stamp(t):
    ms = round(t * 1000)
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def mean_level(path):
    err = ff("ffmpeg", "-hide_banner", "-i", path, "-af", "volumedetect", "-f", "null", "-").stderr
    return float(re.search(r"mean_volume: ([-\d.]+)", err).group(1))


def cmd_join(slug, gap="0.45"):
    """One voice file per shot (audio/<slug>/vo/sNN.*) -> voiceover, exact shot lengths, captions."""
    sb, gap = load(slug), float(gap)
    vo, shots = ROOT / "audio" / slug / "vo", sb["shots"]
    files, missing = [], []
    for s in shots:
        hits = [f for e in ("wav", "mp3", "m4a") for f in vo.glob(f"{s['id']}.{e}")]
        if len(hits) != 1 or not s.get("narration", "").strip():
            missing.append(s["id"])
        else:
            files.append(hits[0])
    if missing:
        sys.exit("Need narration text and exactly one voice file for: " + ", ".join(missing))
    levels = [mean_level(f) for f in files]
    target = sorted(levels)[len(levels) // 2]
    cmd, flt = ["ffmpeg", "-v", "error", "-y"], ""
    for i, f in enumerate(files):
        cmd += ["-i", f]
        flt += (f"[{i}:a]aresample=48000,aformat=channel_layouts=mono,volume={target - levels[i]:.2f}dB,"
                f"alimiter=limit=0.95:level=0,apad=pad_dur={gap}[a{i}];")
    flt += "".join(f"[a{i}]" for i in range(len(files))) + f"concat=n={len(files)}:v=0:a=1[v]"
    voice = ROOT / sb["voiceover"]
    ff(*cmd, "-filter_complex", flt, "-map", "[v]", "-c:a", "pcm_s16le", voice)
    srt, n, at = [], 0, 0.0
    for s, f in zip(shots, files):
        d = dur(f)
        s["duration"] = round(d + gap, 3)
        if s.get("type") == "veo":  # cards already show their own text
            parts = phrases(s["narration"])
            cuts = align([weight(p) for p in parts], [g for g in silences(f) if g[1] < d - 0.1], d)
            if cuts is None:  # fewer pauses than phrases: share the time by text length
                acc, size, cuts = 0.0, sum(map(weight, parts)), []
                for p in parts[:-1]:
                    acc += weight(p)
                    cuts.append((acc / size * d,) * 2)
            edges = [0.0] + [y for _, y in cuts] + [d]
            for p, x, y in zip(parts, edges, edges[1:]):
                n += 1
                srt.append(f"{n}\n{stamp(at + x)} --> {stamp(at + y)}\n{p}\n")
        warn = "  OVER 11 s: split this shot in two" if s.get("type") == "veo" and s["duration"] > 11.1 else ""
        print(f"{s['id']} starts {at:6.2f}s  length {s['duration']:5.2f}s{warn}")
        at += s["duration"]
    shots[-1]["duration"] = round(shots[-1]["duration"] + 1.5, 3)  # breathing room at the end
    (ROOT / sb["captions"]).write_text("\n".join(srt), encoding="utf-8", newline="\n")
    save(slug, sb)
    print(f"voiceover {dur(voice):.2f}s, {n} captions")


def cmd_import(slug, *pairs):
    sb = load(slug)
    shots = {s["id"]: s for s in sb["shots"]}
    plan, failed = [], False
    for pair in pairs:
        sid, _, pattern = pair.partition("=")
        if sid not in shots or not pattern:
            sys.exit(f"Use sNN=\"Pattern*\" with a shot in the storyboard (got {pair})")
        hits = [f for f in DOWNLOADS.glob(pattern + ("" if pattern.endswith(".mp4") else "*.mp4"))
                if f.stat().st_mtime > time.time() - 24 * 3600]
        if len(hits) != 1:
            print(f"{sid}: expected 1 new file, found {len(hits)}"); failed = True
        else:
            plan.append((sid, hits[0]))
    if failed or not plan or len({f for _, f in plan}) != len(plan):
        sys.exit("Nothing copied. Make each pattern match exactly one different file.")
    for sid, f in plan:
        if dur(f) < 3:
            sys.exit(f"{f.name} is too short; nothing more copied.")
        dst = ROOT / shots[sid]["clip"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            shutil.move(dst, dst.with_name(f"{dst.stem}-old-{int(time.time())}.mp4"))
        shutil.copy2(f, dst)
        shots[sid]["status"] = "done"
        shots[sid]["credits_used"] = shots[sid].get("credits_used", 0) + sb.get("credits_per_shot", 10)
        print(f"{sid} <- {f.name}")
    save(slug, sb)


def cmd_sheet(slug):
    clips = [ROOT / s["clip"] for s in load(slug)["shots"] if (ROOT / s["clip"]).exists()]
    if not clips:
        sys.exit("No clips yet.")
    out = ROOT / "shots" / slug / "contact-sheet.jpg"
    cmd, flt = ["ffmpeg", "-v", "error", "-y"], ""
    for i, c in enumerate(clips):
        cmd += ["-i", c]
        flt += (f"[{i}:v]fps=4/{dur(c):.3f},scale=480:270:force_original_aspect_ratio=increase,crop=480:270,"
                f"setsar=1,tpad=stop_mode=clone:stop=4,trim=end_frame=4,tile=4x1[r{i}];")
    rows = "".join(f"[r{i}]" for i in range(len(clips)))
    flt += f"{rows}vstack=inputs={len(clips)}[v]" if len(clips) > 1 else "[r0]null[v]"
    ff(*cmd, "-filter_complex", flt, "-map", "[v]", "-frames:v", "1", out)
    print(out, "| rows:", ", ".join(c.stem for c in clips))


def cmd_preview(slug):
    out = ROOT / "final" / f"{slug}-720p.mp4"
    ff("ffmpeg", "-v", "error", "-y", "-i", ROOT / "final" / f"{slug}.mp4", "-vf", "scale=1280:-2",
       "-c:v", "libx264", "-crf", "25", "-c:a", "aac", "-b:a", "128k", out)
    print(f"{out} ({out.stat().st_size / 1e6:.1f} MB)")


def cmd_status(slug=None):
    for f in sorted((ROOT / "storyboards").glob("*.json")):
        sb = json.loads(f.read_text(encoding="utf-8"))
        s_ = sb["slug"]
        if slug and s_ != slug:
            continue
        need = [s["id"] for s in sb["shots"] if not s.get("clip") or not (ROOT / s["clip"]).exists()]
        print(f"{s_}: script={'yes' if (ROOT / f'scripts/{s_}.md').exists() else 'no'} "
              f"voice={'yes' if (ROOT / sb['voiceover']).exists() else 'no'} "
              f"clips missing={', '.join(need) or 'none'} "
              f"final={'yes' if (ROOT / f'final/{s_}.mp4').exists() else 'no'} "
              f"flow credits={sum(s.get('credits_used', 0) for s in sb['shots'])}")


if __name__ == "__main__":
    fn = globals().get(f"cmd_{sys.argv[1]}") if len(sys.argv) > 1 else None
    if not fn:
        sys.exit(__doc__)
    fn(*sys.argv[2:])
