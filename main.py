import os
import json
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Header, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from pypdf import PdfReader


# ============================================================
# ASSAWIN API
# ============================================================

app = FastAPI(
    title="ASSAWIN API",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# CONFIGURATION GROQ
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY non configurée")

MODEL_NAME = "llama-3.3-70b-versatile"


def get_groq_client():
    if not GROQ_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY non configurée sur le serveur."
        )

    return Groq(api_key=GROQ_API_KEY)


# ============================================================
# MODELES DPGF
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


# ============================================================
# ROUTES SYSTEME
# ============================================================

@app.get("/")
def home():
    return {
        "status": "ok",
        "service": "ASSAWIN Engine API",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "ai": "groq",
        "model": MODEL_NAME
    }


# ============================================================
# GET /analyze
# Permet d'ouvrir l'URL dans Chrome sans erreur 404
# ============================================================

@app.get("/analyze")
def analyze_info():
    return {
        "service": "ASSAWIN DMS™",
        "endpoint": "/analyze",
        "method": "POST",
        "status": "ready",
        "description": "Envoyez un fichier PDF pour lancer une analyse ASSAWIN.",
        "documentation": "/docs"
    }


# ============================================================
# POST /api/v1/ai/analyze-line
# Analyse d'une ligne DPGF
# ============================================================

@app.post(
    "/api/v1/ai/analyze-line",
    response_model=DPGFAnalysisResponse
)
def analyze_line(
    payload: DPGFAnalysisRequest,
    x_tenant_id: Optional[str] = Header(None)
):

    client = get_groq_client()

    prompt = f"""
Tu es ASSAWIN AI, expert senior du chiffrage BTP.

Analyse cette ligne brute de DPGF/CCTP :

"{payload.raw_line}"

Unité renseignée :
{payload.context_unit or "Non précisée"}

Prix renseigné :
{payload.context_price if payload.context_price is not None else "Non précisé"}

Réponds STRICTEMENT en JSON valide avec exactement ces clés :

{{
  "designation_clean": "string",
  "unit": "string ou null",
  "quantity": 1.0,
  "suggested_price": 0.0,
  "confidence_score": 0.0,
  "risk_score": 0.0,
  "risk_explanation": "string"
}}

Règles :
- quantity doit être numérique.
- suggested_price doit être numérique.
- confidence_score entre 0 et 1.
- risk_score entre 0 et 1.
- Ne mets aucun texte hors JSON.
"""

    try:

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={
                "type": "json_object"
            },
            temperature=0.1
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError("Réponse IA vide.")

        result = json.loads(content)

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Erreur d'analyse IA : {str(e)}"
        )


# ============================================================
# EXTRACTION TEXTE PDF
# ============================================================

def extract_pdf_text(file_path: str) -> str:

    reader = PdfReader(file_path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text() or ""

        if text.strip():

            pages.append(
                f"--- PAGE {page_number} ---\n{text}"
            )

    return "\n\n".join(pages)


# ============================================================
# POST /analyze
# ANALYSE DCE / CCTP
# ============================================================

@app.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # Vérification fichier
    # --------------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Nom du fichier manquant."
        )

    extension = Path(file.filename).suffix.lower()

    if extension != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="ASSAWIN accepte actuellement uniquement les PDF."
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Le fichier PDF est vide."
        )

    temp_path = None

    try:

        # ----------------------------------------------------
        # Création fichier temporaire
        # ----------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:

            temp_file.write(content)
            temp_path = temp_file.name

        # ----------------------------------------------------
        # Extraction
        # ----------------------------------------------------

        document_text = extract_pdf_text(temp_path)

        if not document_text.strip():

            raise HTTPException(
                status_code=422,
                detail=(
                    "Aucun texte exploitable trouvé dans ce PDF. "
                    "Le document semble être scanné ou protégé."
                )
            )

        # ----------------------------------------------------
        # Limitation sécurité / contexte
        # ----------------------------------------------------

        MAX_CHARS = 100000

        truncated = len(document_text) > MAX_CHARS

        document_text = document_text[:MAX_CHARS]

        # ----------------------------------------------------
        # PROMPT ASSAWIN DMS
        # ----------------------------------------------------

        prompt = f"""
Tu es ASSAWIN DMS™, moteur d'intelligence documentaire spécialisé
dans le BTP, le chiffrage, les DCE, CCTP et DPGF.

Analyse rigoureusement le document suivant.

OBJECTIFS :

1. Identifier les obligations contractuelles.
2. Identifier les prescriptions techniques importantes.
3. Identifier les incohérences potentielles.
4. Identifier les risques de chiffrage.
5. Identifier les prestations ou informations nécessitant vérification.
6. Identifier les éléments pouvant affecter la marge.
7. Donner des recommandations opérationnelles.

IMPORTANT :

- Ne jamais présenter une hypothèse comme un fait certain.
- Ne jamais inventer une quantité.
- Ne jamais inventer un prix.
- Indiquer "A_VERIFIER" lorsque l'information est insuffisante.
- Indiquer la page lorsque celle-ci est identifiable.
- L'analyse constitue une aide à la décision et nécessite une validation humaine.

DOCUMENT :

{document_text}

Réponds STRICTEMENT avec ce JSON :

{{
  "summary": "Résumé général du dossier",
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "findings": [
    {{
      "type": "OBLIGATION|INCOHERENCE|RISQUE|OMISSION|A_VERIFIER",
      "severity": "LOW|MEDIUM|HIGH|CRITICAL",
      "title": "Titre court",
      "description": "Description précise",
      "source": "Page ou section",
      "recommendation": "Action recommandée",
      "confidence": 0.0
    }}
  ],
  "commercial_alerts": [],
  "technical_alerts": [],
  "questions_to_clarify": []
}}

Les scores confidence doivent être compris entre 0 et 1.

Ne retourne aucun texte avant ou après le JSON.
"""

        # ----------------------------------------------------
        # IA GROQ
        # ----------------------------------------------------

        client = get_groq_client()

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={
                "type": "json_object"
            },
            temperature=0.1
        )

        raw_response = response.choices[0].message.content

        if not raw_response:
            raise ValueError("Réponse IA vide.")

        # ----------------------------------------------------
        # JSON
        # ----------------------------------------------------

        analysis = json.loads(raw_response)

        # ----------------------------------------------------
        # Réponse ASSAWIN
        # ----------------------------------------------------

        return {
            "success": True,
            "filename": file.filename,
            "model": MODEL_NAME,
            "pages": len(PdfReader(temp_path).pages),
            "truncated": truncated,
            "analysis": analysis
        }

    except HTTPException:
        raise

    except json.JSONDecodeError as e:

        raise HTTPException(
            status_code=500,
            detail=f"Réponse IA JSON invalide : {str(e)}"
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Erreur ASSAWIN : {str(e)}"
        )

    finally:

        if temp_path and os.path.exists(temp_path):

            try:
                os.remove(temp_path)
            except Exception:
                pass


