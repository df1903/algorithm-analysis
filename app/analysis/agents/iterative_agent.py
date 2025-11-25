"""
Agente especializado en análisis de complejidad de algoritmos ITERATIVOS
"""
from typing import Dict, Any, List
import json


from app.analysis.agents.base_agent import BaseAgent
from app.analysis.schemas_extraction import IterativeExtraction


class IterativeAgent(BaseAgent):
    """
    Agente especializado en analizar algoritmos ITERATIVOS.
    
    Usa tools específicas para loops:
    - analyze_loops: Analiza todos los loops (tipo, bounds, anidamiento)
    - count_operations_in_loop: Cuenta operaciones por iteración
    - detect_conditionals: Para identificar best/worst cases
    """
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Sobrescribe para exponer solo tools relevantes para iteración.
        
        Returns:
            Lista de tools específicas para algoritmos iterativos
        """
        all_tools = super().get_tool_definitions()
        
        # Solo incluir tools relevantes para iterativos
        relevant_tools = [
            "analyze_loops",
            "count_operations_in_loop",
            "detect_conditionals"
        ]
        
        return [tool for tool in all_tools if tool["name"] in relevant_tools]
    
    def build_prompt(self, ast_node: Dict[str, Any], subroutine_name: str) -> str:
        """
        Construye el prompt especializado para análisis iterativo.
        
        Args:
            ast_node: Nodo AST de la subrutina iterativa
            subroutine_name: Nombre de la subrutina
            
        Returns:
            Prompt estructurado para Claude
        """
        prompt = f"""
Eres un experto en análisis de complejidad de algoritmos ITERATIVOS.

Tu tarea es analizar la siguiente función iterativa y extraer las funciones de eficiencia (sumatorias) para los casos:
- Best case (mejor caso)
- Worst case (peor caso)  
- Average case (caso promedio)

**IMPORTANTE:** NO resuelvas las sumatorias. Solo EXTRÁELAS del código.

**AST de la función:**
```json
{json.dumps(ast_node, indent=2, ensure_ascii=False)}
```

**Nombre de la función:** {subroutine_name}

**Tools disponibles:**
Tienes acceso a las siguientes tools para analizar el AST con precisión:

1. `analyze_loops(subroutine)` 
   - Analiza todos los loops en el algoritmo
   - Retorna: tipo (FOR/WHILE/REPEAT), bounds (inicio, fin), nivel de anidamiento

2. `count_operations_in_loop(loop_body)`
   - Cuenta operaciones dentro de un loop
   - Retorna: número de operaciones por iteración

3. `detect_conditionals(subroutine)`
   - Detecta IFs que pueden generar diferentes casos
   - Retorna: condiciones, posiciones

**Instrucciones:**

1. USA las tools para analizar el AST (no adivines del JSON)

2. Para cada loop:
   - Identifica el rango: de dónde a dónde itera (ej: i=1 to n)
   - Identifica cuántas operaciones hay por iteración
   - Si hay loops anidados, construye sumatorias anidadas

3. Para cada caso (best/worst/average):
   - Si hay condicionales (IF), determina cuándo se ejecuta más/menos código
   - Construye la sumatoria que representa el trabajo total
   - Formato: Σ(i=inicio to fin) costo_por_iteracion

4. Si NO hay diferencia entre casos (misma sumatoria para todos), usa la misma

5. Retorna un JSON con esta estructura EXACTA:
```json
{{
  "best_case": {{
    "function": "Σ(...) o expresión matemática",
    "description": "Breve explicación de cuándo ocurre este caso"
  }},
  "worst_case": {{
    "function": "Σ(...) o expresión matemática",
    "description": "Breve explicación de cuándo ocurre este caso"
  }},
  "average_case": {{
    "function": "Σ(...) o expresión matemática",
    "description": "Breve explicación de cuándo ocurre este caso"
  }}
}}
```

**Ejemplos de funciones que debes extraer:**

- Loop simple: Σ(i=1 to n) O(1) 
- Loops anidados: Σ(i=1 to n) Σ(j=1 to i) O(1)
- Loop con condición: 
  - Best: Σ(i=1 to n) O(1)  (no entra al IF)
  - Worst: Σ(i=1 to n) O(n)  (siempre entra al IF con loop interno)
- Loop logarítmico: Σ(i=1 to log(n)) O(1)  (cuando i *= 2)

**Notación:**
- Usa Σ() para sumatorias
- Usa O(1), O(n), O(log n) para representar costos
- Si el bound del loop es variable (ej: j=1 to i), menciónalo en la sumatoria

**RECUERDA:** Solo extrae las sumatorias. NO las resuelvas. NO calcules la complejidad O(), Ω(), Θ().

Comienza usando las tools para analizar el AST.
"""
        return prompt
    
    def analyze(self, ast_node: Dict[str, Any], subroutine_name: str = "function") -> Dict[str, Any]:
        """
        Analiza un algoritmo iterativo y extrae las funciones de eficiencia.
        
        Args:
            ast_node: Nodo AST de la subrutina iterativa
            subroutine_name: Nombre de la subrutina (opcional)
            
        Returns:
            Diccionario con estructura IterativeExtraction:
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
            max_iterations=5 # Iterativos pueden tener múltiples loops anidados
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

