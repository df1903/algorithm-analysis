"""
Tools para análisis del AST

Funciones que los agentes de Claude pueden llamar para analizar
el AST con precisión matemática en lugar de "adivinar"
"""

from typing import List, Dict, Any, Optional
from app.parsing.ast_nodes import *



# TOOLS PARA ALGORITMOS RECURSIVOS


def find_recursive_calls(subroutine: Subroutine) -> Dict[str, Any]:
    """
    Encuentra todas las llamadas recursivas dentro de una subrutina.

    Analiza llamadas directas, en returns, assignments y dentro de estructuras
    de control como loops e if-statements.

    Args:
        subroutine (Subroutine): Nodo AST que representa la subrutina.

    Returns:
        dict: Información sobre las llamadas recursivas detectadas:
            - count (int): Número total de llamadas recursivas.
            - positions (list[str]): Ubicaciones en el AST donde ocurren.
            - arguments (list[list[str]]): Argumentos pasados en cada llamada.
    """
    func_name = subroutine.name
    calls = []
    positions = []
    
    def search_calls(statements: List[Statement], path: str = "body"):
        for i, stmt in enumerate(statements):
            current_path = f"{path}[{i}]"
            
            # En CallStatement
            if isinstance(stmt, CallStatement):
                if stmt.function_name == func_name:
                    calls.append(stmt.arguments)
                    positions.append(f"{current_path}.call")
            
            # En ReturnStatement
            elif isinstance(stmt, ReturnStatement):
                if _expression_has_call(stmt.value, func_name):
                    # Extraer argumentos del FunctionCall
                    args = _extract_call_args(stmt.value, func_name)
                    calls.append(args)
                    positions.append(f"{current_path}.return")
            
            # En Assignment
            elif isinstance(stmt, Assignment):
                if _expression_has_call(stmt.value, func_name):
                    args = _extract_call_args(stmt.value, func_name)
                    calls.append(args)
                    positions.append(f"{current_path}.assignment")
            
            # Buscar en loops
            elif isinstance(stmt, ForLoop):
                search_calls(stmt.body.statements, f"{current_path}.for")
            elif isinstance(stmt, WhileLoop):
                search_calls(stmt.body.statements, f"{current_path}.while")
            elif isinstance(stmt, RepeatLoop):
                search_calls(stmt.statements, f"{current_path}.repeat")
            
            # Buscar en if
            elif isinstance(stmt, IfStatement):
                search_calls(stmt.then_block.statements, f"{current_path}.then")
                if stmt.else_block:
                    search_calls(stmt.else_block.statements, f"{current_path}.else")
    
    search_calls(subroutine.body)
    
    return {
        "count": len(calls),
        "positions": positions,
        "arguments": [_args_to_string(args) for args in calls]
    }


def detect_base_case(subroutine: Subroutine) -> Dict[str, Any]:
    """
    Tool: Detecta el caso base de la recursión
    
    Returns:
        {
            "exists": bool,
            "condition": str,  # La condición del caso base
            "return_value": str,  # Qué retorna en caso base
            "position": str
        }
    """
    # Buscar el primer IF que NO tenga llamada recursiva en el then
    for i, stmt in enumerate(subroutine.body):
        if isinstance(stmt, IfStatement):
            # Verificar si then NO tiene recursión
            has_recursion_then = _has_recursion_in_block(
                stmt.then_block.statements, 
                subroutine.name
            )
            
            if not has_recursion_then:
                # Este podría ser el caso base
                condition_str = _expression_to_string(stmt.condition)
                return_value = _extract_return_value(stmt.then_block.statements)
                
                return {
                    "exists": True,
                    "condition": condition_str,
                    "return_value": return_value,
                    "position": f"body[{i}].then"
                }
    
    return {
        "exists": False,
        "condition": None,
        "return_value": None,
        "position": None
    }


def analyze_recursion_parameter(subroutine: Subroutine, param_name: str) -> Dict[str, str]:
    """
    Tool: Analiza cómo se reduce el parámetro en llamadas recursivas
    
    Args:
        param_name: Nombre del parámetro a analizar (ej: "n")
    
    Returns:
        {
            "pattern": "n-1" | "n/2" | "n-k" | "custom",
            "reduction_factor": str,  # "1", "2", "k"
            "examples": [str]  # Expresiones encontradas
        }
    """
    recursive_calls = find_recursive_calls(subroutine)
    
    if recursive_calls["count"] == 0:
        return {
            "pattern": "none",
            "reduction_factor": "0",
            "examples": []
        }
    
    # Analizar los argumentos de cada llamada
    patterns = []
    for args_str in recursive_calls["arguments"]:
        for arg in args_str:
            if param_name in arg:
                patterns.append(arg)
    
    # Detectar patrón común
    if not patterns:
        return {
            "pattern": "constant",
            "reduction_factor": "0",
            "examples": []
        }
    
    # Clasificar patrón
    first_pattern = patterns[0]
    
    if "-1" in first_pattern or "- 1" in first_pattern:
        pattern_type = "n-1"
        reduction = "1"
    elif "/2" in first_pattern or "div 2" in first_pattern:
        pattern_type = "n/2"
        reduction = "2"
    elif "/" in first_pattern or "div" in first_pattern:
        pattern_type = "n/b"
        reduction = "b"
    else:
        pattern_type = "custom"
        reduction = "unknown"
    
    return {
        "pattern": pattern_type,
        "reduction_factor": reduction,
        "examples": patterns
    }



# TOOLS PARA ALGORITMOS ITERATIVOS


def analyze_loops(subroutine: Subroutine) -> Dict[str, Any]:
    """
    Tool: Analiza todos los loops del algoritmo
    
    Returns:
        {
            "total_loops": int,
            "max_nesting": int,
            "loops": [{
                "type": "FOR" | "WHILE" | "REPEAT",
                "variable": str,
                "start": str,
                "end": str,
                "nesting_level": int,
                "position": str
            }]
        }
    """
    loops_info = []
    max_nesting = 0
    
    def analyze_statements(statements: List[Statement], nesting: int, path: str):
        nonlocal max_nesting
        max_nesting = max(max_nesting, nesting)
        
        for i, stmt in enumerate(statements):
            current_path = f"{path}[{i}]"
            
            if isinstance(stmt, ForLoop):
                loop_data = {
                    "type": "FOR",
                    "variable": stmt.variable,
                    "start": _expression_to_string(stmt.start),
                    "end": _expression_to_string(stmt.end),
                    "nesting_level": nesting,
                    "position": current_path
                }
                loops_info.append(loop_data)
                
                # Analizar loops anidados
                analyze_statements(stmt.body.statements, nesting + 1, f"{current_path}.body")
            
            elif isinstance(stmt, WhileLoop):
                loop_data = {
                    "type": "WHILE",
                    "variable": "condition-based",
                    "start": "unknown",
                    "end": "unknown",
                    "nesting_level": nesting,
                    "position": current_path
                }
                loops_info.append(loop_data)
                analyze_statements(stmt.body.statements, nesting + 1, f"{current_path}.body")
            
            elif isinstance(stmt, RepeatLoop):
                loop_data = {
                    "type": "REPEAT",
                    "variable": "condition-based",
                    "start": "unknown",
                    "end": "unknown",
                    "nesting_level": nesting,
                    "position": current_path
                }
                loops_info.append(loop_data)
                analyze_statements(stmt.statements, nesting + 1, f"{current_path}.body")
            
            # Buscar en if
            elif isinstance(stmt, IfStatement):
                analyze_statements(stmt.then_block.statements, nesting, f"{current_path}.then")
                if stmt.else_block:
                    analyze_statements(stmt.else_block.statements, nesting, f"{current_path}.else")
    
    analyze_statements(subroutine.body, 0, "body")
    
    return {
        "total_loops": len(loops_info),
        "max_nesting": max_nesting,
        "loops": loops_info
    }


def count_operations_in_loop(loop_body: List[Statement]) -> int:
    """
    Tool: Cuenta operaciones dentro de un loop
    
    Returns:
        Número aproximado de operaciones O(?) por iteración
    """
    op_count = 0
    
    for stmt in loop_body:
        if isinstance(stmt, Assignment):
            op_count += 1
        elif isinstance(stmt, CallStatement):
            op_count += 1
        elif isinstance(stmt, (ForLoop, WhileLoop, RepeatLoop)):
            # Loop anidado cuenta como operación compleja
            op_count += 10  
    
    return max(op_count, 1) 

def detect_conditionals(subroutine: Subroutine) -> List[Dict[str, str]]:
    """
    Tool: Detecta todos los condicionales (para identificar casos best/worst)
    
    Returns:
        [{
            "condition": str,
            "position": str,
            "has_recursion_then": bool,
            "has_recursion_else": bool
        }]
    """
    conditionals = []
    
    def search_ifs(statements: List[Statement], path: str):
        """ 
            Busca estructuras condicionales (IfStatements) dentro de una lista de 
            sentencias y extrae información relevante sobre ellas.

            La función analiza:
            - La condición del IF.
            - La posición dentro del AST (ruta).
            - Si en el bloque THEN hay llamadas recursivas.
            - Si en el bloque ELSE hay llamadas recursivas.
            - IFs anidados dentro de THEN y ELSE.
            - IFs dentro de loops (for, while).

            Esta función es recursiva y acumula los resultados en la lista
            `conditionals` definida en el ámbito externo.

            Args:
                statements (list[Statement]): Lista de sentencias a analizar del AST.
                path (str): Cadena que representa la ruta actual dentro del árbol
                    para identificar la ubicación del IF (ejemplo: "body[2].then[1]").

            Side Effects:
                Modifica la lista externa `conditionals` agregando diccionarios con:
                    - condition (str): condición del IF convertida a string.
                    - position (str): ubicación en el AST.
                    - has_recursion_then (bool): True si THEN contiene recursión.
                    - has_recursion_else (bool): True si ELSE contiene recursión.

            Returns:
                None: El resultado se acumula en la lista `conditionals` externa.
        """
        for i, stmt in enumerate(statements):
            if isinstance(stmt, IfStatement):
                cond_data = {
                    "condition": _expression_to_string(stmt.condition),
                    "position": f"{path}[{i}]",
                    "has_recursion_then": _has_recursion_in_block(
                        stmt.then_block.statements,
                        subroutine.name
                    ),
                    "has_recursion_else": _has_recursion_in_block(
                        stmt.else_block.statements if stmt.else_block else [],
                        subroutine.name
                    )
                }
                conditionals.append(cond_data)
                
                # Buscar IFs anidados
                search_ifs(stmt.then_block.statements, f"{path}[{i}].then")
                if stmt.else_block:
                    search_ifs(stmt.else_block.statements, f"{path}[{i}].else")
            
            # Buscar en loops
            elif isinstance(stmt, ForLoop):
                search_ifs(stmt.body.statements, f"{path}[{i}].for")
            elif isinstance(stmt, WhileLoop):
                search_ifs(stmt.body.statements, f"{path}[{i}].while")
    
    search_ifs(subroutine.body, "body")
    return conditionals


    
# FUNCIONES AUXILIARES


def _expression_has_call(expr: Expression, func_name: str) -> bool:
    """Verifica si una expresión contiene llamada a función"""
    if isinstance(expr, FunctionCall):
        return expr.function_name == func_name
    elif isinstance(expr, BinaryOp):
        return (_expression_has_call(expr.left, func_name) or 
                _expression_has_call(expr.right, func_name))
    elif isinstance(expr, UnaryOp):
        return _expression_has_call(expr.operand, func_name)
    return False


def _extract_call_args(expr: Expression, func_name: str) -> List[Expression]:
    """Extrae los argumentos de un FunctionCall dentro de una expresión"""
    if isinstance(expr, FunctionCall) and expr.function_name == func_name:
        return expr.arguments
    elif isinstance(expr, BinaryOp):
        left_args = _extract_call_args(expr.left, func_name)
        if left_args:
            return left_args
        return _extract_call_args(expr.right, func_name)
    elif isinstance(expr, UnaryOp):
        return _extract_call_args(expr.operand, func_name)
    return []


def _args_to_string(args: List[Expression]) -> List[str]:
    """  Convierte una lista de expresiones AST en sus representaciones string.

    Args:
        args (list[Expression]): Lista de argumentos del AST.

    Returns:
        list[str]: Lista de las expresiones convertidas a texto."""
    return [_expression_to_string(arg) for arg in args]


def _expression_to_string(expr: Expression) -> str:
    """Convierte una expresión del AST a string legible"""
    if isinstance(expr, Number):
        return str(expr.value)
    elif isinstance(expr, Variable):
        return expr.name
    elif isinstance(expr, BinaryOp):
        left = _expression_to_string(expr.left)
        right = _expression_to_string(expr.right)
        return f"{left} {expr.operator} {right}"
    elif isinstance(expr, UnaryOp):
        operand = _expression_to_string(expr.operand)
        return f"{expr.operator}{operand}"
    elif isinstance(expr, FunctionCall):
        args = ", ".join(_expression_to_string(arg) for arg in expr.arguments)
        return f"{expr.function_name}({args})"
    else:
        return str(expr)


def _has_recursion_in_block(statements: List[Statement], func_name: str) -> bool:
    """Verifica si hay recursión en un bloque de statements"""
    for stmt in statements:
        if isinstance(stmt, CallStatement) and stmt.function_name == func_name:
            return True
        elif isinstance(stmt, ReturnStatement):
            if _expression_has_call(stmt.value, func_name):
                return True
        elif isinstance(stmt, Assignment):
            if _expression_has_call(stmt.value, func_name):
                return True
    return False


def _extract_return_value(statements: List[Statement]) -> Optional[str]:
    """Extrae el valor de return en un bloque"""
    for stmt in statements:
        if isinstance(stmt, ReturnStatement):
            return _expression_to_string(stmt.value)
    return None