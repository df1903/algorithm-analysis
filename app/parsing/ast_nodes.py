"""
Nodos del AST (Abstract Syntax Tree) para el analizador de complejidades.

Cada clase representa un elemento del pseudocódigo y tendrá métodos
para calcular su complejidad computacional.
"""

from typing import List, Optional, Union
from dataclasses import dataclass

# ============================================================================
# NODOS BASE
# ============================================================================


class ASTNode:
    """Clase base para todos los nodos del AST"""
    line: Optional[int] = None  # Línea del código fuente (para debugging)
    
    def __repr__(self):
        return f"{self.__class__.__name__}(...)"

# ============================================================================
# PROGRAMA Y ESTRUCTURA PRINCIPAL
# ============================================================================

@dataclass
class Program(ASTNode):
    """Programa completo: clases + algoritmo"""
    classes: List['ClassDefinition']
    algorithm: 'Algorithm'
    
    def __repr__(self):
        return f"Program(classes={len(self.classes)}, algorithm={self.algorithm})"


@dataclass
class ClassDefinition(ASTNode):
    """Definición de una clase: Casa {area color propietario}"""
    name: str
    attributes: List[str]
    
    def __repr__(self):
        return f"Class({self.name}, attributes={self.attributes})"


@dataclass
class Algorithm(ASTNode):
    """Algoritmo completo con subrutinas y algoritmo principal"""
    subroutines: List['Subroutine']
    main: 'MainAlgorithm'
    
    def __repr__(self):
        return f"Algorithm(subroutines={len(self.subroutines)})"


@dataclass
class Subroutine(ASTNode):
    """Definición de subrutina/función: factorial(n) begin ... end"""
    name: str
    parameters: List['Parameter']
    declarations: List['Declaration']
    body: List['Statement']
    
    def __repr__(self):
        return f"Subroutine({self.name}, params={len(self.parameters)})"


@dataclass
class MainAlgorithm(ASTNode):
    """Algoritmo principal: begin ... end"""
    declarations: List['Declaration']
    body: List['Statement']
    
    def __repr__(self):
        return f"MainAlgorithm(statements={len(self.body)})"

# ============================================================================
# PARÁMETROS Y DECLARACIONES
# ============================================================================

@dataclass
class Parameter(ASTNode):
    """Parámetro de una subrutina"""
    name: str
    param_type: str  # 'simple', 'array', 'object'
    class_name: Optional[str] = None  # Para objetos
    dimensions: Optional[int] = None   # Para arreglos
    
    def __repr__(self):
        return f"Parameter({self.name}, type={self.param_type})"


@dataclass
class Declaration(ASTNode):
    """Declaración local: A[10] o Persona p"""
    name: str
    decl_type: str  # 'array' o 'object'
    size: Optional['Expression'] = None     # Para arreglos
    class_name: Optional[str] = None        # Para objetos
    
    def __repr__(self):
        return f"Declaration({self.name}, type={self.decl_type})"

# ============================================================================
# SENTENCIAS (STATEMENTS)
# ============================================================================

@dataclass
class Statement(ASTNode):
    """Clase base para todas las sentencias"""
    pass


@dataclass
class Assignment(Statement):
    """Asignación: x := 5"""
    variable: 'Variable'
    value: 'Expression'
    
    def __repr__(self):
        return f"Assignment({self.variable} := {self.value})"


@dataclass
class ForLoop(Statement):
    """Ciclo FOR: for i := 1 to n do begin ... end"""
    variable: str
    start: 'Expression'
    end: 'Expression'
    body: 'Block'
    
    def __repr__(self):
        return f"ForLoop({self.variable}: {self.start} to {self.end})"


@dataclass
class WhileLoop(Statement):
    """Ciclo WHILE: while (condicion) do begin ... end"""
    condition: 'Expression'
    body: 'Block'
    
    def __repr__(self):
        return f"WhileLoop(condition={self.condition})"


@dataclass
class RepeatLoop(Statement):
    """Ciclo REPEAT: repeat ... until (condicion)"""
    body: List[Statement]
    condition: 'Expression'
    
    def __repr__(self):
        return f"RepeatLoop(statements={len(self.body)})"


@dataclass
class IfStatement(Statement):
    """Condicional IF: if (cond) then begin ... end else begin ... end"""
    condition: 'Expression'
    then_block: 'Block'
    else_block: Optional['Block'] = None
    
    def __repr__(self):
        has_else = "with else" if self.else_block else "no else"
        return f"IfStatement({has_else})"


@dataclass
class CallStatement(Statement):
    """Llamada a subrutina: call funcion(a, b, c)"""
    function_name: str
    arguments: List['Expression']
    
    def __repr__(self):
        return f"CallStatement({self.function_name}, args={len(self.arguments)})"


@dataclass
class ReturnStatement(Statement):
    """Return: return expresion"""
    value: 'Expression'
    
    def __repr__(self):
        return f"ReturnStatement({self.value})"


@dataclass
class Comment(Statement):
    """Comentario: ► texto"""
    text: str
    
    def __repr__(self):
        return f"Comment('{self.text[:20]}...')"


@dataclass
class Block(ASTNode):
    """Bloque de código: begin ... end"""
    statements: List[Statement]
    
    def __repr__(self):
        return f"Block(statements={len(self.statements)})"

# ============================================================================
# EXPRESIONES
# ============================================================================

@dataclass
class Expression(ASTNode):
    """Clase base para todas las expresiones"""
    pass


@dataclass
class Number(Expression):
    """Número: 5, 3.14"""
    value: Union[int, float]
    
    def __repr__(self):
        return f"Number({self.value})"


@dataclass
class Boolean(Expression):
    """Booleano: T, F, true, false"""
    value: bool
    
    def __repr__(self):
        return f"Boolean({self.value})"


@dataclass
class Null(Expression):
    """NULL"""
    def __repr__(self):
        return "Null()"


@dataclass
class Variable(Expression):
    """Variable: x, A[i], M[i][j], obj.campo"""
    name: str
    indices: Optional[List['Expression']] = None    # Para A[i][j]
    field: Optional[str] = None                     # Para obj.campo
    field_indices: Optional[List['Expression']] = None  # Para obj.arr[i]
    is_range: bool = False                          # Para A[1..j]
    range_start: Optional['Expression'] = None
    range_end: Optional['Expression'] = None
    
    def __repr__(self):
        if self.indices:
            return f"Variable({self.name}[...])"
        elif self.field:
            return f"Variable({self.name}.{self.field})"
        elif self.is_range:
            return f"Variable({self.name}[{self.range_start}..{self.range_end}])"
        return f"Variable({self.name})"


@dataclass
class BinaryOp(Expression):
    """Operación binaria: x + y, a * b, etc."""
    operator: str  # '+', '-', '*', '/', 'mod', 'div', '^', 'and', 'or', '<', '>', etc.
    left: Expression
    right: Expression
    
    def __repr__(self):
        return f"BinaryOp({self.left} {self.operator} {self.right})"


@dataclass
class UnaryOp(Expression):
    """Operación unaria: -x, not x"""
    operator: str  # '-', '+', 'not'
    operand: Expression
    
    def __repr__(self):
        return f"UnaryOp({self.operator} {self.operand})"


@dataclass
class FunctionCall(Expression):
    """Llamada a función: factorial(n), suma(a, b)"""
    function_name: str
    arguments: List[Expression]
    
    def __repr__(self):
        return f"FunctionCall({self.function_name}, args={len(self.arguments)})"


@dataclass
class Length(Expression):
    """length(A)"""
    variable: Variable
    
    def __repr__(self):
        return f"Length({self.variable})"


@dataclass
class Ceiling(Expression):
    """┌expresión┐"""
    expression: Expression
    
    def __repr__(self):
        return f"Ceiling({self.expression})"


@dataclass
class Floor(Expression):
    """└expresión┘"""
    expression: Expression
    
    def __repr__(self):
        return f"Floor({self.expression})"


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def print_ast(node: ASTNode, indent: int = 0):
    """Imprime el AST de forma legible"""
    prefix = "  " * indent
    print(f"{prefix}{node.__class__.__name__}", end="")
    
    if isinstance(node, Program):
        print()
        for cls in node.classes:
            print_ast(cls, indent + 1)
        print_ast(node.algorithm, indent + 1)
    
    elif isinstance(node, Algorithm):
        print()
        for sub in node.subroutines:
            print_ast(sub, indent + 1)
        print_ast(node.main, indent + 1)
    
    elif isinstance(node, MainAlgorithm):
        print(f" ({len(node.body)} statements)")
        for stmt in node.body:
            print_ast(stmt, indent + 1)
    
    elif isinstance(node, ForLoop):
        print(f" ({node.variable}: {node.start} to {node.end})")
        print_ast(node.body, indent + 1)
    
    elif isinstance(node, Block):
        print(f" ({len(node.statements)} statements)")
        for stmt in node.statements:
            print_ast(stmt, indent + 1)
    
    elif isinstance(node, Assignment):
        print()
        print(f"{prefix}  Variable: ", end="")
        print_ast(node.variable, 0)
        print(f"{prefix}  Value: ", end="")
        print_ast(node.value, 0)
    
    elif isinstance(node, BinaryOp):
        print(f" ({node.operator})")
        print_ast(node.left, indent + 1)
        print_ast(node.right, indent + 1)
    
    else:
        print(f": {node}")


