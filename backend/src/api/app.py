from __future__ import annotations

from api.compat import FastAPI
from api.routes.analytics import router as analytics_router
from api.routes.alerts_recommendations import router as alerts_router
from api.routes.behavior import router as behavior_router
from api.routes.profiles import router as profiles_router
from api.routes.reports import router as reports_router
from api.routes.system import router as system_router
from models.database import init_database, use_mysql_persistence

try:
    from fastapi.middleware.cors import CORSMiddleware
except ModuleNotFoundError:  # pragma: no cover - used only by lightweight import tests
    CORSMiddleware = None  # type: ignore[assignment]


def create_app() -> FastAPI:
    app = FastAPI(title="Retail Behavior Analytics API", version="0.1.0")
    if hasattr(app, "on_event") and use_mysql_persistence():

        @app.on_event("startup")
        def _startup_init_database() -> None:
            init_database()

    if CORSMiddleware is not None and hasattr(app, "add_middleware"):
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://127.0.0.1:5173",
                "http://127.0.0.1:5174",
                "http://127.0.0.1:5175",
                "http://localhost:5173",
                "http://localhost:5174",
                "http://localhost:5175",
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    app.include_router(behavior_router, prefix="/api")
    app.include_router(analytics_router, prefix="/api")
    app.include_router(profiles_router, prefix="/api")
    app.include_router(alerts_router, prefix="/api")
    app.include_router(reports_router, prefix="/api")
    app.include_router(system_router, prefix="/api")
    return app


app = create_app()
