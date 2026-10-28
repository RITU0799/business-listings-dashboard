"""
Collect business-oriented points of interest from OpenStreetMap via Overpass.
Educational assignment collector. Respect OSM attribution and Overpass usage policies.
Coverage and phone availability vary by location.
"""

import argparse
import csv
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

CITIES = {
    "Mumbai": (19.0760, 72.8777),
    "Pune": (18.5204, 73.8567),
    "Bengaluru": (12.9716, 77.5946),
    "Hyderabad": (17.3850, 78.4867),
    "Delhi": (28.6139, 77.2090),
    "Chennai": (13.0827, 80.2707),
}

# Commercial-oriented OSM tags. Avoid broad amenity/healthcare/tourism
# queries that return many non-business public facilities.
TAGS = ["shop", "office", "craft", "commercial", "industrial"]

EXCLUDED_AMENITIES = {
    "place_of_worship", "police", "fire_station", "prison",
    "school", "university", "kindergarten", "bus_station",
    "parking", "fountain", "bench", "toilets", "shelter",
    "community_centre", "grave_yard", "courthouse",
}

FIELDS = [
    "business_name", "category", "city", "address", "phone", "source"
]


def query_city(lat, lon, radius=12000):
    clauses = "\n".join(
        f'nwr(around:{radius},{lat},{lon})["{tag}"]["name"];'
        for tag in TAGS
    )
    # Include named restaurants and other common commercial amenities.
    clauses += f"""
    nwr(around:{radius},{lat},{lon})["amenity"~"^(restaurant|cafe|fast_food|bank|pharmacy|fuel|clinic|hospital|cinema|marketplace|hotel)$"]["name"];
    """
    return f'[out:json][timeout:90];({clauses});out center tags;'


def get_json(query):
    data = urllib.parse.urlencode({"data": query}).encode()
    last_error = None

    for endpoint in ENDPOINTS:
        try:
            request = urllib.request.Request(
                endpoint,
                data=data,
                headers={
                    "User-Agent":
                    "BusinessListingsInternAssignment/1.0 (educational project)"
                },
            )
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            last_error = exc
            time.sleep(3)

    raise RuntimeError(f"All Overpass endpoints failed: {last_error}")


def get_category(tags):
    for key in TAGS:
        if tags.get(key):
            return str(tags[key]).replace("_", " ").title()

    amenity = tags.get("amenity")
    if amenity:
        return str(amenity).replace("_", " ").title()

    return "Business"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--per-city-limit", type=int, default=100)
    parser.add_argument("--output", default="data/osm_listings_v2.csv")
    parser.add_argument("--pause", type=float, default=3.0)
    parser.add_argument(
        "--radius", type=int, default=12000,
        help="Search radius in metres around each city centre",
    )
    args = parser.parse_args()

    if args.limit < 1:
        parser.error("--limit must be at least 1")
    if args.radius < 1000:
        parser.error("--radius must be at least 1000 metres")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    found = {}
    per_city = {city: 0 for city in CITIES}

    for city, (lat, lon) in CITIES.items():
        print(f"Querying commercial listings around {city}...")

        try:
            result = get_json(query_city(lat, lon, args.radius))
        except Exception as exc:
            print(f"Warning: {city} query failed: {exc}")
            time.sleep(max(1.0, args.pause))
            continue

        city_records = 0

        for item in result.get("elements", []):
            tags = item.get("tags", {})
            name = (tags.get("name") or "").strip()
            if not name:
                continue

            amenity = (tags.get("amenity") or "").casefold()
            if amenity in EXCLUDED_AMENITIES:
                continue

            # Ignore records without a commercial/business-oriented tag.
            if not any(tags.get(key) for key in TAGS) and amenity not in {
                "restaurant", "cafe", "fast_food", "bank", "pharmacy",
                "fuel", "clinic", "hospital", "cinema", "marketplace", "hotel"
            }:
                continue

            # Use the configured city consistently so address subareas such
            # as Baner or Kalyani Nagar do not become separate city labels.
            address_parts = [
                tags.get("addr:housenumber"),
                tags.get("addr:street"),
                tags.get("addr:suburb"),
                city,
                tags.get("addr:postcode"),
                "India",
            ]
            address = ", ".join(str(part) for part in address_parts if part)

            key = (name.casefold(), city.casefold(), address.casefold())
            if key in found:
                continue

            found[key] = {
                "business_name": name,
                "category": get_category(tags),
                "city": city,
                "address": address or f"{city}, India (address not available in OSM)",
                "phone": (
                    tags.get("contact:phone")
                    or tags.get("phone")
                    or ""
                ),
                "source": "OpenStreetMap",
            }

            city_records += 1

            if city_records >= args.per_city_limit:
                break
            
            if len(found) >= args.limit:
                break

        per_city[city] = city_records
        print(f"  Collected {city_records} records; total {len(found)}")

        # Don't stop just because one city has enough results. Stop only
        # after a city query when the requested overall limit is reached.
        if len(found) >= args.limit:
            break

        time.sleep(max(1.0, args.pause))

    with output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(found.values())

    print(f"\nSaved {len(found)} unique records to {output}")
    print("\nRecords collected by city:")
    for city, count in per_city.items():
        print(f"  {city}: {count}")

    if len(found) < args.limit:
        print(
            "\nWARNING: Fewer records than requested were returned. "
            "Do not claim the 500-record target is met until you verify "
            "the actual CSV row count."
        )


if __name__ == "__main__":
    main()
