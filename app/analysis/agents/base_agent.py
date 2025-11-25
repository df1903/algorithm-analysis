"""
Agente Base para análisis de complejidad usando Claude API + Tools
"""
from anthropic import Anthropic
from typing import Dict, Any, List, Optional
import os
import json
from dotenv import load_dotenv

# Importe de tools
try:
    from app.analysis.tools.ast_analyzer import (
        find_recursive_calls,
        detect_base_case,
        analyze_recursion_parameter,
        analyze_loops,
        count_operations_in_loop,
        detect_conditionals
    )
except ImportError as e:
    print(f" Warning: No se pudieron importar las tools de ast_analyzer: {e}")
    # Definir errores si falla
    find_recursive_calls = lambda x: {"error": "Tool not available"}
    detect_base_case = lambda x: {"error": "Tool not available"}
    analyze_recursion_parameter = lambda x, y: {"error": "Tool not available"}
    analyze_loops = lambda x: {"error": "Tool not available"}
    count_operations_in_loop = lambda x: {"error": "Tool not available"}
    detect_conditionals = lambda x: {"error": "Tool not available"}


class BaseAgent:
    """
    Agente base que maneja la interacción con Claude API + Tools.
    Los agentes especializados heredan de esta clase.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el agente con la API key de Anthropic.
        
        Args:
            api_key: API key de Anthropic. Si no se provee, busca en variable de entorno.
        """
        load_dotenv()
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Se requiere API key de Anthropic. "
                "Provéela como argumento o en variable de entorno ANTHROPIC_API_KEY"
            )
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"
        
        # Mapeo de nombres de tools a funciones Python
        self.tool_functions = {
            "find_recursive_calls": find_recursive_calls,
            "detect_base_case": detect_base_case,
            "analyze_recursion_parameter": analyze_recursion_parameter,
            "analyze_loops": analyze_loops,
            "count_operations_in_loop": count_operations_in_loop,
            "detect_conditionals": detect_conditionals
        }
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Define las tools disponibles para Claude en formato Anthropic API.
        Subclases pueden sobrescribir para limitar tools específicas.
        
        Returns:
            Lista de definiciones de tools en formato JSON Schema
        """
        return [
            {
                "name": "find_recursive_calls",
                "description": (
                    "Encuentra todas las llamadas recursivas en una subrutina. "
                    "Retorna el número de llamadas, posiciones y argumentos usados."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "subroutine": {
                            "type": "object",
                            "description": "Objeto AST de la subrutina a analizar"
                        }
                    },
                    "required": ["subroutine"]
                }
            },
            {
                "name": "detect_base_case",
                "description": (
                    "Detecta el caso base en una función recursiva. "
                    "Retorna la condición del caso base, el valor de retorno y su posición."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "subroutine": {
                            "type": "object",
                            "description": "Objeto AST de la subrutina a analizar"
                        }
                    },
                    "required": ["subroutine"]
                }
            },
            {
                "name": "analyze_recursion_parameter",
                "description": (
                    "Analiza cómo se reduce el parámetro en las llamadas recursivas. "
                    "Identifica patrones como n-1, n/2, n-k, etc."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "subroutine": {
                            "type": "object",
                            "description": "Objeto AST de la subrutina"
                        },
                        "param_name": {
                            "type": "string",
                            "description": "Nombre del parámetro a analizar (ej: 'n')"
                        }
                    },
                    "required": ["subroutine", "param_name"]
                }
            },
            {
                "name": "analyze_loops",
                "description": (
                    "Analiza todos los loops en un algoritmo. "
                    "Retorna tipo, bounds, nivel de anidamiento de cada loop."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "subroutine": {
                            "type": "object",
                            "description": "Objeto AST de la subrutina"
                        }
                    },
                    "required": ["subroutine"]
                }
            },
            {
                "name": "count_operations_in_loop",
                "description": (
                    "Cuenta el número de operaciones dentro de un loop. "
                    "Útil para determinar el costo por iteración."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "loop_body": {
                            "type": "array",
                            "description": "Lista de statements dentro del loop"
                        }
                    },
                    "required": ["loop_body"]
                }
            },
            {
                "name": "detect_conditionals",
                "description": (
                    "Detecta condicionales (IF) en el algoritmo. "
                    "Útil para identificar casos best/worst/average diferentes."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "subroutine": {
                            "type": "object",
                            "description": "Objeto AST de la subrutina"
                        }
                    },
                    "required": ["subroutine"]
                }
            }
        ]
    
    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """
        Ejecuta una tool localmente.
        
        Args:
            tool_name: Nombre de la tool a ejecutar
            tool_input: Argumentos para la tool
            
        Returns:
            Resultado de ejecutar la tool
        """
        if tool_name not in self.tool_functions:
            raise ValueError(f"Tool desconocida: {tool_name}")
        
        tool_func = self.tool_functions[tool_name]
        
        try:
            result = tool_func(**tool_input)
            return result
        except Exception as e:
            return {
                "error": str(e),
                "tool": tool_name,
                "input": tool_input
            }
    
    def call_claude(
        self,
        messages: List[Dict[str, Any]],
        max_tokens: int = 8000,
        temperature: float = 0.0
    ) -> Dict[str, Any]:
        """
        Llama a Claude API con tools disponibles.
        
        Args:
            messages: Lista de mensajes (conversación)
            max_tokens: Máximo de tokens en la respuesta
            temperature: Temperatura del modelo (0 = determinista)
            
        Returns:
            Respuesta completa de Claude API
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            tools=self.get_tool_definitions(),
            messages=messages
        )
        
        return response
    
    def run_with_tool_loop(
        self,
        initial_prompt: str,
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Ejecuta el loop completo: Claude → Tool → Claude → ...
        
        Args:
            initial_prompt: Prompt inicial para Claude  
            max_iterations: Máximo de iteraciones
            
        Returns:
            Respuesta final de Claude después de usar todas las tools necesarias
        """
        
        messages = [{"role": "user", "content": initial_prompt}]
        
        for iteration in range(max_iterations):
            # Llamar a Claude
            response = self.call_claude(messages)
            
            # Verificar si Claude terminó 
            if response.stop_reason == "end_turn":
                # Claude terminó, extraer respuesta final
                final_text = ""
                for content_block in response.content:
                    if content_block.type == "text":
                        final_text += content_block.text
                
                return {
                    "success": True,
                    "response": final_text,
                    "iterations": iteration + 1
                }
            
            # Claude pidió usar una tool
            if response.stop_reason == "tool_use":
                # Agregar respuesta de Claude a mensajes
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })
                
                # Ejecutar todas las tools que Claude pidió
                tool_results = []
                
                for content_block in response.content:
                    if content_block.type == "tool_use":
                        tool_name = content_block.name
                        tool_input = content_block.input
                        tool_id = content_block.id
                        
                        # Ejecutar tool localmente
                        tool_result = self.execute_tool(tool_name, tool_input)
                        
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": json.dumps(tool_result, ensure_ascii=False)
                        })
                
                # Agregar resultados de tools a mensajes
                messages.append({
                    "role": "user",
                    "content": tool_results
                })
                
                # Continuar el loop 
                continue
            
            # return de error inesperado
            return {
                "success": False,
                "error": f"Stop reason inesperado: {response.stop_reason}",
                "iterations": iteration + 1
            }
        
        # return de maximo de iteraciones alcanzado
        return {
            "success": False,
            "error": "Se excedió el máximo de iteraciones",
            "iterations": max_iterations
        }
    
    def analyze(self, ast_node: Dict[str, Any]) -> Dict[str, Any]:
        """
        Método principal que subclases deben implementar.
        
        Args:
            ast_node: Nodo del AST a analizar
            
        Returns:
            Análisis de complejidad según el schema correspondiente
        """
        raise NotImplementedError("Subclases deben implementar el método analyze()")


