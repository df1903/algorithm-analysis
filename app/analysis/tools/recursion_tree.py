"""
Tool para analizar complejidad usando árbol de recursión
Útil para visualizar el trabajo en cada nivel
"""
import math
from typing import Dict, Any, Optional


def analyze_recursion_tree(recurrence: str) -> Dict[str, Any]:
    """
    Analiza una recurrencia usando árbol de recursión
    
    Args:
        recurrence: Como "T(n) = 2T(n/2) + O(n)"
        
    Returns:
        Dict con análisis del árbol
    """
    import re
    
    # Patrón: T(n) = aT(n/b) + f(n)
    pattern = r'T\(n\)\s*=\s*(\d+)T\(n/(\d+)\)\s*\+\s*O?\((.+?)\)'
    
    match = re.search(pattern, recurrence)
    if not match:
        return {
            "success": False,
            "error": "No se pudo parsear como recurrencia divide-y-conquista"
        }
    
    a = int(match.group(1))  # Llamadas recursivas
    b = int(match.group(2))  # Factor de división
    f_n = match.group(3).strip()  # Trabajo por nivel
    
    # Calcular profundidad del árbol
    depth = f"log_{b}(n)"
    
    # Calcular nodos por nivel
    nodes_per_level = []
    work_per_level = []
    
    for level in range(4):  # Mostrar 4 niveles
        nodes = a ** level
        
        # Tamaño del problema en este nivel
        if level == 0:
            size = "n"
        else:
            size = f"n/{b**level}"
        
        nodes_per_level.append(f"Nivel {level}: {nodes} nodos")
        
        # Trabajo en este nivel
        if f_n == "1":
            work = f"{nodes} × O(1) = O({nodes})"
        elif f_n == "n":
            work = f"{nodes} × O({size}) = O(n)"
        else:
            work = f"{nodes} × O({f_n}) en tamaño {size}"
        
        work_per_level.append(work)
    
    # Estimación de complejidad total
    # Suma del trabajo en todos los niveles
    if f_n == "n":
        total_work = f"O(n) por nivel × {depth} niveles = O(n log n)"
    elif f_n == "1":
        total_leaves = f"{a}^{depth} = n^(log_{b}({a}))"
        total_work = f"Hojas: {total_leaves}"
    else:
        total_work = "Ver Teorema Maestro para cálculo exacto"
    
    return {
        "success": True,
        "a": a,
        "b": b,
        "f_n": f_n,
        "tree_depth": depth,
        "nodes_per_level": nodes_per_level,
        "work_per_level": work_per_level,
        "total_work": total_work,
        "explanation": f"Árbol con ramificación {a} y profundidad {depth}. " +
                      f"Trabajo de O({f_n}) en cada nodo."
    }