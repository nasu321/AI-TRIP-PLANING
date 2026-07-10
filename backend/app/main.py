"""
FastAPI Main Application Entry Point
Agentic AI Smart Travel & Recommendation Platform
"""
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.routers import trips, reports, users

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown events."""
    logger.info("🚀 Starting Agentic AI Travel Platform...")
    await init_db()

    # Load all open datasets into memory
    from app.services.data_manager import data_manager
    data_manager.load()
    stats = data_manager.get_stats()
    logger.info(
        f"📊 Datasets loaded: {stats['airports']:,} airports | {stats['routes']:,} routes | "
        f"{stats['airlines']:,} airlines | {stats['hotel_cities']} hotel cities | "
        f"{stats['budget_cities']} budget cities | {stats['flight_routes']} flight routes"
    )

    # Create reports directory
    os.makedirs(settings.REPORTS_DIR, exist_ok=True)
    logger.info(f"📁 Reports directory: {settings.REPORTS_DIR}")
    logger.info(f"🤖 LLM Provider: {settings.LLM_PROVIDER}")
    logger.info(f"💾 Database: {settings.DATABASE_TYPE}")
    logger.info(f"✅ Platform ready! Backend running on port {settings.BACKEND_PORT}")

    yield

    logger.info("🛑 Shutting down Travel Platform...")


# Initialize FastAPI app
app = FastAPI(
    title="Agentic AI Travel Platform",
    description="""
    ## 🌍 Agentic AI Smart Travel & Recommendation Platform

    A multi-agent AI system for intelligent, personalized travel planning.

    ### Features
    - **Multi-Agent AI**: LangGraph-powered agents for weather, hotels, flights, reviews, budget
    - **Smart Recommendations**: Weighted scoring algorithm for hotels and attractions
    - **Review Intelligence**: Sentiment analysis with pros/cons extraction
    - **Travel Score**: Quantitative trip confidence score (0-100)
    - **PDF Reports**: Professional PDF generation
    - **WhatsApp Delivery**: Automated report delivery via Twilio
    - **Personalization**: Travel persona classification and adaptive tips
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(trips.router)
app.include_router(reports.router)
app.include_router(users.router)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "Agentic AI Travel Platform",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    from app.services.data_manager import data_manager
    stats = data_manager.get_stats()
    return {
        "status": "healthy",
        "llm_provider": settings.LLM_PROVIDER,
        "llm_configured": settings.is_llm_configured,
        "database": settings.DATABASE_TYPE,
        "mock_weather": settings.USE_MOCK_WEATHER,
        "mock_places": settings.USE_MOCK_PLACES,
        "mock_flights": settings.USE_MOCK_FLIGHTS,
        "mock_whatsapp": settings.USE_MOCK_WHATSAPP,
        "datasets": stats,
    }


@app.get("/api/data/info", tags=["Datasets"])
async def dataset_info():
    """Returns linked dataset metadata and record counts."""
    from app.services.data_manager import data_manager
    data_manager.load()
    return {
        "stats": data_manager.get_stats(),
        "registry": data_manager.get_registry(),
        "sources": [
            {"name": "OpenFlights", "url": "https://github.com/jpatokal/openflights", "license": "ODbL"},
            {"name": "OKFN Country Codes", "url": "https://github.com/datasets/country-codes", "license": "CC0"},
            {"name": "Numbeo Cost of Living Index", "url": "https://www.numbeo.com/cost-of-living/", "license": "Research Use"},
            {"name": "IATA Economics", "url": "https://www.iata.org/en/iata-repository/publications/economic-reports/", "license": "Research Use"},
            {"name": "STR Global Hotel Reports", "url": "https://str.com/", "license": "Research Use"},
        ]
    }


@app.get("/api/data/lookup", tags=["Datasets"])
async def lookup_destination(destination: str):
    """Lookup real database values for a destination."""
    import math, json
    from fastapi.responses import Response
    from app.services.data_manager import data_manager
    data_manager.load()

    raw = {
        "destination": destination,
        "airports":       data_manager.find_airports(destination),
        "hotel_prices":   data_manager.get_hotel_prices(destination),
        "cost_of_living": data_manager.get_cost_of_living(destination),
        "flight_prices":  data_manager.get_flight_prices(destination),
        "airlines":       data_manager.get_airlines_serving(destination),
        "real_routes":    data_manager.get_routes_to(destination, limit=8),
        "attractions":    data_manager.get_attractions(destination),
    }

    def nan_clean(obj):
        if isinstance(obj, dict):
            return {k: nan_clean(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [nan_clean(i) for i in obj]
        if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
            return None
        return obj

    safe = nan_clean(raw)
    return Response(content=json.dumps(safe), media_type="application/json")
