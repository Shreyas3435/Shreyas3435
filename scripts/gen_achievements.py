"""Render the achievements wall from live GitHub data.

Every medal is computed from real profile stats, so tiers only go up when
the underlying numbers do. Runs daily in .github/workflows/achievements.yml.

Usage: GITHUB_TOKEN=... python scripts/gen_achievements.py <login> assets/achievements.svg
"""
import datetime as dt
import json
import os
import sys
import urllib.request

LOGIN, OUT = sys.argv[1], sys.argv[2]

SANS = "'Segoe UI',Inter,'Helvetica Neue',Arial,sans-serif"
MONO = "'JetBrains Mono','Fira Code',Consolas,'Courier New',monospace"
BG, PANEL, LINE = "#07090c", "#0d1117", "#21262d"
SILVER, MUTED, SIGNAL = "#e6edf3", "#7d8590", "#34d399"

TIERS = [  # name, base colour, highlight
    ("LOCKED", "#30363d", "#484f58"),
    ("BRONZE", "#b07443", "#e0a271"),
    ("SILVER", "#9aa4af", "#e6edf3"),
    ("GOLD", "#c99a2e", "#ffd76a"),
    ("DIAMOND", "#3fb8d6", "#b6f0ff"),
]

# Certifications are not on the GitHub API, so they are listed by hand.
CERTIFICATIONS = ["Tata Group Cybersecurity", "Mastercard Cybersecurity"]


def gql(query, **variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"},
    )
    body = json.load(urllib.request.urlopen(req, timeout=30))
    if "errors" in body:
        raise SystemExit(body["errors"])
    return body["data"]


def stats():
    u = gql(
        """query($l:String!){user(login:$l){createdAt
          pullRequests(states:MERGED){totalCount}
          repositories(ownerAffiliations:OWNER,privacy:PUBLIC,first:100,isFork:false){totalCount
            nodes{stargazerCount homepageUrl languages(first:10){nodes{name}}}}
          contributionsCollection{contributionYears}}}""",
        l=LOGIN,
    )["user"]
    commits = 0
    for year in u["contributionsCollection"]["contributionYears"]:
        c = gql(
            """query($l:String!,$f:DateTime!,$t:DateTime!){user(login:$l){
              contributionsCollection(from:$f,to:$t){totalCommitContributions restrictedContributionsCount}}}""",
            l=LOGIN, f=f"{year}-01-01T00:00:00Z", t=f"{year}-12-31T23:59:59Z",
        )["user"]["contributionsCollection"]
        commits += c["totalCommitContributions"] + c["restrictedContributionsCount"]
    repos = u["repositories"]["nodes"]
    created = dt.datetime.fromisoformat(u["createdAt"].replace("Z", "+00:00"))
    return {
        "years": (dt.datetime.now(dt.timezone.utc) - created).days // 365,
        "active_years": len(u["contributionsCollection"]["contributionYears"]),
        "commits": commits,
        "repos": u["repositories"]["totalCount"],
        "langs": len({l["name"] for r in repos for l in r["languages"]["nodes"]}),
        "merged": u["pullRequests"]["totalCount"],
        "live": sum(1 for r in repos if r["homepageUrl"]),
        "stars": sum(r["stargazerCount"] for r in repos),
    }


def medals(s):
    # title, subtitle, value, thresholds for bronze/silver/gold/diamond, glyph
    return [
        ("Commit Machine", "all-time contributions", s["commits"], (50, 250, 1000, 2500), "commit"),
        ("Veteran", "years on GitHub", s["years"], (1, 3, 5, 8), "clock"),
        ("Polyglot", "languages shipped", s["langs"], (3, 6, 9, 12), "code"),
        ("Architect", "public repositories", s["repos"], (5, 15, 30, 60), "stack"),
        ("Shipper", "merged pull requests", s["merged"], (2, 16, 64, 128), "merge"),
        ("Live Wire", "projects deployed live", s["live"], (1, 3, 6, 10), "bolt"),
        ("Marathoner", "active years", s["active_years"], (1, 3, 5, 8), "flame"),
        ("Cyber Certified", "security certifications", len(CERTIFICATIONS), (1, 2, 4, 6), "shield"),
    ]


def tier_of(value, th):
    t = sum(value >= x for x in th)
    lo = th[t - 1] if t else 0
    nxt = th[t] if t < len(th) else None
    pct = 1.0 if nxt is None else (value - lo) / (nxt - lo)
    return t, nxt, max(0.0, min(1.0, pct))


GLYPHS = {
    "commit": '<circle r="7" fill="none" stroke-width="3"/><path d="M-20 0H-7M7 0H20" stroke-width="3"/>',
    "clock": '<circle r="15" fill="none" stroke-width="3"/><path d="M0-9V0L7 5" fill="none" stroke-width="3"/>',
    "code": '<path d="M-8-10L-18 0L-8 10M8-10L18 0L8 10" fill="none" stroke-width="3"/>',
    "stack": '<path d="M0-14L16-6L0 2L-16-6Z M-16 2L0 10L16 2 M-16 9L0 17L16 9" fill="none" stroke-width="2.6" stroke-linejoin="round"/>',
    "merge": '<circle cx="-8" cy="-12" r="4" fill="none" stroke-width="2.6"/><circle cx="-8" cy="13" r="4" fill="none" stroke-width="2.6"/><circle cx="10" cy="2" r="4" fill="none" stroke-width="2.6"/><path d="M-8-8V9M-8-4C-8 2 0 2 6 2" fill="none" stroke-width="2.6"/>',
    "bolt": '<path d="M3-17L-11 3H0L-3 17L11-3H0Z" stroke-width="2.4" stroke-linejoin="round"/>',
    "flame": '<path d="M0-17C6-8 13-3 10 7C8 14 3 17 0 17C-6 17-11 12-11 5C-11-2-5-4-3-10C0-6 2-4 0-17Z" fill="none" stroke-width="2.6" stroke-linejoin="round"/>',
    "shield": '<path d="M0-17L14-11V0C14 9 7 15 0 18C-7 15-14 9-14 0V-11Z" fill="none" stroke-width="2.6" stroke-linejoin="round"/><path d="M-6 0L-1 5L7-4" fill="none" stroke-width="2.6"/>',
}


def hexagon(r):
    import math
    return " ".join(f"{r * math.cos(math.radians(60 * i - 90)):.1f},{r * math.sin(math.radians(60 * i - 90)):.1f}" for i in range(6))


def card(i, x, y, title, sub, value, th, glyph):
    t, nxt, pct = tier_of(value, th)
    name, base, hi = TIERS[t]
    w, h = 270, 250
    mx, my = x + w / 2, y + 82
    delay = 0.15 * i
    locked = t == 0
    ink = MUTED if locked else hi
    progress = "MAX TIER" if nxt is None else f"{value} / {nxt} → {TIERS[t + 1][0].lower()}"
    glow = f'<polygon class="halo" points="{hexagon(58)}" fill="{hi}" opacity=".18" style="animation-delay:{delay:.2f}s"/>' if t >= 3 else ""
    return f'''<g class="pop" style="animation-delay:{delay:.2f}s">
  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{PANEL}" stroke="{LINE}"/>
  <g transform="translate({mx} {my})">
    {glow}
    <polygon points="{hexagon(50)}" fill="url(#g{t})" stroke="{hi}" stroke-width="2"/>
    <polygon points="{hexagon(41)}" fill="{BG}" fill-opacity=".72" stroke="{base}" stroke-width="1.2"/>
    <g stroke="{ink}" fill="{ink}" stroke-linecap="round">{GLYPHS[glyph]}</g>
    <g clip-path="url(#hexclip)"><rect class="glint" x="-90" y="-60" width="26" height="120" fill="#fff" opacity=".22" transform="skewX(-20)" style="animation-delay:{1.2 + delay:.2f}s"/></g>
    <rect x="-34" y="40" width="68" height="18" rx="9" fill="{BG}" stroke="{base}"/>
    <text y="53" text-anchor="middle" font-family="{MONO}" font-size="10" font-weight="700" fill="{ink}" letter-spacing="1.5">{name}</text>
  </g>
  <text x="{mx}" y="{y + 176}" text-anchor="middle" font-family="{SANS}" font-size="18" font-weight="800" fill="{SILVER}">{title}</text>
  <text x="{mx}" y="{y + 195}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{MUTED}"><tspan fill="{SILVER}" font-weight="700">{value}</tspan> {sub}</text>
  <rect x="{x + 24}" y="{y + 210}" width="{w - 48}" height="6" rx="3" fill="#161b22"/>
  <rect class="fill" x="{x + 24}" y="{y + 210}" width="{(w - 48) * pct:.1f}" height="6" rx="3" fill="{SIGNAL if nxt else hi}" style="animation-delay:{0.6 + delay:.2f}s"/>
  <text x="{mx}" y="{y + 234}" text-anchor="middle" font-family="{MONO}" font-size="10.5" fill="{MUTED}">{progress}</text>
</g>'''


def render(s):
    ms = medals(s)
    W, H = 1200, 676
    tiers = [tier_of(v, th)[0] for _, _, v, th, _ in ms]
    xp = sum(t * 250 + int(tier_of(v, th)[2] * 250) for t, (_, _, v, th, _) in zip(tiers, ms))
    level, into = xp // 1000 + 1, (xp % 1000) / 1000
    unlocked = sum(t > 0 for t in tiers)
    cards = []
    for i, m in enumerate(ms):
        cards.append(card(i, 24 + (i % 4) * 292, 130 + (i // 4) * 264, *m))
    grads = "".join(
        f'<linearGradient id="g{i}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{hi}"/><stop offset=".5" stop-color="{base}"/><stop offset="1" stop-color="{hi}" stop-opacity=".7"/></linearGradient>'
        for i, (_, base, hi) in enumerate(TIERS)
    )
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Achievements: level {level}, {unlocked} of {len(ms)} unlocked">
<defs>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#1b2128"/></pattern>
  {grads}
  <clipPath id="hexclip"><polygon points="{hexagon(50)}"/></clipPath>
  <linearGradient id="xp" x1="0" x2="1"><stop offset="0" stop-color="#1f8f68"/><stop offset="1" stop-color="{SIGNAL}"/></linearGradient>
</defs>
<style>
  .pop{{opacity:0;animation:pop .6s cubic-bezier(.2,.8,.2,1.2) forwards}}
  @keyframes pop{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:none}}}}
  .glint{{animation:glint 5s ease-in-out infinite}}
  @keyframes glint{{0%{{transform:skewX(-20deg) translateX(0)}}30%,100%{{transform:skewX(-20deg) translateX(200px)}}}}
  .fill{{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:fill 1.2s cubic-bezier(.3,0,.2,1) forwards}}
  @keyframes fill{{to{{transform:scaleX(1)}}}}
  .halo{{animation:halo 2.4s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
  @keyframes halo{{50%{{transform:scale(1.12);opacity:.05}}}}
  .ping{{animation:ping 2s ease-out infinite;transform-box:fill-box;transform-origin:center}}
  @keyframes ping{{from{{transform:scale(1);opacity:.7}}to{{transform:scale(3);opacity:0}}}}
</style>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="{BG}" stroke="{LINE}"/>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="url(#dots)"/>

<g transform="translate(24 24)">
  <rect width="{W - 48}" height="84" rx="14" fill="{PANEL}" stroke="{LINE}"/>
  <polygon transform="translate(52 42)" points="{hexagon(30)}" fill="url(#g3)" stroke="#ffd76a" stroke-width="2"/>
  <text x="52" y="50" text-anchor="middle" font-family="{SANS}" font-size="22" font-weight="800" fill="{BG}">{level}</text>
  <text x="100" y="36" font-family="{MONO}" font-size="11" fill="{MUTED}" letter-spacing="2">PLAYER LEVEL</text>
  <text x="100" y="62" font-family="{SANS}" font-size="24" font-weight="800" fill="{SILVER}">Level {level} <tspan font-size="15" font-weight="600" fill="{MUTED}">· {xp:,} XP · {unlocked}/{len(ms)} unlocked</tspan></text>
  <text x="{W - 72}" y="36" text-anchor="end" font-family="{MONO}" font-size="11" fill="{MUTED}">{int(into * 100)}% to level {level + 1}</text>
  <rect x="{W - 72 - 420}" y="48" width="420" height="10" rx="5" fill="#161b22"/>
  <rect class="fill" x="{W - 72 - 420}" y="48" width="{420 * into:.1f}" height="10" rx="5" fill="url(#xp)" style="animation-delay:.4s"/>
  <circle cx="{W - 72 - 420 - 16}" cy="53" r="4" fill="{SIGNAL}"/><circle class="ping" cx="{W - 72 - 420 - 16}" cy="53" r="4" fill="{SIGNAL}"/>
</g>
{"".join(cards)}
<text x="{W - 28}" y="{H - 10}" text-anchor="end" font-family="{MONO}" font-size="10" fill="#484f58">synced from the GitHub API · {stamp}</text>
</svg>'''


if __name__ == "__main__":
    s = stats()
    print(json.dumps(s))
    open(OUT, "w").write(render(s))
