"""
Pipeline de análisis completo: Parsing → Clasificación  → Caché

Función compartida usada por /ast y /natural-to-pseudocode
"""
import json
import traceback

from typing import Optional, Dict, Any
from app.parsing.parser import PseudocodeParser
from app.parsing.transformer import PseudocodeTransformer
from app.parsing.serializer import ast_to_dict
from app.analysis.classifier import AlgorithmClassifier
from app.analysis.analysis_orchestrator import AnalysisOrchestrator
from app.analysis.agents.resolver_agent import ResolverAgent
from app.storage.supabase_client import supabase_client
from app.storage.cache_utils import (
    generate_pseudocode_hash,
    extract_cache_data,
    reconstruct_analysis
)


def analyze_pseudocode_internal(
    pseudocode: str,
    natural_description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Análisis completo de pseudocódigo con caché.
    
    Args:
        pseudocode: Texto del pseudocódigo a analizar
        natural_description: Descripción en lenguaje natural (opcional)
        
    Returns:
        Dict con: ast, pretty, classification, analysis, resolution
        
    Raises:
        Exception: Si hay error en parsing o análisis
    """
    
    # PASO 1: BUSCAR EN CACHÉ
    
    pseudocode_hash = generate_pseudocode_hash(pseudocode)
    
    try:
        cache_response = supabase_client.client.table("algorithms_cache")\
            .select("*")\
            .eq("pseudocode_hash", pseudocode_hash)\
            .execute()
        
        if cache_response.data and len(cache_response.data) > 0:
            # ENCONTRADO EN CACHÉ
            cached = cache_response.data[0]
            
            # Incrementar contador
            supabase_client.client.table("algorithms_cache")\
                .update({"times_requested": cached["times_requested"] + 1})\
                .eq("id", cached["id"])\
                .execute()
            
            # Reconstruir análisis (Fase 1)
            analysis_result = reconstruct_analysis(cached)
            
            # Reconstruir resolution (Fase 2)
            resolution_result = _reconstruct_resolution_from_cache(cached)
            
            return {
                "ast": {"from_cache": True, "algorithm_name": cached["algorithm_name"]},
                "pretty": "[Desde caché]",
                "classification": {"from_cache": True},
                "analysis": analysis_result,
                "resolution": resolution_result
            }
    
    except Exception as cache_error:
        print(f"Error en caché (continuando sin caché): {cache_error}")
    
    # PASO 2: NO ESTÁ EN CACHÉ → ANALIZAR
    

    
    # Parser y clasificación
    parser = PseudocodeParser()
    lark_tree = parser.parse(pseudocode)
    
    transformer = PseudocodeTransformer()
    ast_obj = transformer.transform(lark_tree)
    
    classifier = AlgorithmClassifier(ast_obj)
    classification = classifier.classify_all()
    
    ast_json = ast_to_dict(ast_obj)
    pretty = lark_tree.pretty()
    
    analysis_result = None
    resolution_result = None
    
    if ast_json["algorithm"]["subroutines"]:
        
        # Lógica inteligente de selección de subrutina
        recursive_idx = None
        for idx, cls in enumerate(classification["subroutines"]):
            if cls["type"] == "RECURSIVE":
                recursive_idx = idx
                break
        
        # Decidir qué función analizar
        if recursive_idx is not None:
            use_idx = recursive_idx
        
        elif len(ast_json["algorithm"]["subroutines"]) >= 2:
            use_idx = len(ast_json["algorithm"]["subroutines"]) - 1
        
        else:
            use_idx = 0
        
        # Analizar la subrutina seleccionada
        first_subroutine = ast_json["algorithm"]["subroutines"][use_idx]
        subroutine_classification = classification["subroutines"][use_idx]
        
        # FASE 1: EXTRACCIÓN
        
        orchestrator = AnalysisOrchestrator()
        analysis_result = orchestrator.analyze(
            ast_node=first_subroutine,
            classification=subroutine_classification["type"],
            subroutine_name=first_subroutine["name"]
        )
        
        # PASO 3: FASE 2 - RESOLUCIÓN DE COMPLEJIDADES
        
        if not isinstance(analysis_result, dict) or "error" not in analysis_result:
            try:
                
                resolver = ResolverAgent()
                resolution_result = resolver.resolve_algorithm(analysis_result)

                # Mostrar resultados
                if resolution_result.has_different_cases:
                    if resolution_result.best_case:
                        best_theta = resolution_result.best_case.resolution.Theta or resolution_result.best_case.resolution.O
                    if resolution_result.worst_case:
                        worst_theta = resolution_result.worst_case.resolution.Theta or resolution_result.worst_case.resolution.O
                    if resolution_result.average_case:
                        avg_theta = resolution_result.average_case.resolution.Theta or resolution_result.average_case.resolution.O
                else:
                    if resolution_result.unified_case:
                        unified_theta = resolution_result.unified_case.resolution.Theta or resolution_result.unified_case.resolution.O
                
                
            except Exception as resolver_error:
                print(f"\nError en Fase 2: {resolver_error}")
                traceback.print_exc()
                resolution_result = None
        
        # PASO 4: GUARDAR EN CACHÉ (CON natural_description)
        
        if not isinstance(analysis_result, dict) or "error" not in analysis_result:
            try:
                
                # Extraer datos de Fase 1 y Fase 2
                cache_data = extract_cache_data(
                    analysis_result, 
                    pseudocode,
                    resolution_result,
                    natural_description=natural_description  # ← CLAVE
                )
                
                # Insertar en Supabase
                supabase_client.client.table("algorithms_cache")\
                    .insert(cache_data)\
                    .execute()
                
            except Exception as save_error:
                print(f"\nError guardando en caché: {save_error}")
                traceback.print_exc()
    
    return {
        "ast": ast_json,
        "pretty": pretty,
        "classification": classification,
        "analysis": analysis_result,
        "resolution": resolution_result.model_dump() if resolution_result else None
    }


def _reconstruct_resolution_from_cache(cached: Dict) -> Optional[Dict]:
    """Reconstruye el objeto resolution desde caché"""
    
    has_phase2 = (
        cached.get("unified_case_O") or 
        cached.get("best_case_O") or 
        cached.get("worst_case_O")
    )
    
    if not has_phase2:
        return None
    
    resolution_result = {
        "has_different_cases": cached["has_different_cases"],
        "algorithm_name": cached["algorithm_name"],
        "algorithm_type": cached["algorithm_type"]
    }
    
    if cached["has_different_cases"]:
        # Casos diferentes
        if cached.get("best_case_O"):
            best_resolved = {}
            if cached.get("best_case_resolved"):
                try:
                    best_resolved = json.loads(cached["best_case_resolved"])
                except:
                    pass
            
            resolution_result["best_case"] = {
                "case_type": "best",
                "original_equation": cached.get("best_case_function", ""),
                "resolution": {
                    "O": cached["best_case_O"],
                    "Omega": cached["best_case_Omega"],
                    "Theta": cached["best_case_Theta"],
                    "is_tight_bound": cached["best_case_Theta"] is not None,
                    "method": cached["best_case_method"],
                    "steps": best_resolved.get("steps", []),
                    "explanation": best_resolved.get("explanation", "")
                }
            }
        
        if cached.get("worst_case_O"):
            worst_resolved = {}
            if cached.get("worst_case_resolved"):
                try:
                    worst_resolved = json.loads(cached["worst_case_resolved"])
                except:
                    pass
            
            resolution_result["worst_case"] = {
                "case_type": "worst",
                "original_equation": cached.get("worst_case_function", ""),
                "resolution": {
                    "O": cached["worst_case_O"],
                    "Omega": cached["worst_case_Omega"],
                    "Theta": cached["worst_case_Theta"],
                    "is_tight_bound": cached["worst_case_Theta"] is not None,
                    "method": cached["worst_case_method"],
                    "steps": worst_resolved.get("steps", []),
                    "explanation": worst_resolved.get("explanation", "")
                }
            }
        
        if cached.get("average_case_O"):
            avg_resolved = {}
            if cached.get("average_case_resolved"):
                try:
                    avg_resolved = json.loads(cached["average_case_resolved"])
                except:
                    pass
            
            resolution_result["average_case"] = {
                "case_type": "average",
                "original_equation": cached.get("average_case_function", ""),
                "resolution": {
                    "O": cached["average_case_O"],
                    "Omega": cached["average_case_Omega"],
                    "Theta": cached["average_case_Theta"],
                    "is_tight_bound": cached["average_case_Theta"] is not None,
                    "method": cached["average_case_method"],
                    "steps": avg_resolved.get("steps", []),
                    "explanation": avg_resolved.get("explanation", "")
                }
            }
    
    else:
        # Caso unificado
        if cached.get("unified_case_O"):
            unified_resolved = {}
            if cached.get("resolution_method"):
                try:
                    unified_resolved = json.loads(cached["resolution_method"])
                except:
                    pass
            
            resolution_result["unified_case"] = {
                "case_type": "unified",
                "original_equation": cached.get("unified_function", ""),
                "resolution": {
                    "O": cached["unified_case_O"],
                    "Omega": cached["unified_case_Omega"],
                    "Theta": cached["unified_case_Theta"],
                    "is_tight_bound": cached["unified_case_Theta"] is not None,
                    "method": cached["unified_case_method"],
                    "steps": unified_resolved.get("steps", []),
                    "explanation": unified_resolved.get("explanation", "")
                }
            }
    
    return resolution_result