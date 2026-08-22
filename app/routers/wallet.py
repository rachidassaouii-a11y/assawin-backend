from typing import List
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/wallet", tags=["Wallet"])

class WalletProject(BaseModel):
    id: str
    name: str
    status: str
    total_value: float

class WalletSummary(BaseModel):
    total_projects: int
    total_revenue: float
    total_pending: float
    cash_flow: float
    next_priority: str
    projects: List[WalletProject]

@router.get("/", response_model=WalletSummary)
async def get_wallet_summary():
    return WalletSummary(
        total_projects=5,
        total_revenue=25000.00,
        total_pending=8000.00,
        cash_flow=17000.00,
        next_priority="Créer un devis pour le projet Alpha",
        projects=[
            WalletProject(id="1", name="Projet Alpha", status="En cours", total_value=12000.00),
            WalletProject(id="2", name="Projet Beta", status="Devis envoyé", total_value=5000.00)
        ]
    )
