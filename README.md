# Traveling Woodpecker

Home page of the motorcycle logbook at https://travelingwoodpecker.github.io

- `data/trips.json` — the list of every ride (source of truth)
- `assets/site.css` — shared design, loaded by every country repo
- `tools/build.py` — rebuilds this home page and each country's index page

To add a ride: add it to `data/trips.json`, then run `python3 tools/build.py`
from this folder and push this repo plus the country repos that changed.
Trip pages (e.g. `usa/2025-norcal-oregon/`) are hand-built and never overwritten.
