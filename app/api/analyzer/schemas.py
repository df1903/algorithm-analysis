from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pydantic import Field


from app.analysis.schemas_extraction import (
    RecursiveExtraction,
    IterativeExtraction,
)


class AnalyzerRequest(BaseModel):
    text: str
    want_diagram: bool = False

class Bound(BaseModel):
    big_o: str
    big_omega: str
    big_theta: Optional[str] = None
    strong_bounds: Optional[str] = None

class Step(BaseModel):
    description: str

class AnalyzerResponse(BaseModel):
    normalized_pseudocode: str
    bounds: Bound
    reasoning: List[Step]
    artifacts: Optional[Dict[str, Any]] = None


class AstRequest(BaseModel):
    """Petición para obtener el AST a partir de código en texto."""

    text: str


class AstResponse(BaseModel):
    """Respuesta con el AST serializado a JSON."""

    ast: Dict[str, Any]
    pretty: Optional[str] = None
    classification: dict
    analysis: RecursiveExtraction | IterativeExtraction
    resolution: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Resolución de complejidad (Fase 2: O, Ω, Θ)"
    )
    error: Optional[str] = None
    
    
class NaturalLanguageRequest(BaseModel):
    description: str = Field(
        description="Descripción del algoritmo en lenguaje natural",     
    )