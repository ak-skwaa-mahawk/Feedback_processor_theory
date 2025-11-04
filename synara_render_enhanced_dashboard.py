#!/usr/bin/env python3
import json, argparse
from datetime import datetime
from jinja2 import Template

def load_entries(path):
    with open(path) as f:
        return json.load(f)

def render(entries, template_path, output_path, auto_refresh=True, refresh_interval=300):
    with open(template_path, "r", encoding="utf-8") as f:
        tmpl = Template(f.read())
    html = tmpl.render(
        generation_time=datetime.utcnow().isoformat()+"Z",
        entries=entries,
        auto_refresh=auto_refresh,
        refresh_interval=refresh_interval
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Rendered {output_path} (auto_refresh={auto_refresh}, refresh_interval={refresh_interval}s)")

def main():
    p = argparse.ArgumentParser(description="Render Synara enhanced dashboard")
    p.add_argument("--entries", default="sync_results.json")
    p.add_argument("--template", default="synara_sync_dashboard_template_enhanced.html")
    p.add_argument("--output", default="synara_sync_dashboard.html")
    p.add_argument("--auto-refresh", choices=["yes","no"], default="yes")
    p.add_argument("--refresh-interval", type=int, default=300)
    args = p.parse_args()

    entries = load_entries(args.entries)
    render(entries, args.template, args.output,
           auto_refresh=(args.auto_refresh=="yes"),
           refresh_interval=args.refresh_interval)

if __name__ == "__main__":
    main()