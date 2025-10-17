"""
Transformer: Convierte el árbol de Lark en nodos del AST (objetos Python).

Este archivo toma el árbol sintáctico generado por Lark y lo transforma
en objetos Python definidos en ast_nodes.py para facilitar el análisis.
"""

from lark import Transformer, Tree, Token
from parsing.ast_nodes import *

class PseudocodeTransformer(Transformer):
    """
    Transforma el árbol de Lark en nodos del AST.
    
    Cada método corresponde a una regla de la gramática:
    - El nombre del método debe coincidir con el nombre de la regla
    - Recibe los hijos del nodo como argumentos
    - Retorna un objeto del AST
    """
    
    # ========================================================================
    # PROGRAMA Y ESTRUCTURA PRINCIPAL
    # ========================================================================
    
    def start(self, items):
        """start: program"""
        return items[0]
    
    def program(self, items):
        """program: class_definition* algorithm"""
        classes = []
        algorithm = None
        
        for item in items:
            if isinstance(item, ClassDefinition):
                classes.append(item)
            elif isinstance(item, Algorithm):
                algorithm = item
        
        return Program(classes=classes, algorithm=algorithm)
    
    def class_definition(self, items):
        """class_definition: CNAME "{" attribute_list "}"""
        class_name = items[0].value
        attributes = items[1]
        return ClassDefinition(name=class_name, attributes=attributes)
    
    def attribute_list(self, items):
        """attribute_list: CNAME+"""
        return [token.value for token in items]
    
    def algorithm(self, items):
        """algorithm: subroutine_definition* main_algorithm"""
        subroutines = []
        main = None
        
        for item in items:
            if isinstance(item, Subroutine):
                subroutines.append(item)
            elif isinstance(item, MainAlgorithm):
                main = item
        
        return Algorithm(subroutines=subroutines, main=main)
    
    def main_algorithm(self, items):
        """main_algorithm: "begin" local_declarations? statement* "end"""
        declarations = []
        statements = []
        
        for item in items:
            if isinstance(item, Declaration):
                declarations.append(item)
            elif isinstance(item, list) and all(isinstance(x, Declaration) for x in item):
                declarations.extend(item)
            elif isinstance(item, Statement):
                statements.append(item)
        
        return MainAlgorithm(declarations=declarations, body=statements)
    
    def subroutine_definition(self, items):
        """subroutine_definition: CNAME "(" parameter_list? ")" "begin" local_declarations? statement* "end"""
        name = items[0].value
        parameters = []
        declarations = []
        statements = []
        
        for item in items[1:]:
            if isinstance(item, Parameter):
                parameters.append(item)
            elif isinstance(item, list):
                if all(isinstance(x, Parameter) for x in item):
                    parameters.extend(item)
                elif all(isinstance(x, Declaration) for x in item):
                    declarations.extend(item)
            elif isinstance(item, Declaration):
                declarations.append(item)
            elif isinstance(item, Statement):
                statements.append(item)
        
        return Subroutine(name=name, parameters=parameters, 
                         declarations=declarations, body=statements)
    
    # ========================================================================
    # DECLARACIONES Y PARÁMETROS
    # ========================================================================
    
    def local_declarations(self, items):
        """local_declarations: local_declaration+"""
        return items
    
    def local_declaration(self, items):
        """local_declaration: CNAME "[" expression "]" | CNAME CNAME"""
        if len(items) == 2 and isinstance(items[1], Expression):
            # Es un arreglo: nombre[tamaño]
            name = items[0].value
            size = items[1]
            return Declaration(name=name, decl_type='array', size=size)
        else:
            # Es un objeto: Clase nombre
            class_name = items[0].value
            obj_name = items[1].value
            return Declaration(name=obj_name, decl_type='object', class_name=class_name)
    
    def parameter_list(self, items):
        """parameter_list: parameter ("," parameter)*"""
        return items
    
    def parameter(self, items):
        """Se procesa en las reglas específicas"""
        return items[0]
    
    def simple_parameter(self, items):
        """simple_parameter: CNAME"""
        return Parameter(name=items[0].value, param_type='simple')
    
    def array_parameter(self, items):
        """array_parameter: CNAME ("[" expression? "]")+ (".." "[" expression "]")?"""
        name = items[0].value
        dimensions = sum(1 for item in items[1:] if isinstance(item, (Expression, type(None))))
        return Parameter(name=name, param_type='array', dimensions=dimensions)
    
    def object_parameter(self, items):
        """object_parameter: CNAME CNAME"""
        class_name = items[0].value
        param_name = items[1].value
        return Parameter(name=param_name, param_type='object', class_name=class_name)
    
    # ========================================================================
    # SENTENCIAS (STATEMENTS)
    # ========================================================================
    
    def statement(self, items):
        """statement: assignment | for_loop | while_loop | ..."""
        return items[0]
    
    def assignment(self, items):
        """assignment: variable ASSIGN expression"""
        # items puede ser [variable, expression] o [variable, ASSIGN_token, expression]
        variable = items[0]
        # Filtrar para obtener solo la expresión
        value = None
        for item in items[1:]:
            if isinstance(item, Expression):
                value = item
                break
        
        if value is None:
            value = items[-1]  # Último elemento
        
        return Assignment(variable=variable, value=value)
    
    def for_loop(self, items):
        """for_loop: "for" CNAME ASSIGN expression "to" expression "do" block"""
        variable = items[0].value
        # Filtrar tokens y obtener solo expresiones
        expressions = [item for item in items[1:] if isinstance(item, Expression)]
        blocks = [item for item in items[1:] if isinstance(item, Block)]
        
        start = expressions[0] if len(expressions) > 0 else Number(0)
        end = expressions[1] if len(expressions) > 1 else Number(0)
        body = blocks[0] if blocks else Block([])
        
        return ForLoop(variable=variable, start=start, end=end, body=body)
    
    def while_loop(self, items):
        """while_loop: "while" "(" condition ")" "do" block"""
        condition = items[0]
        body = items[1]
        return WhileLoop(condition=condition, body=body)
    
    def repeat_loop(self, items):
        """repeat_loop: "repeat" statement+ "until" "(" condition ")"""
        statements = items[:-1]
        condition = items[-1]
        return RepeatLoop(body=statements, condition=condition)
    
    def if_statement(self, items):
        """if_statement: "if" "(" condition ")" "then" block ("else" block)?"""
        condition = items[0]
        then_block = items[1]
        else_block = items[2] if len(items) > 2 else None
        return IfStatement(condition=condition, then_block=then_block, else_block=else_block)
    
    def call_statement(self, items):
        """call_statement: "call" CNAME "(" argument_list? ")"""
        function_name = items[0].value
        arguments = items[1] if len(items) > 1 else []
        return CallStatement(function_name=function_name, arguments=arguments)
    
    def return_statement(self, items):
        """return_statement: "return" expression"""
        return ReturnStatement(value=items[0])
    
    def comment(self, items):
        """comment: COMMENT"""
        text = items[0].value.strip()
        if text.startswith('►'):
            text = text[1:].strip()
        return Comment(text=text)
    
    def block(self, items):
        """block: "begin" statement* "end" | statement"""
        statements = [item for item in items if isinstance(item, Statement)]
        return Block(statements=statements)
    
    def argument_list(self, items):
        """argument_list: expression ("," expression)*"""
        return items
    
    def condition(self, items):
        """condition: expression"""
        return items[0]
    
    # ========================================================================
    # VARIABLES
    # ========================================================================
    
    def variable(self, items):
        """variable: CNAME | CNAME "[" ... | CNAME "." CNAME | ..."""
        if len(items) == 1:
            return Variable(name=items[0].value)
        
        elif len(items) >= 2:
            name = items[0].value
            
            if isinstance(items[1], Token) and items[1].type == 'CNAME':
                field = items[1].value
                if len(items) > 2:
                    indices = items[2:]
                    return Variable(name=name, field=field, field_indices=indices)
                else:
                    return Variable(name=name, field=field)
            
            elif isinstance(items[1], tuple):
                range_start, range_end = items[1]
                return Variable(name=name, is_range=True, 
                              range_start=range_start, range_end=range_end)
            
            else:
                indices = items[1:]
                return Variable(name=name, indices=indices)
        
        return Variable(name=items[0].value)
    
    def range(self, items):
        """range: expression ".." expression"""
        return (items[0], items[1])
    
    # ========================================================================
    # EXPRESIONES
    # ========================================================================
    
    def expression(self, items):
        """expression: logical_or"""
        return items[0]
    
    def logical_or(self, items):
        """logical_or: logical_and ("or" logical_and)*"""
        if len(items) == 1:
            return items[0]
        
        result = items[0]
        for i in range(1, len(items)):
            result = BinaryOp(operator="or", left=result, right=items[i])
        return result
    
    def logical_and(self, items):
        """logical_and: logical_not ("and" logical_not)*"""
        if len(items) == 1:
            return items[0]
        
        result = items[0]
        for i in range(1, len(items)):
            result = BinaryOp(operator="and", left=result, right=items[i])
        return result
    
    def logical_not(self, items):
        """logical_not: "not" logical_not | comparison"""
        if len(items) == 1:
            return items[0]
        else:
            return UnaryOp(operator="not", operand=items[0])
    
    def comparison(self, items):
        """comparison: arithmetic (comp_op arithmetic)*"""
        if len(items) == 1:
            return items[0]
        
        result = items[0]
        i = 1
        while i < len(items):
            if i + 1 < len(items):
                operator = items[i]
                right = items[i + 1]
                result = BinaryOp(operator=operator, left=result, right=right)
                i += 2
            else:
                break
        
        return result
    
    def comp_op(self, items):
        """comp_op: "<" | ">" | "<=" | ">=" | "=" | "!=" | "≤" | "≥" | "≠"""
        if len(items) == 0:
            return "="
        
        op = items[0].value if isinstance(items[0], Token) else str(items[0])
        
        if op == "≤":
            return "<="
        elif op == "≥":
            return ">="
        elif op == "≠":
            return "!="
        return op
    
    def arithmetic(self, items):
        """arithmetic: term (("+"|"-") term)*"""
        if len(items) == 1:
            return items[0]
        
        result = items[0]
        i = 1
        while i < len(items):
            if i + 1 < len(items):
                operator_item = items[i]
                
                if isinstance(operator_item, Token):
                    operator = operator_item.value
                elif isinstance(operator_item, str):
                    operator = operator_item
                else:
                    operator = str(operator_item)
                
                right = items[i + 1]
                result = BinaryOp(operator=operator, left=result, right=right)
                i += 2
            else:
                break
        
        return result
    
    def term(self, items):
        """term: factor (("*"|"/"|"mod"|"div") factor)*"""
        if len(items) == 1:
            return items[0]
        
        result = items[0]
        i = 1
        while i < len(items):
            if i + 1 < len(items):
                operator_item = items[i]
                
                if isinstance(operator_item, Token):
                    operator = operator_item.value
                elif isinstance(operator_item, str):
                    operator = operator_item
                else:
                    operator = str(operator_item)
                
                right = items[i + 1]
                result = BinaryOp(operator=operator, left=result, right=right)
                i += 2
            else:
                break
        
        return result
    
    def factor(self, items):
        """factor: ("+" | "-") factor | power"""
        if len(items) == 1:
            return items[0]
        else:
            operator = items[0].value if isinstance(items[0], Token) else items[0]
            operand = items[1]
            return UnaryOp(operator=operator, operand=operand)
    
    def power(self, items):
        """power: atom ("^" atom)*"""
        if len(items) == 1:
            return items[0]
        
        result = items[-1]
        for i in range(len(items) - 2, -1, -1):
            result = BinaryOp(operator="^", left=items[i], right=result)
        return result
    
    def atom(self, items):
        """atom: NUMBER | BOOLEAN | NULL | variable | function_call | ..."""
        return items[0]
    
    # ========================================================================
    # VALORES LITERALES
    # ========================================================================
    
    def NUMBER(self, token):
        """Terminal NUMBER"""
        value = token.value
        if '.' in value:
            return Number(float(value))
        return Number(int(value))
    
    def BOOLEAN(self, token):
        """Terminal BOOLEAN"""
        value = token.value.lower()
        return Boolean(value in ('t', 'true'))
    
    def NULL(self, token):
        """Terminal NULL"""
        return Null()
    
    def CNAME(self, token):
        """Terminal CNAME - usado en contextos específicos"""
        return token
    
    def ASSIGN(self, token):
        """Terminal ASSIGN - se ignora en el AST"""
        return token
    
    # ========================================================================
    # FUNCIONES ESPECIALES
    # ========================================================================
    
    def function_call(self, items):
        """function_call: CNAME "(" argument_list? ")"""
        function_name = items[0].value
        arguments = items[1] if len(items) > 1 else []
        return FunctionCall(function_name=function_name, arguments=arguments)
    
    def length(self, items):
        """length: "length" "(" variable ")"""
        return Length(variable=items[0])
    
    def ceiling(self, items):
        """ceiling: "┌" expression "┐"""
        return Ceiling(expression=items[0])
    
    def floor(self, items):
        """floor: "└" expression "┘"""
        return Floor(expression=items[0])


# ============================================================================
# FUNCIÓN AUXILIAR PARA USAR EL TRANSFORMER
# ============================================================================

# def parse_pseudocode(code: str, grammar_path: str = None):
#     """
#     Parsea pseudocódigo y retorna el AST en forma de objetos Python.
    
#     Args:
#         code: Código en pseudocódigo
#         grammar_path: Ruta opcional al archivo .lark
    
#     Returns:
#         Program: Objeto raíz del AST
#     """
#     from .parser import PseudocodeParser
    
#     # Usar el parser separado
#     parser = PseudocodeParser(grammar_path)
#     tree = parser.parse(code)
    
#     # Transformar a objetos Python
#     transformer = PseudocodeTransformer()
#     ast = transformer.transform(tree)
    
#     return ast


