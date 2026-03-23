"""Flask API to serve flight route data for visualization."""

from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from main import findoriginnames, finddestinationnames, findallroutes
from pathlib import Path
import json

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

def parse_geocode(geocode_str):
    """Parse geocode string 'LAT,LNG' into float coordinates."""
    if not geocode_str:
        return None
    try:
        s = str(geocode_str)
        # Many rows store: "City, ST\n(LAT, LNG)". Extract numbers inside parentheses.
        import re
        m = re.search(r"\(([+-]?\d+\.?\d*),\s*([+-]?\d+\.?\d*)\)", s)
        if m:
            lat = float(m.group(1))
            lng = float(m.group(2))
            return {"lat": lat, "lng": lng}
        # Fallback to simple comma-separated lat,lng
        parts = s.strip().split(',')
        if len(parts) >= 2:
            # take last two parts as lat,lng
            lat = float(parts[-2])
            lng = float(parts[-1])
            return {"lat": lat, "lng": lng}
    except (ValueError, AttributeError):
        pass
    return None

@app.route('/api/airports/origins', methods=['GET'])
def get_origin_airports():
    """Get all origin airports with geocodes."""
    try:
        origins = findoriginnames("flight_data.csv")
        data = []
        for airport, geocode in origins:
            coords = parse_geocode(geocode)
            if coords:
                data.append({
                    "airport": airport,
                    "geocode": geocode,
                    "lat": coords["lat"],
                    "lng": coords["lng"],
                    "type": "origin"
                })
        return jsonify({"count": len(data), "airports": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/airports/all', methods=['GET'])
def get_all_airports():
    """Get all unique airports (origins + destinations) with geocodes."""
    try:
        origins = findoriginnames("flight_data.csv")
        destinations = finddestinationnames("flight_data.csv")

        # Combine and deduplicate; prefer geocoded entries
        all_airports: dict[str, dict] = {}

        def try_add(code: str, geocode: str):
            if not isinstance(code, str):
                return
            existing = all_airports.get(code)
            coords = parse_geocode(geocode) if geocode else None
            if coords:
                # overwrite existing if it has no coords
                if not existing or existing.get('lat') is None:
                    all_airports[code] = {
                        "airport": code,
                        "geocode": geocode,
                        "lat": coords["lat"],
                        "lng": coords["lng"],
                    }
            else:
                # ensure key exists (without coords) if nothing else
                if not existing:
                    all_airports[code] = {"airport": code}

        for airport, geocode in origins:
            try_add(airport, geocode)
        for airport, geocode in destinations:
            try_add(airport, geocode)

        # Return only airports that have lat/lng for plotting
        data = [v for v in all_airports.values() if v.get('lat') is not None]
        return jsonify({"count": len(data), "airports": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/routes', methods=['GET'])
def get_routes():
    """Get all routes."""
    try:
        routes = findallroutes("flight_data.csv")
        # routes is now a list of (origin, destination) pairs
        data = [{"origin": o, "destination": d} for o, d in routes]
        return jsonify({"count": len(data), "routes": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/map', methods=['GET'])
def get_map():
    """Generate and return an interactive map (HTML) of routes.

    Query params:
      - origin: optional; filter routes by origin city name (case-insensitive)
      - limit: optional int; limit number of routes plotted
    """
    origin = request.args.get('origin')
    limit = request.args.get('limit', type=int)
    try:
        # Import the map builder from the helper script
        from plot_routes_on_map import build_map

        csv_path = Path("flight_data.csv")
        out_path, count = build_map(csv_path, origin_filter=origin, limit=limit)

        html = out_path.read_text(encoding='utf-8')
        return Response(html, content_type='text/html')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Run on port 5001 to avoid conflicts on macOS (port 5000 sometimes reserved).
    app.run(debug=True, port=5001)
