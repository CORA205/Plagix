# Plagix — Détection de Plagiat par Traduction

Microservice FastAPI qui détecte le plagiat translinguistique en comparant des documents français avec une base de référence en anglais via similarité cosinus sur des embeddings multilingues.

---

## Installation

### 1. Cloner le repo
git clone https://github.com/ton_username/Plagiat_analysis.git
cd Plagiat_analysis

### 2. Créer et activer le venv
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac

### 3. Installer les dépendances
pip install -r requirements.txt

### 4. Télécharger le modèle spaCy
python -m spacy download fr_core_news_sm


## Lancement
uvicorn main:app --reload

Swagger UI : http://localhost:8000/docs

---

## Endpoint

### `POST /analyze/`
Soumet un document en français (PDF, TXT, DOCX).

**Réponse :**
```json
{
  "matches": [
    {
      "french_sentence": "L'intelligence artificielle transforme le monde.",
      "best_match_english": "Artificial Intelligence is the future of tech innovation",
      "similarity_score": 0.8421,
      "verdict": "Plagiat par traduction"
    }
  ]
}
```

**Erreurs gérées :**
- `400` Format de fichier non supporté
- `400` Document vide
- `400` Langue détectée différente du français
- `422` Requête mal formée

---

## Déploiement

🔗 [Lien de démonstration](https://ton-lien-deploy.com)