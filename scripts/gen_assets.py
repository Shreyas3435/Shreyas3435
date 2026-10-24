"""Generate the animated SVG assets for the GitHub profile README.

Usage: python scripts/gen_assets.py assets assets/icons
"""
import math
import random
import re
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
ICONS = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

SANS = "'Segoe UI',Inter,'Helvetica Neue',Arial,sans-serif"
MONO = "'JetBrains Mono','Fira Code',Consolas,'Courier New',monospace"
BLUE, PURPLE, GREEN, CYAN, PINK = "#58a6ff", "#a371f7", "#3fb950", "#39d0d8", "#f778ba"


def icon_path(name):
    return re.search(r' d="([^"]+)"', (ICONS / f"{name}.svg").read_text()).group(1)


# ---------------------------------------------------------------- hero
def hero():
    W, H = 1200, 420
    rnd = random.Random(7)
    stars = [(rnd.uniform(0, W), rnd.uniform(0, H * 0.62), rnd.uniform(0.6, 1.8)) for _ in range(70)]
    star_svg = "\n".join(
        f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="#c9d1d9" class="tw" style="animation-delay:{rnd.uniform(0, 4):.2f}s;animation-duration:{rnd.uniform(2.5, 5):.1f}s"/>'
        for x, y, r in stars
    )

    # Perspective grid: vertical lines converge on a vanishing point.
    vx, vy, gy = W / 2, 250, 300
    verticals = "\n".join(
        f'<line x1="{vx + (i * 12):.0f}" y1="{gy}" x2="{vx + i * 140:.0f}" y2="{H}"/>' for i in range(-12, 13)
    )
    horizontals = "\n".join(f'<line x1="0" y1="{gy + (k ** 1.7) * 2.2:.1f}" x2="{W}" y2="{gy + (k ** 1.7) * 2.2:.1f}"/>' for k in range(1, 14))

    # Orbit system on the right.
    cx, cy = 1010, 200
    orbits = [
        (60, 18, ["TS", "PY"], BLUE),
        (98, 26, ["AI", "SQL", "MCP"], PURPLE),
        (136, 34, ["SEC", "API", "UX", "CI"], GREEN),
    ]
    orbit_svg = []
    for idx, (r, dur, labels, col) in enumerate(orbits):
        nodes = []
        for j, lab in enumerate(labels):
            a = 2 * math.pi * j / len(labels) + idx
            nx, ny = cx + r * math.cos(a), cy + r * math.sin(a)
            w = 14 + 8 * len(lab)
            nodes.append(
                f'<g class="up" style="animation-duration:{dur}s">'
                f'<rect x="{nx - w / 2:.1f}" y="{ny - 11:.1f}" width="{w}" height="22" rx="11" fill="#0d1117" stroke="{col}" stroke-width="1.4"/>'
                f'<text x="{nx:.1f}" y="{ny + 4.5:.1f}" text-anchor="middle" font-family="{MONO}" font-size="12" font-weight="700" fill="{col}">{lab}</text></g>'
            )
        orbit_svg.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" stroke-opacity=".28" stroke-dasharray="3 6"/>'
            f'<g class="spin" style="animation-duration:{dur}s{";animation-direction:reverse" if idx == 1 else ""}">{"".join(nodes)}</g>'
        )
    # .up counter-rotates labels; reversed orbit needs reversed counter-rotation.
    orbit_markup = "\n".join(orbit_svg).replace(
        'class="up" style="animation-duration:26s"', 'class="up" style="animation-duration:26s;animation-direction:normal"'
    )

    chips = ["TypeScript", "Python", "FastAPI", "Next.js", "PostgreSQL", "LLM Agents"]
    chip_svg, x = [], 72
    for i, c in enumerate(chips):
        w = 22 + 8.2 * len(c)
        chip_svg.append(
            f'<g class="fade" style="animation-delay:{2.4 + i * 0.15:.2f}s">'
            f'<rect x="{x:.0f}" y="262" width="{w:.0f}" height="28" rx="14" fill="#161b22" stroke="#30363d"/>'
            f'<text x="{x + w / 2:.0f}" y="281" text-anchor="middle" font-family="{MONO}" font-size="12.5" fill="#c9d1d9">{c}</text></g>'
        )
        x += w + 10

    name = "Shreyas Alva"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Shreyas Alva, full-stack engineer building AI agents and secure systems">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#03050c"/><stop offset=".6" stop-color="#0a1024"/><stop offset="1" stop-color="#140b2e"/></linearGradient>
  <linearGradient id="name" x1="0" y1="0" x2="1" y2="0" spreadMethod="repeat">
    <stop offset="0" stop-color="{BLUE}"/><stop offset=".33" stop-color="{PURPLE}"/><stop offset=".66" stop-color="{CYAN}"/><stop offset="1" stop-color="{BLUE}"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="-1 0;0 0" dur="6s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="gridFade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff"/></linearGradient>
  <mask id="gm"><rect x="0" y="300" width="{W}" height="{H - 300}" fill="url(#gridFade)"/></mask>
  <radialGradient id="core"><stop offset="0" stop-color="#fff"/><stop offset=".35" stop-color="{BLUE}"/><stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></radialGradient>
  <filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="60"/></filter>
  <filter id="glow" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <linearGradient id="scan" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset=".5" stop-color="{CYAN}" stop-opacity=".35"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></linearGradient>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  <clipPath id="type"><rect x="70" y="200" height="40" width="0"><animate attributeName="width" from="0" to="760" begin="1s" dur="1.6s" fill="freeze" calcMode="spline" keySplines=".3 0 .2 1" keyTimes="0;1"/></rect></clipPath>
</defs>
<style>
  .tw{{animation:tw ease-in-out infinite}}
  @keyframes tw{{0%,100%{{opacity:.15}}50%{{opacity:.9}}}}
  .grid line{{stroke:{PURPLE};stroke-width:1;stroke-opacity:.55}}
  .hmove{{animation:hm 2.4s linear infinite}}
  @keyframes hm{{from{{transform:translateY(0)}}to{{transform:translateY(22px)}}}}
  .blob{{animation:drift 18s ease-in-out infinite alternate}}
  @keyframes drift{{from{{transform:translate(0,0)}}to{{transform:translate(80px,30px)}}}}
  .spin{{transform-origin:{cx}px {cy}px;animation:spin linear infinite}}
  .up{{transform-box:fill-box;transform-origin:center;animation:spin linear infinite reverse}}
  @keyframes spin{{to{{transform:rotate(360deg)}}}}
  .fade{{opacity:0;animation:fade .6s ease forwards}}
  @keyframes fade{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
  .g1{{animation:g1 5s steps(1) infinite}}.g2{{animation:g2 5s steps(1) infinite}}
  @keyframes g1{{0%,90%,100%{{transform:none;opacity:0}}91%{{transform:translate(-4px,1px);opacity:.8}}93%{{transform:translate(3px,-2px);opacity:.8}}95%{{opacity:0}}}}
  @keyframes g2{{0%,90%,100%{{transform:none;opacity:0}}92%{{transform:translate(4px,2px);opacity:.8}}94%{{transform:translate(-3px,0);opacity:.8}}96%{{opacity:0}}}}
  .pulse{{animation:pulse 2s ease-out infinite;transform-box:fill-box;transform-origin:center}}
  @keyframes pulse{{from{{transform:scale(1);opacity:.8}}to{{transform:scale(3.2);opacity:0}}}}
  .scan{{animation:scan 7s ease-in-out infinite}}
  @keyframes scan{{0%{{transform:translateX(-300px)}}60%,100%{{transform:translateX({W + 300}px)}}}}
  .core{{animation:breathe 3s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
  @keyframes breathe{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.12)}}}}
  .caret{{animation:blink 1s step-end infinite}}
  @keyframes blink{{50%{{opacity:0}}}}
</style>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <g filter="url(#blur)" opacity=".55">
    <circle class="blob" cx="260" cy="120" r="150" fill="#1f6feb"/>
    <circle class="blob" cx="900" cy="80" r="140" fill="#8957e5" style="animation-delay:-6s"/>
    <circle class="blob" cx="620" cy="360" r="160" fill="#0e7490" style="animation-delay:-12s"/>
  </g>
  {star_svg}
  <g class="grid" mask="url(#gm)">
    {verticals}
    <g class="hmove">{horizontals}</g>
  </g>
  <rect class="scan" x="0" y="0" width="240" height="{H}" fill="url(#scan)" opacity=".5"/>

  <!-- left column -->
  <text x="72" y="92" font-family="{MONO}" font-size="15" fill="{GREEN}" class="fade" style="animation-delay:.2s">~/shreyas $ <tspan fill="#8b949e">./init --profile</tspan></text>
  <g class="fade" style="animation-delay:.5s">
    <text x="70" y="180" font-family="{SANS}" font-size="86" font-weight="800" letter-spacing="-2" fill="{CYAN}" class="g1">{name}</text>
    <text x="70" y="180" font-family="{SANS}" font-size="86" font-weight="800" letter-spacing="-2" fill="{PINK}" class="g2">{name}</text>
    <text x="70" y="180" font-family="{SANS}" font-size="86" font-weight="800" letter-spacing="-2" fill="url(#name)" filter="url(#glow)">{name}</text>
  </g>
  <g clip-path="url(#type)">
    <text x="72" y="226" font-family="{MONO}" font-size="18" letter-spacing="1.8" fill="#c9d1d9">FULL-STACK ENGINEER <tspan fill="{PURPLE}">//</tspan> AI AGENTS &amp; MCP <tspan fill="{PURPLE}">//</tspan> SECURE SYSTEMS<tspan class="caret" fill="{CYAN}"> _</tspan></text>
  </g>
  {"".join(chip_svg)}
  <g class="fade" style="animation-delay:3.4s">
    <rect x="72" y="320" width="300" height="34" rx="17" fill="#0d1117" fill-opacity=".85" stroke="{GREEN}" stroke-opacity=".6"/>
    <circle cx="94" cy="337" r="5" fill="{GREEN}"/><circle class="pulse" cx="94" cy="337" r="5" fill="{GREEN}"/>
    <text x="110" y="342" font-family="{MONO}" font-size="13" fill="#e6edf3">open to collaborations &amp; ideas</text>
  </g>

  <!-- right column: orbit system -->
  <g class="fade" style="animation-delay:.8s">
    <circle class="core" cx="{cx}" cy="{cy}" r="46" fill="url(#core)" opacity=".9"/>
    <circle cx="{cx}" cy="{cy}" r="30" fill="#0d1117" stroke="{BLUE}" stroke-width="2"/>
    <text x="{cx}" y="{cy + 8}" text-anchor="middle" font-family="{SANS}" font-size="22" font-weight="800" fill="#e6edf3">SA</text>
    {orbit_markup}
  </g>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="none" stroke="#30363d"/>
</g>
</svg>'''


# ------------------------------------------------------------- buttons
def button(label, sub, icon_d, col, width=250):
    H = 64
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{H}" viewBox="0 0 {width} {H}" role="img" aria-label="{label}">
<defs>
  <linearGradient id="b" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{col}"/><stop offset=".5" stop-color="{PURPLE}"/><stop offset="1" stop-color="{CYAN}"/>
    <animateTransform attributeName="gradientTransform" type="rotate" values="0 .5 .5;360 .5 .5" dur="4s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="sh" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".14"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <clipPath id="c"><rect x="2" y="2" width="{width - 4}" height="{H - 4}" rx="14"/></clipPath>
</defs>
<style>.sh{{animation:sh 3.5s ease-in-out infinite}}@keyframes sh{{0%{{transform:translateX(-120px)}}50%,100%{{transform:translateX({width + 40}px)}}}}
.ar{{animation:ar 1.6s ease-in-out infinite}}@keyframes ar{{50%{{transform:translateX(4px)}}}}</style>
<rect x="2" y="2" width="{width - 4}" height="{H - 4}" rx="14" fill="#0b0f19"/>
<g clip-path="url(#c)"><rect class="sh" x="0" y="0" width="90" height="{H}" fill="url(#sh)"/></g>
<rect x="2" y="2" width="{width - 4}" height="{H - 4}" rx="14" fill="none" stroke="url(#b)" stroke-width="2"/>
<rect x="16" y="14" width="36" height="36" rx="10" fill="{col}" fill-opacity=".14"/>
<g transform="translate(24 22) scale(.8333)"><path d="{icon_d}" fill="{col}"/></g>
<text x="66" y="30" font-family="{SANS}" font-size="16" font-weight="700" fill="#e6edf3">{label}</text>
<text x="66" y="47" font-family="{MONO}" font-size="11" fill="#8b949e">{sub}</text>
<text class="ar" x="{width - 30}" y="38" font-family="{SANS}" font-size="18" font-weight="700" fill="{col}">→</text>
</svg>'''


# ----------------------------------------------------- section headers
def header(idx, title, hint, col):
    W, H = 900, 64
    x0 = 68 + 15 * len(title) + 40
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{title}">
<defs>
  <linearGradient id="t" x1="0" x2="1"><stop offset="0" stop-color="{col}"/><stop offset="1" stop-color="{PURPLE}"/></linearGradient>
  <linearGradient id="l" x1="{x0}" x2="{W}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{col}"/><stop offset=".6" stop-color="{PURPLE}" stop-opacity=".6"/><stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></linearGradient>
</defs>
<style>
  .ln{{stroke-dasharray:900;stroke-dashoffset:900;animation:draw 1.6s .3s cubic-bezier(.3,0,.2,1) forwards}}
  @keyframes draw{{to{{stroke-dashoffset:0}}}}
  .dot{{animation:run 4s 1.9s ease-in-out infinite;opacity:0}}
  @keyframes run{{0%{{transform:translateX(0);opacity:0}}10%{{opacity:1}}90%{{opacity:1}}100%{{transform:translateX({W - x0 - 20}px);opacity:0}}}}
  .in{{animation:in .6s ease both}}
  @keyframes in{{from{{opacity:0;transform:translateX(-10px)}}to{{opacity:1;transform:none}}}}
  .cur{{animation:b 1s step-end infinite}}@keyframes b{{50%{{opacity:0}}}}
</style>
<g class="in">
  <rect x="1" y="12" width="52" height="30" rx="8" fill="{col}" fill-opacity=".12" stroke="{col}" stroke-opacity=".7"/>
  <text x="27" y="32" text-anchor="middle" font-family="{MONO}" font-size="14" font-weight="700" fill="{col}">{idx}</text>
  <text x="68" y="36" font-family="{SANS}" font-size="26" font-weight="800" fill="url(#t)">{title}<tspan class="cur" fill="{col}">▍</tspan></text>
  <text x="68" y="56" font-family="{MONO}" font-size="12" fill="#8b949e">{hint}</text>
</g>
<line class="ln" x1="{x0}" y1="27" x2="{W}" y2="27" stroke="url(#l)" stroke-width="2"/>
<circle class="dot" cx="{x0}" cy="27" r="3.5" fill="{col}"/>
</svg>'''


# --------------------------------------------------------------- footer
def footer():
    W, H = 1200, 150
    words = ["Building.", "Learning.", "Improving.", "Repeat."]
    cols = [BLUE, PURPLE, CYAN, GREEN]
    spans, x = [], 0
    for i, (w, c) in enumerate(zip(words, cols)):
        spans.append(f'<tspan fill="{c}" class="w" style="animation-delay:{i * 0.5:.1f}s">{w} </tspan>')
    verticals = "\n".join(f'<line x1="{600 + i * 12}" y1="0" x2="{600 + i * 120}" y2="{H}"/>' for i in range(-14, 15))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Building. Learning. Improving. Repeat.">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#140b2e"/><stop offset="1" stop-color="#03050c"/></linearGradient>
  <linearGradient id="f" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <mask id="m"><rect width="{W}" height="{H}" fill="url(#f)"/></mask>
  <clipPath id="c"><rect width="{W}" height="{H}" rx="18"/></clipPath>
</defs>
<style>
  .grid line{{stroke:{PURPLE};stroke-opacity:.45}}
  .mv{{animation:mv 2.4s linear infinite}}@keyframes mv{{to{{transform:translateY(-20px)}}}}
  .w{{animation:w 4s ease-in-out infinite}}@keyframes w{{0%,100%{{opacity:.35}}20%,40%{{opacity:1}}}}
</style>
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <g class="grid" mask="url(#m)">{verticals}<g class="mv">{"".join(f'<line x1="0" y1="{20 * k}" x2="{W}" y2="{20 * k}"/>' for k in range(0, 10))}</g></g>
  <text x="600" y="72" text-anchor="middle" font-family="{SANS}" font-size="30" font-weight="800" letter-spacing="1">{"".join(spans)}</text>
  <text x="600" y="104" text-anchor="middle" font-family="{MONO}" font-size="13" fill="#8b949e">thanks for stopping by — star something you like ⭐</text>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="none" stroke="#30363d"/>
</g>
</svg>'''


(OUT / "hero.svg").write_text(hero())
(OUT / "footer.svg").write_text(footer())

buttons = {
    "btn-linkedin": ("LinkedIn", "let's connect", icon_path("linkedin"), "#4c9aff"),
    "btn-portfolio": ("Portfolio", "portfolio.vercel.app", icon_path("vercel"), "#e6edf3"),
    "btn-projects": ("Projects", "see what I've shipped", icon_path("github"), GREEN),
}
for fname, args in buttons.items():
    (OUT / f"{fname}.svg").write_text(button(*args))

headers = [
    ("01", "About me", "const shreyas = new Engineer()", BLUE),
    ("02", "Now building", "git log --since='this month'", PURPLE),
    ("03", "Tech stack", "cat package.json | jq .deps", CYAN),
    ("04", "Featured projects", "ls ~/projects --sort=impact", GREEN),
    ("05", "GitHub analytics", "gh api /users/Shreyas3435", PINK),
    ("06", "Recent activity", "tail -f ~/.activity.log", "#d29922"),
]
for idx, title, hint, col in headers:
    slug = title.lower().replace(" ", "-")
    (OUT / f"h-{idx}-{slug}.svg").write_text(header(idx, title, hint, col))

print("\n".join(sorted(p.name for p in OUT.glob("*.svg"))))
