"""Render the GitHub analytics panel and recent-activity log from live data.

Runs daily in .github/workflows/profile-data.yml.

Usage: GITHUB_TOKEN=... python scripts/gen_stats.py <login> <assets-dir>
"""
import datetime as dt
import json
import os
import sys
import urllib.request
from pathlib import Path

LOGIN, OUT = sys.argv[1], Path(sys.argv[2])

SANS = "'Segoe UI',Inter,'Helvetica Neue',Arial,sans-serif"
MONO = "'JetBrains Mono','Fira Code',Consolas,'Courier New',monospace"
BG, PANEL, LINE = "#07090c", "#0d1117", "#21262d"
SILVER, MUTED, DIM, SIGNAL = "#e6edf3", "#7d8590", "#484f58", "#34d399"
LANG_SHADES = [SIGNAL, "#26a37a", "#1b7a5c", "#8b949e", "#545d68"]
DOTS = '<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#1b2128"/></pattern>'
CSS = f"""
  .fade{{opacity:0;animation:fade .7s ease forwards}}
  @keyframes fade{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
  .grow{{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:grow 1.2s cubic-bezier(.3,0,.2,1) forwards}}
  @keyframes grow{{to{{transform:scaleX(1)}}}}
  .line{{stroke-dasharray:2000;stroke-dashoffset:2000;animation:draw 2.2s .3s ease forwards}}
  @keyframes draw{{to{{stroke-dashoffset:0}}}}
  .caret{{animation:blink 1s step-end infinite}}@keyframes blink{{50%{{opacity:0}}}}
"""

NOW = dt.datetime.now(dt.timezone.utc)


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


def fetch():
    u = gql(
        """query($l:String!){user(login:$l){createdAt
          pullRequests(states:MERGED){totalCount}
          contributionsCollection{contributionYears
            contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}
          repositories(ownerAffiliations:OWNER,privacy:PUBLIC,isFork:false,first:100,orderBy:{field:PUSHED_AT,direction:DESC}){
            totalCount nodes{name pushedAt primaryLanguage{name}
              languages(first:10,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}}}}}}""",
        l=LOGIN,
    )
    commits = 0
    for year in u["contributionsCollection"]["contributionYears"]:
        c = gql(
            """query($l:String!,$f:DateTime!,$t:DateTime!){user(login:$l){
              contributionsCollection(from:$f,to:$t){totalCommitContributions restrictedContributionsCount}}}""",
            l=LOGIN, f=f"{year}-01-01T00:00:00Z", t=f"{year}-12-31T23:59:59Z",
        )["contributionsCollection"]
        commits += c["totalCommitContributions"] + c["restrictedContributionsCount"]
    u["allCommits"] = commits
    return u


def streaks(days):
    counts = [d["contributionCount"] for d in days if d["date"] <= NOW.date().isoformat()]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    current = 0
    for i, c in enumerate(reversed(counts)):
        if c:
            current += 1
        elif i:  # today may still be empty
            break
    return current, longest


def stats_svg(u):
    W, H = 900, 400
    cal = u["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    weekly = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in cal["weeks"]]
    cur, longest = streaks(days)
    years = (NOW - dt.datetime.fromisoformat(u["createdAt"].replace("Z", "+00:00"))).days // 365
    repos = u["repositories"]

    tiles = [
        (f'{cal["totalContributions"]:,}', "contributions", "last 12 months"),
        (f'{u["allCommits"]:,}', "commits", "all-time"),
        (f'{cur}d', "current streak", f"longest {longest}d"),
        (str(repos["totalCount"]), "public repos", f'{u["pullRequests"]["totalCount"]} PRs merged'),
        (f"{years}y", "on GitHub", f'since {u["createdAt"][:4]}'),
    ]
    body = []
    tw = (W - 48 - 4 * 12) / 5
    for i, (big, label, sub) in enumerate(tiles):
        x = 24 + i * (tw + 12)
        body.append(
            f'<g class="fade" style="animation-delay:{i * 0.1:.1f}s">'
            f'<rect x="{x:.1f}" y="24" width="{tw:.1f}" height="96" rx="10" fill="{PANEL}" stroke="{LINE}"/>'
            f'<text x="{x + 18:.1f}" y="64" font-family="{SANS}" font-size="28" font-weight="800" fill="{SILVER}">{big}</text>'
            f'<text x="{x + 18:.1f}" y="86" font-family="{MONO}" font-size="11.5" fill="{SIGNAL}">{label}</text>'
            f'<text x="{x + 18:.1f}" y="104" font-family="{MONO}" font-size="10.5" fill="{DIM}">{sub}</text></g>'
        )

    # weekly contributions area chart
    cx, cy, cw, ch = 24, 140, 520, 236
    body.append(f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="10" fill="{PANEL}" stroke="{LINE}"/>')
    body.append(f'<text x="{cx + 18}" y="{cy + 28}" font-family="{MONO}" font-size="11" fill="{MUTED}" letter-spacing="2">WEEKLY CONTRIBUTIONS</text>')
    px0, py0, pw, ph = cx + 18, cy + 50, cw - 36, ch - 86
    peak = max(weekly) or 1
    step = pw / max(1, len(weekly) - 1)
    ptsl = [(px0 + i * step, py0 + ph - v / peak * ph) for i, v in enumerate(weekly)]
    line = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in ptsl)
    area = f"{line} L{px0 + pw:.1f} {py0 + ph} L{px0} {py0 + ph} Z"
    for g in range(4):
        gy = py0 + ph * g / 3
        body.append(f'<line x1="{px0}" y1="{gy:.1f}" x2="{px0 + pw}" y2="{gy:.1f}" stroke="#161b22"/>')
    body.append(f'<text x="{px0 + pw}" y="{py0 - 8}" text-anchor="end" font-family="{MONO}" font-size="10" fill="{DIM}">peak {peak}/wk</text>')
    body.append(f'<path d="{area}" fill="url(#area)"/>')
    body.append(f'<path class="line" d="{line}" fill="none" stroke="{SIGNAL}" stroke-width="2" stroke-linejoin="round"/>')
    lx, ly = ptsl[-1]
    body.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="4" fill="{SIGNAL}"/>')
    first = dt.date.fromisoformat(days[0]["date"]).strftime("%b %Y")
    body.append(f'<text x="{px0}" y="{py0 + ph + 22}" font-family="{MONO}" font-size="10" fill="{DIM}">{first}</text>')
    body.append(f'<text x="{px0 + pw}" y="{py0 + ph + 22}" text-anchor="end" font-family="{MONO}" font-size="10" fill="{DIM}">now</text>')

    # language breakdown by bytes
    size = {}
    for r in repos["nodes"]:
        for e in r["languages"]["edges"]:
            size[e["node"]["name"]] = size.get(e["node"]["name"], 0) + e["size"]
    total = sum(size.values()) or 1
    top = sorted(size.items(), key=lambda kv: -kv[1])[:5]
    lx0, lw = cx + cw + 12, W - 24 - (cx + cw + 12)
    body.append(f'<rect x="{lx0}" y="{cy}" width="{lw}" height="{ch}" rx="10" fill="{PANEL}" stroke="{LINE}"/>')
    body.append(f'<text x="{lx0 + 18}" y="{cy + 28}" font-family="{MONO}" font-size="11" fill="{MUTED}" letter-spacing="2">LANGUAGES</text>')
    bx, bw = lx0 + 18, lw - 36
    x = bx
    body.append(f'<clipPath id="bar"><rect x="{bx}" y="{cy + 44}" width="{bw}" height="10" rx="5"/></clipPath><g clip-path="url(#bar)" class="grow">')
    for i, (name, sz) in enumerate(top):
        w = bw * sz / total
        body.append(f'<rect x="{x:.1f}" y="{cy + 44}" width="{w + 1:.1f}" height="10" fill="{LANG_SHADES[i]}"/>')
        x += w
    body.append(f'<rect x="{x:.1f}" y="{cy + 44}" width="{bx + bw - x:.1f}" height="10" fill="#30363d"/></g>')
    for i, (name, sz) in enumerate(top):
        ry = cy + 88 + i * 30
        body.append(
            f'<g class="fade" style="animation-delay:{0.5 + i * 0.1:.1f}s"><rect x="{bx}" y="{ry - 9}" width="10" height="10" rx="2" fill="{LANG_SHADES[i]}"/>'
            f'<text x="{bx + 20}" y="{ry}" font-family="{SANS}" font-size="14" fill="{SILVER}">{name}</text>'
            f'<text x="{bx + bw}" y="{ry}" text-anchor="end" font-family="{MONO}" font-size="12" fill="{MUTED}">{sz / total * 100:.1f}%</text></g>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="GitHub analytics for {LOGIN}">
<defs>{DOTS}<linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{SIGNAL}" stop-opacity=".28"/><stop offset="1" stop-color="{SIGNAL}" stop-opacity="0"/></linearGradient></defs>
<style>{CSS}</style>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="{BG}" stroke="{LINE}"/>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="url(#dots)"/>
{"".join(body)}
<text x="{W - 24}" y="{H - 8}" text-anchor="end" font-family="{MONO}" font-size="9.5" fill="#30363d">synced {NOW:%Y-%m-%d}</text>
</svg>'''


def ago(ts):
    d = (NOW - dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))).days
    return "today" if d == 0 else "1 day ago" if d == 1 else f"{d} days ago"


def activity_svg(u):
    repos = [r for r in u["repositories"]["nodes"] if r["name"] != LOGIN][:6]
    W, H = 900, 70 + len(repos) * 34
    rows = []
    for i, r in enumerate(repos):
        y = 62 + i * 34
        lang = (r["primaryLanguage"] or {}).get("name", "—")
        rows.append(
            f'<g class="fade" style="animation-delay:{0.2 + i * 0.25:.2f}s">'
            f'<text x="24" y="{y}" font-family="{MONO}" font-size="13" fill="{DIM}">{r["pushedAt"][:10]}</text>'
            f'<text x="134" y="{y}" font-family="{MONO}" font-size="13" fill="{SIGNAL}">push</text>'
            f'<text x="190" y="{y}" font-family="{MONO}" font-size="13" font-weight="700" fill="{SILVER}">{r["name"]}</text>'
            f'<text x="560" y="{y}" font-family="{MONO}" font-size="13" fill="{MUTED}">{lang}</text>'
            f'<text x="{W - 24}" y="{y}" text-anchor="end" font-family="{MONO}" font-size="13" fill="{DIM}">{ago(r["pushedAt"])}</text></g>'
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Recently pushed public repositories">
<defs>{DOTS}</defs>
<style>{CSS}</style>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="{BG}" stroke="{LINE}"/>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="url(#dots)"/>
<text x="24" y="30" font-family="{MONO}" font-size="12" fill="{MUTED}"><tspan fill="{SIGNAL}">$</tspan> git log --all-repos --public -n {len(repos)}<tspan class="caret" fill="{SIGNAL}"> ▍</tspan></text>
<line x1="24" y1="40" x2="{W - 24}" y2="40" stroke="{LINE}"/>
{"".join(rows)}
</svg>'''


if __name__ == "__main__":
    u = fetch()
    (OUT / "stats.svg").write_text(stats_svg(u))
    (OUT / "activity.svg").write_text(activity_svg(u))
    print("ok")
