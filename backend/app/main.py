import os
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import BigInteger, Column, DateTime, Index, String, func, select
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .schemas import BulkListingsIn, CountItem, DashboardSummary, ListingOut

class Listing(Base):
    __tablename__ = "listing_master"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    business_name = Column(String(255), nullable=False)
    category = Column(String(120), nullable=False)
    city = Column(String(120), nullable=False)
    address = Column(String(500), nullable=True)
    phone = Column(String(50), nullable=True)
    source = Column(String(120), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    __table_args__ = (
        Index("idx_listing_city", "city"),
        Index("idx_listing_category", "category"),
        Index("idx_listing_source", "source"),
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    # SQL schema can also be created using database/schema.sql.
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Business Listings Dashboard API",
    description="Bulk business-listing ingestion and dashboard aggregation endpoints.",
    version="1.0.0",
    lifespan=lifespan,
)
origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "service": "business-listings-api"}

@app.post("/api/listings/bulk")
def bulk_insert(payload: BulkListingsIn, db: Session = Depends(get_db)):
    rows = [item.model_dump() for item in payload.listings]
    try:
        db.execute(Listing.__table__.insert(), rows)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Bulk insert failed. Check database connection and schema.") from exc
    return {"inserted": len(rows), "message": "Listings inserted successfully"}

@app.get("/api/listings", response_model=list[ListingOut])
def get_listings(limit: int = Query(default=100, ge=1, le=1000), offset: int = Query(default=0, ge=0), db: Session = Depends(get_db)):
    return db.scalars(select(Listing).order_by(Listing.id.desc()).offset(offset).limit(limit)).all()

@app.get("/api/dashboard/summary", response_model=DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db)):
    total = db.scalar(select(func.count(Listing.id))) or 0
    cities = db.scalar(select(func.count(func.distinct(Listing.city)))) or 0
    categories = db.scalar(select(func.count(func.distinct(Listing.category)))) or 0
    sources = db.scalar(select(func.count(func.distinct(Listing.source)))) or 0
    return DashboardSummary(total_listings=total, distinct_cities=cities, distinct_categories=categories, distinct_sources=sources)

def grouped_counts(db: Session, column, limit: int = 20):
    statement = (
        select(column.label("label"), func.count(Listing.id).label("count"))
        .group_by(column)
        .order_by(func.count(Listing.id).desc(), column.asc())
        .limit(limit)
    )
    return [{"label": row.label or "Unknown", "count": row.count} for row in db.execute(statement).all()]

@app.get("/api/dashboard/city-counts", response_model=list[CountItem])
def city_counts(limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db)):
    return grouped_counts(db, Listing.city, limit)

@app.get("/api/dashboard/category-counts", response_model=list[CountItem])
def category_counts(limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db)):
    return grouped_counts(db, Listing.category, limit)

@app.get("/api/dashboard/source-counts", response_model=list[CountItem])
def source_counts(limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db)):
    return grouped_counts(db, Listing.source, limit)
