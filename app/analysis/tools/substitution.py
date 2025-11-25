"""
Tool para resolver recurrencias por método de sustitución
Útil para recurrencias lineales y patrones simples
"""
import re
from typing import Dict, Any, Optional, List
import math


def extract_linear_recurrence(recurrence: str) -> Optional[Dict[str, Any]]:
    """
    Extrae parámetros de una recurrencia lineal
    
    Args:
        recurrence: String como "T(n) = T(n-1) + O(1)"
        
    Returns:
        Dict con 'decrement' y 'cost' o None
        
    Examples:
        "T(n) = T(n-1) + O(1)" → {'decrement': 1, 'cost': '1'}
        "T(n) = T(n-2) + O(n)" → {'decrement': 2, 'cost': 'n'}
    """
    # Patrón: T(n) = T(n-k) + O(f(n))
    pattern = r'T\(n\)\s*=\s*T\(n\s*-\s*(\d+)\)\s*\+\s*O\((.+?)\)'
    
    match = re.search(pattern, recurrence)
    if not match:
        return None
    
    decrement = int(match.group(1))
    cost = match.group(2).strip()
    
    return {
        'decrement': decrement,
        'cost': cost
    }


def generate_substitution_steps(decrement: int, cost: str, steps: int = 4) -> List[str]:
    """
    Genera los pasos de sustitución
    
    Args:
        decrement: Cuánto decrece (1, 2, etc.)
        cost: Costo por nivel ("1", "n", etc.)
        steps: Número de pasos a mostrar
        
    Returns:
        Lista de pasos como strings
    """
    steps_list = [
        f"T(n) = T(n-{decrement}) + {cost}"
    ]
    
    for i in range(1, steps):
        k = decrement * i
        if cost == "1":
            accumulated = f"{i}·c"
        else:
            accumulated = f"{i}·{cost}"
        
        steps_list.append(
            f"T(n) = T(n-{k}) + {accumulated}"
        )
    
    return steps_list


def determine_pattern(decrement: int, cost: str) -> str:
    """
    Determina el patrón general de la recurrencia
    
    Args:
        decrement: Cuánto decrece
        cost: Costo por nivel
        
    Returns:
        Patrón como string
    """
    if cost == "1":
        return f"T(n) = T(0) + (n/{decrement})·c"
    else:
        return f"T(n) = T(0) + (n/{decrement})·{cost}"


def calculate_complexity_from_pattern(decrement: int, cost: str) -> str:
    """
    Calcula la complejidad final desde el patrón
    
    Args:
        decrement: Cuánto decrece
        cost: Costo por nivel
        
    Returns:
        Complejidad como "O(...)"
    """
    # Número de niveles = n/decrement
    levels = f"n/{decrement}" if decrement > 1 else "n"
    
    # Complejidad = niveles × costo por nivel
    if cost == "1":
        # O(n/k × 1) = O(n)
        return "O(n)"
    elif cost == "n":
        # O(n × n) = O(n²)
        return "O(n²)"
    elif cost == "log n":
        # O(n × log n) = O(n log n)
        return "O(n log n)"
    else:
        # General
        return f"O({levels} × {cost})"


def solve_by_substitution(recurrence: str) -> Dict[str, Any]:
    """
    Resuelve una recurrencia por método de sustitución
    
    Args:
        recurrence: Recurrencia como "T(n) = T(n-1) + O(1)"
        
    Returns:
        Dict con la solución y pasos
    """
    # Extraer parámetros
    params = extract_linear_recurrence(recurrence)
    
    if not params:
        return {
            "success": False,
            "error": "No se pudo parsear la recurrencia. Debe ser lineal: T(n) = T(n-k) + O(f(n))",
            "recurrence": recurrence
        }
    
    decrement = params['decrement']
    cost = params['cost']
    
    # Generar pasos
    steps = generate_substitution_steps(decrement, cost, steps=4)
    
    # Determinar patrón
    pattern = determine_pattern(decrement, cost)
    
    # Calcular complejidad
    complexity = calculate_complexity_from_pattern(decrement, cost)
    
    # Construir explicación
    explanation_parts = [
        f"Aplicando método de sustitución:",
        f"Expandimos la recurrencia {4} veces:",
    ]
    
    for step in steps:
        explanation_parts.append(f"  {step}")
    
    explanation_parts.extend([
        f"",
        f"Observamos el patrón: {pattern}",
        f"Con n/{decrement} niveles hasta llegar al caso base",
        f"Por lo tanto: {complexity}"
    ])
    
    return {
        "success": True,
        "recurrence": recurrence,
        "decrement": decrement,
        "cost": cost,
        "steps": steps,
        "pattern": pattern,
        "complexity": complexity,
        "explanation": "\n".join(explanation_parts)
    }


def solve_divide_conquer_substitution(recurrence: str) -> Dict[str, Any]:
    """
    Resuelve recurrencias divide-y-conquista por sustitución
    Para casos donde el Teorema Maestro no aplica
    
    Args:
        recurrence: Como "T(n) = 2T(n/2) + n"
        
    Returns:
        Dict con solución
    """
    # Patrón: T(n) = aT(n/b) + f(n)
    pattern = r'T\(n\)\s*=\s*(\d+)T\(n/(\d+)\)\s*\+\s*(.+)'
    
    match = re.search(pattern, recurrence)
    if not match:
        return {
            "success": False,
            "error": "No se pudo parsear como recurrencia divide-y-conquista"
        }
    
    a = int(match.group(1))
    b = int(match.group(2))
    f_n = match.group(3).strip()
    
    # Ejemplo de expansión (simplificado)
    steps = [
        f"T(n) = {a}T(n/{b}) + {f_n}",
        f"T(n) = {a}[{a}T(n/{b**2}) + {f_n}/{b}] + {f_n}",
        f"T(n) = {a**2}T(n/{b**2}) + {a}{f_n}/{b} + {f_n}",
        "...",
        f"Patrón: Suma de {f_n} en cada nivel, con log_{b}(n) niveles"
    ]
    
    # Estimación simple (mejor usar Teorema Maestro)
    
    levels = f"log_{b}(n)"
    
    return {
        "success": True,
        "a": a,
        "b": b,
        "f_n": f_n,
        "steps": steps,
        "levels": levels,
        "explanation": f"Expandiendo {3} niveles, observamos el patrón. Hay {levels} niveles en total.",
        "note": "Para mayor precisión, use el Teorema Maestro"
    }