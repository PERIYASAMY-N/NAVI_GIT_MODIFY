import os
import urllib.request
import json

def fetch(url, token=None):
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'GitHub-Language-Stats')
    if token:
        req.add_header('Authorization', f'token {token}')
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def main():
    token = os.environ.get('GITHUB_TOKEN')
    username = 'PERIYASAMY-N'
    repos = fetch(f'https://api.github.com/users/{username}/repos?per_page=100', token)
    
    if not isinstance(repos, list):
        print("Failed to fetch repos.")
        return

    lang_stats = {}
    for repo in repos:
        if repo.get('fork') or repo.get('size', 0) == 0:
            continue
        langs_url = repo.get('languages_url')
        if not langs_url:
            continue
        langs = fetch(langs_url, token)
        if isinstance(langs, dict):
            for lang, bytes_count in langs.items():
                lang_stats[lang] = lang_stats.get(lang, 0) + bytes_count
            
    total_bytes = sum(lang_stats.values())
    if total_bytes == 0:
        print("No language data found.")
        return
        
    sorted_langs = sorted(lang_stats.items(), key=lambda item: item[1], reverse=True)[:8]
    
    # SVG Generation
    svg_width = 500
    row_height = 30
    padding = 20
    header_height = 40
    svg_height = header_height + (len(sorted_langs) * row_height) + padding
    
    # Standard GitHub colors
    colors = {
        'Java': '#b07219', 'JavaScript': '#f1e05a', 'Python': '#3572A5', 
        'HTML': '#e34c26', 'CSS': '#563d7c', 'TypeScript': '#3178c6', 
        'C++': '#f34b7d', 'C': '#555555', 'C#': '#178600', 
        'PHP': '#4F5D95', 'Ruby': '#701516', 'Go': '#00ADD8',
        'Jupyter Notebook': '#DA5B0B', 'Shell': '#89e051'
    }
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}">
  <style>
    .bg {{ fill: #0d1117; stroke: #30363d; stroke-width: 1px; rx: 6px; }}
    .title {{ font: 600 16px 'Segoe UI', Ubuntu, Sans-Serif; fill: #c9d1d9; }}
    .lang {{ font: 400 14px 'Segoe UI', Ubuntu, Sans-Serif; fill: #8b949e; }}
    .pct {{ font: 600 14px 'Segoe UI', Ubuntu, Sans-Serif; fill: #c9d1d9; }}
    .bar-bg {{ fill: #21262d; rx: 5px; }}
    .bar {{ rx: 5px; }}
  </style>
  <rect class="bg" width="{svg_width-2}" height="{svg_height-2}" x="1" y="1" />
  <text x="20" y="30" class="title">Languages</text>
'''
    
    y_offset = header_height + 10
    for lang, bytes_count in sorted_langs:
        pct = (bytes_count / total_bytes) * 100
        color = colors.get(lang, '#8b949e')
        bar_max_width = 250
        bar_width = max((pct / 100) * bar_max_width, 4) # min width 4px
        
        svg += f'''
  <g transform="translate(20, {y_offset})">
    <text x="0" y="14" class="lang" width="100">{lang}</text>
    <rect class="bar-bg" x="110" y="3" width="{bar_max_width}" height="12" />
    <rect class="bar" x="110" y="3" width="{bar_width}" height="12" fill="{color}" />
    <text x="375" y="14" class="pct">{pct:.1f}%</text>
  </g>'''
        y_offset += row_height
        
    svg += '\\n</svg>'
    
    os.makedirs('dist', exist_ok=True)
    with open('dist/github-language-stats.svg', 'w', encoding='utf-8') as f:
        f.write(svg)

if __name__ == '__main__':
    main()
