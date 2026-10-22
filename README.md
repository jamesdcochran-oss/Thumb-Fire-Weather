# Thumb Fire Weather

Fire weather dashboard for Michigan's Thumb: Huron, Sanilac, and St. Clair counties.
Weather comes live from NWS Detroit/Pontiac (DTX) via api.weather.gov; hotspots come from NASA FIRMS (VIIRS 48h),
filtered to your CalTopo Thumb boundary polygon (`thumb_boundary.geojson`) by `scripts/update_hotspots.sh`, run every 30 minutes by GitHub Actions. The boundary and each county (Huron, Sanilac, St. Clair) are drawn on the map, and county cards count hotspots inside actual county borders (US Census shapes)., run every 30 minutes by GitHub Actions.
