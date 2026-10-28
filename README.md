# Business Listings Dashboard

A full-stack business listing management and analytics application developed for the **Honeybee Digital Data Science Internship Assignment 2026**, using React, FastAPI, and MySQL.

## Features

- Bulk import of business listings through a FastAPI REST endpoint.
- MySQL database with a `listing_master` table.
- Dashboard summary with total listings, distinct cities, and distinct categories.
- City-wise, category-wise, and source-wise aggregation APIs.
- Interactive React dashboard with KPI cards, bar charts, and pie charts.
- OpenStreetMap/Overpass data collection script.
- Synthetic demonstration data clearly distinguished from source-derived records.
- SQL database schema and database dump for setup and restoration.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React.js, Vite, Recharts |
| Backend | Python, FastAPI |
| Database | MySQL 8+ |
| Database connectivity | SQLAlchemy, PyMySQL |
| Data collection | OpenStreetMap / Overpass API |
| API documentation | FastAPI Swagger UI |
| Version control | Git and GitHub |

## Project Structure

```text
business-listings-dashboard/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── schemas.py
│   │   └── __init__.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── package-lock.json
│   └── index.html
├── data/
│   ├── sample_listings.csv
│   ├── osm_listings_candidate.csv
│   └── other CSV datasets
├── scripts/
│   ├── generate_sample_data.py
│   ├── import_csv.py
│   └── scrape_osm.py
├── database/
│   ├── schema.sql
│   └── business_listings.sql
├── README.md
└── .gitignore
```

## Prerequisites

Install the following software before running the application:

- Python 3.10 or later
- Node.js and npm
- MySQL Server 8 or later
- Git

## Setup and Installation

### 1. Clone the repository

```powershell
git clone https://github.com/RITU0799/business-listings-dashboard.git
cd business-listings-dashboard
```

### 2. Create the MySQL database

Open MySQL Workbench or the MySQL command-line client and execute:

```sql
SOURCE path/to/business-listings-dashboard/database/schema.sql;
```

Alternatively, open `database/schema.sql` in MySQL Workbench and execute the script.

The schema creates the `business_listings` database and the `listing_master` table.

To restore the included database dump instead, use MySQL Workbench's import functionality or execute the dump against a suitable MySQL instance. Do not import both the full dump and the same dataset again unless duplicate records are intended.

### 3. Configure the backend

Open PowerShell in the project root and run:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `backend/.env` and configure the database connection string and allowed frontend origins according to the settings supported by the application.

Example database URL:

```text
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@127.0.0.1:3306/business_listings
```

Replace `YOUR_PASSWORD` with your own MySQL password. Do not commit the actual `.env` file or expose database credentials.

Start the FastAPI server from the `backend` directory:

```powershell
python -m uvicorn app.main:app --reload
```

The API will be available at:

- API base URL: `http://127.0.0.1:8000`
- Interactive API documentation: `http://127.0.0.1:8000/docs`

### 4. Load business listing data

Open a separate PowerShell terminal at the project root.

To import the included synthetic demonstration dataset:

```powershell
python scripts/import_csv.py --csv data/sample_listings.csv
```

To import the included OpenStreetMap candidate dataset:

```powershell
python scripts/import_csv.py --csv data/osm_listings_candidate.csv --batch-size 250
```

The second command imports the prepared CSV; it does not perform a new scraping operation.

To attempt a new OpenStreetMap collection, use the collection script and check the resulting records before importing them:

```powershell
python -m pip install requests
python scripts/scrape_osm.py --limit 500 --output data/osm_listings.csv
```

Only import the generated file if the collection completed successfully and its contents have been checked. Public Overpass services can be unavailable or rate-limited. Respect applicable usage policies and do not bypass access controls.

### 5. Start the React frontend

Open another PowerShell terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, usually:

`http://127.0.0.1:5173/`

Keep both the backend and frontend terminals running while using the dashboard.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | API health check |
| POST | `/api/listings/bulk` | Bulk insert business listing records |
| GET | `/api/listings?limit=100` | Retrieve business listings |
| GET | `/api/dashboard/summary` | Retrieve total listings and distinct counts |
| GET | `/api/dashboard/city-counts` | Aggregate listings by city |
| GET | `/api/dashboard/category-counts` | Aggregate listings by category |
| GET | `/api/dashboard/source-counts` | Aggregate listings by source |

Use the interactive Swagger UI at `/docs` to inspect and test the endpoints.

## Dataset and Data Quality

The current local database contains **1,297 records**:

| Data source | Records |
|---|---:|
| OpenStreetMap candidate dataset | 697 |
| Synthetic demonstration dataset | 600 |
| **Total** | **1,297** |

The database summary previously reported six distinct city labels and 75 distinct categories across these records.

The OpenStreetMap records are source-derived, but some fields are incomplete: phone numbers are missing for many listings, and some addresses contain only general location information. Category labels may also require normalization.

The 600 synthetic records are demonstration data. They must not be represented as real businesses collected from websites. The source field is used to distinguish the synthetic records from OpenStreetMap records.

These counts describe the current prepared dataset and may differ after subsequent imports or database changes.

## Challenges and Limitations

- Public data services may impose rate limits or temporary availability restrictions.
- Business listing sources do not consistently provide phone numbers and complete addresses.
- City and category labels may need standardization for reliable aggregation.
- Synthetic data is useful for testing bulk import, database operations, and dashboard functionality, but does not establish successful real-world data collection.
- Dashboard results depend on the quality and completeness of the imported dataset.

## Submission Deliverables

- **GitHub repository:** https://github.com/RITU0799/business-listings-dashboard
- **Database schema:** `database/schema.sql`
- **Database dump:** `database/business_listings.sql`
- **Demo video:** A 3–5 minute walkthrough of the running dashboard, API endpoints, database, and data collection approach.

## License and Data Use

This repository was prepared for an internship assignment. Review the applicable terms and attribution requirements for any third-party datasets before redistributing them. Synthetic demonstration records are included only to support application testing.