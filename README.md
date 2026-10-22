# Thumb Fire Weather

Fire weather dashboard for Michigan's Thumb: Huron, Sanilac, and St. Clair counties.
Weather comes live from NWS Detroit/Pontiac (DTX) via api.weather.gov; hotspots come from NASA FIRMS (VIIRS 48h),
filtered to the Thumb by `scripts/update_hotspots.sh`, run every 30 minutes by GitHub Actions.
