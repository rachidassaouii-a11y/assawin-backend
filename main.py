import os
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from groq import Groq

app = FastAPI(title="ASSAWIN API", version="1.0.0")

# Configuration CORS pour autoriser le frontend Vite local et Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DPGFAnalysisRequest(BaseModel):
    raw_line: str
    context_unit: Optional[str] = None
    context_price: Optional[float] = None

class DPGFAnalysisResponse(BaseModel):
    designation_clean: str
    unit: Optional[str]
    quantity: float
    suggested_price: float
    confidence_score: float
    risk_score: float
    risk_explanation: str

@app.get("/")
def home():
    return {"status": "ok", "service": "ASSAWIN Engine API"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/api/v1/ai/analyze-line", response_model=DPGFAnalysisResponse)
def analyze_line(payload: DPGFAnalysisRequest, x_tenant_id: Optional[str] = Header(None)):
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise HTTPException(status_code=500, detail="Clé GROQ_API_KEY non configurée")

    client = Groq(api_key=groq_api_key)

    prompt = f"""Tu es un expert en chiffrage BTP pour le logiciel ASSAWIN.
Analyse cette ligne brute de DPGF/CCTP : "{payload.raw_line}".
Unité renseignée : {payload.context_unit or 'Non précisée'}.
Prix renseigné : {payload.context_price or 'Non précisé'}.

Réponds STRICTEMENT au format JSON avec ces clés exactes :
- designation_clean (string)
- unit (string ou null)
- quantity (number, par défaut 1.0)
- suggested_price (number)
- confidence_score (number entre 0.0 et 1.0)
- risk_score (number entre 0.0 et 1.0)
- risk_explanation (string)
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        import json
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'analyse IA : {str(e)}")



