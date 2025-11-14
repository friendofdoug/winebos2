#!/usr/bin/env python3
import os, csv, datetime, requests

BASE = os.path.dirname(os.path.dirname(__file__))
CSV_OUT = os.path.join(BASE, "data", "events.csv")
ORG_FILE = os.path.join(BASE, "data", "eventbrite_organizers.txt")
Q_FILE = os.path.join(BASE, "data", "eventbrite_search.txt")
TOKEN = os.environ.get("EB_TOKEN")
API = "https://www.eventbriteapi.com/v3"
FIELDS = ["id","title","start","end","venue_name","address","neighborhood","price_min","price_max","organizer","tags","ticket_url","source_url","last_seen","status","lat","lon","city","state","postal_code"]

def write_rows(rows):
    need_header = not os.path.exists(CSV_OUT) or os.path.getsize(CSV_OUT) == 0
    with open(CSV_OUT, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if need_header: w.writeheader()
        for r in rows: w.writerow(r)

def get(path, params=None):
    if not TOKEN: raise RuntimeError("Set EB_TOKEN to use Eventbrite importer.")
    r = requests.get(API+path, headers={"Authorization": f"Bearer {TOKEN}"}, params=params or {}, timeout=30)
    r.raise_for_status()
    return r.json()

def as_row(ev, venue=None, org_name=""):
    addr = ""
    if venue:
        parts = [venue.get("address",{}).get(k) for k in ["address_1","city","region"]]
        addr = ", ".join([p for p in parts if p])
    return {
        "id": f"eb-{ev.get('id')}",
        "title": (ev.get("name") or {}).get("text","(untitled)"),
        "start": (ev.get("start") or {}).get("local") or "",
        "end": (ev.get("end") or {}).get("local") or "",
        "venue_name": (venue or {}).get("name") or "TBA",
        "address": addr,
        "neighborhood": "",
        "price_min": "",
        "price_max": "",
        "organizer": org_name,
        "tags": "tasting",
        "ticket_url": ev.get("url"),
        "source_url": ev.get("url"),
        "last_seen": datetime.date.today().isoformat(),
        "status": "scheduled",
        "lat": "",
        "lon": "",
        "city": (venue or {}).get("address",{}).get("city",""),
        "state": (venue or {}).get("address",{}).get("region",""),
        "postal_code": (venue or {}).get("address",{}).get("postal_code",""),
    }

def import_organizer(org_id):
    data = get(f"/organizations/{org_id}/events/", {"status":"live,started","order_by":"start_asc"})
    rows = []
    for ev in data.get("events",[]):
        venue = get(f"/venues/{ev['venue_id']}/") if ev.get("venue_id") else None
        rows.append(as_row(ev, venue, ""))  # org name optional
    write_rows(rows); print(f"Imported {len(rows)} from organizer {org_id}")

def import_search(query):
    data = get("/events/search/", {"q": query, "location.address":"Boston, MA", "sort_by":"date"})
    rows = []
    for ev in data.get("events",[]):
        venue = get(f"/venues/{ev['venue_id']}/") if ev.get("venue_id") else None
        rows.append(as_row(ev, venue, ""))
    write_rows(rows); print(f"Imported {len(rows)} from search '{query}'")

def lines(path):
    if not os.path.exists(path): return []
    with open(path) as f:
        for raw in f:
            s = raw.strip()
            if s and not s.startswith("#"): yield s

if __name__ == "__main__":
    did = False
    for org in lines(ORG_FILE): import_organizer(org); did = True
    for q in lines(Q_FILE): import_search(q); did = True
    if not did:
        print("No Eventbrite config found. Add organizers or queries to data/.")
