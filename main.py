import os
import tempfile
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

app = FastAPI(title="ASSAWIN - Risk Detection Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RiskItem(BaseModel):
    category: str = Field(description="Catégorie du risque (ex: Pénalités, Planning, Prix, Juridique)")
    clause_reference: str = Field(description="Référence de la clause ou section du document")
    severity: str = Field(description="Niveau de sévérité : ÉLEVÉ, MOYEN, FAIBLE")
    description: str = Field(description="Description concise de la clause problématique")
    financial_impact: str = Field(description="Impact financier estimé ou risque sous-jacent")
    recommendation: str = Field(description="Action recommandée pour l'entreprise BTP")

class AnalysisResponse(BaseModel):
    filename: str
    risk_score: int = Field(description="Score global de risque de 0 à 100")
    risks: List[RiskItem]

llm = ChatOpenAI(model="gpt-4o", temperature=0)
parser = JsonOutputParser(pydantic_object=AnalysisResponse)

SYSTEM_PROMPT = """Tu es un expert en analyse de risques contractuels BTP (CCTP, CCAP, DPGF).
Ton rôle est d'analyser le document fourni et d'identifier les risques financiers, juridiques et opérationnels majeurs pour l'entreprise de bâtiment.

Recherche spécifiquement :
1. Les pénalités de retard excessives ou non plafonnées.
2. Les clauses de révision ou d'actualisation de prix défavorables.
3. Les transferts de responsabilités inhabituels (ex: études d'exécution à la charge de l'entreprise non prévues).
4. Les jalons de planning irréalistes.
5. Les conditions de paiement et retenues de garantie litigieuses.

Sois précis, factuel et concis.
{format_instructions}
"""

prompt_template = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("user", "Voici le texte extrait du document BTP à analyser :\n\n{text}")
])

chain = prompt_template | llm | parser

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_document(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont supportés pour le moment.")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        loader = PyPDFLoader(tmp_path)
        docs = loader.load()
        full_text = "\n".join([page.page_content for page in docs])
        extracted_text = full_text[:30000] 

        os.remove(tmp_path)

        result = chain.invoke({
            "text": extracted_text,
            "format_instructions": parser.get_format_instructions()
        })

        result["filename"] = file.filename
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse : {str(e)}")
