import csv
import random
from pathlib import Path

random.seed(2026)
OUT = Path(__file__).resolve().parents[1] / "data" / "sample_listings.csv"
cities = {
    "Mumbai": ["Andheri", "Bandra", "Dadar", "Powai", "Thane"],
    "Pune": ["Hinjawadi", "Kothrud", "Baner", "Shivajinagar", "Wakad"],
    "Bengaluru": ["Whitefield", "Indiranagar", "Koramangala", "Jayanagar", "HSR Layout"],
    "Hyderabad": ["Madhapur", "Gachibowli", "Kukatpally", "Begumpet", "Miyapur"],
    "Delhi": ["Dwarka", "Rohini", "Saket", "Karol Bagh", "Lajpat Nagar"],
    "Chennai": ["Adyar", "Velachery", "T Nagar", "Anna Nagar", "Tambaram"],
}
categories = {
    "Restaurant": ["Cafe", "Family Restaurant", "South Indian Restaurant", "Bakery", "Fast Food Outlet"],
    "Healthcare": ["Dental Clinic", "Diagnostic Centre", "Physiotherapy Clinic", "General Clinic", "Pharmacy"],
    "Retail": ["Grocery Store", "Clothing Store", "Electronics Shop", "Book Store", "Furniture Store"],
    "Professional Services": ["CA Office", "IT Services", "Consultancy", "Real Estate Agency", "Travel Agency"],
    "Automotive": ["Car Repair", "Two Wheeler Service", "Car Dealer", "Tyre Shop", "Car Wash"],
    "Education": ["Coaching Centre", "Computer Institute", "Preschool", "Language Classes", "Training Centre"],
}
prefixes = ["Bright", "Urban", "Green", "Prime", "Metro", "Silver", "Blue", "Smart", "Royal", "Modern",
            "Sunrise", "Evergreen", "Apex", "Star", "Golden", "NextGen", "City", "Classic", "Happy", "Trusted"]
suffixes = ["Hub", "Point", "Centre", "House", "Services", "Corner", "World", "Studio", "Mart", "Solutions"]
rows = []
for i in range(600):
    city = random.choice(list(cities))
    area = random.choice(cities[city])
    group = random.choice(list(categories))
    category = random.choice(categories[group])
    name = f"{random.choice(prefixes)} {category} {random.choice(suffixes)} {i+1:03d}"
    # Reserved fictional numbers; synthetic records are explicitly labelled.
    phone = f"+91-00000-{i:05d}" if i % 4 != 0 else ""
    rows.append({
        "business_name": name,
        "category": group,
        "city": city,
        "address": f"{random.randint(1, 250)}, {area}, {city}, India",
        "phone": phone,
        "source": "Sample Dataset (Synthetic)",
    })
OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["business_name", "category", "city", "address", "phone", "source"])
    writer.writeheader()
    writer.writerows(rows)
print(f"Wrote {len(rows)} synthetic demo rows to {OUT}")
