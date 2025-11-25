"""
Schemas para la resolución de complejidades
Define la estructura de las complejidades resueltas
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal


class ResolvedComplexity(BaseModel):
    """
    Representa una complejidad resuelta con sus tres notaciones
    """
    O: str = Field(
        description="Cota superior (Big-O)",
        example="O(n log n)"
    )
    
    Omega: str = Field(
        description="Cota inferior (Omega)",
        example="Ω(n log n)"
    )
    
    Theta: Optional[str] = Field(
        default=None,
        description="Cota ajustada (Theta). Solo si O = Omega",
        example="Θ(n log n)"
    )
    
    is_tight_bound: bool = Field(
        description="True si O = Omega (hay cota fuerte Theta)",
        example=True
    )
    
    method: Literal[
        "teorema_maestro",
        "sustitucion",
        "arbol_recursion",
        "analisis_directo",
        "simplificacion_sumatorias",
        "unknown",
        "error"
    ] = Field(
        description="Método usado para resolver",
        example="teorema_maestro"
    )
    
    steps: list[str] = Field(
        default_factory=list,
        description="Pasos matemáticos detallados del razonamiento",
        example=[
            "Recurrencia: T(n) = 2T(n/2) + O(n)",
            "Parámetros: a=2, b=2, f(n)=n",
            "Calcular: log_2(2) = 1",
            "Comparar: f(n)=n vs n^1=n → Iguales",
            "Caso 2 del Teorema Maestro",
            "Resultado: T(n) = Θ(n log n)"
        ]
    )
    
    explanation: str = Field(
        description="Explicación narrativa completa de la resolución",
        example="Aplicando el Teorema Maestro para T(n) = 2T(n/2) + O(n). Con a=2 llamadas recursivas y división por b=2, calculamos log_b(a)=1. Como f(n)=n coincide con n^1, estamos en Caso 2, resultando en Θ(n log n)."
    )


class CaseResolution(BaseModel):
    """
    Resolución completa de un caso (best/worst/average)
    Incluye la ecuación original y su resolución
    """
    case_type: Literal["best", "worst", "average", "unified"] = Field(
        description="Tipo de caso",
        example="worst"
    )
    
    original_equation: str = Field(
        description="Ecuación original desde Fase 1",
        example="T(n) = 2T(n/2) + O(n)"
    )
    
    resolution: ResolvedComplexity = Field(
        description="Complejidad resuelta con O, Ω, Θ"
    )


class AlgorithmResolution(BaseModel):
    """
    Resolución completa de un algoritmo (todos sus casos)
    """
    algorithm_name: str = Field(
        description="Nombre del algoritmo",
        example="mergesort"
    )
    
    algorithm_type: Literal["RECURSIVE", "ITERATIVE"] = Field(
        description="Tipo de algoritmo",
        example="RECURSIVE"
    )
    
    has_different_cases: bool = Field(
        description="Si los casos best/worst/average son diferentes",
        example=False
    )
    
    # Casos individuales
    best_case: Optional[CaseResolution] = Field(
        default=None,
        description="Resolución del mejor caso"
    )
    
    worst_case: Optional[CaseResolution] = Field(
        default=None,
        description="Resolución del peor caso"
    )
    
    average_case: Optional[CaseResolution] = Field(
        default=None,
        description="Resolución del caso promedio"
    )
    
    # Caso unificado 
    unified_case: Optional[CaseResolution] = Field(
        default=None,
        description="Resolución única cuando todos los casos son iguales"
    )