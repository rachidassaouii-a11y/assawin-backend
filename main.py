import os
import tempfile
import google.generativeai as genai
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.document_loaders import PyPDFLoader

# Configuration de Gemini
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

app = FastAPI(title="ASSAWIN - Risk Detection Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)):
    try:
        # Sauvegarde temporaire du PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Extraction du texte
        loader = PyPDFLoader(tmp_path)
        docs = loader.load()
        full_text = "\n".join([page.page_content for page in docs])
        os.remove(tmp_path)

        # Appel à Gemini
        prompt = f"""Tu es un expert en analyse de risques contractuels BTP. 
        Analyse ce texte et retourne UNIQUEMENT un JSON structuré avec : 
        'filename', 'risk_score' (int), et une liste 'risks' contenant 
        (category, clause_reference, severity, description, financial_impact, recommendation).
        
        Texte à analyser : {full_text[:20000]}"""

        response = model.generate_content(prompt)
        
        # Nettoyage pour récupérer juste le JSON
        clean_json = response.text.replace('```json', '').replace('```', '')
        import json
        return json.loads(clean_json)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
