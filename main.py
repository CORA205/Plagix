from fastapi import FastAPI, UploadFile, File, HTTPException
from schemas.models import Match, AnalysisResponse
import fitz
import io
import spacy
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from langdetect import detect, LangDetectException
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Chargement du modèle spacy français
nlp = spacy.load("fr_core_news_sm")
logger.info("Modèle spacy français chargé")

# Initialisation du modele d'embeddings
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
logger.info("Modèle d'encodage(vectorisation) chargé")

text_corpus = [
    "Artificial Intelligence is the future of tech innovation",
    "This is an AI Engineer Recrutement test",
    "This projet is a FastAPI project"
]


async def extract_text(doc: UploadFile):
    file_bytes = io.BytesIO(await doc.read())
    ext = doc.filename.rsplit(".", 1)[-1].lower()

    extracted_text = ""
    with fitz.open(stream=file_bytes, filetype=ext) as doc:
        for page in doc:
            extracted_text += page.get_text()

    return extracted_text.replace("\n", "")

def split_sentences(text: str) -> list[str]:
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents]


app = FastAPI(
    title="Plagix"
)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/analyze/")
async def cross_lingual(file: UploadFile = File(...)):

    start_time = time.time()
    logger.info(f"Nouvelle requête reçue — fichier : {file.filename}")

    if not file.filename.endswith((".pdf", ".txt", ".docx")):
        logger.warning(f"Format refusé : {file.filename}")
        raise HTTPException(
            status_code=400,
            detail="Formats acceptés : PDF, TXT, DOCX"
        )

    text = await extract_text(file)
    logger.info("Contenu du document extrait")

    if not text.strip():
        logger.warning("Document vide reçu")
        raise HTTPException(
            status_code=400,
            detail="Le document est vide ou illisible"
        )

    try:
        lang = detect(text)
    except LangDetectException:
        logger.error("Impossible de détecter la langue du document")
        raise HTTPException(
            status_code=400,
            detail="Impossible de détecter la langue du document"
        )

    if lang != "fr":
        logger.warning(f"Langue détectée non supportée : {lang}")
        raise HTTPException(
            status_code=400,
            detail=f"Langue détectée : {lang}. Seul le français est accepté."
        )

    logger.info("Langue détectée : français")

    # Découpage du doc en sentences
    doc_sentences = split_sentences(text)
    logger.info(f"{len(doc_sentences)} phrases extraites")

    # Vectorisation des sentences
    doc_embeddings = model.encode(doc_sentences)
    logger.info("Embeddings du document générés")

    # Vectorisation des textes du corpus
    corpus_embeddings = model.encode(text_corpus)
    logger.info("Embeddings du corpus générés")

    similarities = cosine_similarity(
        doc_embeddings,
        corpus_embeddings
    )

    threshold = 0.70

    results = []
    for i, sentence in enumerate(doc_sentences):
        scores = similarities[i]
        best_idx = scores.argmax()
        best_score = float(scores[best_idx])

        results.append(Match(
            french_sentence=sentence,
            best_match_english=text_corpus[best_idx],
            similarity_score=round(best_score, 4),
            verdict="Plagiat par traduction" if best_score >= threshold else "Non suspect"
        ))

    elapsed = round(time.time() - start_time, 3)
    logger.info(f"Analyse terminée en {elapsed}s — {len(results)} correspondances retournées")

    return AnalysisResponse(matches=results)