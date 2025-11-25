"""
Agente especializado en análisis de complejidad de algoritmos RECURSIVOS
"""
from typing import Dict, Any, List
import json


from app.analysis.agents.base_agent import BaseAgent
from app.analysis.schemas_extraction import RecursiveExtraction


class RecursiveAgent(BaseAgent):
    """
    Agente especializado en analizar algoritmos RECURSIVOS.
    
    Usa tools específicas para recursión:
    - find_recursive_calls: Encuentra llamadas recursivas
    - detect_base_case: Detecta el caso base
    - analyze_recursion_parameter: Analiza cómo se reduce el parámetro
    - detect_conditionals: Para identificar best/worst cases
    """
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Sobrescribe para exponer solo tools relevantes para recursión.
        
        Returns:
            Lista de tools específicas para algoritmos recursivos
        """
        all_tools = super().get_tool_definitions()
        
        # Solo incluir tools relevantes para recursión
        relevant_tools = [
            "find_recursive_calls",
            "detect_base_case",
            "analyze_recursion_parameter",
            "detect_conditionals"
        ]
        
        return [tool for tool in all_tools if tool["name"] in relevant_tools]
    
    def build_prompt(self, ast_node: Dict[str, Any], subroutine_name: str) -> str:
        """
        Construye el prompt especializado para análisis recursivo.
        
        Args:
            ast_node: Nodo AST de la subrutina recursiva
            subroutine_name: Nombre de la subrutina
            
        Returns:
            Prompt estructurado para Claude
        """
        prompt = f"""
Eres un experto en análisis de complejidad de algoritmos RECURSIVOS.

Tu tarea es analizar la siguiente función recursiva y extraer las ecuaciones de recurrencia para los casos:
- Best case (mejor caso)
- Worst case (peor caso)  
- Average case (caso promedio)

**IMPORTANTE:** NO resuelvas las ecuaciones. Solo EXTRÁELAS del código.

**AST de la función:**
```json
{json.dumps(ast_node, indent=2, ensure_ascii=False)}
```

**Nombre de la función:** {subroutine_name}

**Tools disponibles:**
Tienes acceso a las siguientes tools para analizar el AST con precisión:

1. `find_recursive_calls(subroutine)` 
   - Encuentra todas las llamadas recursivas
   - Retorna: número de llamadas, posiciones, argumentos

2. `detect_base_case(subroutine)`
   - Detecta el caso base (condición de parada)
   - Retorna: condición, valor de retorno, posición

3. `analyze_recursion_parameter(subroutine, param_name)`
   - Analiza cómo se reduce el parámetro
   - Retorna: patrón (n-1, n/2, n/b), factor de reducción

4. `detect_conditionals(subroutine)`
   - Detecta IFs que pueden generar diferentes casos
   - Retorna: condiciones, qué caminos tienen recursión

**Instrucciones:**

1. USA las tools para analizar el AST (no adivines del JSON)
2. Identifica el caso base: T(0) = ? o T(1) = ?
3. Para cada caso (best/worst/average):
   - Identifica cuántas llamadas recursivas hay
   - Identifica el parámetro de reducción (n-1, n/2, etc.)
   - Identifica el trabajo adicional f(n)
   - Construye la ecuación: T(n) = a*T(n/b) + f(n)

4. Si NO hay diferencia entre casos (misma ecuación para todos), usa la misma ecuación

5. Retorna un JSON con esta estructura EXACTA:
```json
{{
  "best_case": {{
    "function": "T(n) = ...",
    "base_case": "T(0) = ... o T(1) = ...",
    "description": "Breve explicación de cuándo ocurre este caso"
  }},
  "worst_case": {{
    "function": "T(n) = ...",
    "base_case": "T(0) = ... o T(1) = ...",
    "description": "Breve explicación de cuándo ocurre este caso"
  }},
  "average_case": {{
    "function": "T(n) = ...",
    "base_case": "T(0) = ... o T(1) = ...",
    "description": "Breve explicación de cuándo ocurre este caso"
  }}
}}
```

**Ejemplos de ecuaciones que debes extraer:**

- Factorial: T(n) = T(n-1) + O(1), T(0) = O(1)
- Fibonacci recursivo: T(n) = T(n-1) + T(n-2) + O(1), T(0) = T(1) = O(1)
- Merge Sort: T(n) = 2T(n/2) + O(n), T(1) = O(1)
- Binary Search: T(n) = T(n/2) + O(1), T(1) = O(1)

**RECUERDA:** Solo extrae las ecuaciones. NO las resuelvas. NO calcules la complejidad O(), Ω(), Θ().

Comienza usando las tools para analizar el AST.
"""
        return prompt
    
    def analyze(self, ast_node: Dict[str, Any], subroutine_name: str = "function") -> Dict[str, Any]:
        """
        Analiza un algoritmo recursivo y extrae las ecuaciones de recurrencia.
        
        Args:
            ast_node: Nodo AST de la subrutina recursiva
            subroutine_name: Nombre de la subrutina (opcional)
            
        Returns:
            Diccionario con estructura RecursiveExtraction:
            {
                "best_case": {...},
                "worst_case": {...},
                "average_case": {...}
            }
        """
        # Construir prompt
        prompt = self.build_prompt(ast_node, subroutine_name)
        
        # Ejecutar loop con tools
        result = self.run_with_tool_loop(
            initial_prompt=prompt,
            max_iterations=5  # Recursivos pueden necesitar más iteraciones
        )
        
        if not result["success"]:
            return {
                "error": result.get("error", "Unknown error"),
                "iterations": result.get("iterations", 0)
            }
        
        # Parsear respuesta de Claude
        try:
            # Claude debería retornar JSON
            response_text = result["response"]
            
            # Intentar extraer JSON de la respuesta
            
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                # Asumir que toda la respuesta es JSON
                json_text = response_text.strip()
            
            # Parsear JSON
            extraction = json.loads(json_text)
            
            return {
                "success": True,
                "extraction": extraction,
                "iterations": result["iterations"],
                "raw_response": response_text
            }
            
        except json.JSONDecodeError as e:
            return {
                "error": f"No se pudo parsear la respuesta como JSON: {e}",
                "raw_response": result["response"],
                "iterations": result["iterations"]
            }

