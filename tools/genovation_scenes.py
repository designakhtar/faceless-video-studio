"""Free animated-graphic stand-ins for the 13 Veo shots of genovation-ai-robots.

Builds graphics/genovation-ai-robots/<id>-hf/index.html from the s12-hf card (fonts, gsap).
Render each with: npx --no-install hyperframes render -o ../<id>.mp4 (inside the folder).
Content sits in the top ~78% so burned-in captions stay clear.
"""
import json, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG = "genovation-ai-robots"
GDIR = os.path.join(ROOT, "graphics", SLUG)
BASE = os.path.join(GDIR, "s12-hf")

ROBOT = """<svg viewBox="0 0 200 240" width="{w}" class="{cls}"><defs>
<linearGradient id="pearl{n}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F2F5FB"/><stop offset="1" stop-color="#9AA6C0"/></linearGradient></defs>
<ellipse cx="100" cy="95" rx="62" ry="78" fill="url(#pearl{n})"/>
<path d="M52 120 Q100 180 148 120" fill="none" stroke="#7C88A6" stroke-width="2"/>
<line x1="44" y1="92" x2="58" y2="92" stroke="#7C88A6" stroke-width="2"/><line x1="142" y1="92" x2="156" y2="92" stroke="#7C88A6" stroke-width="2"/>
<ellipse class="eye" cx="76" cy="92" rx="12" ry="6" fill="#2F6BFF"/><ellipse class="eye" cx="124" cy="92" rx="12" ry="6" fill="#2F6BFF"/>
<circle class="eyeglow" cx="76" cy="92" r="18" fill="#7FB2FF" opacity=".35"/><circle class="eyeglow" cx="124" cy="92" r="18" fill="#7FB2FF" opacity=".35"/>
<path d="M82 132 Q100 142 118 132" fill="none" stroke="#5A6684" stroke-width="3" stroke-linecap="round"/>
<rect x="84" y="170" width="32" height="26" rx="6" fill="#3A4462"/>
<path d="M30 240 Q30 196 100 196 Q170 196 170 240 Z" fill="#2B3350"/>
<line x1="60" y1="214" x2="140" y2="214" stroke="#2F6BFF" stroke-width="3" opacity=".9"/></svg>"""


def robot(w=220, cls="", n=0):
    return ROBOT.format(w=w, cls=cls, n=n)


PHONE = """<svg viewBox="0 0 200 200" width="{w}" id="{id}"><rect x="40" y="70" width="120" height="90" rx="18" fill="#1B2747" stroke="#7FB2FF" stroke-width="4"/>
<path d="M30 74 Q100 20 170 74 L150 96 Q100 64 50 96 Z" fill="#2F6BFF"/><circle cx="100" cy="118" r="20" fill="none" stroke="#7FB2FF" stroke-width="4"/>
<circle class="led" cx="140" cy="146" r="6" fill="#FF5A5A"/></svg>"""

TEMPLATE_HEAD = open(os.path.join(BASE, "index.html"), encoding="utf-8").read().split("</style>")[0]

EXTRA_CSS = """
.scene{position:absolute;left:0;right:0;top:70px;height:760px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;}
.row{display:flex;gap:40px;align-items:center;justify-content:center;}
.pill{border:2px solid rgba(127,178,255,.45);border-radius:20px;padding:22px 34px;background:rgba(14,26,58,.7);font-size:38px;}
.lbl{color:var(--hi);font-size:26px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;margin-top:14px;}
.ring{position:absolute;border:4px solid var(--hi);border-radius:50%;opacity:0;}
.coin{position:absolute;width:56px;height:56px;border-radius:50%;background:radial-gradient(circle at 35% 35%,#FFE89A,#E0A82E 60%,#8C6210);box-shadow:0 0 18px rgba(255,200,80,.5);}
.panel{border:2px solid rgba(127,178,255,.5);border-radius:26px;background:rgba(14,26,58,.85);box-shadow:0 30px 90px rgba(47,107,255,.35);}
.bubble{border-radius:30px;padding:26px 40px;font-size:44px;max-width:1100px;}
"""


def page(sid, dur, body, script):
    return f"""{TEMPLATE_HEAD}{EXTRA_CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="1920" data-height="1080">
<div id="glow" class="clip" data-start="0" data-duration="{dur}" data-track-index="0"></div>
<div id="streak" class="clip" data-start="0" data-duration="{dur}" data-track-index="1"></div>
<div id="card" class="clip" data-start="0" data-duration="{dur}" data-track-index="2">
{body}
</div></div>
<script>
const D={dur};
const tl=gsap.timeline({{paused:true}});
tl.fromTo("#glow",{{scale:.85,opacity:.5}},{{scale:1.12,opacity:1,duration:D,ease:"sine.inOut"}},0);
tl.fromTo("#streak",{{x:0}},{{x:3200,duration:1.1,ease:"power2.inOut"}},0);
tl.fromTo("#card",{{scale:1}},{{scale:1.04,duration:D,ease:"none"}},0);
const IN=(sel,t,y=40)=>tl.fromTo(sel,{{opacity:0,y:y}},{{opacity:1,y:0,duration:.6,ease:"power3.out"}},t);
{script}
tl.to("#card",{{opacity:0,duration:.3,ease:"power1.in"}},D-0.35);
window.__timelines["main"]=tl; tl.seek(0);
</script></body></html>"""


def scenes(d):
    S = {}
    # s01 night call, nobody answers
    S["s01"] = (f"""<div class="scene">
<div class="kicker" id="k">11:00 PM</div>
<div style="position:relative;width:520px;height:420px;margin:30px 0">
<div class="ring" id="r1" style="left:110px;top:60px;width:300px;height:300px"></div>
<div class="ring" id="r2" style="left:60px;top:10px;width:400px;height:400px"></div>
<div style="position:absolute;left:110px;top:60px">{PHONE.format(w=300, id='ph')}</div></div>
<div class="serif big" id="t" style="font-size:110px">Nobody picks up.</div></div>""",
    """IN("#k",.2); IN("#t",2.6);
for(let i=0;i<4;i++){tl.fromTo("#ph",{rotation:-6},{rotation:6,duration:.08,repeat:7,yoyo:true},.4+i*1.2);
 tl.fromTo(["#r1","#r2"],{opacity:.8,scale:.8},{opacity:0,scale:1.3,duration:1,stagger:.2},.4+i*1.2);}
tl.to(".led",{opacity:.15,duration:.3},D-1.6);""")

    # s02 leaking bucket
    coins = "".join(f'<div class="coin" id="c{i}" style="left:{230+ (i%3)*40}px;top:250px"></div>' for i in range(9))
    S["s02"] = (f"""<div class="scene"><div class="row" style="gap:90px">
<div style="position:relative;width:520px;height:600px">
<svg viewBox="0 0 300 260" width="420" style="position:absolute;left:50px;top:0">
<path d="M40 30 L260 30 L230 240 L70 240 Z" fill="#6B4A2B" stroke="#3B2614" stroke-width="6"/>
<line x1="55" y1="90" x2="245" y2="90" stroke="#3B2614" stroke-width="6"/><line x1="62" y1="170" x2="238" y2="170" stroke="#3B2614" stroke-width="6"/>
<path d="M140 240 L150 200 L136 180 L152 150" stroke="#050814" stroke-width="6" fill="none"/></svg>{coins}</div>
<div style="text-align:left">
<div class="pill" id="p1">Missed calls</div><div class="pill" id="p2" style="margin-top:26px">Leads nobody rang back</div>
<div class="pill" id="p3" style="margin-top:26px">Quotes nobody chased</div>
<div class="serif" id="t" style="font-size:78px;margin-top:44px;color:#FFD36B">Your business is leaking money.</div></div></div></div>""",
    """for(let i=0;i<9;i++){tl.fromTo("#c"+i,{y:0,opacity:1,x:0},{y:420,x:(i%2?60:-60),opacity:0,duration:1.1,ease:"power2.in"},.3+i*.75);}
IN("#p1",.5); IN("#p2",1.8); IN("#p3",3.1); IN("#t",4.6);""")

    # s04 Gena wakes up
    S["s04"] = (f"""<div class="scene"><div id="rb">{robot(330, 'gena', 4)}</div>
<div class="kicker" id="k" style="margin-top:26px">Genovation AI</div>
<div class="serif" id="t" style="font-size:80px;margin-top:14px">Finds the leaks. Then plugs them.</div></div>""",
    """tl.fromTo("#rb",{opacity:0,scale:.92},{opacity:1,scale:1,duration:1.2,ease:"power2.out"},0);
tl.fromTo(".eye",{scaleY:.05,transformOrigin:"50% 50%",opacity:.3},{scaleY:1,opacity:1,duration:.5,ease:"power2.out"},1.1);
tl.fromTo(".eyeglow",{opacity:0},{opacity:.45,duration:.4,yoyo:true,repeat:3},1.2);
IN("#k",2.0); IN("#t",2.5);""")

    # s06 answer, qualify, book, remind
    steps = ["Answer", "Qualify", "Book", "Remind"]
    pills = "".join(f'<div class="pill" id="st{i}"><span style="color:var(--hi)">{i+1}</span> {s}</div>' for i, s in enumerate(steps))
    S["s06"] = (f"""<div class="scene"><div class="row" style="gap:70px">
<div id="rb">{robot(250, '', 6)}</div>
<div class="panel" id="cal" style="width:520px;padding:34px;text-align:left">
<div class="lbl" style="margin:0">Tomorrow</div>
<div style="font-size:40px;margin-top:20px;opacity:.5">8:00 AM</div>
<div id="slot" style="font-size:44px;margin-top:16px;padding:18px 24px;border-radius:16px;background:rgba(47,107,255,.15);border:2px solid transparent">9:00 AM &nbsp;New customer</div>
<div style="font-size:40px;margin-top:16px;opacity:.5">10:00 AM</div></div></div>
<div class="kicker" id="k" style="margin-top:40px">Answered at 11 PM</div>
<div class="row" style="margin-top:26px;gap:24px">{pills}</div></div>""",
    """IN("#rb",.1); IN("#cal",.6); IN("#k",1.0);
for(let i=0;i<4;i++) IN("#st"+i,1.6+i*1.1,20);
tl.to("#slot",{background:"#2F6BFF",borderColor:"#7FB2FF",duration:.4},4.2);""")

    # s07 five agents
    names = ["Reception", "Sales", "Operations", "Marketing", "Finance"]
    team = "".join(f'<div id="a{i}" style="width:300px">{robot(190, "", 70+i)}<div class="lbl">{n}</div></div>' for i, n in enumerate(names))
    S["s07"] = (f"""<div class="scene"><div class="kicker" id="k">Meet your new team</div>
<div class="row" style="gap:20px;margin-top:40px">{team}</div>
<div class="serif" id="t" style="font-size:76px;margin-top:46px">Five AI agents, working together.</div></div>""",
    """IN("#k",.2); for(let i=0;i<5;i++) IN("#a"+i,1.0+i*.7,60); IN("#t",5.0);
tl.fromTo(".eye",{opacity:.3},{opacity:1,duration:.3,stagger:.35},1.4);""")

    # s08 one dashboard
    tiles = "".join(f'<div class="pill" id="d{i}" style="font-size:30px;padding:18px 20px">{n}</div>' for i, n in enumerate(names))
    S["s08"] = (f"""<div class="scene"><div class="panel" id="dash" style="width:1400px;padding:44px">
<div class="kicker" style="text-align:left">Gen AI Operating System</div>
<div class="row" style="gap:18px;margin-top:30px">{tiles}</div>
<div style="display:flex;gap:18px;margin-top:30px;height:150px;align-items:flex-end">
{''.join(f'<div class="bar" style="flex:1;height:{h}%;background:linear-gradient(#7FB2FF,#2F6BFF);border-radius:10px 10px 0 0"></div>' for h in [40,62,55,80,70,92,85])}</div></div>
<div class="row" id="f" style="margin-top:44px;gap:30px"><div class="tag">One login</div><div class="tag">One bill</div><div class="tag">Shared memory</div></div></div>""",
    """IN("#dash",.2,60); for(let i=0;i<5;i++) tl.fromTo("#d"+i,{opacity:0,x:(i-2)*160,y:-200},{opacity:1,x:0,y:0,duration:.8,ease:"power3.out"},.8+i*.35);
tl.fromTo(".bar",{scaleY:0,transformOrigin:"50% 100%"},{scaleY:1,duration:.7,stagger:.12,ease:"power2.out"},2.8);
IN("#f",4.6);""")

    # s09 software and websites
    S["s09"] = (f"""<div class="scene"><div class="row" style="gap:60px">
<div class="panel" id="win" style="width:900px;height:520px;padding:0;overflow:hidden;text-align:left">
<div style="height:54px;background:rgba(127,178,255,.15);display:flex;gap:12px;align-items:center;padding-left:22px">
<i style="width:16px;height:16px;border-radius:50%;background:#FF6B6B"></i><i style="width:16px;height:16px;border-radius:50%;background:#FFD36B"></i><i style="width:16px;height:16px;border-radius:50%;background:#6BE39A"></i></div>
<div id="b1" style="margin:34px;height:120px;border-radius:16px;background:linear-gradient(90deg,#2F6BFF,#7FB2FF)"></div>
<div style="display:flex;gap:24px;margin:0 34px">{''.join(f'<div class="blk" style="flex:1;height:200px;border-radius:16px;background:rgba(127,178,255,.18)"></div>' for _ in range(3))}</div></div>
<div class="panel" id="app" style="width:250px;height:480px;border-radius:40px;padding:30px">
{''.join(f'<div class="ab" style="height:70px;border-radius:14px;margin-bottom:20px;background:rgba(127,178,255,{a})"></div>' for a in [.5,.25,.25,.25,.25])}</div></div>
<div class="serif" id="t" style="font-size:74px;margin-top:40px">Software and websites, yours forever.</div>
<div class="tag" id="g" style="margin-top:22px">No per-seat fees, ever</div></div>""",
    """IN("#win",.2,60); IN("#b1",.9,20); tl.fromTo(".blk",{opacity:0,y:30},{opacity:1,y:0,stagger:.25,duration:.5},1.3);
IN("#app",1.6,60); tl.fromTo(".ab",{opacity:0,x:-20},{opacity:1,x:0,stagger:.18,duration:.4},2.1); IN("#t",3.0); IN("#g",3.8);""")

    # s10 AI search says your name
    S["s10"] = ("""<div class="scene"><div class="kicker" id="k">Get found by AI</div>
<div class="bubble" id="q" style="background:rgba(127,178,255,.14);border:2px solid rgba(127,178,255,.4);margin-top:40px;align-self:center;margin-left:-300px">Who's the best company in town?</div>
<div class="bubble" id="a" style="background:#2F6BFF;margin-top:30px;margin-left:300px;font-weight:700">It's <span class="serif" style="font-weight:400">your business.</span></div>
<div class="serif" id="t" style="font-size:66px;margin-top:50px">We make sure AI says your name.</div></div>""",
    """IN("#k",.1); IN("#q",.5,30); tl.fromTo("#a",{opacity:0,scale:.8},{opacity:1,scale:1,duration:.5,ease:"back.out(2)"},2.0);
tl.fromTo("#a",{boxShadow:"0 0 0 rgba(127,178,255,0)"},{boxShadow:"0 0 80px rgba(127,178,255,.9)",duration:.6,yoyo:true,repeat:3},2.5); IN("#t",3.0);""")

    # s11 video content
    frames = "".join('<div style="width:200px;height:130px;border-radius:10px;background:linear-gradient(135deg,#1B2C5C,#2F6BFF)"></div>' for _ in range(6))
    S["s11"] = (f"""<div class="scene"><div class="kicker" id="k">Video and UGC content</div>
<div id="strip" style="margin-top:40px;padding:26px 40px;background:#0A0F1E;border-top:14px dashed #333C58;border-bottom:14px dashed #333C58;display:flex;gap:26px">{frames}</div>
<svg id="play" viewBox="0 0 100 100" width="170" style="margin-top:-250px;position:relative"><circle cx="50" cy="50" r="48" fill="rgba(255,255,255,.92)"/><path d="M40 30 L72 50 L40 70 Z" fill="#2F6BFF"/></svg>
<div class="serif" id="t" style="font-size:72px;margin-top:110px">Video that sells for you.</div>
<div class="tag" id="g" style="margin-top:22px">You never have to be on camera</div></div>""",
    """IN("#k",.1); tl.fromTo("#strip",{opacity:0,x:-900},{opacity:1,x:0,duration:1.4,ease:"power3.out"},.4);
tl.fromTo("#play",{opacity:0,scale:.3},{opacity:1,scale:1,duration:.5,ease:"back.out(2)"},1.8); IN("#t",2.6); IN("#g",3.4);""")

    # s13 30 days, less than one salary
    S["s13"] = ("""<div class="scene"><div class="row" style="gap:120px">
<div style="text-align:center"><div class="serif" id="n" style="font-size:260px;line-height:1;color:#FFD36B">30</div><div class="lbl">days to live</div></div>
<div id="vs" style="font-size:60px;color:var(--mute)">·</div>
<div style="text-align:center"><div class="serif" id="s" style="font-size:110px;line-height:1.1">Less than<br>one salary</div></div></div></div>""",
    """tl.fromTo("#n",{opacity:0,scale:.6},{opacity:1,scale:1,duration:.7,ease:"back.out(1.6)"},.2); IN("#vs",1.0); IN("#s",1.4);""")

    # s14 guarantee shield
    S["s14"] = ("""<div class="scene"><div style="position:relative">
<div class="ring" id="r1" style="left:-60px;top:-60px;width:400px;height:400px"></div>
<svg id="sh" viewBox="0 0 200 230" width="280"><path d="M100 8 L188 40 L180 130 Q170 190 100 222 Q30 190 20 130 L12 40 Z" fill="#2F6BFF" stroke="#7FB2FF" stroke-width="8"/>
<path id="ck" d="M60 116 L90 146 L146 86" fill="none" stroke="#fff" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
<div class="kicker" id="k" style="margin-top:30px">Our guarantee</div>
<div class="serif" id="t" style="font-size:80px;margin-top:14px">Not live in 30 days?<br>You don't pay for the build.</div></div>""",
    """tl.fromTo("#sh",{opacity:0,scale:.5},{opacity:1,scale:1,duration:.7,ease:"back.out(1.7)"},.1);
tl.fromTo("#ck",{strokeDasharray:200,strokeDashoffset:200},{strokeDashoffset:0,duration:.6},.7);
tl.fromTo("#r1",{opacity:.8,scale:.7},{opacity:0,scale:1.5,duration:1.4,repeat:2},.8); IN("#k",1.1); IN("#t",1.6);""")

    # s15 town at dawn
    import random
    random.seed(15)
    blds, wins = [], []
    x = 0
    while x < 1700:
        w = random.randint(110, 200); h = random.randint(160, 380)
        blds.append(f'<rect x="{x}" y="{460-h}" width="{w-10}" height="{h}" fill="#0B1430"/>')
        for wy in range(460 - h + 30, 440, 56):
            for wx in range(x + 20, x + w - 40, 46):
                wins.append(f'<rect class="win" x="{wx}" y="{wy}" width="22" height="28" fill="#7FB2FF" opacity="0"/>')
        x += w
    S["s15"] = (f"""<div class="scene" style="justify-content:flex-start">
<div class="serif" id="t1" style="font-size:96px;margin-top:40px">Plug the holes first.</div>
<div class="serif" id="t2" style="font-size:96px;color:#FFD36B">Then fill the bucket.</div>
<svg viewBox="0 0 1700 460" width="1700" style="margin-top:30px"><circle id="sun" cx="850" cy="470" r="120" fill="#FFB85C" opacity=".8"/>{''.join(blds)}{''.join(wins)}</svg></div>""",
    """IN("#t1",.1); IN("#t2",1.2); tl.fromTo("#sun",{attr:{cy:520}},{attr:{cy:380},duration:D,ease:"none"},0);
tl.to(".win",{opacity:.9,duration:.2,stagger:{each:.012,from:"random"}},.4);""")

    # s16 question
    S["s16"] = (f"""<div class="scene"><div id="rb">{robot(250, '', 16)}</div>
<div class="serif" id="t" style="font-size:100px;margin-top:30px">So, what is the leak<br>costing <span style="color:#FFD36B">you?</span></div></div>""",
    """IN("#rb",0,30); IN("#t",.5);""")
    return S


def main(only=None):
    sb = json.load(open(os.path.join(ROOT, "storyboards", f"{SLUG}.json"), encoding="utf-8"))
    dur = {s["id"]: s["duration"] for s in sb["shots"]}
    for sid, (body, script) in scenes(dur).items():
        if only and sid not in only:
            continue
        out = os.path.join(GDIR, f"{sid}-hf")
        if not os.path.isdir(out):
            shutil.copytree(BASE, out)
        json.dump({"id": f"{SLUG}-{sid}", "name": f"{SLUG}-{sid}"}, open(os.path.join(out, "meta.json"), "w"))
        open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(page(sid, dur[sid], body, script))
        print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1:] or None)
