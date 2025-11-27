"""
Generador de diagramas Mermaid desde AST

Este módulo traduce estructuras AST de pseudocódigo Pascal-like
a sintaxis Mermaid para visualización de flujos algorítmicos.
"""

from typing import List, Optional, Union, Dict
from app.parsing.ast_nodes import (
    # Nodos principales
    Program,
    Algorithm,
    Subroutine,
    MainAlgorithm,
    Block,
    
    # Statements
    Statement,
    Assignment,
    ForLoop,
    WhileLoop,
    RepeatLoop,
    IfStatement,
    CallStatement,
    ReturnStatement,
    Comment,
    
    # Expressions
    Expression,
    Number,
    Boolean,
    Variable,
    BinaryOp,
    UnaryOp,
    FunctionCall,
    Length,
    Ceiling,
    Floor,
    Null
)


class MermaidGenerator:
    """
    Genera diagramas de flujo Mermaid desde AST
    
    Ejemplo de uso:
        generator = MermaidGenerator()
        mermaid_code = generator.generate(ast_obj)
    """
    
    def __init__(self):
        """Inicializa el generador"""
        self.node_counter = 0
        self.mermaid_lines = []
        
    def generate(self, ast_obj: Union[Program, Subroutine]) -> str:
        """
        Genera código Mermaid completo desde un AST
        
        Args:
            ast_obj: Program completo o Subroutine específica
            
        Returns:
            str: Código Mermaid válido
        """
        # Resetear estado
        self.node_counter = 0
        self.mermaid_lines = []
        
        # Header
        self.mermaid_lines.append("flowchart TD")
        
        # Determinar qué generar
        if isinstance(ast_obj, Program):
            target = ast_obj.algorithm.main
            name = "main"
            params = []
        elif isinstance(ast_obj, Subroutine):
            target = ast_obj
            name = ast_obj.name
            params = [p.name for p in ast_obj.parameters]
        else:
            raise ValueError(f"Tipo no soportado: {type(ast_obj)}")
        
        # Nodo de inicio
        start_id = "START"
        if params:
            params_str = ", ".join(params)
            start_label = self._escape_text(f"{name}({params_str})")
        else:
            start_label = self._escape_text(name)
        
        self.mermaid_lines.append(f"    {start_id}([{start_label}])")
        
        # Procesar el cuerpo
        body_statements = target.body if isinstance(target, Subroutine) else target.body
        
        if body_statements:
            first_stmt_id = self._process_statements(body_statements)
            self.mermaid_lines.append(f"    {start_id} --> {first_stmt_id}")
        else:
            # Si no hay statements, conectar directo al fin
            end_id = "END"
            self.mermaid_lines.append(f"    {end_id}([Fin])")
            self.mermaid_lines.append(f"    {start_id} --> {end_id}")
        
        return "\n".join(self.mermaid_lines)
    
    def _process_statements(self, statements: List[Statement]) -> str:
        """
        Procesa una lista de statements y retorna el ID del primer nodo
        
        Args:
            statements: Lista de statements a procesar
            
        Returns:
            str: ID del primer nodo generado
        """
        if not statements:
            end_id = "END"
            self.mermaid_lines.append(f"    {end_id}([Fin])")
            return end_id
        
        first_id = None
        prev_id = None
        prev_stmt = None
        
        for i, stmt in enumerate(statements):
            stmt_id = self._process_statement(stmt)
            
            if stmt_id is None:  # Comentarios
                continue
            
            if first_id is None:
                first_id = stmt_id
            
            # Conectar con el statement anterior
            if prev_id is not None and prev_stmt is not None:
                # Si el anterior es un loop, conectar la salida
                if isinstance(prev_stmt, (ForLoop, WhileLoop)):
                    # Para loops, la rama "salida" conecta al siguiente statement
                    if isinstance(prev_stmt, ForLoop):
                        end_text = self._expression_to_text(prev_stmt.end)
                        self.mermaid_lines.append(f"    {prev_id} -->|{self._escape_text(f'{prev_stmt.variable} > {end_text}')}| {stmt_id}")
                    elif isinstance(prev_stmt, WhileLoop):
                        self.mermaid_lines.append(f"    {prev_id} -->|False| {stmt_id}")
                elif isinstance(prev_stmt, RepeatLoop):
                    # Para repeat, la condición True conecta al siguiente
                    self.mermaid_lines.append(f"    {prev_id} -->|True| {stmt_id}")
                elif isinstance(prev_stmt, IfStatement):
                    # Si el IF no es terminal, conectar
                    if not self._is_terminal_statement(prev_stmt):
                        self.mermaid_lines.append(f"    {prev_id} --> {stmt_id}")
                elif not self._is_terminal_statement(prev_stmt):
                    # Otros statements no terminales
                    self.mermaid_lines.append(f"    {prev_id} --> {stmt_id}")
            
            prev_id = stmt_id
            prev_stmt = stmt
        
        # Crear nodo END
        end_id = "END"
        self.mermaid_lines.append(f"    {end_id}([Fin])")
        
        # Conectar último statement al END
        if prev_id and prev_stmt:
            if isinstance(prev_stmt, ReturnStatement):
                # Returns SIEMPRE conectan al END
                self.mermaid_lines.append(f"    {prev_id} --> {end_id}")
            elif isinstance(prev_stmt, (ForLoop, WhileLoop)):
                # Para loops, la salida va al END
                if isinstance(prev_stmt, ForLoop):
                    end_text = self._expression_to_text(prev_stmt.end)
                    self.mermaid_lines.append(f"    {prev_id} -->|{self._escape_text(f'{prev_stmt.variable} > {end_text}')}| {end_id}")
                elif isinstance(prev_stmt, WhileLoop):
                    self.mermaid_lines.append(f"    {prev_id} -->|False| {end_id}")
            elif isinstance(prev_stmt, RepeatLoop):
                self.mermaid_lines.append(f"    {prev_id} -->|True| {end_id}")
            elif not self._is_terminal_statement(prev_stmt):
                self.mermaid_lines.append(f"    {prev_id} --> {end_id}")
        
        return first_id
    
    def _is_terminal_statement(self, stmt: Statement) -> bool:
        """
        Determina si un statement es terminal (no continúa el flujo)
        
        Args:
            stmt: Statement a verificar
            
        Returns:
            bool: True si es terminal
        """
        if isinstance(stmt, ReturnStatement):
            return True
        
        if isinstance(stmt, IfStatement):
            # Un IF es terminal si AMBAS ramas son terminales
            then_terminal = self._block_is_terminal(stmt.then_block)
            
            if stmt.else_block:
                else_terminal = self._block_is_terminal(stmt.else_block)
            else:
                # Si no hay else, no es terminal
                else_terminal = False
            
            return then_terminal and else_terminal
        
        return False
    
    def _block_is_terminal(self, block: Block) -> bool:
        """
        Determina si un bloque termina con statement terminal
        
        Args:
            block: Bloque a verificar
            
        Returns:
            bool: True si el último statement es terminal
        """
        if not block or not block.statements:
            return False
        
        last_stmt = block.statements[-1]
        return self._is_terminal_statement(last_stmt)
    
    def _process_statement(self, stmt: Statement) -> Optional[str]:
        """
        Procesa un statement individual y retorna su ID
        
        Args:
            stmt: Statement a procesar
            
        Returns:
            str: ID del nodo generado, o None para comentarios
        """
        if isinstance(stmt, Assignment):
            return self._process_assignment(stmt)
        elif isinstance(stmt, IfStatement):
            return self._process_if(stmt)
        elif isinstance(stmt, ForLoop):
            return self._process_for(stmt)
        elif isinstance(stmt, WhileLoop):
            return self._process_while(stmt)
        elif isinstance(stmt, RepeatLoop):
            return self._process_repeat(stmt)
        elif isinstance(stmt, CallStatement):
            return self._process_call(stmt)
        elif isinstance(stmt, ReturnStatement):
            return self._process_return(stmt)
        elif isinstance(stmt, Comment):
            # Los comentarios no generan nodos
            return None
        else:
            # Statement desconocido
            stmt_id = self._get_next_id("STMT")
            label = self._escape_text(str(stmt))
            self.mermaid_lines.append(f"    {stmt_id}[{label}]")
            return stmt_id
    
    def _process_assignment(self, stmt: Assignment) -> str:
        """Procesa una asignación"""
        stmt_id = self._get_next_id("ASSIGN")
        var_text = self._expression_to_text(stmt.variable)
        val_text = self._expression_to_text(stmt.value)
        label = self._escape_text(f"{var_text} := {val_text}")
        self.mermaid_lines.append(f"    {stmt_id}[{label}]")
        return stmt_id
    
    def _process_if(self, stmt: IfStatement) -> str:
        """Procesa un condicional IF"""
        # Nodo de decisión
        if_id = self._get_next_id("IF")
        condition_text = self._expression_to_text(stmt.condition)
        label = self._escape_text(condition_text + "?")
        self.mermaid_lines.append(f"    {if_id}{{{label}}}")
        
        # Procesar bloque THEN
        then_ids = self._process_block_statements(stmt.then_block)
        if then_ids:
            self.mermaid_lines.append(f"    {if_id} -->|True| {then_ids['first']}")
            # Si el bloque THEN termina con return, conectar al END
            if self._block_is_terminal(stmt.then_block):
                self.mermaid_lines.append(f"    {then_ids['last']} --> END")
            # Si no es terminal, NO conectar aquí - se conectará después al siguiente statement
        
        # Procesar bloque ELSE si existe
        if stmt.else_block:
            else_ids = self._process_block_statements(stmt.else_block)
            if else_ids:
                self.mermaid_lines.append(f"    {if_id} -->|False| {else_ids['first']}")
                # Si el bloque ELSE termina con return, conectar al END
                if self._block_is_terminal(stmt.else_block):
                    self.mermaid_lines.append(f"    {else_ids['last']} --> END")
                # Si no es terminal, NO conectar aquí
        else:
            # Si no hay ELSE, NO conectar nada - el statement siguiente se conectará
            pass
        
        return if_id
    
    def _process_block_statements(self, block: Block) -> Optional[Dict[str, str]]:
        """
        Procesa statements de un bloque y retorna primer y último ID
        
        Args:
            block: Bloque a procesar
            
        Returns:
            dict con 'first' y 'last' IDs, o None si está vacío
        """
        if not block or not block.statements:
            return None
        
        first_id = None
        prev_id = None
        
        for stmt in block.statements:
            stmt_id = self._process_statement(stmt)
            
            if stmt_id is None:  # Comentarios
                continue
            
            if first_id is None:
                first_id = stmt_id
            
            if prev_id is not None:
                self.mermaid_lines.append(f"    {prev_id} --> {stmt_id}")
            
            prev_id = stmt_id
        
        return {'first': first_id, 'last': prev_id} if first_id else None
    
    def _process_for(self, stmt: ForLoop) -> str:
        """Procesa un ciclo FOR"""
        # Nodo de decisión del loop
        for_id = self._get_next_id("FOR")
        start_text = self._expression_to_text(stmt.start)
        end_text = self._expression_to_text(stmt.end)
        label = self._escape_text(f"{stmt.variable} := {start_text} to {end_text}")
        self.mermaid_lines.append(f"    {for_id}{{{label}}}")
        
        # Procesar el cuerpo del loop
        body_ids = self._process_block_statements(stmt.body)
        
        if body_ids:
            # Nodo de incremento
            incr_id = self._get_next_id("INCR")
            incr_label = self._escape_text(f"{stmt.variable} := {stmt.variable} + 1")
            self.mermaid_lines.append(f"    {incr_id}[{incr_label}]")
            
            # Conexiones: FOR -> Body -> Incremento -> FOR
            self.mermaid_lines.append(f"    {for_id} -->|{self._escape_text(f'{stmt.variable} ≤ {end_text}')}| {body_ids['first']}")
            self.mermaid_lines.append(f"    {body_ids['last']} --> {incr_id}")
            self.mermaid_lines.append(f"    {incr_id} --> {for_id}")
        
        # El FOR retorna su ID y el código que lo llama decidirá qué hacer con la salida
        return for_id
    
    def _process_while(self, stmt: WhileLoop) -> str:
        """Procesa un ciclo WHILE"""
        # Nodo de decisión
        while_id = self._get_next_id("WHILE")
        condition_text = self._expression_to_text(stmt.condition)
        label = self._escape_text(condition_text)
        self.mermaid_lines.append(f"    {while_id}{{{label}}}")
        
        # Procesar el cuerpo
        body_ids = self._process_block_statements(stmt.body)
        
        if body_ids:
            # Conexiones: WHILE -> Body -> WHILE
            self.mermaid_lines.append(f"    {while_id} -->|True| {body_ids['first']}")
            self.mermaid_lines.append(f"    {body_ids['last']} --> {while_id}")
        
        # NO conectar salida aquí - se conectará automáticamente
        return while_id
        
    def _process_repeat(self, stmt: RepeatLoop) -> str:
        """Procesa un ciclo REPEAT"""
        # El REPEAT ejecuta el cuerpo primero, luego evalúa
        first_id = None
        prev_id = None
        
        # Procesar cuerpo
        if stmt.body:
            for s in stmt.body:
                s_id = self._process_statement(s)
                if s_id is None:
                    continue
                
                if first_id is None:
                    first_id = s_id
                
                if prev_id is not None:
                    self.mermaid_lines.append(f"    {prev_id} --> {s_id}")
                
                prev_id = s_id
            
            # Nodo de decisión al final
            repeat_cond_id = self._get_next_id("REPEAT")
            condition_text = self._expression_to_text(stmt.condition)
            label = self._escape_text(condition_text + "?")
            self.mermaid_lines.append(f"    {repeat_cond_id}{{{label}}}")
            
            # Conectar último statement del body a la condición
            if prev_id:
                self.mermaid_lines.append(f"    {prev_id} --> {repeat_cond_id}")
            
            # Si condición es False, repetir
            self.mermaid_lines.append(f"    {repeat_cond_id} -->|False| {first_id}")
            
            # Si condición es True, NO conectar aquí - se conectará automáticamente
            # Retornar el ID de la condición para que el siguiente statement se conecte
            return repeat_cond_id
        
        # Si no hay body, crear nodo placeholder
        empty_id = self._get_next_id("REPEAT")
        self.mermaid_lines.append(f"    {empty_id}[ ]")
        return empty_id
    
    def _process_call(self, stmt: CallStatement) -> str:
        """Procesa una llamada a función"""
        call_id = self._get_next_id("CALL")
        args_text = ", ".join([self._expression_to_text(arg) for arg in stmt.arguments])
        label = self._escape_text(f"call {stmt.function_name}({args_text})")
        self.mermaid_lines.append(f"    {call_id}[{label}]")
        return call_id
    
    def _process_return(self, stmt: ReturnStatement) -> str:
        """Procesa un return"""
        ret_id = self._get_next_id("RET")
        val_text = self._expression_to_text(stmt.value)
        label = self._escape_text(f"return {val_text}")
        self.mermaid_lines.append(f"    {ret_id}[{label}]")
        return ret_id
    
    def _expression_to_text(self, expr: Expression) -> str:
        """
        Convierte una expresión a texto legible
        
        Args:
            expr: Expresión a convertir
            
        Returns:
            str: Representación en texto de la expresión
        """
        if isinstance(expr, Number):
            return str(expr.value)
        
        elif isinstance(expr, Boolean):
            return "T" if expr.value else "F"
        
        elif isinstance(expr, Null):
            return "NULL"
        
        elif isinstance(expr, Variable):
            text = expr.name
            if expr.indices:
                indices_text = "][".join([self._expression_to_text(idx) for idx in expr.indices])
                text += f"[{indices_text}]"
            if expr.field:
                text += f".{expr.field}"
            if expr.is_range:
                start = self._expression_to_text(expr.range_start)
                end = self._expression_to_text(expr.range_end)
                text += f"[{start}..{end}]"
            return text
        
        elif isinstance(expr, BinaryOp):
            left = self._expression_to_text(expr.left)
            right = self._expression_to_text(expr.right)
            return f"{left} {expr.operator} {right}"
        
        elif isinstance(expr, UnaryOp):
            operand = self._expression_to_text(expr.operand)
            return f"{expr.operator}{operand}"
        
        elif isinstance(expr, FunctionCall):
            args_text = ", ".join([self._expression_to_text(arg) for arg in expr.arguments])
            return f"{expr.function_name}({args_text})"
        
        elif isinstance(expr, Length):
            var_text = self._expression_to_text(expr.variable)
            return f"length({var_text})"
        
        elif isinstance(expr, Ceiling):
            expr_text = self._expression_to_text(expr.expression)
            return f"ceil({expr_text})"
        
        elif isinstance(expr, Floor):
            expr_text = self._expression_to_text(expr.expression)
            return f"floor({expr_text})"
        
        else:
            return str(expr)
    
    def _get_next_id(self, prefix: str = "NODE") -> str:
        """
        Genera ID único para un nodo
        
        Args:
            prefix: Prefijo del ID
            
        Returns:
            str: ID único
        """
        self.node_counter += 1
        return f"{prefix}{self.node_counter}"
    
    def _escape_text(self, text: str) -> str:
        """
        Escapa caracteres especiales para Mermaid
        
        Args:
            text: Texto a escapar
            
        Returns:
            str: Texto escapado entre comillas
        """
        # Escapar corchetes
        text = text.replace('[', r'\[')
        text = text.replace(']', r'\]')
        
        # Escapar comillas
        text = text.replace('"', r'\"')
        
        # Envolver en comillas
        return f'"{text}"'