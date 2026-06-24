from fastapi import FastAPI

from db_end.db1 import engine, Base
import db_end.models

from backend.routers import auth_router, invoice_router,ai_router


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GenAI Invoice Dashboard API",
    version="0.1.0"
)


app.include_router(
    auth_router.router,
    prefix="/auth",
    tags=["Authentication"]
)


app.include_router(
    invoice_router.router,
    prefix="/invoices",
    tags=["Invoices"]
)



app.include_router(
    ai_router.router,
    prefix="/ai",
    tags=["AI Consultation"]
)

@app.get("/")
def root():
    return {
        "status": "running",
        "service": "GenAI Invoice Dashboard API"
    }
