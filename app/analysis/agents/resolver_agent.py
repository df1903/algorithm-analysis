"""
Agente resolvedor de complejidades (Fase 2)
Toma ecuaciones de Fase 1 y las resuelve usando técnicas matemáticas
"""
from typing import Dict, Any, Optional, Union, List
from app.analysis.agents.base_agent import BaseAgent
from app.analysis.schemas_resolution import (
    ResolvedComplexity,
    CaseResolution,
    AlgorithmResolution
)
from app.analysis.schemas_extraction import (
    RecursiveExtraction,
    IterativeExtraction,
    ExtractedCase
)

# Importar las tools de resolución
from app.analysis.tools.master_theorem import apply_master_theorem
from app.analysis.tools.summation_solver import simplify_summation
from app.analysis.tools.substitution import solve_by_substitution
from app.analysis.tools.recursion_tree import analyze_recursion_tree


class ResolverAgent(BaseAgent):
    """
    Agente especializado en resolver ecuaciones de complejidad
    Usa tools como Teorema Maestro, Sustitución, Sumatorias, etc.
    """
    
    def __init__(self):
        """
        Inicializa el ResolverAgent con sus tools de Fase 2
        """
        super().__init__()
        self.tools = self._create_resolution_tools()
        
        
        # SOBRESCRIBIR tool_functions con las tools de resolución
        
        self.tool_functions = {
            "apply_master_theorem": self._wrap_master_theorem,
            "simplify_summation": self._wrap_summation,
            "solve_by_substitution": self._wrap_substitution,
            "analyze_recursion_tree": self._wrap_recursion_tree
        }
        
        
    
    def _create_resolution_tools(self) -> list:
        """
        Define las tools de resolución de complejidades
        
        Returns:
            Lista de herramientas para Claude
        """
        return [
            {
                "name": "apply_master_theorem",
                "description": (
                    "Aplica el Teorema Maestro para resolver recurrencias de la forma T(n) = aT(n/b) + f(n). "
                    "Identifica automáticamente el caso (1, 2 o 3) y calcula la complejidad. "
                    "Úsalo para recurrencias divide-y-conquista como Merge Sort, Binary Search, etc. "
                    "Devuelve los pasos detallados y la complejidad final."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "recurrence": {
                            "type": "string",
                            "description": "Recurrencia a resolver, como 'T(n) = 2T(n/2) + O(n)'"
                        }
                    },
                    "required": ["recurrence"]
                }
            },
            {
                "name": "simplify_summation",
                "description": (
                    "Simplifica sumatorias y calcula su complejidad. "
                    "Maneja sumatorias simples (Σ(i=1 to n) i) y anidadas (Σ Σ). "
                    "Úsalo para algoritmos iterativos como Selection Sort, Bubble Sort, etc. "
                    "Devuelve la fórmula simplificada y los pasos de resolución."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "summation": {
                            "type": "string",
                            "description": "Sumatoria a simplificar, como 'Σ(i=1 to n) i'"
                        }
                    },
                    "required": ["summation"]
                }
            },
            {
                "name": "solve_by_substitution",
                "description": (
                    "Resuelve recurrencias lineales por método de sustitución. "
                    "Úsalo para recurrencias como T(n) = T(n-1) + O(1), útil para Factorial, Fibonacci iterativo, etc. "
                    "Muestra la expansión paso a paso y el patrón identificado."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "recurrence": {
                            "type": "string",
                            "description": "Recurrencia lineal, como 'T(n) = T(n-1) + O(1)'"
                        }
                    },
                    "required": ["recurrence"]
                }
            },
            {
                "name": "analyze_recursion_tree",
                "description": (
                    "Analiza complejidad usando árbol de recursión. "
                    "Método alternativo para visualizar el trabajo en cada nivel del árbol. "
                    "Úsalo cuando otros métodos no sean suficientes o como método complementario."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "recurrence": {
                            "type": "string",
                            "description": "Recurrencia a analizar, como 'T(n) = 2T(n/2) + O(n)'"
                        }
                    },
                    "required": ["recurrence"]
                }
            }
        ]
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Sobrescribe el método del BaseAgent para devolver tools de resolución
        """
        return self.tools
    
    
    def _wrap_master_theorem(self, recurrence: str) -> Dict[str, Any]:
        """Wrapper para apply_master_theorem"""

        result = apply_master_theorem(recurrence)
        
        return result
    
    def _wrap_summation(self, summation: str) -> Dict[str, Any]:
        """Wrapper para simplify_summation"""

        result = simplify_summation(summation)
        
        return result
    
    def _wrap_substitution(self, recurrence: str) -> Dict[str, Any]:
        """Wrapper para solve_by_substitution"""

        result = solve_by_substitution(recurrence)
       
        return result
    
    def _wrap_recursion_tree(self, recurrence: str) -> Dict[str, Any]:
        """Wrapper para analyze_recursion_tree"""

        result = analyze_recursion_tree(recurrence)
        
        return result
    
    def _build_resolution_prompt(self, equation: str, case_type: str) -> str:
        """
        Construye el prompt para resolver una ecuación
        
        Args:
            equation: Ecuación a resolver (ej: "T(n) = 2T(n/2) + O(n)")
            case_type: Tipo de caso ("best", "worst", "average", "unified")
            
        Returns:
            Prompt para Claude
        """
        return f"""Eres un experto en análisis de algoritmos. Tu tarea es resolver la siguiente ecuación de complejidad y proporcionar las notaciones O (Big-O), Ω (Omega) y Θ (Theta).

**Ecuación a resolver ({case_type} case):**
{equation}

**Instrucciones OBLIGATORIAS:**

1. **IDENTIFICA el tipo de ecuación:**
   - ¿Es T(n) = aT(n/b) + f(n)? → USA apply_master_theorem
   - ¿Es T(n) = T(n-k) + f(n)? → USA solve_by_substitution
   - ¿Es Σ(...)? → USA simplify_summation
   - ¿Es O(1) o constante? → análisis directo (no necesitas tool)

2. **DEBES USAR UNA TOOL** (excepto para O(1)):
   - NO intentes resolver manualmente
   - SIEMPRE llama a la tool apropiada primero
   - Usa el resultado de la tool para construir tu respuesta

3. **Calcula las tres notaciones:**
   - **O (Big-O)**: Cota superior
   - **Ω (Omega)**: Cota inferior  
   - **Θ (Theta)**: Cota ajustada (solo si O = Ω)

4. **Devuelve el resultado en formato JSON** con esta estructura:
```json
{{
    "O": "O(...)",
    "Omega": "Ω(...)",
    "Theta": "Θ(...)" o null,
    "is_tight_bound": true/false,
    "method": "nombre_del_metodo",
    "steps": ["paso 1", "paso 2", ...],
    "explanation": "Explicación narrativa completa"
}}
```

**IMPORTANTE:**
- Para O y Ω, SIEMPRE deben tener el mismo orden si la ecuación es determinística
- is_tight_bound = true si O = Ω (entonces existe Theta)
- Los steps deben ser detallados y mostrar el razonamiento matemático
- La explanation debe ser narrativa y académica
- El method debe ser uno de: "teorema_maestro", "sustitucion", "arbol_recursion", "analisis_directo", "simplificacion_sumatorias", "unknown"

Comienza el análisis."""

    def resolve_case(self, equation: str, case_type: str = "unified") -> ResolvedComplexity:
        """
        Resuelve UNA ecuación de complejidad
        
        Args:
            equation: Ecuación como "T(n) = 2T(n/2) + O(n)"
            case_type: Tipo de caso
            
        Returns:
            ResolvedComplexity con O, Ω, Θ
        """

        
        # Construir prompt
        prompt = self._build_resolution_prompt(equation, case_type)
        
        # Ejecutar con tool loop
        result = self.run_with_tool_loop(prompt, max_iterations=4)
        
        if not result.get("success", False):
            # Error en resolución
            return ResolvedComplexity(
                O="O(?)",
                Omega="Ω(?)",
                Theta=None,
                is_tight_bound=False,
                method="error",
                steps=["No se pudo resolver la ecuación"],
                explanation=f"Error: {result.get('error', 'Desconocido')}"
            )
        
        # Parsear resultado
        try:
            response_text = result.get("response", "")
            
            # Extraer JSON del response
            import json
            import re
            
            # Buscar JSON en el texto
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                final_answer = json.loads(json_match.group())
            else:
                raise ValueError("No se encontró JSON en la respuesta")
            
            return ResolvedComplexity(
                O=final_answer.get("O", "O(?)"),
                Omega=final_answer.get("Omega", "Ω(?)"),
                Theta=final_answer.get("Theta"),
                is_tight_bound=final_answer.get("is_tight_bound", False),
                method=final_answer.get("method", "unknown"),
                steps=final_answer.get("steps", []),
                explanation=final_answer.get("explanation", "")
            )
        
        except Exception as e:
            print(f" Error parseando resultado: {e}")
            return ResolvedComplexity(
                O="O(?)",
                Omega="Ω(?)",
                Theta=None,
                is_tight_bound=False,
                method="error",
                steps=[],
                explanation=f"Error parseando: {str(e)}"
            )
    
    def resolve_algorithm(
        self, 
        phase1_result: Union[RecursiveExtraction, IterativeExtraction]
    ) -> AlgorithmResolution:
        """
        Resuelve TODOS los casos de un algoritmo completo
        """
        
        if phase1_result.has_different_cases:
            
            
            best = None
            worst = None
            average = None
            
            # Resolver best case
            if phase1_result.best_case:
                
                # CREAR NUEVO AGENTE LIMPIO
                resolver_best = ResolverAgent()
                best_resolution = resolver_best.resolve_case(
                    phase1_result.best_case.function,
                    "best"
                )
                best = CaseResolution(
                    case_type="best",
                    original_equation=phase1_result.best_case.function,
                    resolution=best_resolution
                )
                del resolver_best
            
            # Resolver worst case
            if phase1_result.worst_case:
                
                # CREAR NUEVO AGENTE LIMPIO
                resolver_worst = ResolverAgent()
                worst_resolution = resolver_worst.resolve_case(
                    phase1_result.worst_case.function,
                    "worst"
                )
                worst = CaseResolution(
                    case_type="worst",
                    original_equation=phase1_result.worst_case.function,
                    resolution=worst_resolution
                )
                del resolver_worst
            
            # Resolver average case
            if phase1_result.average_case:
                
                # CREAR NUEVO AGENTE LIMPIO
                resolver_avg = ResolverAgent()
                average_resolution = resolver_avg.resolve_case(
                    phase1_result.average_case.function,
                    "average"
                )
                average = CaseResolution(
                    case_type="average",
                    original_equation=phase1_result.average_case.function,
                    resolution=average_resolution
                )
                del resolver_avg
            
            return AlgorithmResolution(
                algorithm_name=phase1_result.algorithm_name,
                algorithm_type=phase1_result.algorithm_type,
                has_different_cases=True,
                best_case=best,
                worst_case=worst,
                average_case=average,
                unified_case=None
            )
        
        else:
            # ===== CASO UNIFICADO =====
            
            
            # CAMBIO 2: CREAR NUEVO AGENTE también para caso unificado
            resolver_unified = ResolverAgent()  
            unified_resolution = resolver_unified.resolve_case(  
                phase1_result.unified_case.function,
                "unified"
            )
            del resolver_unified  
            
            unified = CaseResolution(
                case_type="unified",
                original_equation=phase1_result.unified_case.function,
                resolution=unified_resolution
            )
            
            return AlgorithmResolution(
                algorithm_name=phase1_result.algorithm_name,
                algorithm_type=phase1_result.algorithm_type,
                has_different_cases=False,
                best_case=None,
                worst_case=None,
                average_case=None,
                unified_case=unified
            )