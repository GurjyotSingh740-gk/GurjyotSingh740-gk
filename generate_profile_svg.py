import os
import requests
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

USERNAME = "GurjyotSingh740-gk"
NAME = os.getenv("PROFILE_NAME", "Gurjyot Singh")
ROLE = os.getenv("PROFILE_ROLE", "Cloud / DevOps Engineer")
LOCATION = os.getenv("PROFILE_LOCATION", "Delhi, India")
EMAIL = os.getenv("PROFILE_EMAIL", "sgurjyot740@gmail.com")
LINKEDIN = os.getenv("PROFILE_LINKEDIN", "https://www.linkedin.com/in/gurjyot-singh-6b75a0232/")
PORTFOLIO = os.getenv("PROFILE_PORTFOLIO", "https://gurjyotsingh740-gk.github.io/Tech-Portfolio/")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

FEATURES = [
    "AWS • Docker • Kubernetes • CI/CD • Terraform",
    "Serverless • Monitoring • Cloud Automation • IoT",
]

PROJECTS = [
    "Step Functions Image Pipeline",
    "Elastic Beanstalk Multi-Zone App",
    "Autoscale Shop on Kubernetes",
    "SnapShift IoT File Transfer",
]

COLORS = {
    "dark": {
        "bg": "#0d1117",
        "panel": "#161b22",
        "text": "#c9d1d9",
        "muted": "#8b949e",
        "accent": "#58a6ff",
        "green": "#3fb950",
        "border": "#30363d",
    },
    "light": {
        "bg": "#ffffff",
        "panel": "#f6f8fa",
        "text": "#24292f",
        "muted": "#57606a",
        "accent": "#0969da",
        "green": "#1a7f37",
        "border": "#d0d7de",
    },
}

def github_graphql(query, variables=None):
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": variables or {}},
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]

def get_profile_data(username):
    query = """
    query($login: String!) {
      user(login: $login) {
        followers {
          totalCount
        }
        repoCount: repositories(ownerAffiliations: OWNER, isFork: false) {
          totalCount
        }
        contributionsCollection {
          contributionCalendar {
            totalContributions
          }
        }
        repoStars: repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
          nodes {
            stargazerCount
          }
        }
      }
    }
    """
    data = github_graphql(query, {"login": username})["user"]
    stars = sum(repo["stargazerCount"] for repo in data["repoStars"]["nodes"] if repo)
    return {
        "followers": data["followers"]["totalCount"],
        "repos": data["repoCount"]["totalCount"],
        "contributions": data["contributionsCollection"]["contributionCalendar"]["totalContributions"],
        "stars": stars,
    }

def get_uptime_string(start_date):
    now = datetime.now()
    diff = relativedelta(now, start_date)
    return f"{diff.years}y {diff.months}m {diff.days}d"

def esc(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

def build_svg(theme, stats):
    c = COLORS[theme]
    updated = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
    uptime = get_uptime_string(datetime(2024, 7, 1))

    lines = [
        f"{NAME.lower().replace(' ', '')}@cloud:~$ whoami",
        NAME,
        "",
        f"{NAME.lower().replace(' ', '')}@cloud:~$ cat profile.yaml",
        f"role: {ROLE}",
        f"location: {LOCATION}",
        f"status: open to opportunities",
        "",
        f"{NAME.lower().replace(' ', '')}@cloud:~$ kubectl get profile-stats",
        f"repos: {stats['repos']}",
        f"stars: {stats['stars']}",
        f"followers: {stats['followers']}",
        f"contributions: {stats['contributions']}",
        "",
        f"{NAME.lower().replace(' ', '')}@cloud:~$ printenv CORE_STACK",
        FEATURES[0],
        FEATURES[1],
        "",
        f"{NAME.lower().replace(' ', '')}@cloud:~$ ls featured-projects/",
        *[f"- {p}" for p in PROJECTS],
        "",
        f"{NAME.lower().replace(' ', '')}@cloud:~$ contact --show",
        f"email: {EMAIL}",
        f"linkedin: {LINKEDIN}",
        f"portfolio: {PORTFOLIO}",
        "",
        f"{NAME.lower().replace(' ', '')}@cloud:~$ systemctl status profile",
        f"uptime: {uptime}",
        f"last_updated: {updated}",
        "theme: terminal-profile",
    ]

    y = 95
    text_nodes = []
    for line in lines:
        fill = c["text"]
        if "@cloud:~$" in line:
            fill = c["green"]
        elif line.startswith("role:") or line.startswith("status:") or line.startswith("theme:"):
            fill = c["accent"]
        elif line.startswith("email:") or line.startswith("linkedin:") or line.startswith("portfolio:") or line.startswith("uptime:") or line.startswith("last_updated:"):
            fill = c["muted"]

        text_nodes.append(
            f'<text x="36" y="{y}" fill="{fill}" font-size="20" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, Liberation Mono, monospace">{esc(line)}</text>'
        )
        y += 30

    svg = f'''<svg width="1200" height="1020" viewBox="0 0 1200 1020" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="1200" height="1020" rx="20" fill="{c["bg"]}"/>
  <rect x="20" y="20" width="1160" height="980" rx="16" fill="{c["panel"]}" stroke="{c["border"]}"/>

  <circle cx="50" cy="50" r="6" fill="#ff5f56"/>
  <circle cx="70" cy="50" r="6" fill="#ffbd2e"/>
  <circle cx="90" cy="50" r="6" fill="#27c93f"/>

  <text x="112" y="55" fill="{c["muted"]}" font-size="15" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, Liberation Mono, monospace">profile-terminal</text>

  <line x1="32" y1="70" x2="1168" y2="70" stroke="{c["border"]}" stroke-width="1"/>

  {''.join(text_nodes)}
</svg>'''
    return svg

def main():
    if not GITHUB_TOKEN:
        raise RuntimeError("GITHUB_TOKEN is required")

    try:
        stats = get_profile_data(USERNAME)
    except Exception as e:
        print(f"GitHub API fetch failed: {e}")
        stats = {
            "followers": 0,
            "repos": 0,
            "contributions": 0,
            "stars": 0,
        }

    with open("dark_mode.svg", "w", encoding="utf-8") as f:
        f.write(build_svg("dark", stats))

    with open("light_mode.svg", "w", encoding="utf-8") as f:
        f.write(build_svg("light", stats))

if __name__ == "__main__":
    main()
