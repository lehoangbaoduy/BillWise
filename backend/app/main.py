import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.auth import router as auth_router
from app.api.budgets import router as budgets_router
from app.api.cashback import router as cashback_router
from app.api.categories import router as categories_router
from app.api.dashboard import router as dashboard_router
from app.api.goals import router as goals_router
from app.api.ocr import router as ocr_router
from app.api.payment_methods import router as payment_methods_router
from app.api.recurring_bills import router as recurring_bills_router
from app.api.transactions import router as transactions_router
from app.core.config import settings
from app.core.rate_limit import limiter

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

app = FastAPI(title="BillWise API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_base_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(payment_methods_router)
app.include_router(categories_router)
app.include_router(transactions_router)
app.include_router(budgets_router)
app.include_router(goals_router)
app.include_router(dashboard_router)
app.include_router(ocr_router)
app.include_router(recurring_bills_router)
app.include_router(cashback_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
