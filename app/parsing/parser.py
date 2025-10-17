"""
Parser: Parsea pseudocódigo usando Lark.

Este módulo se encarga únicamente de:
1. Cargar la gramática desde pseudocode.lark
2. Crear el parser de Lark
3. Parsear código y retornar el árbol sintáctico

NO se encarga de transformar el árbol a objetos Python.
Esa es responsabilidad del transformer.py
"""

from lark import Lark
import os


class PseudocodeParser:
    """
    Parser de pseudocódigo que usa Lark.
    
    Responsabilidades:
    - Cargar la gramática desde el archivo .lark
    - Crear y configurar el parser de Lark
    - Parsear código y retornar árboles sintácticos
    
    """
    
    def __init__(self, grammar_path: str = None):
        """
        Inicializa el parser.
        
        Args:
            grammar_path: Ruta al archivo .lark. Si es None, usa la ruta por defecto.
        """
        if grammar_path is None:
            # Ruta por defecto (relativa a este archivo)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            grammar_path = os.path.join(current_dir, 'grammar', 'pseudocode.lark')
        
        self.grammar_path = grammar_path
        self.parser = self._create_parser()
    
    def _create_parser(self):
        """
        Crea el parser de Lark cargando la gramática.
        
        Returns:
            Lark: Parser configurado
        """
        # Cargar gramática
        with open(self.grammar_path, 'r', encoding='utf-8') as f:
            grammar = f.read()
        
        # Crear parser con configuración óptima
        parser = Lark(
            grammar,
            start='start',      # Punto de inicio de la gramática
            parser='lalr',      # Algoritmo LALR (más rápido)
            propagate_positions=True,  # Para rastrear líneas (debugging)
            maybe_placeholders=False   # Desactivar placeholders
        )
        
        return parser
    
    def parse(self, code: str):
        """
        Parsea código pseudocódigo y retorna el árbol sintáctico.
        
        Args:
            code: Código en pseudocódigo (string)
        
        Returns:
            Tree: Árbol sintáctico de Lark
        
        Raises:
            lark.exceptions.LarkError: Si hay error de sintaxis
        """
        return self.parser.parse(code)
    
    def parse_file(self, filepath: str):
        """
        Lee y parsea un archivo de pseudocódigo.
        
        Args:
            filepath: Ruta al archivo .txt o .pseudo
        
        Returns:
            Tree: Árbol sintáctico de Lark
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        
        return self.parse(code)


# ============================================================================
# FUNCIÓN DE CONVENIENCIA
# ============================================================================

def parse_pseudocode(code: str, grammar_path: str = None):
    """
    Función de conveniencia para parsear pseudocódigo rápidamente.
    
    Args:
        code: Código en pseudocódigo
        grammar_path: Ruta opcional a la gramática
    
    Returns:
        Tree: Árbol sintáctico de Lark
    
    Example:
        >>> tree = parse_pseudocode("begin x := 5 end")
        >>> print(tree.pretty())
    """
    parser = PseudocodeParser(grammar_path)
    return parser.parse(code)