"""
TEST: Funciones Recursivas en el AST

Este archivo prueba si el sistema parsea correctamente funciones recursivas
y cómo se representan en el AST.
"""

import sys
import os

if os.path.exists('app/parsing'):
    sys.path.insert(0, 'app')

from parsing.parser import PseudocodeParser
from parsing.transformer import PseudocodeTransformer
from parsing.ast_nodes import *

# ============================================================================
# EJEMPLO 1: FACTORIAL (RECURSIÓN SIMPLE)
# ============================================================================

print("="*70)
print("EJEMPLO 1: FACTORIAL - RECURSIÓN SIMPLE")
print("="*70)
print()

code_factorial = """
factorial(n)
begin
    if (n <= 1) then
    begin
        return 1
    end
    else
    begin
        return n * factorial(n - 1)
    end
end

begin
    result := factorial(5)
end
"""

print("📝 CÓDIGO:")
print(code_factorial)

# Parsear y transformar
parser = PseudocodeParser()
transformer = PseudocodeTransformer()

tree = parser.parse(code_factorial)
ast = transformer.transform(tree)

print("✅ Parseado y transformado exitosamente")
print()

# ============================================================================
# EXPLORAR LA ESTRUCTURA DEL AST
# ============================================================================

print("🔍 ESTRUCTURA DEL AST:")
print_ast(ast)
print()

# ============================================================================
# ANALIZAR LA SUBRUTINA
# ============================================================================

print("="*70)
print("ANÁLISIS DETALLADO DE LA FUNCIÓN RECURSIVA")
print("="*70)
print()

# Obtener la subrutina
subroutine = ast.algorithm.subroutines[0]

print(f"📦 Subrutina:")
print(f"   - Nombre: {subroutine.name}")
print(f"   - Número de parámetros: {len(subroutine.parameters)}")
print(f"   - Parámetro 1: {subroutine.parameters[0].name} (tipo: {subroutine.parameters[0].param_type})")
print(f"   - Número de statements: {len(subroutine.body)}")
print()

# Analizar el cuerpo de la función
print(f"📦 Cuerpo de la función:")
for i, stmt in enumerate(subroutine.body):
    print(f"   Statement {i+1}: {type(stmt).__name__}")

# El cuerpo tiene un IF statement
if_stmt = subroutine.body[0]
print()
print(f"📦 IF Statement (caso base y recursivo):")
print(f"   - Tipo: {type(if_stmt).__name__}")
print(f"   - Tiene condición: {if_stmt.condition is not None}")
print(f"   - Tiene THEN: {if_stmt.then_block is not None}")
print(f"   - Tiene ELSE: {if_stmt.else_block is not None}")
print()

# THEN block (caso base)
print(f"📦 THEN block (caso base: n <= 1):")
then_stmt = if_stmt.then_block.statements[0]
print(f"   - Tipo: {type(then_stmt).__name__}")
if isinstance(then_stmt, ReturnStatement):
    print(f"   - Retorna: {then_stmt.value}")
    if isinstance(then_stmt.value, Number):
        print(f"   - Valor: {then_stmt.value.value}")
print()

# ELSE block (caso recursivo)
print(f"📦 ELSE block (caso recursivo):")
else_stmt = if_stmt.else_block.statements[0]
print(f"   - Tipo: {type(else_stmt).__name__}")
if isinstance(else_stmt, ReturnStatement):
    print(f"   - Retorna: {else_stmt.value}")
    if isinstance(else_stmt.value, BinaryOp):
        print(f"   - Es una operación: {else_stmt.value.operator}")
        print(f"   - Izquierda: {else_stmt.value.left}")
        print(f"   - Derecha: {else_stmt.value.right}")
        
        # La parte derecha es la llamada recursiva
        if isinstance(else_stmt.value.right, FunctionCall):
            print()
            print("   🔄 LLAMADA RECURSIVA DETECTADA:")
            print(f"      - Función: {else_stmt.value.right.function_name}")
            print(f"      - Argumentos: {else_stmt.value.right.arguments}")
            
            # Analizar el argumento (n - 1)
            if len(else_stmt.value.right.arguments) > 0:
                arg = else_stmt.value.right.arguments[0]
                print(f"      - Tipo de argumento: {type(arg).__name__}")
                if isinstance(arg, BinaryOp):
                    print(f"      - Operación: {arg.operator}")
                    print(f"      - Izquierda: {arg.left}")
                    print(f"      - Derecha: {arg.right}")
print()

# Analizar el algoritmo principal
print("="*70)
print("ALGORITMO PRINCIPAL (LLAMADA A LA FUNCIÓN)")
print("="*70)
print()

main = ast.algorithm.main
main_stmt = main.body[0]

print(f"📦 Primera sentencia del main:")
print(f"   - Tipo: {type(main_stmt).__name__}")

if isinstance(main_stmt, Assignment):
    print(f"   - Variable: {main_stmt.variable.name}")
    
    if isinstance(main_stmt.value, FunctionCall):
        print(f"   - Llama a función: {main_stmt.value.function_name}")
        print(f"   - Con argumentos: {main_stmt.value.arguments}")
        if len(main_stmt.value.arguments) > 0:
            arg = main_stmt.value.arguments[0]
            if isinstance(arg, Number):
                print(f"   - Valor del argumento: {arg.value}")
print()

# ============================================================================
# EJEMPLO 2: FIBONACCI (RECURSIÓN MÚLTIPLE)
# ============================================================================

print("="*70)
print("EJEMPLO 2: FIBONACCI - RECURSIÓN MÚLTIPLE")
print("="*70)
print()

code_fibonacci = """
fibonacci(n)
begin
    if (n <= 1) then
    begin
        return n
    end
    else
    begin
        return fibonacci(n - 1) + fibonacci(n - 2)
    end
end

begin
    result := fibonacci(6)
end
"""

print("📝 CÓDIGO:")
print(code_fibonacci)

# Parsear y transformar
tree_fib = parser.parse(code_fibonacci)
ast_fib = transformer.transform(tree_fib)

print("✅ Parseado y transformado exitosamente")
print()

print("🔍 ESTRUCTURA DEL AST:")
print_ast(ast_fib)
print()

# Analizar las llamadas recursivas
print("="*70)
print("ANÁLISIS: DOBLE RECURSIÓN")
print("="*70)
print()

fib_sub = ast_fib.algorithm.subroutines[0]
fib_if = fib_sub.body[0]
fib_else = fib_if.else_block.statements[0]

print(f"📦 Return del caso recursivo:")
print(f"   - Tipo: {type(fib_else).__name__}")

if isinstance(fib_else, ReturnStatement):
    ret_value = fib_else.value
    print(f"   - Retorna: {type(ret_value).__name__}")
    
    if isinstance(ret_value, BinaryOp):
        print(f"   - Operador: {ret_value.operator}")
        print()
        
        # Primera llamada recursiva
        if isinstance(ret_value.left, FunctionCall):
            print("   🔄 PRIMERA LLAMADA RECURSIVA:")
            print(f"      - Función: {ret_value.left.function_name}")
            print(f"      - Argumentos: {ret_value.left.arguments}")
        
        # Segunda llamada recursiva
        if isinstance(ret_value.right, FunctionCall):
            print()
            print("   🔄 SEGUNDA LLAMADA RECURSIVA:")
            print(f"      - Función: {ret_value.right.function_name}")
            print(f"      - Argumentos: {ret_value.right.arguments}")

print()

# ============================================================================
# EJEMPLO 3: SUMA RECURSIVA DE ARREGLO
# ============================================================================

print("="*70)
print("EJEMPLO 3: SUMA RECURSIVA DE ARREGLO")
print("="*70)
print()

code_sum = """
sumaArray(A, inicio, fin)
begin
    if (inicio > fin) then
    begin
        return 0
    end
    else
    begin
        return A[inicio] + sumaArray(A, inicio + 1, fin)
    end
end

begin
    total := sumaArray(A, 1, 10)
end

"""

print("📝 CÓDIGO:")
print(code_sum)

# Parsear y transformar
tree_sum = parser.parse(code_sum)
ast_sum = transformer.transform(tree_sum)

print("✅ Parseado y transformado exitosamente")
print()

print("🔍 ESTRUCTURA DEL AST:")
print_ast(ast_sum)
print()

# Analizar parámetros
sum_sub = ast_sum.algorithm.subroutines[0]
print("📦 Función con múltiples parámetros:")
print(f"   - Nombre: {sum_sub.name}")
print(f"   - Número de parámetros: {len(sum_sub.parameters)}")
for i, param in enumerate(sum_sub.parameters):
    print(f"   - Parámetro {i+1}: {param.name} (tipo: {param.param_type})")
print()

# ============================================================================
# RESUMEN Y CONCLUSIONES
# ============================================================================



print("="*70)
print("FIN DEL TEST DE RECURSIÓN")
print("="*70)