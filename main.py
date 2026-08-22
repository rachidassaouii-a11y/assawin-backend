from app.routers import devis
app.include_router(devis.router, prefix="/api/v1")
