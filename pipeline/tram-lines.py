#!/usr/bin/env python3
# Which routes of ZTP's tram feed are TRAMS? The feed codes every route as
# extended type 900, but it also carries the replacement buses (7x) and the
# temporary tram lines (also 7x) under their own numbers — the number tells
# nothing. The shapes do: a tram's shape lies on the tracks, a bus's on the
# roads. Share of shape points within ~25 m of an OSM tram track, per route.
#   python3 pipeline/tram-lines.py <gtfs-t dir> <krakow-tram.json>          the table + the two lists
#   python3 pipeline/tram-lines.py <gtfs-t dir> <krakow-tram.json> --list   the tram list alone, for --tram
import csv, json, math, sys
from collections import defaultdict
gdir, osm = sys.argv[1], sys.argv[2]
LIST = '--list' in sys.argv
LAT0 = 50.06; kx = 111320 * math.cos(math.radians(LAT0)); ky = 110540
CELL = 25.0
def cell(lon, lat): return (int(lon * kx // CELL), int(lat * ky // CELL))
track = set()
for el in json.load(open(osm))['elements']:
    g = el.get('geometry') or []
    for i in range(len(g)):
        a = g[i]
        if i:
            b = g[i - 1]
            n = max(1, int(math.hypot((a['lon'] - b['lon']) * kx, (a['lat'] - b['lat']) * ky) / 10))
            for k in range(n):
                t = k / n
                track.add(cell(b['lon'] + (a['lon'] - b['lon']) * t, b['lat'] + (a['lat'] - b['lat']) * t))
        track.add(cell(a['lon'], a['lat']))
near = lambda c: any((c[0] + dx, c[1] + dy) in track for dx in (-1, 0, 1) for dy in (-1, 0, 1))
routes = {r['route_id']: r['route_short_name'].strip() for r in csv.DictReader(open(gdir + '/routes.txt', encoding='utf-8-sig'))}
shape_routes = defaultdict(set)
for t in csv.DictReader(open(gdir + '/trips.txt', encoding='utf-8-sig')):
    if t.get('shape_id'): shape_routes[t['shape_id']].add(routes.get(t['route_id']))
hit = defaultdict(int); tot = defaultdict(int)
for p in csv.DictReader(open(gdir + '/shapes.txt', encoding='utf-8-sig')):
    ls = shape_routes.get(p['shape_id'])
    if not ls: continue
    ok = near(cell(float(p['shape_pt_lon']), float(p['shape_pt_lat'])))
    for l in ls:
        tot[l] += 1
        if ok: hit[l] += 1
share = {l: hit[l] / tot[l] for l in tot}
key = lambda s: (len(s), s)
trams = sorted([l for l in share if share[l] >= 0.7], key=key)
buses = sorted([l for l in share if share[l] < 0.7], key=key)
if LIST:
    print(','.join(trams))
else:
    for l in sorted(share, key=key): print(f"{l:>4} {share[l]*100:5.1f}% {'tram' if share[l] >= 0.7 else 'BUS (replacement)'}")
    print('tram:', ','.join(trams))
    print('bus :', ','.join(buses))
