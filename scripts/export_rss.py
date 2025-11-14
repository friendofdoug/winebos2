#!/usr/bin/env python3
import os, json, datetime, html
from dateutil import parser
from email.utils import format_datetime

BASE = os.path.dirname(os.path.dirname(__file__))
JSON_IN = os.path.join(BASE, "site", "events.json")
RSS_OUT = os.path.join(BASE, "site", "rss.xml")
SITE_URL = os.environ.get("SITE_URL", "https://example.org")
TITLE = os.environ.get("SITE_TITLE", "Boston Wine Events — Upcoming")
DESC = "Aggregated wine tastings, classes, and dinners in the Boston area."

def rfc2822(dt):
    try:
        return format_datetime(parser.isoparse(dt))
    except Exception:
        return format_datetime(datetime.datetime.utcnow())

def main():
    data = json.load(open(JSON_IN))
    items = []
    for e in data.get("events", []):
        link = e.get("ticket_url") or e.get("source_url") or SITE_URL
        title = f"{e.get('title','')} — {e.get('venue_name','')}"
        desc = html.escape(", ".join(filter(None,[e.get('neighborhood'), e.get('address')]))) or ""
        pub = rfc2822(e.get("start",""))
        items.append(f"""
  <item>
    <title>{html.escape(title)}</title>
    <link>{html.escape(link)}</link>
    <guid isPermaLink="false">{html.escape(e.get('id',''))}</guid>
    <pubDate>{pub}</pubDate>
    <description>{desc}</description>
  </item>""")
    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>{html.escape(TITLE)}</title>
  <link>{SITE_URL}</link>
  <description>{html.escape(DESC)}</description>
  <lastBuildDate>{rfc2822(data.get("generated",""))}</lastBuildDate>
  {''.join(items)}
</channel>
</rss>"""
    open(RSS_OUT,"w").write(rss)
    print(f"Wrote {RSS_OUT} with {len(items)} items.")

if __name__ == "__main__":
    main()
