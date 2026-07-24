#!/usr/bin/env python3
"""Recolecta estadisticas de colaboracion del repositorio (commits y PRs por
colaborador) usando el API de GitHub y las guarda en docs/data/stats.json para
que el dashboard las grafique. Pensado para correr en GitHub Actions con
GITHUB_TOKEN, o localmente con un token en GITHUB_TOKEN / GH_TOKEN."""
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

API = "https://api.github.com"


def gh_get(path, token):
    url = path if path.startswith("http") else API + path
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "pokeapi-perf-lab-stats")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def paginate(path, token):
    items = []
    page = 1
    sep = "&" if "?" in path else "?"
    while True:
        chunk = gh_get(f"{path}{sep}per_page=100&page={page}", token)
        if not isinstance(chunk, list) or not chunk:
            break
        items.extend(chunk)
        if len(chunk) < 100:
            break
        page += 1
        if page > 30:  # tope de seguridad
            break
    return items


def main():
    repo = os.environ.get("GITHUB_REPOSITORY") or (sys.argv[1] if len(sys.argv) > 1 else None)
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not repo:
        print("Falta GITHUB_REPOSITORY (owner/repo)", file=sys.stderr)
        sys.exit(1)

    # Commits por colaborador
    contributors = paginate(f"/repos/{repo}/contributors", token)
    people = {}
    total_commits = 0
    for c in contributors:
        login = c.get("login")
        if not login:
            continue
        commits = int(c.get("contributions", 0))
        total_commits += commits
        people[login] = {
            "login": login,
            "avatar": c.get("avatar_url", ""),
            "url": c.get("html_url", ""),
            "commits": commits,
            "prs_opened": 0,
            "prs_merged": 0,
        }

    # Pull Requests (todos los estados)
    pulls = paginate(f"/repos/{repo}/pulls?state=all", token)
    prs_open = prs_merged = prs_closed = 0
    for pr in pulls:
        user = (pr.get("user") or {}).get("login")
        merged = pr.get("merged_at") is not None
        state = pr.get("state")
        if state == "open":
            prs_open += 1
        elif merged:
            prs_merged += 1
        else:
            prs_closed += 1
        if user:
            p = people.setdefault(user, {
                "login": user,
                "avatar": (pr.get("user") or {}).get("avatar_url", ""),
                "url": (pr.get("user") or {}).get("html_url", ""),
                "commits": 0, "prs_opened": 0, "prs_merged": 0,
            })
            p["prs_opened"] += 1
            if merged:
                p["prs_merged"] += 1

    ordered = sorted(people.values(), key=lambda x: (x["commits"], x["prs_merged"]), reverse=True)

    data = {
        "repo": repo,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "totals": {
            "commits": total_commits,
            "contributors": len(people),
            "prs_total": len(pulls),
            "prs_open": prs_open,
            "prs_merged": prs_merged,
            "prs_closed": prs_closed,
        },
        "contributors": ordered,
    }

    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "data")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "stats.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"OK -> {path}")
    print(f"  commits={total_commits} colaboradores={len(people)} PRs={len(pulls)} (merged={prs_merged})")


if __name__ == "__main__":
    main()
