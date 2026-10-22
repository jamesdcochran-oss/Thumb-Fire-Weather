# Thumb Fire Weather

Fire weather dashboard for Michigan's Thumb: Huron, Sanilac, and St. Clair counties.

- **Weather:** NWS hourly forecast (DTX) via api.weather.gov, fetched live in the browser.
- **Hotspots:** NASA FIRMS VIIRS 48 h (NOAA-20, NOAA-21, S-NPP), filtered to the Thumb bbox
  (lon −84.3…−82.0, lat 42.4…44.4) by `scripts/update_hotspots.py`, run every 30 min by GitHub Actions.
  Output: `hotspots.csv` + `hotspots-meta.json` (generation time, feed status, counts).
- If every FIRMS feed fails, the workflow fails and the previous dataset is kept — an outage is never
  published as zero detections. The page flags data older than 3 h as stale.
- County counts are satellite detections within 30 km of each county reference point, not county-wide fire counts.
