#!/usr/bin/env python3
import csv, json, os, datetime
BASE = os.path.dirname(os.path.dirname(__file__))
CSV_IN = os.path.join(BASE, "data", "events.csv")
JSON_OUT = os.path.join(BASE, "site", "events.json")
def fnum(x):
    try: return float(x)
    except: return None
def row_to_event(row):
    return {
        "id": row.get("id"), "title": row.get("title"),
        "start": row.get("start"), "end": row.get("end") or None,
        "venue_name": row.get("venue_name"), "address": row.get("address") or None,
        "neighborhood": row.get("neighborhood") or None,
        "price_min": fnum(row.get("price_min")), "price_max": fnum(row.get("price_max")),
        "organizer": row.get("organizer") or None,
        "tags": [t.strip() for t in (row.get("tags") or '').split(',') if t.strip()],
        "ticket_url": row.get("ticket_url") or None, "source_url": row.get("source_url") or None,
        "last_seen": row.get("last_seen") or None, "status": row.get("status") or "scheduled",
        "lat": fnum(row.get("lat")), "lon": fnum(row.get("lon")),
        "city": row.get("city") or None, "state": row.get("state") or None, "postal_code": row.get("postal_code") or None,
    }
rows=[]
with open(CSV_IN, newline='') as f:
    r=csv.DictReader(f)
    for row in r: rows.append(row_to_event(row))
rows.sort(key=lambda e: e.get('start') or '')
with open(JSON_OUT,'w') as f:
    json.dump({"generated": datetime.datetime.utcnow().isoformat()+'Z', "events": rows}, f, indent=2)
print(f"Wrote {JSON_OUT} with {len(rows)} events.")
