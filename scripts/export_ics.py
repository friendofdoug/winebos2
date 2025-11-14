#!/usr/bin/env python3
import os, json, uuid
from icalendar import Calendar, Event
from dateutil import parser

BASE = os.path.dirname(os.path.dirname(__file__))
JSON_IN = os.path.join(BASE, "site", "events.json")
ICS_OUT = os.path.join(BASE, "site", "events.ics")

if __name__ == "__main__":
    data = json.load(open(JSON_IN))
    cal = Calendar()
    cal.add('prodid', '-//Boston Wine Events//EN')
    cal.add('version', '2.0')
    for e in data.get("events", []):
        ev = Event()
        ev.add('uid', e.get('id') or uuid.uuid4().hex+'@boston-wine-events')
        ev.add('summary', e.get('title','(untitled)'))
        if e.get('start'): ev.add('dtstart', parser.isoparse(e['start']))
        if e.get('end'):   ev.add('dtend',   parser.isoparse(e['end']))
        loc = e.get('venue_name','')
        if e.get('address'): loc = f"{loc}, {e['address']}"
        ev.add('location', loc)
        if e.get('ticket_url'): ev.add('url', e['ticket_url'])
        cal.add_component(ev)
    open(ICS_OUT, "wb").write(cal.to_ical())
    print(f"Wrote {ICS_OUT} with {len(data.get('events',[]))} events.")
