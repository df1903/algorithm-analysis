"""
TEST DE FLUJO COMPLETO: De código → Árbol Lark → Objetos Python

Este archivo demuestra paso a paso cómo funciona todo el sistema:
1. Código de entrada (pseudocódigo)
2. Parser de Lark (usa pseudocode.lark)
3. Árbol sintáctico de Lark
4. Transformer (usa ast_nodes.py)
5. Objetos Python finales

VERSIÓN ACTUALIZADA: Usa la arquitectura separada (parser.py + transformer.py)
"""

import sys
import os

# Ajustar path si es necesario
if os.path.exists('app/parsing'):
    sys.path.insert(0, 'app')

from parsing.parser import PseudocodeParser
from parsing.transformer import PseudocodeTransformer
from parsing.ast_nodes import *

# ============================================================================
# PASO 1: CREAR EL PARSER
# ============================================================================

print("="*70)
print("PASO 1: CREANDO EL PARSER (parser.py)")
print("="*70)

parser = PseudocodeParser()

print("✅ Parser creado exitosamente")
print(f"   - Gramática cargada desde: {parser.grammar_path}")
print("   - Usa: pseudocode.lark + Lark")
print("   - Algoritmo: LALR (Look-Ahead LR)")
print()

# ============================================================================
# PASO 2: CÓDIGO DE PRUEBA
# ============================================================================

print("="*70)
print("PASO 2: CÓDIGO DE ENTRADA")
print("="*70)

# Código simple para probar
code = """
begin
    x := 5
end
"""

print("Pseudocódigo:")
print(code)
print()

# ============================================================================
# PASO 3: PARSEAR EL CÓDIGO (Lark genera el árbol)
# ============================================================================

print("="*70)
print("PASO 3: PARSEANDO EL CÓDIGO → GENERANDO ÁRBOL DE LARK")
print("="*70)

tree = parser.parse(code)

print("✅ Código parseado exitosamente")
print("\nÁrbol de Lark generado (versión simplificada):")
print(tree.pretty())
print()

# ============================================================================
# PASO 4: CREAR EL TRANSFORMER
# ============================================================================

print("="*70)
print("PASO 4: CREANDO EL TRANSFORMER (transformer.py)")
print("="*70)

transformer = PseudocodeTransformer()

print("✅ Transformer creado")
print("   - Usa las clases de ast_nodes.py")
print("   - Convertirá el árbol de Lark → Objetos Python")
print()

# ============================================================================
# PASO 5: TRANSFORMAR EL ÁRBOL → OBJETOS PYTHON (AST)
# ============================================================================

print("="*70)
print("PASO 5: TRANSFORMANDO ÁRBOL → OBJETOS PYTHON (AST)")
print("="*70)

ast = transformer.transform(tree)

print("✅ Árbol transformado exitosamente")
print("\nTipo del resultado:", type(ast))
print("Valor:", ast)
print()

# ============================================================================
# PASO 6: EXPLORAR EL AST RESULTANTE
# ============================================================================

print("="*70)
print("PASO 6: EXPLORANDO EL AST RESULTANTE")
print("="*70)

print("Estructura completa del AST:")
print_ast(ast)
print()

# ============================================================================
# PASO 7: ACCEDER A DATOS ESPECÍFICOS DEL AST
# ============================================================================

print("="*70)
print("PASO 7: ACCEDIENDO A DATOS ESPECÍFICOS")
print("="*70)

print("📦 Objeto raíz:")
print(f"   - Tipo: {type(ast).__name__}")
print(f"   - Clases definidas: {len(ast.classes)}")
print()

print("📦 Algoritmo:")
algo = ast.algorithm
print(f"   - Tipo: {type(algo).__name__}")
print(f"   - Subrutinas: {len(algo.subroutines)}")
print()

print("📦 Algoritmo principal:")
main = algo.main
print(f"   - Tipo: {type(main).__name__}")
print(f"   - Declaraciones: {len(main.declarations)}")
print(f"   - Sentencias: {len(main.body)}")
print()

print("📦 Primera sentencia:")
stmt = main.body[0]
print(f"   - Tipo: {type(stmt).__name__}")
print(f"   - Variable: {stmt.variable}")
print(f"   - Valor: {stmt.value}")
print()

print("📦 Variable de la asignación:")
var = stmt.variable
print(f"   - Tipo: {type(var).__name__}")
print(f"   - Nombre: {var.name}")
print()

print("📦 Valor de la asignación:")
val = stmt.value
print(f"   - Tipo: {type(val).__name__}")
print(f"   - Valor: {val.value}")
print()

# ============================================================================
# PASO 8: COMPARACIÓN ÁRBOL LARK vs AST
# ============================================================================

print("="*70)
print("PASO 8: COMPARACIÓN ÁRBOL LARK vs AST")
print("="*70)

print("🌳 ÁRBOL DE LARK (texto/estructura):")
print("   start → program → algorithm → main_algorithm → statement → assignment")
print("   └─ assignment tiene:")
print("      ├─ variable (Token CNAME: 'x')")
print("      ├─ ASSIGN (Token: ':=')")
print("      └─ expression (Token NUMBER: '5')")
print()

print("🎯 AST (objetos Python):")
print("   Program → Algorithm → MainAlgorithm → Assignment")
print("   └─ Assignment tiene:")
print("      ├─ variable: Variable(name='x')")
print("      └─ value: Number(value=5)")
print()

print("💡 DIFERENCIA CLAVE:")
print("   Lark: Estructura de texto (tokens y árboles)")
print("   AST:  Objetos Python (con atributos y métodos)")
print()

# ============================================================================
# PASO 9: EJEMPLO MÁS COMPLEJO
# ============================================================================

print("="*70)
print("PASO 9: PROBANDO CON UN EJEMPLO MÁS COMPLEJO")
print("="*70)

code2 = """
begin
    for i := 1 to n do
    begin
        sum := sum + i
    end
end
"""

print("Código:")
print(code2)

# Parsear
tree2 = parser.parse(code2)
print("\n✅ Parseado exitosamente")

# Transformar
ast2 = transformer.transform(tree2)
print("✅ Transformado exitosamente")

print("\nAST resultante:")
print_ast(ast2)
print()

# Explorar el FOR loop
for_loop = ast2.algorithm.main.body[0]
print("📦 Estructura del FOR loop:")
print(f"   - Tipo: {type(for_loop).__name__}")
print(f"   - Variable: {for_loop.variable}")
print(f"   - Inicio: {for_loop.start}")
print(f"   - Fin: {for_loop.end}")
print(f"   - Cuerpo: {for_loop.body}")
print()

# Explorar el cuerpo del FOR
body_stmt = for_loop.body.statements[0]
print("📦 Statement dentro del FOR:")
print(f"   - Tipo: {type(body_stmt).__name__}")
if isinstance(body_stmt, Assignment):
    print(f"   - Variable: {body_stmt.variable.name}")
    print(f"   - Valor: {body_stmt.value}")
    if isinstance(body_stmt.value, BinaryOp):
        print(f"   - Operador: {body_stmt.value.operator}")
        print(f"   - Izquierda: {body_stmt.value.left}")
        print(f"   - Derecha: {body_stmt.value.right}")
print()

# ============================================================================
# PASO 10: DEMOSTRACIÓN DE LA ARQUITECTURA SEPARADA
# ============================================================================

#============================================================================
# RESUMEN FINAL
# ============================================================================

print("="*70)
print("🎉 RESUMEN DEL FLUJO COMPLETO")
print("="*70)

print("""
1️⃣  Código (texto)
    ↓
2️⃣  parser.py → Lee pseudocode.lark
    ↓
3️⃣  Lark Parser (aplica reglas)
    ↓
4️⃣  Árbol de Lark (Tree object)
    ↓
5️⃣  transformer.py → Usa ast_nodes.py
    ↓
6️⃣  Transformer (convierte estructura)
    ↓
7️⃣  AST (objetos Python: Program, ForLoop, etc.)
    ↓
8️⃣  ¡Listo para analizar complejidad!

✅ TODO FUNCIONA JUNTO CON ARQUITECTURA SEPARADA
""")

print("="*70)
print("FIN DEL TEST")
print("="*70)