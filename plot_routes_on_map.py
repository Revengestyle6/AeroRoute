import re
import argparse
from pathlib import Path
import pandas as pd
import folium

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "flight_data.csv"


def parse_geocode(geocode_str):
    """Extract (lat, lon) from various geocode string formats.

    Handles formats like:
    - 'City, ST\n(LAT, LNG)'
    - '(LAT, LNG)'
    - 'LAT, LNG'

    Returns a tuple (lat, lon) as floats or None if not found.
    """
    if not isinstance(geocode_str, str):
        return None
    s = geocode_str.strip()
    # Find the first pair of floats separated by comma
    m = re.search(r"([+-]?\d+\.\d+)\s*,\s*([+-]?\d+\.\d+)", s)
    if not m:
        return None
    try:
        lat = float(m.group(1))
        lon = float(m.group(2))
        return lat, lon
    except ValueError:
        return None


def build_map(csvfile: Path, origin_filter: str = None, limit: int = None):
    data = pd.read_csv(csvfile, low_memory=False)

    m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)  # center of continental US

    routes_plotted = 0

    for row in data.itertuples(index=False):
        try:
            city1 = getattr(row, "city1")
            city2 = getattr(row, "city2")
            geo1 = getattr(row, "Geocoded_City1")
            geo2 = getattr(row, "Geocoded_City2")
        except Exception:
            # If columns are missing, skip the row
            continue

        if pd.isna(city1) or pd.isna(city2) or pd.isna(geo1) or pd.isna(geo2):
            continue

        if origin_filter and str(city1).upper() != origin_filter.upper():
            continue

        coords1 = parse_geocode(str(geo1))
        coords2 = parse_geocode(str(geo2))
        if not coords1 or not coords2:
            continue

        # Draw a line between the two points
        folium.PolyLine(locations=[coords1, coords2], color="blue", weight=2, opacity=0.7).add_to(m)

        # Add small circle markers for origin/destination
        folium.CircleMarker(location=coords1, radius=3, color="green", fill=True, fill_opacity=0.9,
                            popup=f"{city1}").add_to(m)
        folium.CircleMarker(location=coords2, radius=3, color="red", fill=True, fill_opacity=0.9,
                            popup=f"{city2}").add_to(m)

        routes_plotted += 1
        if limit and routes_plotted >= limit:
            break

    out = BASE_DIR / "routes_map.html"
    m.save(out)
    return out, routes_plotted


def main():
    parser = argparse.ArgumentParser(description="Plot flight routes on a USA map (interactive HTML)")
    parser.add_argument("--csv", default=str(CSV_PATH), help="Path to flight CSV file")
    parser.add_argument("--origin", default=None, help="If set, only plot routes from this origin city (case-insensitive)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of routes plotted (for performance)")
    args = parser.parse_args()

    csvfile = Path(args.csv)
    if not csvfile.exists():
        print(f"CSV not found: {csvfile}")
        return

    out, count = build_map(csvfile, origin_filter=args.origin, limit=args.limit)
    print(f"Saved map to: {out} (plotted {count} routes)")


if __name__ == "__main__":
    main()
