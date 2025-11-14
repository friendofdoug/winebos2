#!/usr/bin/env python3
import os, subprocess, sys, pathlib

BASE = pathlib.Path(__file__).resolve().parents[1]
S = BASE / "scripts"

def run(*cmd):
    print("+", " ".join(map(str, cmd)))
    subprocess.check_call(list(cmd))

def maybe(path): return path.exists()

if __name__ == "__main__":
    # Optional imports
    if maybe(BASE / "data" / "sources_ics.txt"):
        run(sys.executable, str(S / "import_ics.py"))
    if maybe(BASE / "data" / "eventbrite_organizers.txt") or maybe(BASE / "data" / "eventbrite_search.txt"):
        if os.environ.get("EB_TOKEN"):
            run(sys.executable, str(S / "import_eventbrite.py"))
        else:
            print("EB_TOKEN not set; skipping Eventbrite import.")
    # Normalize & feeds
    run(sys.executable, str(S / "normalize.py"))
    run(sys.executable, str(S / "export_rss.py"))
    run(sys.executable, str(S / "export_ics.py"))
    print("All done. Open site/index.html")
