#!/usr/bin/env bash
# Pull NASA FIRMS 48h VIIRS (NOAA-20, NOAA-21, S-NPP) + MODIS for CONUS, keep the Michigan Thumb bbox.
set -euo pipefail
W=-84.3; E=-82.0; S=42.4; N=44.4
B=https://firms.modaps.eosdis.nasa.gov/data/active_fire
out=hotspots.csv; tmp=$(mktemp)
for u in noaa-20-viirs-c2/csv/J1_VIIRS_C2_USA_contiguous_and_Hawaii_48h.csv \
         noaa-21-viirs-c2/csv/J2_VIIRS_C2_USA_contiguous_and_Hawaii_48h.csv \
         suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_USA_contiguous_and_Hawaii_48h.csv; do
  curl -fsSL "$B/$u" -o "$tmp.part" || continue
  [ -s "$tmp" ] || head -1 "$tmp.part" > "$tmp"
  awk -F, -v w=$W -v e=$E -v s=$S -v n=$N 'NR>1 && $1>=s && $1<=n && $2>=w && $2<=e' "$tmp.part" >> "$tmp"
done
[ -s "$tmp" ] || echo "latitude,longitude,bright_ti4,scan,track,acq_date,acq_time,satellite,instrument,confidence,version,bright_ti5,frp,daynight" > "$tmp"
mv "$tmp" "$out"; echo "$(($(wc -l < $out)-1)) hotspots in Thumb bbox"
