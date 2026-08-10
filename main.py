# -*- coding: utf-8 -*-
"""
ASSAWIN(TM) API - Backend de DEMONSTRATION (Free Tier)

!!! PORTEE VOLONTAIREMENT LIMITEE !!!
Ce backend tourne sur une stack gratuite (Groq / Render) qui n'offre AUCUNE
garantie d'hebergement en Union Europeenne.

=> A utiliser UNIQUEMENT pour l'Actif 5 (Demo commerciale, donnees fictives
   type "Residence Les Pins" / "Resume X").
=> L'endpoint POST /analyze accepte un upload de PDF -- NE JAMAIS y deposer
   un vrai DCE client. Le flux "Recevoir mon audit DCE gratuit" doit rester
   sur la stack Actif 10 (Next.js / Fastify / Temporal / PostgreSQL,
   hebergement UE), conformement a la contrainte RGPD posee dans l'Actif 7 SS1.
   Chaque reponse de cette API inclut un champ "scope": "DEMO_ONLY" pour le
   rappeler a quiconque consomme cette API sans avoir lu ce fichier.
"""
import os
import json
import tempfile
import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Header, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from pypdf import PdfReader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("assawin-demo-engine")

app = FastAPI(
    title="ASSAWIN API - DEMO Free Tier (donnees fictives uniquement)",
    description="Moteur d'analyse DPGF/CCTP pour la demo commerciale ASSAWIN. Ne pas utiliser en production.",
    version="1.1.0-demo",
)

# Restreint en prod a l'origine Vercel reelle. Tant que la variable n'est
# pas positionnee, reste sur "*" pour ne pas bloquer les tests locaux.
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama-3.3-70b-versatile"

if not GROQ_API_KEY:
    logger.warning("GROQ_API_KEY non configuree.")


def get_groq_client() -> Groq:
    if not GROQ_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GROQ_API_KEY non configuree sur ce service.",
        )
    return Groq(api_key=GROQ_API_KEY)


# ============================================================
# MODELES - analyse d'une ligne DPGF
# ============================================================

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


LINE_SYSTEM_PROMPT = """
Tu es ASSAWIN AI, expert senior du chiffrage BTP, au service d'une DEMO
commerciale (donnees fictives).

Reponds STRICTEMENT sous la forme d'un objet JSON valide, sans aucun texte
avant ou apres, avec exactement ces cles :
{
  "designation_clean": "string",
  "unit": "string ou null",
  "quantity": 1.0,
  "suggested_price": 0.0,
  "confidence_score": 0.0,
  "risk_score": 0.0,
  "risk_explanation": "string"
}
Regles : quantity et suggested_price numeriques ; confidence_score et
risk_score entre 0 et 1.
"""


# ============================================================
# ROUTES SYSTEME
# ============================================================

@app.get("/")
def home():
    return {"status": "ok", "service": "ASSAWIN Demo Engine", "scope": "DEMO_ONLY"}


@app.get("/health")
def health():
    return {"status": "healthy", "ai": "groq", "model": MODEL_NAME, "scope": "DEMO_ONLY"}


@app.get("/analyze")
def analyze_info():
    """Permet d'ouvrir l'URL dans un navigateur sans 404 -- l'endpoint reel est en POST."""
    return {
        "service": "ASSAWIN Demo Engine",
        "endpoint": "/analyze",
        "method": "POST (multipart/form-data, champ 'file', PDF uniquement)",
        "status": "ready",
        "scope": "DEMO_ONLY - ne jamais deposer un vrai DCE client ici",
        "documentation": "/docs",
    }


# ============================================================
# POST /api/v1/ai/analyze-line
# ============================================================

@app.post("/api/v1/ai/analyze-line", response_model=DPGFAnalysisResponse)
def analyze_line(payload: DPGFAnalysisRequest, x_tenant_id: Optional[str] = Header(None)):
    client = get_groq_client()

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": LINE_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Ligne brute: '{payload.raw_line}' | "
                        f"Unite: {payload.context_unit or 'non precisee'} | "
                        f"Prix: {payload.context_price if payload.context_price is not None else 'non precise'}"
                    ),
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        raw_content = completion.choices[0].message.content
        if not raw_content:
            raise ValueError("Reponse IA vide.")

        try:
            data = json.loads(raw_content)
        except json.JSONDecodeError:
            logger.error("Reponse non-JSON du modele: %s", raw_content)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Le moteur IA n'a pas renvoye un JSON exploitable. Reessayez.",
            )

        return DPGFAnalysisResponse(**data)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erreur moteur Groq (analyze-line)")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur d'execution du moteur de demonstration.",
        ) from e


# ============================================================
# POST /analyze -- analyse d'un PDF complet (DEMO uniquement)
# ============================================================

def extract_pdf_text(file_path: str) -> str:
    reader = PdfReader(file_path)
    pages = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(f"--- PAGE {page_number} ---\n{text}")
    return "\n\n".join(pages)


DOCUMENT_SYSTEM_PROMPT = """
Tu es ASSAWIN DMS(TM), moteur d'intelligence documentaire specialise dans le
BTP (DCE, CCTP, DPGF), au service d'une DEMO commerciale.

Objectifs : obligations contractuelles, prescriptions techniques,
incoherences, risques de chiffrage, elements a verifier, impact marge,
recommandations operationnelles.

Regles strictes :
- Ne jamais presenter une hypothese comme un fait certain.
- Ne jamais inventer une quantite ou un prix.
- Indiquer "A_VERIFIER" si l'information est insuffisante.
- Indiquer la page si identifiable.
- Cette analyse est une aide a la decision, elle exige une validation humaine.

Reponds STRICTEMENT avec ce JSON, sans texte avant/apres :
{
  "summary": "string",
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "findings": [
    {
      "type": "OBLIGATION|INCOHERENCE|RISQUE|OMISSION|A_VERIFIER",
      "severity": "LOW|MEDIUM|HIGH|CRITICAL",
      "title": "string",
      "description": "string",
      "source": "string",
      "recommendation": "string",
      "confidence": 0.0
    }
  ],
  "commercial_alerts": [],
  "technical_alerts": [],
  "questions_to_clarify": []
}
"""

MAX_CHARS = 100000


@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nom du fichier manquant.")
    if Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="ASSAWIN Demo accepte uniquement les PDF.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Le fichier PDF est vide.")

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name

        document_text = extract_pdf_text(temp_path)
        if not document_text.strip():
            raise HTTPException(
                status_code=422,
                detail="Aucun texte exploitable trouve (document scanne ou protege).",
            )

        truncated = len(document_text) > MAX_CHARS
        document_text = document_text[:MAX_CHARS]

        client = get_groq_client()
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": DOCUMENT_SYSTEM_PROMPT},
                {"role": "user", "content": f"DOCUMENT :\n\n{document_text}"},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        raw_response = response.choices[0].message.content
        if not raw_response:
            raise ValueError("Reponse IA vide.")

        try:
            analysis = json.loads(raw_response)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Reponse IA JSON invalide : {e}",
            )

        return {
            "success": True,
            "scope": "DEMO_ONLY",
            "filename": file.filename,
            "model": MODEL_NAME,
            "pages": len(PdfReader(temp_path).pages),
            "truncated": truncated,
            "analysis": analysis,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erreur ASSAWIN Demo (/analyze)")
        raise HTTPException(status_code=500, detail=f"Erreur ASSAWIN Demo : {e}") from e
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
