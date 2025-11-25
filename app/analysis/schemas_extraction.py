"""
Schemas: Extracción de ecuaciones/funciones

Detecta automáticamente si los casos son iguales o diferentes
para evitar duplicados y ahorrar recursos
"""

from typing import Literal, Optional, List
from pydantic import BaseModel, Field


# CASO ÚNICO (cuando best/worst/average son idénticos)

class UnifiedCase(BaseModel):
    """
    Representa un caso unificado cuando best/worst/average tienen la misma ecuación.
    Evita duplicar información y ahorra recursos.
    """
    function: str = Field(
        description="Ecuación única que aplica a todos los casos",
        examples=["T(n) = T(n-1) + O(1)", "Σ(i=1 to n) O(1)"]
    )
    applies_to: List[Literal["best", "worst", "average"]] = Field(
        description="Lista de casos a los que aplica esta ecuación"
    )
    explanation: str = Field(
        description="Por qué todos los casos son idénticos"
    )


# CASO INDIVIDUAL (cuando los casos son diferentes)

class ExtractedCase(BaseModel):
    """
    Un caso individual (mejor/peor/promedio) con su función matemática SIN resolver
    """
    case_type: Literal["best", "worst", "average"]
    condition: str = Field(
        description="Condición que activa este caso",
        examples=["n = 0", "array ordenado", "todos los elementos"]
    )
    exists: bool = Field(
        description="Si este caso existe para el algoritmo"
    )
    function: str = Field(
        description="Ecuación de recurrencia o función de eficiencia SIN resolver",
        examples=[
            "T(n) = T(n-1) + O(1)",
            "T(n) = 2T(n/2) + n", 
            "Σ(i=1 to n) O(1)",
            "Σ(i=1 to n) Σ(j=1 to i) O(1)"
        ]
    )
    explanation: str = Field(
        description="Por qué este es el mejor/peor/promedio caso"
    )


# RESULTADO DE EXTRACCIÓN RECURSIVA (MEJORADO)

class RecursiveExtraction(BaseModel):
    """
    Resultado del agente extractor para algoritmos RECURSIVOS
    
    Detecta automáticamente si los 3 casos son iguales.
    Si son iguales, usa unified_case (ahorro de recursos en Fase 2).
    Si son diferentes, usa best_case/worst_case/average_case.
    """
    algorithm_name: str
    algorithm_type: Literal["RECURSIVE"]
    
    # Información estructural del algoritmo
    recursive_calls_count: int = Field(
        description="Cuántas llamadas recursivas hay por invocación"
    )
    base_case_condition: str = Field(
        description="Condición del caso base",
        example="n = 0"
    )
    
    # Indicador de diferencias
    has_different_cases: bool = Field(
        description="True si best/worst/average tienen ecuaciones diferentes. "
                    "False si todos son idénticos."
    )
    
    # OPCIÓN 1: Caso unificado (cuando los 3 son iguales)
    unified_case: Optional[UnifiedCase] = Field(
        default=None,
        description="Usado cuando best/worst/average tienen la misma ecuación. "
                    "Ahorra recursos en Fase 2 (solo 1 resolución en lugar de 3)."
    )
    
    # OPCIÓN 2: Casos individuales (cuando son diferentes)
    best_case: Optional[ExtractedCase] = Field(
        default=None,
        description="Caso mejor. None si se usa unified_case."
    )
    worst_case: Optional[ExtractedCase] = Field(
        default=None,
        description="Caso peor. None si se usa unified_case."
    )
    average_case: Optional[ExtractedCase] = Field(
        default=None,
        description="Caso promedio. None si se usa unified_case o no existe."
    )


# RESULTADO DE EXTRACCIÓN ITERATIVA

class LoopInfo(BaseModel):
    """
    Información de un loop específico
    """
    loop_type: Literal["FOR", "WHILE", "REPEAT"]
    variable: str = Field(description="Variable del loop", example="i")
    bound_start: str = Field(description="Inicio", example="1")
    bound_end: str = Field(description="Fin", example="n")
    nesting_level: int = Field(description="Nivel de anidamiento (0=externo)")


class IterativeExtraction(BaseModel):
    """
    Resultado del agente extractor para algoritmos ITERATIVOS
    
    Detecta automáticamente si los 3 casos son iguales.
    Si son iguales, usa unified_case (ahorro de recursos en Fase 2).
    Si son diferentes, usa best_case/worst_case/average_case.
    """
    algorithm_name: str
    algorithm_type: Literal["ITERATIVE"]
    
    # Información estructural del algoritmo
    loops: list[LoopInfo] = Field(
        description="Todos los loops detectados en el algoritmo"
    )
    max_nesting: int = Field(
        description="Máximo nivel de anidamiento de loops"
    )
    
    # NUEVO: Indicador de diferencias
    has_different_cases: bool = Field(
        description="True si best/worst/average tienen funciones diferentes. "
                    "False si todos son idénticos."
    )
    
    # OPCIÓN 1: Caso unificado (cuando los 3 son iguales)
    unified_case: Optional[UnifiedCase] = Field(
        default=None,
        description="Usado cuando best/worst/average tienen la misma función. "
                    
    )
    
    # OPCIÓN 2: Casos individuales (cuando son diferentes)
    best_case: Optional[ExtractedCase] = Field(
        default=None,
        description="Caso mejor. None si se usa unified_case."
    )
    worst_case: Optional[ExtractedCase] = Field(
        default=None,
        description="Caso peor. None si se usa unified_case."
    )
    average_case: Optional[ExtractedCase] = Field(
        default=None,
        description="Caso promedio. None si se usa unified_case o no existe."
    )



# RESPUESTA FINAL DEL ENDPOINT

class ExtractionResponse(BaseModel):
    """
    Respuesta del endpoint después de Fase 1 (extracción)
    
    Contiene las ecuaciones/funciones extraídas pero NO resueltas
    """
    subroutines: list[RecursiveExtraction | IterativeExtraction ]
    
    # Metadata
    extraction_timestamp: str = Field(
        description="Cuándo se hizo la extracción"
    )
    phase: Literal["extraction"] = Field(
        default="extraction",
        description="Indica que esto es solo Fase 1"
    )