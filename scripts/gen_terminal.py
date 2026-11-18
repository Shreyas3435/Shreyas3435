"""Render the terminal-style profile panels (contributions heatmap, whoami, links).

Runs in .github/workflows/profile-data.yml with live data from the GitHub GraphQL API.

Usage:
  GITHUB_TOKEN=... python scripts/gen_terminal.py <login> <assets-dir>
  python scripts/gen_terminal.py <login> <assets-dir> --demo   # synthetic data, for previews
"""
import datetime as dt
import json
import os
import random
import sys
import urllib.request
from pathlib import Path

LOGIN, OUT = sys.argv[1], Path(sys.argv[2])
DEMO = "--demo" in sys.argv
HOST = "shreyas@github"

MONO = "'JetBrains Mono','Fira Code','SF Mono',Menlo,Consolas,'Courier New',monospace"
BG, WIN, BAR, LINE = "#0d1117", "#010409", "#161b22", "#30363d"
TEXT, MUTED, DIM = "#e6edf3", "#8b949e", "#484f58"
GREEN, BLUE, PURPLE = "#39d353", "#58a6ff", "#bc8cff"
LEVELS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

CSS = """
  .fade{opacity:0;animation:fade .6s ease forwards}
  @keyframes fade{to{opacity:1}}
  .pop{opacity:0;animation:pop .35s ease forwards}
  @keyframes pop{from{opacity:0}to{opacity:1}}
  .rise{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:rise .9s cubic-bezier(.3,0,.2,1) forwards}
  @keyframes rise{to{transform:scaleY(1)}}
  .caret{animation:blink 1s step-end infinite}@keyframes blink{50%{opacity:0}}
  .type{animation:type 1.1s steps(28,end) forwards}
  @keyframes type{from{width:0}}
  .glow{filter:drop-shadow(0 0 3px rgba(57,211,83,.55))}
"""

NOW = dt.datetime.now(dt.timezone.utc)
TODAY = NOW.date().isoformat()


# ---------------------------------------------------------------- data

def gql(query, **variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"},
    )
    body = json.load(urllib.request.urlopen(req, timeout=30))
    if "errors" in body:
        raise SystemExit(body["errors"])
    return body["data"]["user"]


def fetch_days():
    u = gql(
        """query($l:String!){user(login:$l){contributionsCollection{
          contributionCalendar{weeks{contributionDays{date contributionCount weekday}}}}}}""",
        l=LOGIN,
    )
    weeks = u["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [d for w in weeks for d in w["contributionDays"]]


def demo_days():
    rnd = random.Random(7)
    start = NOW.date() - dt.timedelta(days=364 + (NOW.date().weekday() + 1) % 7)
    out = []
    for i in range((NOW.date() - start).days + 1):
        d = start + dt.timedelta(days=i)
        busy = 0.55 + 0.35 * (d.month in (3, 4, 9, 10, 11))
        c = 0 if rnd.random() > busy else int(rnd.expovariate(1 / 6)) + 1
        out.append({"date": d.isoformat(), "contributionCount": c, "weekday": (d.weekday() + 1) % 7})
    return out


def summarize(days):
    days = [d for d in days if d["date"] <= TODAY]
    counts = [d["contributionCount"] for d in days]
    total = sum(counts)
    active = sum(1 for c in counts if c)

    longest = run = 0
    lstart = lend = best_start = None
    for d in days:
        if d["contributionCount"]:
            run += 1
            if run == 1:
                lstart = d["date"]
            if run > longest:
                longest, best_start, lend = run, lstart, d["date"]
        else:
            run = 0

    current, cstart = 0, None
    for i, d in enumerate(reversed(days)):
        if d["contributionCount"]:
            current += 1
            cstart = d["date"]
        elif i:  # today may still be empty
            break

    best = max(days, key=lambda d: d["contributionCount"]) if days else {"date": TODAY, "contributionCount": 0}

    months = {}
    for d in days:
        months[d["date"][:7]] = months.get(d["date"][:7], 0) + d["contributionCount"]
    monthly = sorted(months.items())[-12:]

    return {
        "days": days, "total": total, "active": active, "span": len(days),
        "current": current, "cstart": cstart, "longest": longest, "lstart": best_start, "lend": lend,
        "best": best, "avg": total / active if active else 0, "monthly": monthly,
    }


# ---------------------------------------------------------------- helpers

def fmt(date):
    return dt.date.fromisoformat(date).strftime("%b %-d") if date else "—"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def window(x, y, w, h, title, body, rx=10):
    """A terminal window: title bar with traffic lights, then body."""
    return (
        f'<g><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{WIN}" stroke="{LINE}"/>'
        f'<path d="M{x} {y + 28}V{y + rx}a{rx} {rx} 0 0 1 {rx}-{rx}h{w - 2 * rx}a{rx} {rx} 0 0 1 {rx} {rx}V{y + 28}Z" fill="{BAR}"/>'
        f'<line x1="{x}" y1="{y + 28}" x2="{x + w}" y2="{y + 28}" stroke="{LINE}"/>'
        f'<circle cx="{x + 16}" cy="{y + 14}" r="5" fill="#ff5f57"/>'
        f'<circle cx="{x + 32}" cy="{y + 14}" r="5" fill="#febc2e"/>'
        f'<circle cx="{x + 48}" cy="{y + 14}" r="5" fill="#28c840"/>'
        f'<text x="{x + w / 2}" y="{y + 18}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{MUTED}">{esc(title)}</text>'
        f"{body}</g>"
    )


def prompt(x, y, cmd, size=14, uid="p", delay=0.0, caret=True):
    """`user@host ~ $ cmd` with a typing animation and blinking caret."""
    cw = size * 0.6
    head = f"{HOST} ~ $ "
    w = (len(head) + len(cmd)) * cw + 4
    c = f'<tspan class="caret" fill="{GREEN}"> ▍</tspan>' if caret else ""
    return (
        f'<clipPath id="{uid}"><rect class="type" x="{x}" y="{y - size}" width="{w:.0f}" height="{size * 1.6}" '
        f'style="animation-delay:{delay}s"/></clipPath>'
        f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" font-weight="700" fill="{TEXT}" clip-path="url(#{uid})">'
        f'<tspan fill="{GREEN}">{HOST}</tspan><tspan fill="{BLUE}"> ~</tspan><tspan fill="{MUTED}"> $</tspan> {esc(cmd)}</text>'
        f'<text x="{x + w:.0f}" y="{y}" font-family="{MONO}" font-size="{size}">{c}</text>'
    )


def svg(w, h, label, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">'
        f"<style>{CSS}</style>"
        f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="14" fill="{BG}" stroke="{LINE}"/>'
        f"{body}</svg>\n"
    )


def level(c, peak):
    if not c:
        return 0
    q = c / peak
    return 1 if q <= .25 else 2 if q <= .5 else 3 if q <= .75 else 4


# ---------------------------------------------------------------- panels

def contributions_svg(s):
    W, H = 900, 240
    days = s["days"]
    peak = sorted(d["contributionCount"] for d in days)[int(len(days) * .97)] or 1
    first = dt.date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7  # GitHub weeks start on Sunday
    ncols = (offset + len(days) + 6) // 7
    cell, gap = 12, 3
    gx = 72 + (53 - ncols) * (cell + gap) / 2
    gy = 86

    body = [prompt(24, 36, "./contributions.sh", uid="pc")]
    cells, labels, last_month = [], [], None
    for i, d in enumerate(days):
        col, row = divmod(i + offset, 7)
        x, y = gx + col * (cell + gap), gy + row * (cell + gap)
        lv = level(d["contributionCount"], peak)
        cls = ' class="glow"' if lv == 4 else ""
        cells.append(
            f'<rect{cls} x="{x:.1f}" y="{y}" width="{cell}" height="{cell}" rx="2.5" fill="{LEVELS[lv]}">'
            f'<title>{d["contributionCount"]} on {d["date"]}</title></rect>'
        )
        m = d["date"][:7]
        if m != last_month and col < ncols - 2:
            labels.append((x, f'{dt.date.fromisoformat(d["date"]):%b}'))
            last_month = m
    for i, (x, name) in enumerate(labels):
        if i + 1 < len(labels) and labels[i + 1][0] - x < 40:
            continue  # partial month squeezed against the next label
        body.append(f'<text x="{x:.1f}" y="{gy - 10}" font-family="{MONO}" font-size="11" fill="{MUTED}">{name}</text>')
    # reveal the grid column by column
    for c in range(0, ncols, 4):
        chunk = cells[max(0, c * 7 - offset):max(0, (c + 4) * 7 - offset)]
        body.append(f'<g class="pop" style="animation-delay:{1.2 + c * .025:.2f}s">{"".join(chunk)}</g>')
    for row, lbl in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        body.append(f'<text x="{gx - 40:.1f}" y="{gy + row * (cell + gap) + 10}" font-family="{MONO}" font-size="11" fill="{MUTED}">{lbl}</text>')

    by = gy + 7 * (cell + gap) + 24
    body.append(
        f'<text class="fade" style="animation-delay:2.4s" x="{gx:.1f}" y="{by}" font-family="{MONO}" font-size="13" fill="{TEXT}">'
        f'<tspan font-weight="700" fill="{GREEN}">{s["total"]:,}</tspan> contributions in the last year</text>'
    )
    lx = gx + 53 * (cell + gap) - 5 * (cell + gap) - 70
    body.append(f'<g class="fade" style="animation-delay:2.4s"><text x="{lx - 8:.1f}" y="{by}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{MUTED}">Less</text>')
    for i, c in enumerate(LEVELS):
        body.append(f'<rect x="{lx + i * (cell + gap):.1f}" y="{by - 10}" width="{cell}" height="{cell}" rx="2.5" fill="{c}"/>')
    body.append(f'<text x="{lx + 5 * (cell + gap) + 4:.1f}" y="{by}" font-family="{MONO}" font-size="11" fill="{MUTED}">More</text></g>')
    return svg(W, H, f'{s["total"]:,} contributions in the last year', "".join(body))


# 5x7 pixel font for the monogram
GLYPHS = {
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
}


def monogram(x, y, px, text="SA"):
    out, cx = [], x
    shades = ["#26a641", "#39d353"]
    for li, ch in enumerate(text):
        for r, line in enumerate(GLYPHS[ch]):
            for c, bit in enumerate(line):
                if bit == "1":
                    delay = 0.9 + (r + c + li * 5) * 0.035
                    out.append(
                        f'<rect class="pop glow" style="animation-delay:{delay:.2f}s" x="{cx + c * px}" y="{y + r * px}" '
                        f'width="{px - 2}" height="{px - 2}" rx="2" fill="{shades[(r + c) % 2]}"/>'
                    )
        cx += 6 * px
    return "".join(out)


INFO = [
    ("name", "Shreyas S Alva"),
    ("role", "Full-Stack Engineer"),
    ("focus", "search · AI agents · MCP"),
    ("stack", "TS · Python · Next.js · FastAPI"),
    ("infra", "Linux · Docker · GCP · Vercel"),
    ("also", "AWS Champ · SIH '23 finalist"),
    ("based", "Karnataka, India"),
]


def whoami_svg(s):
    W, H = 900, 480
    body = [prompt(24, 36, "whoami", uid="pw")]

    # left window: neofetch-style card
    lx, ly, lw, lh = 24, 58, 396, 398
    left = [monogram(lx + 24, ly + 50, 14)]
    left.append(f'<text x="{lx + 196}" y="{ly + 66}" font-family="{MONO}" font-size="15" font-weight="700" fill="{GREEN}">shreyas</text>')
    left.append(f'<text x="{lx + 196}" y="{ly + 66}" font-family="{MONO}" font-size="15" font-weight="700" fill="{TEXT}"><tspan dx="63">@</tspan><tspan fill="{BLUE}">github</tspan></text>')
    left.append(f'<line x1="{lx + 196}" y1="{ly + 76}" x2="{lx + 372}" y2="{ly + 76}" stroke="{LINE}" stroke-dasharray="3 3"/>')
    left.append(f'<text x="{lx + 196}" y="{ly + 100}" font-family="{MONO}" font-size="12" fill="{MUTED}">builds things that</text>')
    left.append(f'<text x="{lx + 196}" y="{ly + 118}" font-family="{MONO}" font-size="12" fill="{MUTED}">ship — and search</text>')
    left.append(f'<text x="{lx + 196}" y="{ly + 136}" font-family="{MONO}" font-size="12" fill="{MUTED}">that actually finds.</text>')
    for i, (k, v) in enumerate(INFO):
        yy = ly + 184 + i * 24
        left.append(
            f'<text class="fade" style="animation-delay:{1.6 + i * .12:.2f}s" x="{lx + 24}" y="{yy}" font-family="{MONO}" font-size="13">'
            f'<tspan fill="{GREEN}" font-weight="700">{k}</tspan><tspan fill="{DIM}">{"." * (7 - len(k))}</tspan>'
            f'<tspan fill="{TEXT}" dx="8">{esc(v)}</tspan></text>'
        )
    pal = ["#ff5f57", "#febc2e", "#28c840", BLUE, PURPLE, "#39c5cf", TEXT, DIM]
    for i, c in enumerate(pal):
        left.append(f'<rect class="fade" style="animation-delay:2.6s" x="{lx + 24 + i * 22}" y="{ly + lh - 30}" width="18" height="12" rx="2" fill="{c}"/>')
    body.append(window(lx, ly, lw, lh, f"{HOST}: ~/neofetch", "".join(left)))

    # right window: stats + monthly bars
    rx, ry, rw, rh = 432, 58, 444, 398
    right = []
    tw, th = (rw - 36) / 2, 62
    pct = round(s["active"] / s["span"] * 100) if s["span"] else 0
    tiles = [
        ("current streak", f'{s["current"]}', "days", f'{fmt(s["cstart"])} – today' if s["current"] else "start one today"),
        ("longest streak", f'{s["longest"]}', "days", f'{fmt(s["lstart"])} – {fmt(s["lend"])}'),
        ("contributions", f'{s["total"]:,}', "", "in the last year"),
        ("active days", f'{s["active"]}', f'/ {s["span"]}', f"{pct}% of the year"),
        ("best day", f'{s["best"]["contributionCount"]}', "", fmt(s["best"]["date"])),
        ("avg / active day", f'{s["avg"]:.1f}', "", "contributions"),
    ]
    for i, (lbl, big, unit, sub) in enumerate(tiles):
        col, row = i % 2, i // 2
        x, y = rx + 12 + col * (tw + 12), ry + 40 + row * (th + 10)
        right.append(
            f'<g class="fade" style="animation-delay:{1.4 + i * .12:.2f}s">'
            f'<rect x="{x:.1f}" y="{y}" width="{tw:.1f}" height="{th}" rx="6" fill="{BG}" stroke="{BAR}"/>'
            f'<text x="{x + 12:.1f}" y="{y + 17}" font-family="{MONO}" font-size="10.5" fill="{MUTED}"><tspan fill="{GREEN}">$</tspan> {lbl}</text>'
            f'<text x="{x + 12:.1f}" y="{y + 40}" font-family="{MONO}" font-size="20" font-weight="700" fill="{GREEN if i < 2 else TEXT}">{big}'
            f'<tspan font-size="11" font-weight="400" fill="{MUTED}" dx="6">{unit}</tspan></text>'
            f'<text x="{x + 12:.1f}" y="{y + 54}" font-family="{MONO}" font-size="9.5" fill="{DIM}">{esc(sub)}</text></g>'
        )
    cy = ry + 40 + 3 * (th + 10)
    ch = rh - (cy - ry) - 12
    right.append(f'<rect x="{rx + 12}" y="{cy}" width="{rw - 24}" height="{ch}" rx="6" fill="{BG}" stroke="{BAR}"/>')
    right.append(f'<text x="{rx + 24}" y="{cy + 18}" font-family="{MONO}" font-size="10.5" fill="{MUTED}"><tspan fill="{GREEN}">$</tspan> contributions / month</text>')
    months = s["monthly"]
    mpeak = max((v for _, v in months), default=0) or 1
    bx0, bw_all, base, bh = rx + 28, rw - 56, cy + ch - 22, ch - 52
    slot = bw_all / max(1, len(months))
    for i, (m, v) in enumerate(months):
        h = max(2, v / mpeak * bh)
        x = bx0 + i * slot + slot * .18
        top = v == mpeak
        right.append(
            f'<rect class="rise{" glow" if top else ""}" style="animation-delay:{1.8 + i * .06:.2f}s" x="{x:.1f}" y="{base - h:.1f}" '
            f'width="{slot * .64:.1f}" height="{h:.1f}" rx="2" fill="{GREEN if top else "#26a641"}"><title>{m}: {v}</title></rect>'
        )
        right.append(f'<text x="{x + slot * .32:.1f}" y="{base + 14}" text-anchor="middle" font-family="{MONO}" font-size="9.5" fill="{DIM}">{dt.date.fromisoformat(m + "-01"):%b}</text>')
        if top:
            right.append(f'<text class="fade" style="animation-delay:2.6s" x="{x + slot * .32:.1f}" y="{base - h - 6:.1f}" text-anchor="middle" font-family="{MONO}" font-size="10" fill="{GREEN}">{v:,}</text>')
    body.append(window(rx, ry, rw, rh, f"{HOST}: ~/stats", "".join(right)))
    body.append(f'<text x="{W - 24}" y="{H - 10}" text-anchor="end" font-family="{MONO}" font-size="9.5" fill="{DIM}">synced {NOW:%Y-%m-%d %H:%M} UTC</text>')
    return svg(W, H, "whoami — Shreyas S Alva, Full-Stack Engineer: contribution streaks and stats", "".join(body))


def command_svg(cmd, sub, name):
    W, H = 900, 64 if not sub else 84
    body = prompt(24, 38, cmd, uid=f"p{name}", caret=not sub)
    if sub:
        body += f'<text class="fade" style="animation-delay:1.2s" x="24" y="66" font-family="{MONO}" font-size="13" fill="{MUTED}">{esc(sub)}</text>'
    return svg(W, H, f"$ {cmd}", body)


PILLS = [
    ("portfolio", "portfolio", "#30363d", TEXT),
    ("linkedin", "linkedin", "#1f6feb", "#ffffff"),
    ("email", "email", "#8957e5", "#ffffff"),
    ("repos", "repositories", "#1b7c83", "#ffffff"),
    ("trek", "trek-saathi", "#bf4b8a", "#ffffff"),
]


def pill_svg(label, bg, fg):
    w = int(len(label) * 8.4 + 44)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="34" viewBox="0 0 {w} 34" role="img" aria-label="{label}">'
        f'<rect x=".5" y=".5" width="{w - 1}" height="33" rx="8" fill="{bg}" stroke="#ffffff22"/>'
        f'<text x="16" y="22" font-family="{MONO}" font-size="13" font-weight="700" fill="{fg}" opacity=".7">&gt;</text>'
        f'<text x="30" y="22" font-family="{MONO}" font-size="13" font-weight="700" fill="{fg}">{label}</text></svg>\n'
    )


if __name__ == "__main__":
    s = summarize(demo_days() if DEMO else fetch_days())
    (OUT / "t-contributions.svg").write_text(contributions_svg(s))
    (OUT / "t-whoami.svg").write_text(whoami_svg(s))
    (OUT / "t-links.svg").write_text(command_svg("./links.sh", "Full-Stack Developer · AI Agents & MCP · Search Engineer", "links"))
    (OUT / "t-projects.svg").write_text(command_svg("./projects.sh --featured", "", "projects"))
    (OUT / "t-stack.svg").write_text(command_svg("cat stack.txt", "", "stack"))
    for key, label, bg, fg in PILLS:
        (OUT / f"pill-{key}.svg").write_text(pill_svg(label, bg, fg))
    print("ok", s["total"], s["current"], s["longest"])
