"""Generate the animated SVG assets for the GitHub profile README.

Theme: "silicon" — matte black, engineering dot grid, silver type and
circuit traces with a single emerald signal accent.

Usage: python scripts/gen_assets.py assets assets/icons
"""
import re
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
ICONS = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

SANS = "'Segoe UI',Inter,'Helvetica Neue',Arial,sans-serif"
MONO = "'JetBrains Mono','Fira Code',Consolas,'Courier New',monospace"
BG, PANEL, LINE = "#07090c", "#0d1117", "#21262d"
SILVER, MUTED, TRACE = "#e6edf3", "#7d8590", "#1f3a33"
SIGNAL = "#34d399"


def icon_path(name):
    return re.search(r' d="([^"]+)"', (ICONS / f"{name}.svg").read_text()).group(1)


def pts(*p):
    return "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in p)


DOTS = f'''<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#1b2128"/></pattern>'''

COMMON_CSS = f'''
  .pulse{{stroke:{SIGNAL};stroke-width:2.2;fill:none;stroke-linecap:round;stroke-dasharray:5 95;animation:flow linear infinite}}
  @keyframes flow{{from{{stroke-dashoffset:100}}to{{stroke-dashoffset:0}}}}
  .trace{{stroke:{TRACE};stroke-width:2;fill:none;stroke-linejoin:round}}
  .via{{fill:{BG};stroke:#2b4a42;stroke-width:2}}
  .fade{{opacity:0;animation:fade .7s ease forwards}}
  @keyframes fade{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
  .ping{{animation:ping 2s ease-out infinite;transform-box:fill-box;transform-origin:center}}
  @keyframes ping{{from{{transform:scale(1);opacity:.7}}to{{transform:scale(3);opacity:0}}}}
  .caret{{animation:blink 1s step-end infinite}}
  @keyframes blink{{50%{{opacity:0}}}}
'''


def traces(paths, vias=()):
    out = [f'<path class="trace" d="{d}"/>' for d in paths]
    for i, d in enumerate(paths):
        dur = 2.6 + (i * 0.37) % 2.2
        out.append(f'<path class="pulse" pathLength="100" d="{d}" style="animation-duration:{dur:.2f}s;animation-delay:-{(i * 0.71) % dur:.2f}s"/>')
    out += [f'<circle class="via" cx="{x:.0f}" cy="{y:.0f}" r="4.5"/>' for x, y in vias]
    return "\n".join(out)


# ---------------------------------------------------------------- hero
def hero():
    W, H = 1200, 420
    cx, cy, half = 1010, 205, 65  # chip centre and half size
    offs = [-40, -20, 0, 20, 40]
    paths, vias = [], []

    # left pins fan out and run under the text block, ending in vias
    for i, o in enumerate(offs):
        y = cy + o
        xt = 935 - (4 - i) * 10
        yb = 360 + i * 12
        paths.append(pts((cx - half, y), (xt, y), (xt - (yb - y), yb), (30 + i * 26, yb)))
        vias.append((30 + i * 26, yb))
    # right pins jog then leave the board
    for i, o in enumerate(offs):
        y = cy + o
        paths.append(pts((cx + half, y), (1110, y), (1130, y + o * 0.6), (W, y + o * 0.6)))
    # top and bottom pins
    for j, o in enumerate(offs):
        x = cx + o
        paths.append(pts((x, cy - half), (x, 105), (x + o * 0.6, 85 - abs(o) * 0.2), (x + o * 0.6, 0)))
        paths.append(pts((x, cy + half), (x, 305), (x + o * 0.6, 325), (x + o * 0.6, H)))

    pins = []
    for o in offs:
        pins += [
            f'<rect x="{cx - half - 8}" y="{cy + o - 3}" width="8" height="6" rx="1"/>',
            f'<rect x="{cx + half}" y="{cy + o - 3}" width="8" height="6" rx="1"/>',
            f'<rect x="{cx + o - 3}" y="{cy - half - 8}" width="6" height="8" rx="1"/>',
            f'<rect x="{cx + o - 3}" y="{cy + half}" width="6" height="8" rx="1"/>',
        ]

    chips = ["TypeScript", "Python", "FastAPI", "Next.js", "PostgreSQL", "LLM Agents"]
    chip_svg, x = [], 72
    for i, c in enumerate(chips):
        w = 22 + 8.2 * len(c)
        chip_svg.append(
            f'<g class="fade" style="animation-delay:{2.4 + i * 0.12:.2f}s">'
            f'<rect x="{x:.0f}" y="262" width="{w:.0f}" height="28" rx="6" fill="{PANEL}" stroke="{LINE}"/>'
            f'<text x="{x + w / 2:.0f}" y="281" text-anchor="middle" font-family="{MONO}" font-size="12.5" fill="#adbac7">{c}</text></g>'
        )
        x += w + 10

    name = "Shreyas Alva"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Shreyas Alva, full-stack engineer building AI agents and secure systems">
<defs>
  {DOTS}
  <linearGradient id="silver" x1="0" y1="0" x2="1" y2="0" spreadMethod="repeat">
    <stop offset="0" stop-color="#c9d1d9"/><stop offset=".42" stop-color="#c9d1d9"/><stop offset=".5" stop-color="#ffffff"/><stop offset=".58" stop-color="#c9d1d9"/><stop offset="1" stop-color="#c9d1d9"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="-1 0;1 0" dur="7s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="die" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1c2128"/><stop offset="1" stop-color="#0b0e12"/></linearGradient>
  <radialGradient id="heat"><stop offset="0" stop-color="{SIGNAL}" stop-opacity=".18"/><stop offset="1" stop-color="{SIGNAL}" stop-opacity="0"/></radialGradient>
  <linearGradient id="vign" x1="0" x2="1"><stop offset="0" stop-color="{BG}" stop-opacity=".0"/><stop offset=".55" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}" stop-opacity=".35"/></linearGradient>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="16"/></clipPath>
  <clipPath id="type"><rect x="70" y="200" height="40" width="0"><animate attributeName="width" from="0" to="780" begin="1s" dur="1.6s" fill="freeze" calcMode="spline" keySplines=".3 0 .2 1" keyTimes="0;1"/></rect></clipPath>
</defs>
<style>{COMMON_CSS}
  .ul{{stroke-dasharray:260;stroke-dashoffset:260;animation:draw 1.2s .9s cubic-bezier(.3,0,.2,1) forwards}}
  @keyframes draw{{to{{stroke-dashoffset:0}}}}
  .breathe{{animation:br 3.5s ease-in-out infinite}}
  @keyframes br{{50%{{opacity:.45}}}}
  .led{{animation:led 1.2s steps(2) infinite}}
  @keyframes led{{50%{{fill:#0f3d2e}}}}
</style>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <rect width="{W}" height="{H}" fill="url(#dots)"/>
  <circle class="breathe" cx="{cx}" cy="{cy}" r="190" fill="url(#heat)"/>
  {traces(paths, vias)}

  <!-- chip -->
  <g fill="#8b949e">{"".join(pins)}</g>
  <rect x="{cx - half}" y="{cy - half}" width="{half * 2}" height="{half * 2}" rx="8" fill="url(#die)" stroke="#3d444d" stroke-width="1.5"/>
  <rect x="{cx - half + 12}" y="{cy - half + 12}" width="{half * 2 - 24}" height="{half * 2 - 24}" rx="4" fill="none" stroke="#2d333b" stroke-dasharray="2 4"/>
  <circle cx="{cx - half + 14}" cy="{cy - half + 14}" r="3" fill="#3d444d"/>
  <text x="{cx}" y="{cy + 6}" text-anchor="middle" font-family="{SANS}" font-size="34" font-weight="800" fill="{SILVER}" letter-spacing="1">SA</text>
  <text x="{cx}" y="{cy + 28}" text-anchor="middle" font-family="{MONO}" font-size="9.5" fill="{MUTED}" letter-spacing="1.5">ALVA·X1 · 2026</text>
  <circle class="led" cx="{cx + half - 14}" cy="{cy + half - 14}" r="3" fill="{SIGNAL}"/>
  <rect width="{W}" height="{H}" fill="url(#vign)"/>

  <!-- left column -->
  <text x="72" y="92" font-family="{MONO}" font-size="14" fill="{MUTED}" class="fade" style="animation-delay:.2s"><tspan fill="{SIGNAL}">$</tspan> whoami <tspan fill="#484f58">--verbose</tspan></text>
  <g class="fade" style="animation-delay:.45s">
    <text x="68" y="178" font-family="{SANS}" font-size="84" font-weight="800" letter-spacing="-2" fill="url(#silver)">{name}</text>
  </g>
  <path class="ul" d="M72 196 H332" stroke="{SIGNAL}" stroke-width="3" stroke-linecap="round"/>
  <g clip-path="url(#type)">
    <text x="72" y="230" font-family="{MONO}" font-size="17" letter-spacing="1.5" fill="#adbac7">Full-Stack Engineer <tspan fill="#484f58">/</tspan> AI Agents &amp; MCP <tspan fill="#484f58">/</tspan> Secure Systems<tspan class="caret" fill="{SIGNAL}"> ▍</tspan></text>
  </g>
  {"".join(chip_svg)}
  <g class="fade" style="animation-delay:3.2s">
    <rect x="72" y="314" width="292" height="32" rx="6" fill="{PANEL}" stroke="{LINE}"/>
    <circle cx="92" cy="330" r="4.5" fill="{SIGNAL}"/><circle class="ping" cx="92" cy="330" r="4.5" fill="{SIGNAL}"/>
    <text x="106" y="335" font-family="{MONO}" font-size="12.5" fill="#adbac7">open to collaborations &amp; ideas</text>
  </g>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="none" stroke="{LINE}"/>
</g>
</svg>'''


# ------------------------------------------------------------- buttons
def button(label, sub, icon_d, width=250):
    H = 64
    border = f"M16 2 H{width - 16} Q{width - 2} 2 {width - 2} 16 V{H - 16} Q{width - 2} {H - 2} {width - 16} {H - 2} H16 Q2 {H - 2} 2 {H - 16} V16 Q2 2 16 2 Z"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{H}" viewBox="0 0 {width} {H}" role="img" aria-label="{label}">
<style>
  .run{{fill:none;stroke:{SIGNAL};stroke-width:2;stroke-linecap:round;stroke-dasharray:8 92;animation:r 4s linear infinite}}
  @keyframes r{{from{{stroke-dashoffset:100}}to{{stroke-dashoffset:0}}}}
  .ar{{animation:ar 1.8s ease-in-out infinite}}@keyframes ar{{50%{{transform:translateX(4px)}}}}
</style>
<path d="{border}" fill="{PANEL}" stroke="{LINE}" stroke-width="1.5"/>
<path class="run" pathLength="100" d="{border}"/>
<rect x="14" y="14" width="36" height="36" rx="8" fill="#161b22" stroke="{LINE}"/>
<g transform="translate(22 22) scale(.8333)"><path d="{icon_d}" fill="{SILVER}"/></g>
<text x="64" y="30" font-family="{SANS}" font-size="16" font-weight="700" fill="{SILVER}">{label}</text>
<text x="64" y="47" font-family="{MONO}" font-size="11" fill="{MUTED}">{sub}</text>
<text class="ar" x="{width - 30}" y="38" font-family="{SANS}" font-size="18" font-weight="700" fill="{SIGNAL}">→</text>
</svg>'''


# ----------------------------------------------------- section headers
def header(idx, title, hint):
    W, H = 900, 72
    x0 = 80 + 14 * len(title) + 40
    trace = pts((x0, 30), (W - 120, 30), (W - 100, 50), (W - 24, 50))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{title}">
<defs>{DOTS}</defs>
<style>{COMMON_CSS}
  .draw{{stroke-dasharray:1000;stroke-dashoffset:1000;animation:d 1.6s .3s cubic-bezier(.3,0,.2,1) forwards}}
  @keyframes d{{to{{stroke-dashoffset:0}}}}
</style>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="{BG}" stroke="{LINE}"/>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="url(#dots)"/>
<g class="fade">
  <rect x="18" y="20" width="44" height="32" rx="6" fill="{PANEL}" stroke="#2b4a42"/>
  <text x="40" y="41" text-anchor="middle" font-family="{MONO}" font-size="14" font-weight="700" fill="{SIGNAL}">{idx}</text>
  <text x="80" y="38" font-family="{SANS}" font-size="24" font-weight="800" fill="{SILVER}">{title}<tspan class="caret" fill="{SIGNAL}" font-weight="400">▍</tspan></text>
  <text x="80" y="57" font-family="{MONO}" font-size="12" fill="{MUTED}">{hint}</text>
</g>
<path class="trace draw" d="{trace}"/>
<path class="pulse" pathLength="100" d="{trace}" style="animation-duration:3.2s;animation-delay:1.9s"/>
<circle class="via" cx="{x0}" cy="30" r="4"/><circle class="via" cx="{W - 24}" cy="50" r="4"/>
</svg>'''


# --------------------------------------------------------------- footer
def footer():
    W, H = 1200, 140
    words = ["Building.", "Learning.", "Improving.", "Repeat."]
    spans = "".join(
        f'<tspan class="w" style="animation-delay:{i * 0.8:.1f}s">{w} </tspan>' for i, w in enumerate(words)
    )
    paths = [
        pts((0, 30), (140, 30), (170, 60), (260, 60)),
        pts((0, 110), (110, 110), (140, 80), (230, 80)),
        pts((W, 30), (W - 140, 30), (W - 170, 60), (W - 260, 60)),
        pts((W, 110), (W - 110, 110), (W - 140, 80), (W - 230, 80)),
    ]
    vias = [(260, 60), (230, 80), (W - 260, 60), (W - 230, 80)]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Building. Learning. Improving. Repeat.">
<defs>{DOTS}<clipPath id="c"><rect width="{W}" height="{H}" rx="16"/></clipPath></defs>
<style>{COMMON_CSS}
  .w{{fill:#484f58;animation:w 3.2s ease-in-out infinite}}
  @keyframes w{{0%,100%{{fill:#484f58}}15%,35%{{fill:{SILVER}}}}}
</style>
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="{BG}"/><rect width="{W}" height="{H}" fill="url(#dots)"/>
  {traces(paths, vias)}
  <text x="600" y="70" text-anchor="middle" font-family="{SANS}" font-size="28" font-weight="800" letter-spacing=".5">{spans}</text>
  <text x="600" y="100" text-anchor="middle" font-family="{MONO}" font-size="12.5" fill="{MUTED}"><tspan fill="{SIGNAL}">●</tspan> thanks for stopping by — star something you like</text>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="none" stroke="{LINE}"/>
</g>
</svg>'''


(OUT / "hero.svg").write_text(hero())
(OUT / "footer.svg").write_text(footer())

buttons = {
    "btn-linkedin": ("LinkedIn", "let's connect", icon_path("linkedin")),
    "btn-portfolio": ("Portfolio", "portfolio.vercel.app", icon_path("vercel")),
    "btn-projects": ("Projects", "see what I've shipped", icon_path("github")),
}
for fname, args in buttons.items():
    (OUT / f"{fname}.svg").write_text(button(*args))

headers = [
    ("01", "About me", "const shreyas = new Engineer()"),
    ("02", "Now building", "git log --since='this month'"),
    ("03", "Tech stack", "cat package.json | jq .deps"),
    ("04", "Featured projects", "ls ~/projects --sort=impact"),
    ("05", "Achievements", "./unlock --all --honestly"),
    ("06", "GitHub analytics", "gh api /users/Shreyas3435"),
    ("07", "Recent activity", "tail -f ~/.activity.log"),
]
for idx, title, hint in headers:
    slug = title.lower().replace(" ", "-")
    (OUT / f"h-{idx}-{slug}.svg").write_text(header(idx, title, hint))

print("\n".join(sorted(p.name for p in OUT.glob("*.svg"))))
