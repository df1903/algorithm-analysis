# Analizador de Complejidades Algorítmicas

Sistema inteligente para el análisis automático de complejidad computacional de algoritmos escritos en pseudocódigo, desarrollado como proyecto académico para la asignatura de Análisis y Diseño de Algoritmos en la Universidad de Caldas.

## Descripción

Este sistema recibe algoritmos escritos en pseudocódigo con sintaxis tipo Pascal, los analiza automáticamente mediante técnicas de parsing y agentes especializados basados en Claude API, y determina su complejidad computacional en las notaciones O (peor caso), Ω (mejor caso) y Θ (caso promedio), incluyendo cotas fuertes.

El proyecto implementa una arquitectura de dos fases:

* **Fase 1 (Extracción):** Transforma el pseudocódigo en ecuaciones matemáticas de complejidad mediante agentes especializados (RecursiveAgent, IterativeAgent)
* **Fase 2 (Resolución):** Resuelve las ecuaciones utilizando técnicas matemáticas avanzadas (Teorema Maestro, método de sustitución, análisis de sumatorias, árboles de recursión)

## Características

* Análisis automático de algoritmos recursivos e iterativos
* Soporte para pseudocódigo con sintaxis Pascal-like (FOR, WHILE, REPEAT, IF-THEN-ELSE)
* Detección inteligente de casos unificados para evitar análisis redundantes
* Sistema de caché con Supabase que reduce costos de API en un 96%
* Generación de diagramas de flujo Mermaid para visualización algorítmica
* Traducción de lenguaje natural a pseudocódigo estructurado
* API REST con FastAPI para integración con aplicaciones externas

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                         ENTRADA                                  │
│   Pseudocódigo / Lenguaje Natural                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CAPA DE PARSING                               │
│   ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐   │
│   │ Lark Parser │ →  │ Transformer  │ →  │ AST Serializer  │   │
│   │ (grammar)   │    │ (AST nodes)  │    │ (JSON output)   │   │
│   └─────────────┘    └──────────────┘    └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 CAPA DE CLASIFICACIÓN                            │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                   AlgorithmClassifier                     │  │
│   │  - Detecta tipo: RECURSIVE / ITERATIVE / HYBRID          │  │
│   │  - Cuenta llamadas recursivas                             │  │
│   │  - Mide nivel de anidamiento de loops                     │  │
│   │  - Identifica paradigma algorítmico                       │  │
│   └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 CAPA DE ORQUESTACIÓN                             │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                 AnalysisOrchestrator                      │  │
│   │  1. Verifica caché (Supabase)                             │  │
│   │  2. Selecciona agente según clasificación                 │  │
│   │  3. Detecta casos unificados vs diferentes                │  │
│   │  4. Coordina Fase 1 → Fase 2                              │  │
│   │  5. Guarda resultados en caché                            │  │
│   └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┴─────────────────┐
            ▼                                   ▼
┌───────────────────────┐           ┌───────────────────────┐
│  FASE 1: EXTRACCIÓN   │           │  FASE 2: RESOLUCIÓN   │
│                       │           │                       │
│  RecursiveAgent       │           │  ResolverAgent        │
│  - Claude API         │     →     │  - Claude API         │
│  - Tools de análisis  │           │  - Tools matemáticas  │
│                       │           │                       │
│  IterativeAgent       │           │  4 técnicas:          │
│  - Claude API         │           │  - Teorema Maestro    │
│  - Tools de loops     │           │  - Sustitución        │
│                       │           │  - Sumatorias         │
│  OUTPUT: Ecuación     │           │  - Árbol de recursión │
│  T(n) = 2T(n/2) + n   │           │                       │
└───────────────────────┘           │  OUTPUT: O, Ω, Θ      │
                                    │  Θ(n log n)           │
                                    └───────────────────────┘
```

## Requisitos

### Software

* Python 3.10 o superior
* pip (gestor de paquetes de Python)
* Git

### Servicios Externos

* Cuenta de Anthropic con API Key para Claude
* Cuenta de Supabase (opcional, para sistema de caché)

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/df1903/algorithm-analysis.git
cd algorithm-analysis
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# API de Anthropic (requerido)
ANTHROPIC_API_KEY=sk-ant-api03-...

# Supabase (opcional, para caché)
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 5. Configurar Supabase (opcional)

Si se desea utilizar el sistema de caché, crear la tabla `algorithms_cache` en Supabase con la siguiente estructura:

```sql
CREATE TABLE algorithms_cache (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    pseudocode_hash TEXT UNIQUE NOT NULL,
    pseudocode TEXT NOT NULL,
    natural_description TEXT,
    algorithm_name TEXT,
    algorithm_type TEXT,
    has_different_cases BOOLEAN,
    unified_function TEXT,
    unified_explanation TEXT,
    best_case_function TEXT,
    best_case_explanation TEXT,
    worst_case_function TEXT,
    worst_case_explanation TEXT,
    average_case_function TEXT,
    average_case_explanation TEXT,
    unified_resolved JSONB,
    best_case_resolved JSONB,
    worst_case_resolved JSONB,
    average_case_resolved JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    times_requested INTEGER DEFAULT 1,
    api_cost_usd NUMERIC
);
```

### 6. Ejecutar el servidor

```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en `http://127.0.0.1:8000`

## Uso de la API

### Endpoints Disponibles

| Endpoint                            | Método | Descripción                                          |
| ----------------------------------- | ------- | ----------------------------------------------------- |
| `/analyzer/ast`                   | POST    | Analiza pseudocódigo y retorna complejidad completa  |
| `/analyzer/natural-to-pseudocode` | POST    | Traduce lenguaje natural a pseudocódigo y lo analiza |
| `/analyzer/`                      | GET     | Verifica estado del servicio                          |

### Ejemplo: Análisis de Pseudocódigo

**Request:**

```bash
POST /analyzer/ast
Content-Type: application/json

{
  "text": "factorial(n)\nbegin\n  if (n = 0) then\n  begin\n    return 1\n  end\n  else\n  begin\n    return n * factorial(n - 1)\n  end\nend\n\nbegin\n  resultado := factorial(5)\nend"
}
```

**Response:**

```json
{
  "ast": { ... },
  "classification": {
    "subroutines": [{
      "name": "factorial",
      "type": "RECURSIVE",
      "recursive_calls_count": 1,
      "max_loop_nesting": 0
    }]
  },
  "analysis": {
    "algorithm_name": "factorial",
    "algorithm_type": "RECURSIVE",
    "has_different_cases": false,
    "unified_case": {
      "function": "T(n) = T(n-1) + O(1)",
      "applies_to": ["best", "worst", "average"],
      "explanation": "El factorial siempre hace exactamente n llamadas recursivas..."
    }
  },
  "resolution": {
    "unified_case": {
      "O": "O(n)",
      "Omega": "Ω(n)",
      "Theta": "Θ(n)",
      "is_tight_bound": true,
      "method": "sustitucion",
      "steps": [
        "Expandir T(n) = T(n-1) + O(1)",
        "T(n) = T(n-2) + O(1) + O(1)",
        "Patrón detectado: T(n) = T(0) + n × O(1)",
        "Resultado: T(n) = Θ(n)"
      ]
    }
  }
}
```

### Ejemplo: Lenguaje Natural a Análisis

**Request:**

```bash
POST /analyzer/natural-to-pseudocode
Content-Type: application/json

{
  "description": "Crea una función que busque un elemento en un array ordenado dividiendo el espacio a la mitad"
}
```

**Response:**

```json
{
  "pseudocode": "binary_search(A[], x, low, high)\nbegin\n  if (low > high) then\n  begin\n    return -1\n  end\n  mid := (low + high) div 2\n  if (A[mid] = x) then\n  begin\n    return mid\n  end\n  else\n  begin\n    if (A[mid] > x) then\n    begin\n      return binary_search(A, x, low, mid - 1)\n    end\n    else\n    begin\n      return binary_search(A, x, mid + 1, high)\n    end\n  end\nend",
  "validated": true,
  "attempts": 1,
  "confidence": "high",
  "analysis": { ... },
  "resolution": { ... }
}
```

## Sintaxis del Pseudocódigo

El sistema acepta pseudocódigo con sintaxis tipo Pascal según las convenciones definidas:

### Estructuras de Control

```pascal
// Ciclo FOR
for i := 1 to n do
begin
  // acciones
end

// Ciclo WHILE
while (condicion) do
begin
  // acciones
end

// Ciclo REPEAT
repeat
  // acciones
until (condicion)

// Condicional IF
if (condicion) then
begin
  // acciones
end
else
begin
  // acciones alternativas
end
```

### Asignación y Operadores

```pascal
// Asignación
variable := valor

// Operadores matemáticos
+ - * / mod div

// Operadores relacionales
< > <= >= = !=

// Operadores booleanos
and or not

// Valores booleanos
T F
```

### Arrays y Objetos

```pascal
// Declaración de array
A[100]
A[1..n]

// Acceso a elementos
A[i]
A[1..j]

// Objetos (declarar clase antes del algoritmo)
Casa {area color propietario}
Casa miCasa
miCasa.area := 100
```

### Subrutinas

```pascal
// Definición
nombre_subrutina(param1, param2, arreglo[])
begin
  // acciones
  return valor
end

// Llamada
call nombre_subrutina(arg1, arg2, A)
resultado := nombre_subrutina(arg1, arg2, A)
```

## Algoritmos de Prueba Validados

El sistema ha sido probado y validado con los siguientes algoritmos:

| #  | Algoritmo       | Tipo      | Casos      | Complejidad                      |
| -- | --------------- | --------- | ---------- | -------------------------------- |
| 1  | Factorial       | Recursivo | Unificado  | Θ(n)                            |
| 2  | Fibonacci       | Recursivo | Unificado  | Θ(2ⁿ)                          |
| 3  | Binary Search   | Recursivo | Diferentes | O(log n), Ω(1)                  |
| 4  | Merge Sort      | Recursivo | Unificado  | Θ(n log n)                      |
| 5  | Quick Sort      | Recursivo | Diferentes | O(n²), Ω(n log n), Θ(n log n) |
| 6  | Potencia        | Recursivo | Unificado  | Θ(log n)                        |
| 7  | Torres de Hanoi | Recursivo | Unificado  | Θ(2ⁿ)                          |
| 8  | Linear Search   | Iterativo | Diferentes | O(n), Ω(1)                      |
| 9  | Bubble Sort     | Iterativo | Unificado  | Θ(n²)                          |
| 10 | Selection Sort  | Iterativo | Unificado  | Θ(n²)                          |
| 11 | Insertion Sort  | Iterativo | Diferentes | O(n²), Ω(n)                    |

## Técnicas Matemáticas Implementadas

### 1. Teorema Maestro

Para recurrencias de la forma `T(n) = aT(n/b) + f(n)`:

* **Caso 1:** Si f(n) = O(n^(log_b(a) - ε)), entonces T(n) = Θ(n^log_b(a))
* **Caso 2:** Si f(n) = Θ(n^log_b(a)), entonces T(n) = Θ(n^log_b(a) × log n)
* **Caso 3:** Si f(n) = Ω(n^(log_b(a) + ε)), entonces T(n) = Θ(f(n))

### 2. Método de Sustitución

Para recurrencias lineales `T(n) = T(n-k) + f(n)`:

1. Expandir iterativamente la recurrencia
2. Detectar el patrón de expansión
3. Calcular el número total de operaciones

### 3. Análisis de Sumatorias

Para algoritmos iterativos con loops:

* Sumatorias constantes: Σ(i=1 to n) c = c × n
* Sumatorias lineales: Σ(i=1 to n) i = n(n+1)/2
* Sumatorias anidadas: Σ(i=1 to n) Σ(j=1 to n) 1 = n²

### 4. Árbol de Recursión

Para visualizar el trabajo en cada nivel de la recursión:

* Calcula nodos por nivel
* Suma el trabajo de cada nivel
* Determina la altura del árbol
* Calcula el costo total

## Optimizaciones Implementadas

### Sistema de Caché con Supabase

El sistema implementa caché persistente que:

* Genera hash SHA256 del pseudocódigo normalizado
* Almacena resultados de análisis en base de datos
* Retorna resultados instantáneos para algoritmos previamente analizados
* Reduce costos de API en aproximadamente 96%

**Flujo de caché:**

```
Pseudocódigo → Hash SHA256 → Buscar en BD
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
              CACHÉ HIT                       CACHÉ MISS
              (existe)                        (no existe)
                    │                               │
                    ▼                               ▼
              Retornar                      Analizar con Claude
              resultado                            │
              (<1 seg)                             ▼
                                            Guardar en BD
                                                   │
                                                   ▼
                                            Retornar resultado
```

### Detección de Casos Unificados

El sistema detecta automáticamente cuando el mejor, peor y caso promedio son idénticos, evitando análisis redundantes y reduciendo llamadas a la API en un 66% para estos casos.

### Gestión de Contexto de Agentes

Cada agente utiliza una instancia limpia de Claude API para evitar la acumulación de tokens en el contexto, lo que optimiza el costo y la velocidad de respuesta.

## Estructura del Proyecto

```
algorithm-analysis/
├── app/
│   ├── api/
│   │   └── analyzer/
│   │       ├── router.py         # Endpoints de la API
│   │       └── schemas.py        # Esquemas de request/response
│   │
│   ├── parsing/
│   │   ├── grammar.lark          # Gramática del pseudocódigo
│   │   ├── parser.py             # Parser Lark
│   │   ├── transformer.py        # Transformador AST
│   │   ├── serializer.py         # Serializador JSON
│   │   └── nodes.py              # Clases de nodos AST
│   │
│   ├── analysis/
│   │   ├── classifier.py         # Clasificador de algoritmos
│   │   ├── analysis_orchestrator.py  # Orquestador principal
│   │   │
│   │   ├── agents/
│   │   │   ├── base_agent.py         # Agente base
│   │   │   ├── recursive_agent.py    # Agente para recursivos
│   │   │   ├── iterative_agent.py    # Agente para iterativos
│   │   │   ├── resolver_agent.py     # Agente de resolución
│   │   │   └── translator_agent.py   # Agente de traducción
│   │   │
│   │   ├── tools/
│   │   │   ├── master_theorem.py     # Tool Teorema Maestro
│   │   │   ├── substitution.py       # Tool método sustitución
│   │   │   ├── summation_solver.py   # Tool sumatorias
│   │   │   └── recursion_tree.py     # Tool árbol recursión
│   │   │
│   │   └── schemas_*.py          # Esquemas de datos
│   │
│   ├── storage/
│   │   ├── supabase_client.py    # Cliente Supabase
│   │   └── cache_utils.py        # Utilidades de caché
│   │
│   ├── core/
│   │   └── analysis_pipeline.py  # Pipeline de análisis
│   │
│   └── main.py                   # Punto de entrada FastAPI
│
├── tests/                        # Pruebas unitarias
├── .env                          # Variables de entorno
├── requirements.txt              # Dependencias
└── README.md                     # Este archivo
```

## Tecnologías Utilizadas

| Tecnología                    | Propósito                               |
| ------------------------------ | ---------------------------------------- |
| **Python 3.10+**         | Lenguaje de programación principal      |
| **FastAPI**              | Framework web para la API REST           |
| **Lark**                 | Parser para procesamiento de gramáticas |
| **Anthropic Claude API** | Modelo de lenguaje para análisis        |
| **Supabase**             | Base de datos para sistema de caché     |
| **Pydantic**             | Validación de datos y esquemas          |
| **uvicorn**              | Servidor ASGI                            |


## Documentación Adicional

La documentación completa del proyecto incluye:

* **Informe Técnico:** Análisis detallado de la arquitectura, metodología y resultados
* **Manual de Usuario:** Guía de uso del sistema
* **Manual Técnico:** Documentación del código y APIs

## Autores

Proyecto desarrollado como trabajo académico para la asignatura de Análisis y Diseño de Algoritmos.

**Universidad de Caldas**

Programa de Ingeniería de Sistemas y Computación

2025

## Licencia

Este proyecto es de uso académico. Todos los derechos reservados.

---

## Notas de Desarrollo

### Problemas Conocidos

1. **Consumo de tokens:** El análisis de algoritmos muy complejos puede consumir más tokens de lo esperado. Se recomienda usar el sistema de caché.
2. **Gramática limitada:** Algunas estructuras de pseudocódigo no estándar pueden no ser parseadas correctamente. Consultar la sección de sintaxis para el formato correcto.

### Mejoras Futuras

* Soporte para análisis de complejidad espacial
* Interfaz gráfica web
* Exportación de resultados a PDF
* Soporte para más paradigmas algorítmicos
