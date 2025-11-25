"""
Tool para simplificar y resolver sumatorias
Maneja sumatorias simples y anidadas comunes en análisis de algoritmos
"""
import re
from typing import Dict, Any, Optional


class SummationPattern:
    """
    Representa un patrón de sumatoria conocido con su fórmula
    """
    def __init__(self, pattern: str, formula: str, complexity: str, description: str):
        self.pattern = pattern
        self.formula = formula
        self.complexity = complexity
        self.description = description


# Biblioteca de patrones conocidos
KNOWN_PATTERNS = [
    SummationPattern(
        pattern=r"Σ\(i=1 to n\) O\(1\)",
        formula="n",
        complexity="O(n)",
        description="Sumatoria de constante n veces"
    ),
    SummationPattern(
        pattern=r"Σ\(i=1 to n\) 1",
        formula="n",
        complexity="O(n)",
        description="Sumatoria de 1 desde 1 hasta n"
    ),
    SummationPattern(
        pattern=r"Σ\(i=1 to n\) i",
        formula="n(n+1)/2",
        complexity="O(n²)",
        description="Suma aritmética: 1+2+3+...+n"
    ),
    SummationPattern(
        pattern=r"Σ\(i=1 to n\) i\^2",
        formula="n(n+1)(2n+1)/6",
        complexity="O(n³)",
        description="Suma de cuadrados"
    ),
    SummationPattern(
        pattern=r"Σ\(i=1 to n\) i\^3",
        formula="[n(n+1)/2]²",
        complexity="O(n⁴)",
        description="Suma de cubos"
    ),
    SummationPattern(
        pattern=r"Σ\(i=1 to n\) 2\^i",
        formula="2^(n+1) - 2",
        complexity="O(2^n)",
        description="Serie geométrica con r=2"
    ),
    SummationPattern(
        pattern=r"Σ\(i=0 to log n\) 2\^i",
        formula="2n - 1",
        complexity="O(n)",
        description="Serie geométrica hasta log n"
    ),
]


def normalize_summation(summation: str) -> str:
    """
    Normaliza una sumatoria para facilitar el matching
    
    Args:
        summation: Sumatoria como "Σ(i=1 to n) O(1)"
        
    Returns:
        Versión normalizada
    """
    # Quitar espacios extras
    normalized = ' '.join(summation.split())
    
    # Normalizar O() a forma estándar
    normalized = re.sub(r'O\s*\(\s*1\s*\)', 'O(1)', normalized)
    normalized = re.sub(r'O\s*\(\s*(\w+)\s*\)', r'O(\1)', normalized)
    
    return normalized


def identify_nested_summation(summation: str) -> Optional[Dict[str, Any]]:
    """
    Identifica si es una sumatoria anidada y extrae sus componentes
    
    Args:
        summation: String de sumatoria
        
    Returns:
        Dict con información de la sumatoria anidada o None
    """
    # Patrón para sumatoria doble: Σ(i=1 to n) Σ(j=X to Y) Z
    pattern = r'Σ\(i=1 to n\)\s*Σ\(j=([^)]+)\)\s*(.+)'
    
    match = re.search(pattern, summation)
    if not match:
        return None
    
    inner_range = match.group(1).strip()
    inner_expr = match.group(2).strip()
    
    # Casos comunes de sumatorias anidadas
    if "j=1 to i" in inner_range or "j=i to n" in inner_range:
        return {
            "type": "nested",
            "outer": "i=1 to n",
            "inner_range": inner_range,
            "inner_expr": inner_expr,
            "pattern": "triangular"
        }
    
    if "j=1 to n" in inner_range:
        return {
            "type": "nested",
            "outer": "i=1 to n",
            "inner_range": inner_range,
            "inner_expr": inner_expr,
            "pattern": "rectangular"
        }
    
    return None


def solve_nested_summation(nested_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resuelve una sumatoria anidada
    
    Args:
        nested_info: Información de la sumatoria anidada
        
    Returns:
        Dict con la solución
    """
    pattern = nested_info["pattern"]
    inner_expr = nested_info["inner_expr"]
    
    if pattern == "triangular":
        # Σ(i=1 to n) Σ(j=1 to i) O(1) = Σ(i=1 to n) i = n(n+1)/2
        if "O(1)" in inner_expr or inner_expr == "1":
            return {
                "success": True,
                "simplified": "n(n+1)/2",
                "complexity": "O(n²)",
                "steps": [
                    "Sumatoria anidada: Σ(i=1 to n) Σ(j=1 to i) O(1)",
                    "La sumatoria interna da: Σ(j=1 to i) O(1) = i",
                    "Queda: Σ(i=1 to n) i",
                    "Aplicando fórmula de suma aritmética: n(n+1)/2",
                    "Por lo tanto: O(n²)"
                ],
                "explanation": "Sumatoria triangular donde la sumatoria interna depende del índice externo"
            }
    
    elif pattern == "rectangular":
        # Σ(i=1 to n) Σ(j=1 to n) O(1) = n × n = n²
        if "O(1)" in inner_expr or inner_expr == "1":
            return {
                "success": True,
                "simplified": "n²",
                "complexity": "O(n²)",
                "steps": [
                    "Sumatoria anidada: Σ(i=1 to n) Σ(j=1 to n) O(1)",
                    "La sumatoria interna da: Σ(j=1 to n) O(1) = n",
                    "Queda: Σ(i=1 to n) n = n × n",
                    "Por lo tanto: O(n²)"
                ],
                "explanation": "Sumatoria rectangular donde ambos loops van hasta n independientemente"
            }
    
    return {
        "success": False,
        "error": "Patrón de sumatoria anidada no reconocido"
    }


def simplify_summation(summation: str) -> Dict[str, Any]:
    """
    Simplifica una sumatoria y calcula su complejidad
    
    Args:
        summation: String de sumatoria como "Σ(i=1 to n) i"
        
    Returns:
        Dict con la solución y pasos
    """
    # Normalizar
    normalized = normalize_summation(summation)
    
    # Verificar si es anidada
    nested_info = identify_nested_summation(normalized)
    if nested_info:
        return solve_nested_summation(nested_info)
    
    # Buscar en patrones conocidos
    for pattern in KNOWN_PATTERNS:
        if re.search(pattern.pattern, normalized):
            return {
                "success": True,
                "original": summation,
                "simplified": pattern.formula,
                "complexity": pattern.complexity,
                "explanation": pattern.description,
                "steps": [
                    f"Identificado patrón: {pattern.description}",
                    f"Aplicando fórmula: {pattern.formula}",
                    f"Complejidad: {pattern.complexity}"
                ]
            }
    
    # No se encontró patrón
    return {
        "success": False,
        "error": "No se reconoció el patrón de la sumatoria",
        "original": summation,
        "suggestion": "Puede requerir análisis manual o método de sustitución"
    }


def extract_complexity_order(complexity_str: str) -> int:
    """
    Extrae el orden numérico de una complejidad para comparaciones
    
    Args:
        complexity_str: String como "O(n²)", "O(n log n)"
        
    Returns:
        Orden aproximado (1=lineal, 2=cuadrático, etc.)
    """
    order_map = {
        "O(1)": 0,
        "O(log n)": 0.5,
        "O(n)": 1,
        "O(n log n)": 1.5,
        "O(n²)": 2,
        "O(n³)": 3,
        "O(2^n)": 10,
    }
    
    return order_map.get(complexity_str, 1)