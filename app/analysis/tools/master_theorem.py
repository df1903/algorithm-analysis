"""
Tool para aplicar el Teorema Maestro a recurrencias
Resuelve recurrencias de la forma: T(n) = a·T(n/b) + f(n)
"""
import math
import re
from typing import Dict, Any, Optional


def extract_recurrence_params(recurrence: str) -> Optional[Dict[str, Any]]:
    """
    Extrae parámetros a, b, f(n) de una recurrencia
    
    Args:
        recurrence: String como "T(n) = 2T(n/2) + O(n)" o "T(n) = T(n/2) + O(1)"
        
    Returns:
        Dict con 'a', 'b', 'f_n' o None si no se puede parsear
        
    Examples:
        "T(n) = 2T(n/2) + O(n)" → {'a': 2, 'b': 2, 'f_n': 'n'}
        "T(n) = T(n/2) + O(1)" → {'a': 1, 'b': 2, 'f_n': '1'}
    """
    # Normalizar: eliminar espacios extra
    recurrence = recurrence.strip()
    
    # Patrón 1: Con coeficiente explícito - T(n) = aT(n/b) + O(...)
    pattern1 = r'T\(n\)\s*=\s*(\d+)\s*[*]?\s*T\(n/(\d+)\)\s*\+\s*O\((.+?)\)'
    match = re.search(pattern1, recurrence)
    
    if match:
        a = int(match.group(1))
        b = int(match.group(2))
        f_n = match.group(3).strip()
        return {'a': a, 'b': b, 'f_n': f_n}
    
    # Patrón 2: Sin coeficiente (asumir a=1) - T(n) = T(n/b) + O(...)
    pattern2 = r'T\(n\)\s*=\s*T\(n/(\d+)\)\s*\+\s*O\((.+?)\)'
    match = re.search(pattern2, recurrence)
    
    if match:
        a = 1  # ← Asumir a=1
        b = int(match.group(1))
        f_n = match.group(2).strip()
        return {'a': a, 'b': b, 'f_n': f_n}
    
    # Patrón 3: Sin O() - T(n) = aT(n/b) + f(n)
    pattern3 = r'T\(n\)\s*=\s*(\d+)\s*[*]?\s*T\(n/(\d+)\)\s*\+\s*(.+)'
    match = re.search(pattern3, recurrence)
    
    if match:
        a = int(match.group(1))
        b = int(match.group(2))
        f_n = match.group(3).strip()
        return {'a': a, 'b': b, 'f_n': f_n}
    
    # Patrón 4: Sin O() y sin coeficiente - T(n) = T(n/b) + f(n)
    pattern4 = r'T\(n\)\s*=\s*T\(n/(\d+)\)\s*\+\s*(.+)'
    match = re.search(pattern4, recurrence)
    
    if match:
        a = 1
        b = int(match.group(1))
        f_n = match.group(2).strip()
        return {'a': a, 'b': b, 'f_n': f_n}
    
    return None


def compare_functions(f_n: str, n_log_b_a: float) -> str:
    """
    Compara f(n) con n^(log_b(a)) para determinar el caso del teorema
    
    Args:
        f_n: Función como "n", "n²", "n log n"
        n_log_b_a: Valor de log_b(a)
        
    Returns:
        "case1", "case2", o "case3"
    """
    # Mapeo de notaciones comunes a exponentes
    function_orders = {
        '1': 0,           # O(1) = n^0
        'log n': 0.5,     # Aproximación (menor que n)
        'n': 1,           # O(n) = n^1
        'n log n': 1.1,   # Mayor que n pero menor que n²
        'n²': 2,          # O(n²) = n^2
        'n^2': 2,
        'n³': 3,
        'n^3': 3,
    }
    
    # Obtener el orden de f(n)
    f_order = function_orders.get(f_n.lower(), None)
    
    if f_order is None:
        # Intentar extraer exponente
        exp_match = re.search(r'n\^?(\d+)', f_n)
        if exp_match:
            f_order = int(exp_match.group(1))
        else:
            # No se pudo determinar, asumir caso 2
            return "case2"
    
    # Comparar con épsilon = 0.01 para evitar errores de precisión
    epsilon = 0.01
    
    if f_order < n_log_b_a - epsilon:
        return "case1"
    elif abs(f_order - n_log_b_a) < epsilon:
        return "case2"
    else:
        return "case3"


def apply_master_theorem(recurrence: str) -> Dict[str, Any]:
    """
    Aplica el Teorema Maestro a una recurrencia
    
    Args:
        recurrence: Recurrencia como "T(n) = 2T(n/2) + O(n)"
        
    Returns:
        Dict con el resultado y explicación
    """
    # Extraer parámetros
    params = extract_recurrence_params(recurrence)
    
    if not params:
        return {
            "success": False,
            "error": "No se pudo parsear la recurrencia. Debe ser de la forma T(n) = aT(n/b) + O(f(n))",
            "recurrence": recurrence
        }
    
    a = params['a']
    b = params['b']
    f_n = params['f_n']
    
    # Calcular log_b(a)
    log_b_a = math.log(a) / math.log(b)
    
    # Determinar caso
    case = compare_functions(f_n, log_b_a)
    
    # Construir resultado según el caso
    if case == "case1":
        complexity = f"n^{log_b_a:.2f}".replace('.00', '')
        result = {
            "success": True,
            "case": 1,
            "a": a,
            "b": b,
            "f_n": f_n,
            "log_b_a": round(log_b_a, 2),
            "complexity": complexity,
            "explanation": f"Caso 1: f(n) = O({f_n}) < n^(log_{b}({a})) = n^{log_b_a:.2f}. Por lo tanto, T(n) = Θ({complexity})"
        }
    
    elif case == "case2":
        if log_b_a == 1:
            complexity = "n log n"
        else:
            complexity = f"n^{log_b_a:.2f} log n".replace('.00', '')
        
        result = {
            "success": True,
            "case": 2,
            "a": a,
            "b": b,
            "f_n": f_n,
            "log_b_a": round(log_b_a, 2),
            "complexity": complexity,
            "explanation": f"Caso 2: f(n) = Θ({f_n}) = Θ(n^(log_{b}({a}))). Por lo tanto, T(n) = Θ({complexity})"
        }
    
    else:  # case3
        result = {
            "success": True,
            "case": 3,
            "a": a,
            "b": b,
            "f_n": f_n,
            "log_b_a": round(log_b_a, 2),
            "complexity": f_n,
            "explanation": f"Caso 3: f(n) = Ω({f_n}) > n^(log_{b}({a})) = n^{log_b_a:.2f}. Por lo tanto, T(n) = Θ({f_n})"
        }
    
    return result