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
    ("05", "GitHub analytics", "gh api /users/Shreyas3435"),
    ("06", "Recent activity", "tail -f ~/.activity.log"),
]
for idx, title, hint in headers:
    slug = title.lower().replace(" ", "-")
    (OUT / f"h-{idx}-{slug}.svg").write_text(header(idx, title, hint))


# ------------------------------------------------------- content panels
def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def wrap(text, width):
    lines, cur = [], ""
    for w in text.split():
        if len(cur) + len(w) + 1 > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    return lines + [cur]


def panel(W, H, body, extra_css=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>{DOTS}</defs>
<style>{COMMON_CSS}{extra_css}</style>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="{BG}" stroke="{LINE}"/>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="url(#dots)"/>
{body}
</svg>"""


def logo(name, x, y, size, fill=SILVER):
    k = size / 24
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.4f})"><path d="{icon_path(name)}" fill="{fill}"/></g>'


def terminal():
    W, H = 900, 250
    rows = [
        (54, f'<tspan fill="{SIGNAL}">$</tspan> whoami'),
        (80, f'<tspan fill="{SILVER}" font-weight="700">Shreyas Alva</tspan> <tspan fill="#484f58">·</tspan> Full-Stack &amp; AI Engineer'),
        (104, 'Building agent tooling, MCP servers and products that ship.'),
        (140, f'<tspan fill="{SIGNAL}">$</tspan> cat focus.txt'),
        (166, f'agents <tspan fill="#484f58">·</tspan> developer tooling <tspan fill="#484f58">·</tspan> secure web apps <tspan fill="#484f58">·</tspan> data pipelines'),
        (202, f'<tspan fill="{SIGNAL}">$</tspan> echo $STATUS'),
        (228, f'<tspan fill="{SIGNAL}">●</tspan> <tspan fill="{SILVER}">open to collaborations &amp; interesting problems</tspan><tspan class="caret" fill="{SIGNAL}"> ▍</tspan>'),
    ]
    body = [
        f'<rect x=".5" y=".5" width="{W - 1}" height="30" rx="14" fill="{PANEL}"/><rect x=".5" y="16" width="{W - 1}" height="15" fill="{PANEL}"/>',
        f'<line x1="0" y1="31" x2="{W}" y2="31" stroke="{LINE}"/>',
        ''.join(f'<circle cx="{22 + i * 18}" cy="16" r="5" fill="#30363d"/>' for i in range(3)),
        f'<text x="{W / 2}" y="20" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{MUTED}">shreyas@silicon: ~</text>',
    ]
    for i, (y, t) in enumerate(rows):
        body.append(f'<text class="fade" style="animation-delay:{0.25 + i * 0.35:.2f}s" x="24" y="{y}" font-family="{MONO}" font-size="14" fill="#adbac7">{t}</text>')
    return panel(W, H, "\n".join(body))


def about():
    W = 900
    fields = [
        ("role", '"Full-Stack Developer"'),
        ("focus", '["AI agents & MCP tooling", "secure web apps", "data pipelines"]'),
        ("previously", '"Database Management Intern @ HCL Aftermarket Cloud"'),
        ("education", '"B.E. Computer Science, VTU"'),
        ("certified", '["Tata Group — Cybersecurity", "Mastercard — Cybersecurity"]'),
        ("motto", '"Building. Learning. Improving. Repeat."'),
    ]
    lines = [f'<tspan fill="{SIGNAL}">const</tspan> <tspan fill="{SILVER}">shreyas</tspan> <tspan fill="#484f58">=</tspan> <tspan fill="#484f58">{{</tspan>']
    for k, v in fields:
        v = re.sub(r'"([^"]*)"', lambda m: f'<tspan fill="{SILVER}">"{esc(m.group(1))}"</tspan>', v)
        lines.append(f'  <tspan fill="{MUTED}">{k}</tspan><tspan fill="#484f58">:</tspan>{" " * (12 - len(k))}<tspan fill="#484f58">{v}</tspan>,')
    lines.append('<tspan fill="#484f58">};</tspan>')
    H = 44 + len(lines) * 26
    body = [f'<rect x=".5" y=".5" width="52" height="{H - 1}" rx="14" fill="{PANEL}"/><rect x="40" y=".5" width="13" height="{H - 1}" fill="{PANEL}"/><line x1="53" y1="0" x2="53" y2="{H}" stroke="{LINE}"/>']
    for i, ln in enumerate(lines):
        y = 34 + i * 26
        body.append(f'<text x="38" y="{y}" text-anchor="end" font-family="{MONO}" font-size="12" fill="#484f58">{i + 1}</text>')
        body.append(f'<text class="fade" style="animation-delay:{i * 0.08:.2f}s" x="72" y="{y}" font-family="{MONO}" font-size="14" fill="#484f58" xml:space="preserve">{ln}</text>')
    return panel(W, H, "\n".join(body))


def building():
    W = 900
    items = [
        ("Agent infrastructure", "Compilers that turn OpenAPI specs into scored MCP tool surfaces, and gateways that serve knowledge bundles to agents with trust policies."),
        ("Developer tooling", "Architecture maps of Python and TypeScript repos, CI quality gates and schema-driven data importers."),
        ("Vertical marketplaces", "Verified-manufacturer discovery platforms for D2C founders in India."),
        ("Personal automation", "A local assistant with a deterministic core and on-demand AI."),
    ]
    y, body = 28, []
    rows = []
    for title, desc in items:
        dl = wrap(desc, 92)
        rows.append((y, title, dl))
        y += 34 + len(dl) * 19 + 18
    H = y + 6
    body.append(f'<path class="trace" d="M40 {rows[0][0] + 8} V{rows[-1][0] + 8}"/>')
    body.append(f'<path class="pulse" pathLength="100" d="M40 {rows[0][0] + 8} V{rows[-1][0] + 8}" style="animation-duration:3.5s"/>')
    for i, (ry, title, dl) in enumerate(rows):
        body.append(f'<g class="fade" style="animation-delay:{i * 0.15:.2f}s">')
        body.append(f'<rect x="31" y="{ry - 1}" width="18" height="18" rx="4" fill="{PANEL}" stroke="#2b4a42"/><circle cx="40" cy="{ry + 8}" r="3.5" fill="{SIGNAL}"/>')
        body.append(f'<text x="68" y="{ry + 14}" font-family="{SANS}" font-size="18" font-weight="700" fill="{SILVER}">{title}</text>')
        body.append(f'<rect x="{W - 132}" y="{ry - 2}" width="108" height="22" rx="11" fill="{PANEL}" stroke="#2b4a42"/><text x="{W - 78}" y="{ry + 13}" text-anchor="middle" font-family="{MONO}" font-size="10.5" fill="{SIGNAL}" letter-spacing="1">IN PROGRESS</text>')
        for j, l in enumerate(dl):
            body.append(f'<text x="68" y="{ry + 38 + j * 19}" font-family="{SANS}" font-size="14" fill="{MUTED}">{esc(l)}</text>')
        body.append('</g>')
    return panel(W, H, "\n".join(body))


def stack():
    W = 900
    groups = [
        ("LANGUAGES", [("typescript", "TypeScript"), ("javascript", "JavaScript"), ("python", "Python"), ("php", "PHP"), ("solidity", "Solidity")]),
        ("FRONTEND", [("react", "React"), ("nextdotjs", "Next.js"), ("tailwindcss", "Tailwind"), ("html5", "HTML5"), ("css3", "CSS3")]),
        ("BACKEND & DATA", [("fastapi", "FastAPI"), ("flask", "Flask"), ("nodedotjs", "Node.js"), ("postgresql", "PostgreSQL"), ("mongodb", "MongoDB"), ("sqlite", "SQLite"), ("supabase", "Supabase")]),
        ("INFRA & TOOLING", [("docker", "Docker"), ("linux", "Linux"), ("git", "Git"), ("githubactions", "Actions"), ("vercel", "Vercel"), ("ethereum", "Ethereum")]),
    ]
    tw, th, gap, x0 = 88, 78, 10, 190
    body, y, n = [], 22, 0
    for label, techs in groups:
        body.append(f'<text x="28" y="{y + th / 2 + 4}" font-family="{MONO}" font-size="11" fill="{MUTED}" letter-spacing="2">{esc(label)}</text>')
        body.append(f'<path class="trace" d="M{28 + 9 * len(label) + 12} {y + th / 2} H{x0 - 10}"/>')
        for i, (ic, name) in enumerate(techs):
            x = x0 + i * (tw + gap)
            body.append(f'<g class="fade" style="animation-delay:{n * 0.05:.2f}s">'
                        f'<rect x="{x}" y="{y}" width="{tw}" height="{th}" rx="10" fill="{PANEL}" stroke="{LINE}"/>'
                        f'{logo(ic, x + tw / 2 - 13, y + 14, 26)}'
                        f'<text x="{x + tw / 2}" y="{y + th - 14}" text-anchor="middle" font-family="{MONO}" font-size="10.5" fill="{MUTED}">{name}</text></g>')
            n += 1
        y += th + 16
    return panel(W, y + 6, "\n".join(body))


def project_card(name, repo, desc, tags, live, w=440, h=250):
    dl = wrap(desc, 46)[:4]
    status = (f'<circle cx="28" cy="30" r="4.5" fill="{SIGNAL}"/><circle class="ping" cx="28" cy="30" r="4.5" fill="{SIGNAL}"/>'
              f'<text x="40" y="34" font-family="{MONO}" font-size="10.5" fill="{SIGNAL}" letter-spacing="1.5">LIVE</text>') if live else \
             (f'<circle cx="28" cy="30" r="4" fill="none" stroke="{MUTED}" stroke-width="1.5"/>'
              f'<text x="40" y="34" font-family="{MONO}" font-size="10.5" fill="{MUTED}" letter-spacing="1.5">SOURCE</text>')
    body = [status,
            f'<text x="{w - 24}" y="34" text-anchor="end" font-family="{MONO}" font-size="10.5" fill="#484f58">{esc(repo)}</text>',
            f'<text x="24" y="76" font-family="{SANS}" font-size="22" font-weight="800" fill="{SILVER}">{esc(name)}</text>',
            f'<path d="M24 88 H72" stroke="{SIGNAL}" stroke-width="2" stroke-linecap="round"/>']
    for i, l in enumerate(dl):
        body.append(f'<text x="24" y="{114 + i * 20}" font-family="{SANS}" font-size="14" fill="{MUTED}">{esc(l)}</text>')
    x = 24
    for t in tags:
        tw = 18 + 7.2 * len(t)
        body.append(f'<rect x="{x:.0f}" y="{h - 52}" width="{tw:.0f}" height="24" rx="6" fill="{PANEL}" stroke="{LINE}"/>'
                    f'<text x="{x + tw / 2:.0f}" y="{h - 36}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="#adbac7">{esc(t)}</text>')
        x += tw + 8
    cta = "live demo" if live else "view code"
    body.append(f'<text class="ar" x="{w - 24}" y="{h - 35}" text-anchor="end" font-family="{MONO}" font-size="12" font-weight="700" fill="{SIGNAL}">{cta} →</text>')
    trace = pts((w - 1, 64), (w - 40, 64), (w - 60, 84), (w - 60, 120))
    body.append(f'<path class="trace" d="{trace}"/><path class="pulse" pathLength="100" d="{trace}" style="animation-duration:3s"/><circle class="via" cx="{w - 60}" cy="120" r="4"/>')
    return panel(w, h, "\n".join(body), ".ar{animation:ar 1.8s ease-in-out infinite}@keyframes ar{50%{transform:translateX(3px)}}")


def mini_card(name, desc, tag, w=440, h=96):
    body = [f'<text x="22" y="38" font-family="{SANS}" font-size="16" font-weight="700" fill="{SILVER}">{esc(name)}</text>',
            f'<text x="{w - 22}" y="37" text-anchor="end" font-family="{MONO}" font-size="10.5" fill="{SIGNAL}" letter-spacing="1">{esc(tag)}</text>']
    for i, l in enumerate(wrap(desc, 56)[:2]):
        body.append(f'<text x="22" y="{62 + i * 18}" font-family="{SANS}" font-size="13" fill="{MUTED}">{esc(l)}</text>')
    return panel(w, h, "\n".join(body))


(OUT / "terminal.svg").write_text(terminal())
(OUT / "about.svg").write_text(about())
(OUT / "building.svg").write_text(building())
(OUT / "stack.svg").write_text(stack())

PROJECTS = {
    "p-trek-saathi": ("Trek Saathi", "Shreyas3435/trek-saathi", "Discovery and booking platform for treks in the Western Ghats, with trekker, organizer and admin roles on one FastAPI + Postgres backend.", ["TypeScript", "FastAPI", "PostgreSQL"], True),
    "p-blockchain-pharma": ("Blockchain in Pharma", "Shreyas3435/Blockchain_in_pharma", "Track-and-trace for medicines from manufacturer to customer, keeping quality and pricing transparent on-chain.", ["TypeScript", "Blockchain"], False),
    "p-movie-pipeline": ("Movie Data Pipeline", "Shreyas3435/movie-data-pipeline", "ETL pipeline for movie analytics that pulls from the OMDb API, cleans the data and loads it into SQLite.", ["Python", "SQLite", "ETL"], False),
    "p-portfolio": ("Portfolio", "Shreyas3435/portfolio", "My personal portfolio with projects, experience and contact details in one place.", ["TypeScript", "Next.js", "Vercel"], True),
}
for fname, args in PROJECTS.items():
    (OUT / f"{fname}.svg").write_text(project_card(*args))

MINI = {
    "m-packet-analyzer": ("Network Packet Analyzer", "Captures and inspects network packets for protocol-level analysis.", "SECURITY"),
    "m-image-encryption": ("Pixel Image Encryption", "Encrypts and decrypts images by manipulating pixel values.", "SECURITY"),
    "m-password-checker": ("Password Complexity Checker", "Scores password strength against common complexity rules.", "SECURITY"),
    "m-caesar-cipher": ("Caesar Cipher", "Classic shift cipher for encrypting and decrypting text.", "SECURITY"),
    "m-hashing": ("Hashing", "PHP sign-up and login flow with hashed password storage.", "SECURITY"),
    "m-content-search": ("Website Content Search", "Semantic search over website content with Weaviate vectors, Flask and React.", "AI · SEARCH"),
    "m-ai-summary": ("Ai_Summary", "Dockerised AI document-summary service with a web frontend.", "AI"),
    "m-artifact-editor": ("Artifact Editor", "Template-driven, autosaving user-story editor built as a Frappe app.", "FRAPPE"),
}
for fname, args in MINI.items():
    (OUT / f"{fname}.svg").write_text(mini_card(*args))

print("\n".join(sorted(p.name for p in OUT.glob("*.svg"))))
