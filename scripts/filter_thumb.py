#!/usr/bin/env python3
"""Filter FIRMS CSV rows to points inside the Thumb boundary polygon (CalTopo export).

Reads CSV on stdin (latitude,longitude,...), writes matching rows on stdout.
Boundary file: thumb_boundary.geojson (GeoJSON Polygon, coordinates [lon, lat]).
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOUNDARY = os.path.join(HERE, "thumb_boundary.geojson")

with open(BOUNDARY) as f:
    ring = json.load(f)["features"][0]["geometry"]["coordinates"][0]


def inside(lon, lat):
    """Ray-casting point-in-polygon test."""
    hit = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if (yi > lat) != (yj > lat):
            xint = (xj - xi) * (lat - yi) / (yj - yi) + xi
            if lon < xint:
                hit = not hit
        j = i
    return hit


def main():
    reader = csv.reader(sys.stdin)
    writer = csv.writer(sys.stdout, lineterminator="\n")
    try:
        header = next(reader)
    except StopIteration:
        return
    writer.writerow(header)
    for row in reader:
        if len(row) < 2:
            continue
        try:
            lat, lon = float(row[0]), float(row[1])
        except ValueError:
            continue
        if inside(lon, lat):
            writer.writerow(row)


if __name__ == "__main__":
    main()
