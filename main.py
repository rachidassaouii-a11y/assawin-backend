# ASSAWIN — `main.py` PRODUCTION DEMO


import os
import json
import tempfile
from pathlib import Path

import google.generativeai as genai
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader


# ============================================================
# CONFIGURATION
# ============================================================

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY est absente des variables d'environnement.")

genai.configure(api_key=GOOGLE_API_KEY)

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

model = genai.GenerativeModel(MODEL_NAME)


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="ASSAWIN API",
    description="ASSAWIN — Cognitive ERP for Construction",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://assawin.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def home():
    return {
        "status": "online",
        "service": "ASSAWIN API",
        "version": "1.0.0",
        "ai_model": MODEL_NAME
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "ai": "gemini",
        "model": MODEL_NAME
    }


# ============================================================
# EXTRACTION PDF
# ============================================================

def extract_pdf_text(file_path: str) -> str:

    try:
        reader = PdfReader(file_path)

        pages = []

        for page_number, page in enumerate(reader.pages, start=1):

            text = page.extract_text() or ""

            if text.strip():
                pages.append(
                    f"\n--- PAGE {page_number} ---\n{text}"
                )

        return "\n".join(pages)

    except Exception as e:
        raise RuntimeError(
            f"Impossible d'extraire le PDF : {str(e)}"
        )


# ============================================================
# PROMPT ASSAWIN
# ============================================================

SYSTEM_PROMPT = """
Tu es ASSAWIN AI ENGINE, un expert senior du BTP spécialisé dans
l'analyse des DCE, CCTP, DPGF, BPU et pièces contractuelles.

Ta mission est d'identifier les éléments pouvant avoir un impact
sur le chiffrage, la marge, la conformité ou l'exécution du chantier.

Analyse notamment :

1. OBLIGATIONS CONTRACTUELLES
2. PRESCRIPTIONS TECHNIQUES
3. QUANTITÉS ET PRESTATIONS
4. INCOHÉRENCES
5. OMISSIONS POTENTIELLES
6. RISQUES DE CHIFFRAGE
7. POINTS À VÉRIFIER
8. IMPACT POTENTIEL SUR LA MARGE

Ne prétends jamais avoir détecté une omission avec certitude
si le document ne permet pas de l'établir.

Retourne exclusivement un JSON valide selon cette structure :

{
  "summary": "résumé général",
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "findings": [
    {
      "type": "OBLIGATION|INCOHERENCE|RISQUE|OMISSION|A_VERIFIER",
      "severity": "LOW|MEDIUM|HIGH|CRITICAL",
      "title": "titre court",
      "description": "explication",
      "source": "page ou section si identifiable",
      "recommendation": "action recommandée"
    }
  ],
  "commercial_alerts": [],
  "technical_alerts": [],
  "questions_to_clarify": []
}
"""


# ============================================================
# ANALYSE DOCUMENT
# ============================================================

@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Nom de fichier manquant."
        )

    extension = Path(file.filename).suffix.lower()

    if extension != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="ASSAWIN accepte actuellement uniquement les fichiers PDF."
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Le fichier est vide."
        )

    temp_path = None

    try:

        # ----------------------------------------------------
        # Sauvegarde temporaire
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
                    "Aucun texte exploitable n'a été trouvé dans ce PDF. "
                    "Une version OCR sera nécessaire pour les PDF scannés."
                )
            )

        # ----------------------------------------------------
        # Protection longueur
        # ----------------------------------------------------

        max_chars = 120000

        truncated = len(document_text) > max_chars

        analysis_text = document_text[:max_chars]

        if truncated:
            analysis_text += (
                "\n\n[DOCUMENT TRONQUÉ POUR CETTE DÉMO]"
            )

        # ----------------------------------------------------
        # Appel Gemini
        # ----------------------------------------------------

        prompt = f"""
{SYSTEM_PROMPT}

DOCUMENT À ANALYSER :

{analysis_text}
"""

        response = model.generate_content(prompt)

        raw_text = response.text.strip()

        # ----------------------------------------------------
        # Conversion JSON
        # ----------------------------------------------------

        try:

            clean_text = raw_text

            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]

            if clean_text.startswith("```"):
                clean_text = clean_text[3:]

            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]

            result = json.loads(clean_text.strip())

        except json.JSONDecodeError:

            result = {
                "summary": raw_text,
                "risk_level": "UNKNOWN",
                "findings": [],
                "commercial_alerts": [],
                "technical_alerts": [],
                "questions_to_clarify": [],
                "warning": "La réponse IA n'a pas pu être convertie automatiquement en JSON."
            }

        # ----------------------------------------------------
        # Réponse ASSAWIN
        # ----------------------------------------------------

        return {
            "success": True,
            "filename": file.filename,
            "model": MODEL_NAME,
            "pages_text_extracted": document_text.count("--- PAGE "),
            "truncated": truncated,
            "analysis": result
        }

    except HTTPException:
        raise

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


# ============================================================
# ASK — TEST RAPIDE
# ============================================================

@app.post("/ask")
async def ask(payload: dict):

    query = payload.get("query")

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Le champ 'query' est obligatoire."
        )

    try:

        response = model.generate_content(query)

        return {
            "success": True,
            "response": response.text
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


