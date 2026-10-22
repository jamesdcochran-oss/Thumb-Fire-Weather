#!/usr/bin/env bash
# Pull NASA FIRMS 48h VIIRS (NOAA-20, NOAA-21, S-NPP) for CONUS and keep
# detections inside the Thumb boundary polygon (thumb_boundary.geojson).
set -euo pipefail
B=https://firms.modaps.eosdis.nasa.gov/data/active_fire
out=hotspots.csv
tmp=$(mktemp)
parts=()

for u in noaa-20-viirs-c2/csv/J1_VIIRS_C2_USA_contiguous_and_Hawaii_48h.csv \
         noaa-21-viirs-c2/csv/J2_VIIRS_C2_USA_contiguous_and_Hawaii_48h.csv \
         suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_USA_contiguous_and_Hawaii_48h.csv; do
  part=$(mktemp)
  if curl -fsSL --max-time 120 "$B/$u" | python3 "$(dirname "$0")/filter_thumb.py" > "$part"; then
    [ -s "$part" ] && parts+=("$part")
  else
    echo "warn: could not fetch $u" >&2
  fi
done

if [ ${#parts[@]} -gt 0 ]; then
  head -1 "${parts[0]}" > "$tmp"
  for p in "${parts[@]}"; do tail -n +2 "$p" >> "$tmp"; done
else
  echo "latitude,longitude,bright_ti4,scan,track,acq_date,acq_time,satellite,instrument,confidence,version,bright_ti5,frp,daynight" > "$tmp"
fi

mv "$tmp" "$out"
echo "$(($(wc -l < "$out") - 1)) hotspots inside the Thumb boundary"
