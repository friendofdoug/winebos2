#!/usr/bin/env python3
import os, csv, datetime, uuid, requests
from icalendar import Calendar

BASE = os.path.dirname(os.path.dirname(__file__))
CSV_OUT = os.path.join(BASE, "data", "events.csv")
SRC_FILE = os.path.join(BASE, "data", "sources_ics.txt")
FIELDS = ["id","title","start","end","venue_name","address","neighborhood","price_min","price_max","organizer","tags","ticket_url","source_url","last_seen","status","lat","lon","city","state","postal_code"]

def lines(path):
    with open(path) as f:
        for raw in f:
            u = raw.strip()
            if u and not u.startswith("#"): yield u

def to_iso(dt):
    import datetime as dtm
    if hasattr(dt, "dt"): dt = dt.dt
    if isinstance(dt, dtm.datetime):
        if dt.tzinfo is None:
            # assume US/Eastern if feed is naive
            return dt.replace(tzinfo=dtm.timezone(dtm.timedelta(hours=-5))).isoformat()
        return dt.isoformat()
    if isinstance(dt, dtm.date):
        return dtm.datetime(dt.year, dt.month, dt.day, 0, 0, tzinfo=dtm.timezone(dtm.timedelta(hours=-5))).isoformat()
    return ""

def fetch(url):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.content

def parse_ics(content, source_url):
    cal = Calendar.from_ical(content)
    for comp in cal.walk():
        if comp.name != "VEVENT": 
            continue
        title = str(comp.get('summary', '')).strip() or "Untitled"
        start = comp.get('dtstart'); end = comp.get('dtend')
        loc = str(comp.get('location','')).strip()
        url = str(comp.get('url','')).strip()
        yield {
            "id": f"ics-{uuid.uuid4().hex[:10]}",
            "title": title,
            "start": to_iso(start) if start else "",
            "end": to_iso(end) if end else "",
            "venue_name": loc or "TBA",
            "address": loc or "",
            "neighborhood": "",
            "price_min": "",
            "price_max": "",
            "organizer": "",
            "tags": "tasting",
            "ticket_url": url or "",
            "source_url": source_url,
            "last_seen": datetime.date.today().isoformat(),
            "status": "scheduled",
            "lat": "", "lon": "", "city": "", "state": "", "postal_code": ""
        }

def append_rows(rows):
    need_header = not os.path.exists(CSV_OUT) or os.path.getsize(CSV_OUT) == 0
    with open(CSV_OUT, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if need_header: w.writeheader()
        for r in rows: w.writerow(r)

if __name__ == "__main__":
    if not os.path.exists(SRC_FILE):
        print(f"No {SRC_FILE}; add ICS URLs first."); raise SystemExit
    total = 0
    for url in lines(SRC_FILE):
        try:
            rows = list(parse_ics(fetch(url), url))
            append_rows(rows)
            print(f"Imported {len(rows)} from {url}")
            total += len(rows)
        except Exception as e:
            print(f"Failed {url}: {e}")
    print(f"Done. Imported {total} events.")
