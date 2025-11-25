"""
Agente para traducir lenguaje natural → pseudocódigo válido
Usa las reglas de grammar.lark directamente
"""
from anthropic import Anthropic
from typing import Dict, Any
import os
from dotenv import load_dotenv
from app.parsing.parser import parse_pseudocode



class TranslatorAgent:
    """
    Traduce lenguaje natural a pseudocódigo siguiendo grammar.lark
    
    Estrategia:
    1. Extrae reglas de la gramática Lark
    2. Convierte reglas EBNF → instrucciones legibles
    3. Combina con ejemplos (few-shot)
    4. Valida con parser Lark
    """
    
    # REGLAS EXTRAÍDAS DE grammar.lark (convertidas a lenguaje natural)
    GRAMMAR_INSTRUCTIONS = """
GRAMÁTICA COMPLETA (basada en grammar.lark):

═══════════════════════════════════════════════════════════════════
1. ESTRUCTURA GENERAL DEL PROGRAMA
═══════════════════════════════════════════════════════════════════

programa ::= [definiciones_de_clases]* [definiciones_de_subrutinas]* algoritmo_principal

algoritmo_principal ::= 
    begin
        [sentencias]*
    end

definición_de_subrutina ::=
    nombre_subrutina(parámetros)
    begin
        [sentencias]*
    end

═══════════════════════════════════════════════════════════════════
2. DEFINICIÓN DE CLASES (opcional, antes de subrutinas)
═══════════════════════════════════════════════════════════════════

clase ::= NombreClase { atributo1 atributo2 ... }

Ejemplo:
    Casa { area color propietario }

═══════════════════════════════════════════════════════════════════
3. PARÁMETROS DE SUBRUTINAS
═══════════════════════════════════════════════════════════════════

parámetro_array ::= nombre[] 
                 | nombre[n]
                 | nombre[n]..[m]

parámetro_objeto ::= NombreClase nombre_objeto

parámetro_simple ::= nombre

Ejemplos:
    buscar(A[], x, n)
    procesar(matriz[10][10], Casa miCasa, valor)

═══════════════════════════════════════════════════════════════════
4. SENTENCIAS (statements)
═══════════════════════════════════════════════════════════════════

Las siguientes sentencias son válidas:

a) Declaraciones:
   - Arrays: nombre[tamaño]
   - Objetos: NombreClase nombre_objeto
   
   Ejemplos:
   A[100]
   resultado[50]
   Casa miCasa

b) Asignaciones:
   variable := expresión
   
   Ejemplos:
   x := 5
   suma := suma + A[i]
   miCasa.color := "rojo"

c) Loops FOR:
   for variable := inicio to fin do
   begin
       [sentencias]
   end
   
   Ejemplo:
   for i := 1 to n do
   begin
       suma := suma + A[i]
   end

d) Loops WHILE:
   while (condición) do
   begin
       [sentencias]
   end
   
   Ejemplo:
   while (i < n) do
   begin
       i := i + 1
   end

e) Loops REPEAT:
   repeat
       [sentencias]
   until (condición)
   
   Ejemplo:
   repeat
       i := i + 1
   until (i >= n)

f) Condicionales IF:
   if (condición) then
   begin
       [sentencias]
   end
   else
   begin
       [sentencias]
   end
   
   Nota: El else es opcional
   
   Ejemplo:
   if (x = 0) then
   begin
       return 1
   end
   else
   begin
       return x * factorial(x - 1)
   end

g) Llamadas a subrutinas:
   call nombre_subrutina(argumentos)
   
   O para asignar resultado:
   variable := nombre_subrutina(argumentos)
   
   Ejemplos:
   call quicksort(A, 1, n)
   resultado := buscar(A, x, n)

h) Return:
   return expresión
   
   Ejemplo:
   return A[i]

i) Comentarios:
   ► texto del comentario
   
   Ejemplo:
   ► Este es un comentario

═══════════════════════════════════════════════════════════════════
5. OPERADORES
═══════════════════════════════════════════════════════════════════

ASIGNACIÓN:
    := (OBLIGATORIO, no usar =)

COMPARACIÓN (en condiciones):
    =   (igual)
    !=  (diferente)  ← Usar != en lugar de <>
    <   (menor)
    >   (mayor)
    <=  (menor o igual)
    >=  (mayor o igual)

ARITMÉTICOS:
    +       (suma)
    -       (resta)
    *       (multiplicación)
    /       (división real)
    div     (división entera, NO usar //)
    mod     (módulo, NO usar %)
    ^       (potencia)

LÓGICOS:
    and     (y lógico)
    or      (o lógico)
    not     (negación)

FUNCIONES ESPECIALES:
    length(A)       (longitud de array)
    ┌expresión┐     (techo/ceiling)
    └expresión┘     (piso/floor)

═══════════════════════════════════════════════════════════════════
6. VARIABLES Y ACCESO A DATOS
═══════════════════════════════════════════════════════════════════

Variables simples:
    x, suma, contador

Arrays:
    A[i]
    matriz[i][j]
    A[1..n]  (rango)

Objetos:
    miCasa.area
    miCasa.color

Arrays de objetos:
    casas[i].area

═══════════════════════════════════════════════════════════════════
7. VALORES ESPECIALES
═══════════════════════════════════════════════════════════════════

Booleanos: T, F, true, false
Nulo: NULL, null
Números: 123, 45.67

═══════════════════════════════════════════════════════════════════
8. BLOQUES
═══════════════════════════════════════════════════════════════════

SIEMPRE usar begin...end para:
- Cuerpo de subrutinas
- Bloques de IF/ELSE
- Cuerpos de loops FOR y WHILE
- Algoritmo principal

Ejemplo correcto:
    if (x > 0) then
    begin
        y := x
    end

Ejemplo INCORRECTO:
    if (x > 0) then
        y := x

═══════════════════════════════════════════════════════════════════
9. REGLAS CRÍTICAS
═══════════════════════════════════════════════════════════════════

HACER:
- Usar := para asignación
- Usar = para comparación
- Usar <> para diferente
- Usar div para división entera
- Usar mod para módulo
- Siempre usar begin...end en bloques
- Terminar con bloque principal begin...end

NO HACER:
- Usar = para asignación (es :=)
- Usar != (es <>)
- Usar == (es =)
- Usar // o / para división entera (es div)
- Usar % para módulo (es mod)
- Omitir begin...end en bloques
- Usar sintaxis de otros lenguajes (Python, C, Java)
"""

    # Ejemplos validados
    VALID_EXAMPLES = """
═══════════════════════════════════════════════════════════════════
EJEMPLOS VALIDADOS
═══════════════════════════════════════════════════════════════════

EJEMPLO 1: Búsqueda Lineal (iterativo con return temprano)
───────────────────────────────────────────────────────────────────
linear_search(A[], x, n)
begin
  for i := 1 to n do
  begin
    if (A[i] = x) then
    begin
      return i
    end
  end
  return -1
end

begin
  A[100]
  resultado := linear_search(A, 42, 100)
end

EJEMPLO 2: Factorial (recursivo simple)
───────────────────────────────────────────────────────────────────
factorial(n)
begin
  if (n = 0) then
  begin
    return 1
  end
  else
  begin
    return n * factorial(n - 1)
  end
end

begin
  resultado := factorial(5)
end

EJEMPLO 3: Búsqueda Binaria (recursivo con múltiples parámetros)
───────────────────────────────────────────────────────────────────
binary_search(A[], x, low, high)
begin
  if (low > high) then
  begin
    return -1
  end
  
  mid := (low + high) div 2
  
  if (A[mid] = x) then
  begin
    return mid
  end
  else
  begin
    if (A[mid] > x) then
    begin
      return binary_search(A, x, low, mid - 1)
    end
    else
    begin
      return binary_search(A, x, mid + 1, high)
    end
  end
end

begin
  A[100]
  resultado := binary_search(A, 42, 1, 100)
end

EJEMPLO 4: Bubble Sort (loops anidados con intercambio)
───────────────────────────────────────────────────────────────────
bubble_sort(A[], n)
begin
  for i := 1 to n do
  begin
    for j := 1 to n - 1 do
    begin
      if (A[j] > A[j + 1]) then
      begin
        temp := A[j]
        A[j] := A[j + 1]
        A[j + 1] := temp
      end
    end
  end
end

begin
  A[100]
  call bubble_sort(A, 100)
end

EJEMPLO 5: Fibonacci (recursión múltiple)
───────────────────────────────────────────────────────────────────
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
  resultado := fibonacci(10)
end

EJEMPLO 6: QuickSort (múltiples subrutinas, recursión)
───────────────────────────────────────────────────────────────────
partition(A[], low, high)
begin
  pivot := A[high]
  i := low - 1
  
  for j := low to high - 1 do
  begin
    if (A[j] <= pivot) then
    begin
      i := i + 1
      temp := A[i]
      A[i] := A[j]
      A[j] := temp
    end
  end
  
  temp := A[i + 1]
  A[i + 1] := A[high]
  A[high] := temp
  
  return i + 1
end

quicksort(A[], low, high)
begin
  if (low < high) then
  begin
    pivot := partition(A, low, high)
    call quicksort(A, low, pivot - 1)
    call quicksort(A, pivot + 1, high)
  end
end

begin
  A[100]
  call quicksort(A, 1, 100)
end
"""

    def __init__(self, api_key: str = None):
        """Inicializa el agente"""
        load_dotenv()
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Se requiere ANTHROPIC_API_KEY")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"
    
    def translate(
        self, 
        description: str, 
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """
        Traduce una descripción en lenguaje natural a pseudocódigo válido
        siguiendo la gramática definida en `grammar.lark`. 
        
        El método:
        1. Construye un prompt usando reglas gramaticales y ejemplos validados.
        2. Llama al modelo de Anthropic para generar pseudocódigo.
        3. Valida la salida usando el parser Lark.
        4. Reintenta hasta `max_retries` veces corrigiendo errores de sintaxis.
        
        Args:
            description (str): Descripción en lenguaje natural del algoritmo.
            max_retries (int): Número máximo de intentos permitidos.
        
        Returns:
            Dict[str, Any]: Diccionario con:
                - success (bool): True si se generó pseudocódigo válido.
                - pseudocode (str): Versión generada.
                - validated (bool): True si pasó el parser Lark.
                - attempts (int): Número de intentos usados.
                - confidence (str): Nivel de confianza (high/medium).
                - error (str, opcional): Mensaje de error si falló.
        
        Raises:
            ValueError: Si falta la API key o si ocurre error grave.
        """
        last_error = None
        last_pseudocode = None
        
        for attempt in range(max_retries):
            # Construir prompt
            prompt = self._build_prompt(description, last_error)
            
            # Generar
            result = self._generate_pseudocode(prompt)
            
            if not result["success"]:
                return result
            
            pseudocode = result["pseudocode"]
            last_pseudocode = pseudocode
            
            # VALIDAR con Lark
            is_valid, error = self._validate_with_lark(pseudocode)
            
            if is_valid:
                return {
                    "success": True,
                    "pseudocode": pseudocode,
                    "validated": True,
                    "attempts": attempt + 1,
                    "confidence": "high" if attempt == 0 else "medium"
                }
            else:
                print(f"Intento {attempt + 1}/{max_retries} falló: {error}")
                last_error = error
        
        return {
            "success": False,
            "error": f"No se pudo generar pseudocódigo válido después de {max_retries} intentos",
            "last_attempt": last_pseudocode,
            "last_error": last_error,
            "validated": False
        }
    
    def _build_prompt(
        self, 
        description: str, 
        previous_error: str = None
    ) -> str:
        """    Construye el prompt completo enviado al modelo, incluyendo:
              - Instrucciones gramaticales
              - Ejemplos validados
              - Instrucciones finales
              - Información de errores pasados (si los hay)

              Args:
                  description (str): Descripción del usuario.
                  previous_error (str, optional): Error del intento previo para que el
                      modelo lo corrija específicamente.

              Returns:
                  str: Prompt ensamblado listo para enviar al modelo."""
        
        error_section = ""
        if previous_error:
            error_section = f"""
  ERROR EN INTENTO ANTERIOR:
{previous_error}

IMPORTANTE: Corrige SOLO el error de sintaxis. La lógica está bien.
"""
        
        prompt = f"""{self.GRAMMAR_INSTRUCTIONS}

{self.VALID_EXAMPLES}

═══════════════════════════════════════════════════════════════════
INSTRUCCIONES FINALES
═══════════════════════════════════════════════════════════════════

1. Lee la descripción del usuario
2. Identifica qué tipo de algoritmo es (recursivo, iterativo, etc.)
3. Genera pseudocódigo siguiendo EXACTAMENTE las reglas de gramática
4. Usa los ejemplos como referencia de estilo
5. VERIFICA que uses := para asignación, = para comparación
6. VERIFICA que todos los bloques tengan begin...end
7. VERIFICA que el programa termine con begin...end principal

{error_section}

DESCRIPCIÓN DEL USUARIO:
{description}

Genera SOLO el pseudocódigo completo y válido. Sin explicaciones adicionales.
"""
        return prompt
    
    def _generate_pseudocode(self, prompt: str) -> Dict[str, Any]:
        """Llama a Claude para generar"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}]
            )
            
            pseudocode = response.content[0].text.strip()
            
            # Limpiar markdown
            if "```" in pseudocode:
                lines = pseudocode.split('\n')
                code_lines = []
                in_code = False
                
                for line in lines:
                    if line.strip().startswith('```'):
                        in_code = not in_code
                        continue
                    if in_code or not any(line.strip().startswith(x) for x in ['```', '#', 'Aquí', 'Este']):
                        code_lines.append(line)
                
                pseudocode = '\n'.join(code_lines).strip()
            
            return {
                "success": True,
                "pseudocode": pseudocode
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error generando: {str(e)}"
            }
    
    def _validate_with_lark(self, pseudocode: str) -> tuple:
        """Valida con tu parser Lark"""
        try:
            ast = parse_pseudocode(pseudocode)
            return True, None
        except Exception as e:
            return False, str(e)