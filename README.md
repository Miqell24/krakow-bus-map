# krakow-bus-map

Interactive web map of Kraków public transport (KMK) in the visual logic of the
official KMK network map: **164 bus lines and 23 tram lines** — plus, since
23.08.2026, the **10 Wieliczka commune buses** of the Wielicka Spółka
Transportowa (B2, D2, G3, G4, J1, L1, P2, R2, W2, Z1) on the same sheet — drawn
exactly along roadways and tracks (own HMM/Viterbi map matching on an OSM
graph), line numbers written parallel to every street they use, labeled stops,
true roundabout arcs. WST publishes no GTFS anywhere (odt.org.pl: "Brak umowy z
dostawcą"); `pipeline/kp-wst-gtfs.py` builds one from the operator's own
KiedyPrzyjedzie timetables (public web API, no shapes, no direction_id — stop
sequences are the matching observations). The sister sheet
[krakow-mld-bus-map](https://miqell24.github.io/krakow-mld-bus-map/) adds the
Małopolskie Linie Dowozowe on all of Małopolska.

**Live map:** https://miqell24.github.io/krakow-bus-map/

## Network diagram

`/schematic/` is the second face of this map: an automatic transit diagram of
the same network (ported from the Rybnik Region map, 21.08.2026). Stop order,
branches and shared segments come straight from the two ZTP feeds; the station
graph is contracted into corridors and laid out on an octilinear grid by a
Stott–Rodgers-style local search with a cost built from geographic anchoring,
octant fidelity, crossings, overlaps and bends; the Vistula enters the layout
as a constraint (stations keep their bank, lines cross at their real bridges,
which are drawn as anchors). `npm run schematic` (`pipeline/schematic/`) reads
`data/gtfs*`, `data/osm/wisla.json` and `data/osm/bridges.json` and writes
`data/out/schematic/`; the page exports the whole sheet as one print-quality
PNG with a legend band. Kraków: 187 lines, 1 464 stations, 906 corridors,
13 Vistula bridges recognised, crossings 110 → 42 after the layout.

## Two views

The panel's **Corridors / Lines** switch (ported from the Tricity map, 21.08.2026)
redraws the same network line by line: a roadway carrying up to four lines is
drawn as four coloured strands side by side (each line keeps one colour across the
whole map), anything busier becomes one grey trunk with its numbers beside it in
the lines' colours. `npm run lines` (`pipeline/lines.mjs`) derives the strand
files from `data/out/`; `npm run audit` checks the drawn result (torn ends,
folds, doubles, every line one connected piece).

## Timeline — the map's versions

The panel's **Map version** row (3.09.2026) switches between dated versions of the
network in place: the camera, the view, the base, the picked line, the label
sizes, the density and the mode filters all stay as they are — only the data
changes (MapLibre re-tiles the new GeoJSON and re-runs label placement, with the
settings the layers already hold). Versions are picked by DATE: each one is a
build of `data/out/`, archived by `pipeline/snapshot.mjs` under
`data/out/versions/<YYYY-MM-DD>/` and listed in `data/out/versions.json` with the
feeds it came from and its line list (the row shows the lines added and removed
since the previous version). `#v=2026-08-21` in the URL opens a given version.

**What an archived version holds** (user decision, 3.09.2026: `docs/` must stay
small): the corridor view (`streets`, `labels`, `stops`, `street-names`,
`badges`, `meta`) and the lines view (`lines-*`) — 17 MB on disk, 2 MB on the
wire, of which the corridor view is 1.1 MB. Left out: `route.geojson` (12 MB,
read only by the journey planner, which therefore works on the current build
only — the card says so), the raw GTFS trace (QA) and the network diagram
(it draws the current build anyway). `--full` keeps everything; `--slim` trims
older archives to the rule. Git itself hardly grows: identical files are one
blob, and a new build costs ~2 MB in the pack — it is the checkout (`docs/`)
that carries every version in full.

**The 2026 series.** MPK republishes its feeds every few days, and in 2026 the
network really changed with them (the summer works: detours, temporary tram
lines 70/73/77, tram 17 gone in September). The timeline holds every distinct
NETWORK of the year the sources reach (snapshots whose lines, stop sequences
and shapes are identical collapse into one — `scratchpad/feed-sig.py` logic):
- 13.03.2026 — the ZTP feeds captured by the Wayback Machine (the only 2026
  capture there);
- 26.07.2026 — the feeds this map was first published from;
- 1.08 … 29.08.2026 — the MobilityDatabase snapshot history (mdb-1326 buses,
  mdb-1270 trams; its website shows the last ten per feed, the older ones sit
  behind the API's login), one version per distinct network;
- the current build (feeds of 29.08.2026).
Historical versions are rebuilt with today's pipeline on today's OSM (roads
that changed since are matched as they are now), every version carries the WST
Wieliczka snapshot of 23.08 (the operator publishes no history), and a version's
date is the day its feeds appeared. January, February and April–June are missing:
no public copy of those feeds was found (a MobilityDatabase account would list
them all through the API).

**Which routes of the tram feed are trams.** ZTP codes every route of
`GTFS_KRK_T` as type 900, replacement buses and temporary tram lines alike, all
under their own numbers — so the line list used to be typed by hand in
`package.json`. `pipeline/tram-lines.py` decides it from the geometry instead:
a route whose shape points lie on OSM tram tracks (≥ 70 %) is a tram, the rest
are buses on a detour (in March 2026: 4 and 8). `npm run build` takes its
`--tram` list from it.

- `npm run build` keeps its predecessor by itself: `prebuild` archives the
  current `data/out/`, `postbuild` stamps the new build with its feeds
  (`data/out/version.json`) and rebuilds the list.
- `npm run snapshot` archives the current build by hand; `npm run snapshot --
  --index` only rebuilds the list; `npm run snapshot -- --src DIR --id 2026-08-21
  --note "…" --feeds dir1,dir2` imports an outside build (a historical feed built
  in a scratch copy of the project, or `docs/data` of an old commit:
  `git archive <sha> docs/data | tar -x -C /tmp/x`).
- A version without the lines files greys the Lines segment out; a picked line
  the other version lacks is let go with a note.

## Features

- GTFS (ZTP Kraków) matched onto the OSM road/tram network — mean error ~0.3 m,
  data gaps in the feed bridged by graph routing, unmapped construction sites drawn
  from the raw trace.
- KMK-style rendering: one stroke per roadway, aggregated line numbers rotated
  parallel to streets, shared bus+tram corridors get a single two-color number
  segment, termini labeled with their lines.
- Poster-style base map (warm tinted districts, green parks, blue water,
  pale-yellow motorways), narrow Roboto Condensed labels, stops drawn as
  half-discs oriented to the pole's side of the street, termini as filled discs.
- Panel with bus/tram visibility filters and a clickable line list (click a line to
  see its route with all stops).
- Poster-grade PNG export: the current view re-rendered in tiles at ~+3 zoom levels
  of extra detail (street and stop names become legible as you zoom into the image).
- GTFS shapes.txt quality report (`npm run report` → `data/gtfs-gaps-report.md`).

## Requirements

Node ≥ 18 (no npm dependencies), `curl`, `unzip`, internet on first run.

## Usage

```bash
npm run download   # ZTP GTFS + OSM (Overpass) + MapLibre (cached in data/ and web/vendor/)
npm run build      # extraction + map matching + GeoJSON files into data/out/
npm run serve      # http://localhost:8124
```

## Structure

- `pipeline/download.sh` — input data download
- `pipeline/build.mjs` — GTFS → OSM graph → HMM/Viterbi → `data/out/*.geojson`
- `pipeline/lib/` — csv (streaming), geo (local projection), graph (graph + Dijkstra), hmm (Viterbi)
- `pipeline/report-gaps.mjs` — GTFS shapes.txt gap report
- `web/` — MapLibre GL frontend (vendored, OpenFreeMap positron tiles)
- `docs/` — static bundle published via GitHub Pages (web + data/out copies)

Full plan and roadmap: [PLAN.md](PLAN.md).

## Data attribution

Map data © OpenStreetMap contributors · tiles by OpenFreeMap · timetables: GTFS ZTP Kraków.
