"""
Orquestador del análisis de complejidad.
Conecta el clasificador con los agentes apropiados (Recursive/Iterative).

Detecta automáticamente si los casos son iguales para evitar duplicados.
"""
from typing import Dict, Any, Optional, Union
from enum import Enum
import json

# Importar los SCHEMAS 
from app.analysis.schemas_extraction import (
    RecursiveExtraction,
    IterativeExtraction,
    ExtractedCase,
    UnifiedCase,
    LoopInfo
)

# Importar agentes
try:
    from app.analysis.agents.recursive_agent import RecursiveAgent
    from app.analysis.agents.iterative_agent import IterativeAgent
except ImportError:
    print("Warning: No se pudieron importar los agentes")
    RecursiveAgent = None
    IterativeAgent = None


class AlgorithmType(str, Enum):
    """Tipos de algoritmo según el clasificador"""
    RECURSIVE = "RECURSIVE"
    ITERATIVE = "ITERATIVE"
    HYBRID = "HYBRID"
    SIMPLE = "SIMPLE"


class AnalysisOrchestrator:
    """
    Orquestador principal del análisis de complejidad.
    
    MEJORADO: Detecta si best/worst/average son iguales y unifica automáticamente.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el orquestador y los agentes.
        
        Args:
            api_key: API key de Anthropic (opcional, puede venir de .env)
        """
        self.api_key = api_key
        
        # Inicializar agentes 
        self._recursive_agent = None
        self._iterative_agent = None
    
    @property
    def recursive_agent(self) -> RecursiveAgent:
        """Lazy loading del RecursiveAgent"""
        if self._recursive_agent is None:
            if RecursiveAgent is None:
                raise ImportError("RecursiveAgent no está disponible")
            self._recursive_agent = RecursiveAgent(api_key=self.api_key)
        return self._recursive_agent
    
    @property
    def iterative_agent(self) -> IterativeAgent:
        """Lazy loading del IterativeAgent"""
        if self._iterative_agent is None:
            if IterativeAgent is None:
                raise ImportError("IterativeAgent no está disponible")
            self._iterative_agent = IterativeAgent(api_key=self.api_key)
        return self._iterative_agent
    
    def analyze(
        self,
        ast_node: Dict[str, Any],
        classification: str,
        subroutine_name: str = "algorithm"
    ) -> Union[RecursiveExtraction, IterativeExtraction, Dict[str, Any]]:
        """
        Analiza un algoritmo usando el agente apropiado según su clasificación.
        
        Args:
            ast_node: Nodo AST de la subrutina a analizar
            classification: Clasificación del algoritmo (RECURSIVE, ITERATIVE)
            subroutine_name: Nombre de la subrutina (opcional)
            
        Returns:
            RecursiveExtraction si es RECURSIVE
            IterativeExtraction si es ITERATIVE
            HybridExtraction si es HYBRID
            Dict con error si algo falla
        """
        # Normalizar clasificación
        classification = classification.upper()
        
        # Validar clasificación
        if classification not in [t.value for t in AlgorithmType]:
            return {
                "error": f"Clasificación desconocida: {classification}",
                "algorithm_type": classification
            }
        
        # Por ahora solo soportamos RECURSIVE e ITERATIVE
        if classification not in [AlgorithmType.RECURSIVE.value, AlgorithmType.ITERATIVE.value]:
            return {
                "error": f"Tipo de algoritmo no soportado aún: {classification}. "
                         f"Solo se soportan RECURSIVE e ITERATIVE por ahora.",
                "algorithm_type": classification
            }
        
        try:
            # Decidir qué agente usar
            if classification == AlgorithmType.RECURSIVE.value:
                return self._analyze_recursive(ast_node, subroutine_name)
            elif classification == AlgorithmType.ITERATIVE.value:
                return self._analyze_iterative(ast_node, subroutine_name)
            else:
                return {
                    "error": "Tipo no implementado",
                    "algorithm_type": classification
                }
            
        except Exception as e:
            return {
                "error": f"Error durante el análisis: {str(e)}",
                "algorithm_type": classification
            }
    
    def _analyze_recursive(
        self,
        ast_node: Dict[str, Any],
        subroutine_name: str
    ) -> Union[RecursiveExtraction, Dict[str, Any]]:
        """
        Analiza un algoritmo RECURSIVO usando RecursiveAgent.
        
        MEJORADO: Detecta automáticamente si los casos son iguales y unifica.
        
        Args:
            ast_node: Nodo AST
            subroutine_name: Nombre de la subrutina
            
        Returns:
            RecursiveExtraction con casos unificados o individuales
        """
        # Ejecutar RecursiveAgent
        result = self.recursive_agent.analyze(ast_node, subroutine_name)

        # Verificar si hubo error
        if not result.get("success"):
            return {
                "error": result.get("error", "Error desconocido en RecursiveAgent"),
                "algorithm_type": "RECURSIVE"
            }
        
        # Extraer la información del agente
        extraction = result.get("extraction", {})
        
        # Extraer datos de los 3 casos
        best_case_data = extraction.get("best_case", {})
        worst_case_data = extraction.get("worst_case", {})
        average_case_data = extraction.get("average_case")
        
        # Obtener las ecuaciones
        best_func = best_case_data.get("function", "")
        worst_func = worst_case_data.get("function", "")
        avg_func = average_case_data.get("function", "") if average_case_data else worst_func
        
        
        # DETECCIÓN INTELIGENTE: Si los 3 casos son iguales   

        cases_are_equal = (best_func == worst_func == avg_func) and best_func != ""
        
        
        # CASO 1: Los 3 casos son IGUALES → Usar unified_case
        
        
        if cases_are_equal:
            print(f"Detección: {subroutine_name} tiene casos IGUALES - usando unified_case")
            
            return RecursiveExtraction(
                algorithm_name=subroutine_name,
                algorithm_type="RECURSIVE",
                recursive_calls_count=extraction.get("recursive_calls_count", 1),
                base_case_condition=extraction.get("base_case_condition", "unknown"),
                has_different_cases=False,
                unified_case=UnifiedCase(
                    function=best_func,
                    applies_to=["best", "worst", "average"],
                    explanation=best_case_data.get("description", 
                        "Los 3 casos son idénticos - el algoritmo siempre ejecuta la misma cantidad de trabajo")
                ),
                best_case=None,
                worst_case=None,
                average_case=None
            )
        
        # CASO 2: Los casos son DIFERENTES → Usar casos individuales
        
        else:
            
            # Crear objetos ExtractedCase para cada caso
            best_case = ExtractedCase(
                case_type="best",
                condition=best_case_data.get("condition", "unknown"),
                exists=best_case_data.get("exists", True),
                function=best_func,
                explanation=best_case_data.get("description", "")
            )
            
            worst_case = ExtractedCase(
                case_type="worst",
                condition=worst_case_data.get("condition", "unknown"),
                exists=worst_case_data.get("exists", True),
                function=worst_func,
                explanation=worst_case_data.get("description", "")
            )
            
            # Average case es opcional
            average_case = None
            if average_case_data and avg_func:
                average_case = ExtractedCase(
                    case_type="average",
                    condition=average_case_data.get("condition", "unknown"),
                    exists=average_case_data.get("exists", True),
                    function=avg_func,
                    explanation=average_case_data.get("description", "")
                )
            
            return RecursiveExtraction(
                algorithm_name=subroutine_name,
                algorithm_type="RECURSIVE",
                recursive_calls_count=extraction.get("recursive_calls_count", 1),
                base_case_condition=extraction.get("base_case_condition", "unknown"),
                has_different_cases=True,
                unified_case=None,
                best_case=best_case,
                worst_case=worst_case,
                average_case=average_case
            )
    
    def _analyze_iterative(
        self,
        ast_node: Dict[str, Any],
        subroutine_name: str
    ) -> Union[IterativeExtraction, Dict[str, Any]]:
        """
        Analiza un algoritmo ITERATIVO usando IterativeAgent.
        
        MEJORADO: Detecta automáticamente si los casos son iguales y unifica.
        
        Args:
            ast_node: Nodo AST
            subroutine_name: Nombre de la subrutina
            
        Returns:
            IterativeExtraction con casos unificados o individuales
        """
        # Ejecutar IterativeAgent
        result = self.iterative_agent.analyze(ast_node, subroutine_name)
        
        # Verificar si hubo error
        if not result.get("success"):
            return {
                "error": result.get("error", "Error desconocido en IterativeAgent"),
                "algorithm_type": "ITERATIVE"
            }
        
        # Extraer la información del agente
        extraction = result.get("extraction", {})
        
        # Extraer datos de los 3 casos
        best_case_data = extraction.get("best_case", {})
        worst_case_data = extraction.get("worst_case", {})
        average_case_data = extraction.get("average_case")
        
        # Obtener las funciones
        best_func = best_case_data.get("function", "")
        worst_func = worst_case_data.get("function", "")
        avg_func = average_case_data.get("function", "") if average_case_data else worst_func
        
        # DETECCIÓN INTELIGENTE: Si los 3 casos son iguales   
        
        cases_are_equal = (best_func == worst_func == avg_func) and best_func != ""
        
        # Construir lista de LoopInfo
        loops_data = extraction.get("loops", [])
        loops = []
        for loop_data in loops_data:
            loops.append(LoopInfo(
                loop_type=loop_data.get("type", "FOR"),
                variable=loop_data.get("variable", "i"),
                bound_start=loop_data.get("start", "1"),
                bound_end=loop_data.get("end", "n"),
                nesting_level=loop_data.get("nesting_level", 0)
            ))
        
        # CASO 1: Los 3 casos son IGUALES → Usar unified_case
        
        if cases_are_equal:
            
            return IterativeExtraction(
                algorithm_name=subroutine_name,
                algorithm_type="ITERATIVE",
                loops=loops,
                max_nesting=extraction.get("max_nesting", len(loops)),
                has_different_cases=False,
                unified_case=UnifiedCase(
                    function=best_func,
                    applies_to=["best", "worst", "average"],
                    explanation=best_case_data.get("description", 
                        "Los 3 casos son idénticos - el algoritmo siempre ejecuta la misma cantidad de trabajo")
                ),
                best_case=None,
                worst_case=None,
                average_case=None
            )
        
        # CASO 2: Los casos son DIFERENTES → Usar casos individuales
        
        else:
            
            # Crear objetos ExtractedCase para cada caso
            best_case = ExtractedCase(
                case_type="best",
                condition=best_case_data.get("condition", "unknown"),
                exists=best_case_data.get("exists", True),
                function=best_func,
                explanation=best_case_data.get("description", "")
            )
            
            worst_case = ExtractedCase(
                case_type="worst",
                condition=worst_case_data.get("condition", "unknown"),
                exists=worst_case_data.get("exists", True),
                function=worst_func,
                explanation=worst_case_data.get("description", "")
            )
            
            # Average case es opcional
            average_case = None
            if average_case_data and avg_func:
                average_case = ExtractedCase(
                    case_type="average",
                    condition=average_case_data.get("condition", "unknown"),
                    exists=average_case_data.get("exists", True),
                    function=avg_func,
                    explanation=average_case_data.get("description", "")
                )
            
            return IterativeExtraction(
                algorithm_name=subroutine_name,
                algorithm_type="ITERATIVE",
                loops=loops,
                max_nesting=extraction.get("max_nesting", len(loops)),
                has_different_cases=True,
                unified_case=None,
                best_case=best_case,
                worst_case=worst_case,
                average_case=average_case
            )