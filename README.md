# Business Listings Dashboard

A full-stack internship assignment implementation using **React + FastAPI + MySQL**.

## Features
- Import business listings in bulk through FastAPI.
- MySQL `listing_master` table.
- City-wise, category-wise and source-wise aggregation APIs.
- React dashboard with KPI cards, bar chart and pie chart.
- OpenStreetMap/Overpass collection script (use only in accordance with the source's usage policies).
- Clearly labelled synthetic demo data so the dashboard can be tested when scraping is unavailable.

## Project structure
```text
business-listings-dashboard/
├── backend/
│   ├── app/main.py
│   ├── app/database.py
│   ├── app/schemas.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/App.jsx
│   ├── src/main.jsx
│   ├── src/index.css
│   ├── package.json
│   └── index.html
├── data/
│   └── sample_listings.csv
├── scripts/
│   ├── import_csv.py
│   ├── generate_sample_data.py
│   └── scrape_osm.py
├── database/schema.sql
└── .gitignore
```

## Requirements
- Python 3.10+
- Node.js 18+
- MySQL 8+
- Git (for GitHub submission)

## 1. Create the database
Open MySQL Workbench or the MySQL CLI and run `database/schema.sql`.

The script creates database `business_listings` and table `listing_master`.

## 2. Configure and start the backend (Windows PowerShell)
```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `backend/.env` and set your MySQL username/password. Example:
```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@127.0.0.1:3306/business_listings
CORS_ORIGINS=http://localhost:5173
```

Start API:
```powershell
uvicorn app.main:app --reload
```
Open `http://127.0.0.1:8000/docs` to test endpoints.

> If your MySQL root account has no password, use `mysql+pymysql://root:@127.0.0.1:3306/business_listings`.

## 3. Load data
From the project root, in a second PowerShell terminal:
```powershell
py scripts/import_csv.py --csv data/sample_listings.csv
```
This imports 600 clearly labelled synthetic records. They are for testing the application and **must not be described as real scraped businesses**.

To attempt collection of real, publicly available OpenStreetMap business listings:
```powershell
py -m pip install requests
py scripts/scrape_osm.py --limit 500 --output data/osm_listings.csv
py scripts/import_csv.py --csv data/osm_listings.csv
```
The Overpass public service can rate-limit or reject large queries. If that happens, use the included sample dataset and disclose the limitation, as allowed by the assignment. Do not bypass website access controls or violate terms of service.

## 4. Start the React dashboard
Open a third terminal:
```powershell
cd frontend
npm install
npm run dev
```
Visit `http://localhost:5173`.

## API endpoints
- `GET /health` — API health check
- `POST /api/listings/bulk` — bulk insert records
- `GET /api/listings?limit=100` — list recent records
- `GET /api/dashboard/summary` — total listings and distinct counts
- `GET /api/dashboard/city-counts` — city-wise count
- `GET /api/dashboard/category-counts` — category-wise count
- `GET /api/dashboard/source-counts` — source-wise count

## 5. GitHub submission
From the project root:
```powershell
git init
git add .
git commit -m "Build business listings dashboard assignment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/business-listings-dashboard.git
git push -u origin main
```
Create the empty repository on GitHub first and replace `YOUR_USERNAME`.

## 6. Demo video outline (3–5 minutes)
1. Introduce the React + FastAPI + MySQL architecture (20–30 sec).
2. Show the `listing_master` table and explain fields (30–45 sec).
3. Open `/docs`, show the bulk-insert endpoint and aggregation APIs (45–60 sec).
4. Show the dashboard KPI cards and city/category/source charts (60–90 sec).
5. Explain the data collection script, note whether you used live OSM results or synthetic fallback data, and mention limitations (30–45 sec).

## Challenges / limitations to discuss honestly
- Public directory websites may block automated scraping or restrict reuse.
- OpenStreetMap coverage and Overpass availability vary by city and query size.
- Phone numbers are often absent from public map data.
- Aggregations depend on data quality and consistent city/category labels.
- Synthetic sample records are only for demonstrating end-to-end functionality; they are not evidence of successful real-world scraping.

## Important
The provided `sample_listings.csv` is synthetic demo data. For a submission claiming 500+ collected listings, run the collector and verify the output is real source-derived data, or clearly state that sample data was used.
