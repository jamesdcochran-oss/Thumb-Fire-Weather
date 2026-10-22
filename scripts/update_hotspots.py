#!/usr/bin/env python3
"""Fetch NASA FIRMS 48h VIIRS CSVs (NOAA-20, NOAA-21, S-NPP) and keep the Michigan Thumb bbox.

Writes hotspots.csv + hotspots-meta.json. If every feed fails, exits non-zero and leaves the
existing files untouched, so an outage is never published as "zero detections".
"""
import csv, io, json, os, sys, tempfile, urllib.request
from datetime import datetime, timezone

W, E, S, N = -84.3, -82.0, 42.4, 44.4
BASE = "https://firms.modaps.eosdis.nasa.gov/data/active_fire"
FEEDS = {
    "NOAA-20 VIIRS": "noaa-20-viirs-c2/csv/J1_VIIRS_C2_USA_contiguous_and_Hawaii_24h.csv",
    "NOAA-21 VIIRS": "noaa-21-viirs-c2/csv/J2_VIIRS_C2_USA_contiguous_and_Hawaii_24h.csv",
    "S-NPP VIIRS": "suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_USA_contiguous_and_Hawaii_24h.csv",
}
FIELDS = ["latitude", "longitude", "bright_ti4", "scan", "track", "acq_date", "acq_time",
          "satellite", "instrument", "confidence", "version", "bright_ti5", "frp", "daynight", "feed"]
UA = "Thumb-Fire-Weather (https://github.com/jamesdcochran-oss/Thumb-Fire-Weather)"


def fetch(path):
    req = urllib.request.Request(f"{BASE}/{path}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read().decode("utf-8", "replace")


def num(v):
    try:
        f = float(str(v).strip()) if str(v).strip() else None
        return f if f is not None and f == f else None
    except (TypeError, ValueError):
        return None


def atomic_write(path, writer):
    fd, tmp = tempfile.mkstemp(dir=".", prefix=".tmp-")
    try:
        with os.fdopen(fd, "w", newline="") as f:
            writer(f)
        os.chmod(tmp, 0o644)
        os.replace(tmp, path)
    except BaseException:
        os.unlink(tmp)
        raise


def main():
    rows, ok, failed = [], [], {}
    for name, path in FEEDS.items():
        try:
            reader = csv.DictReader(io.StringIO(fetch(path)))
            if not reader.fieldnames or not {"latitude", "longitude", "acq_date"} <= set(reader.fieldnames):
                raise ValueError(f"unexpected header: {reader.fieldnames}")
            n = 0
            for r in reader:
                lat, lon = num(r.get("latitude")), num(r.get("longitude"))
                if lat is None or lon is None or not (S <= lat <= N and W <= lon <= E):
                    continue
                r["instrument"] = r.get("instrument") or "VIIRS"
                r["feed"] = name
                rows.append({k: r.get(k, "") for k in FIELDS})
                n += 1
            ok.append({"feed": name, "detections": n})
        except Exception as e:  # noqa: BLE001
            failed[name] = str(e)[:200]
            print(f"WARN {name}: {e}", file=sys.stderr)

    if not ok:
        print("ERROR: all FIRMS feeds failed; keeping previous hotspots.csv", file=sys.stderr)
        return 1

    rows.sort(key=lambda r: (r["acq_date"], r["acq_time"].zfill(4)), reverse=True)
    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "window_hours": 24,
        "bbox": {"west": W, "east": E, "south": S, "north": N},
        "feeds_ok": ok,
        "feeds_failed": failed,
        "status": "partial" if failed else "ok",
        "detections": len(rows),
        "latest_observation": f"{rows[0]['acq_date']} {rows[0]['acq_time'].zfill(4)} UTC" if rows else None,
    }

    def write_csv(f):
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        w.writerows(rows)

    atomic_write("hotspots.csv", write_csv)
    atomic_write("hotspots-meta.json", lambda f: (json.dump(meta, f, indent=2), f.write("\n")))
    print(f"{len(rows)} detections in Thumb bbox ({meta['status']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
