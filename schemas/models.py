from pydantic import BaseModel

class Match(BaseModel):
    french_sentence: str
    best_match_english: str
    similarity_score: float
    verdict: str

class AnalysisResponse(BaseModel):
    matches: list[Match]