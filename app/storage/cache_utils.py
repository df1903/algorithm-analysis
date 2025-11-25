"""
Utilidades para manejo de caché
"""
import hashlib
import json
from typing import Optional

def generate_pseudocode_hash(pseudocode: str) -> str:
    """
    Genera hash único del pseudocódigo normalizado
    
    Args:
        pseudocode: Código a hashear
        
    Returns:
        Hash SHA256 en hexadecimal
    """
    # Normalizar: quitar espacios extras
    normalized = ' '.join(pseudocode.split())
    normalized = normalized.lower()
    
    # Generar hash
    return hashlib.sha256(normalized.encode()).hexdigest()


def extract_cache_data(analysis_result, pseudocode: str, resolution_result=None, api_cost: float = 0.008, natural_description: Optional[str] = None) -> dict:
    """
    Extrae datos del análisis para guardar en caché
    
    Args:
        analysis_result: Resultado del orchestrator (RecursiveExtraction o IterativeExtraction)
        pseudocode: Pseudocódigo original
        api_cost: Costo de la llamada a la API
        
    Returns:
        Diccionario con datos para Supabase 
    """
    data = {
        "pseudocode_hash": generate_pseudocode_hash(pseudocode),
        "pseudocode": pseudocode,
        "natural_description": natural_description, 
        "algorithm_name": analysis_result.algorithm_name,
        "algorithm_type": analysis_result.algorithm_type,
        "has_different_cases": analysis_result.has_different_cases,
        "api_cost_usd": api_cost,
    }
    
    # Agregar casos según el tipo
    if analysis_result.has_different_cases:
        # Casos individuales
        if analysis_result.best_case:
            data["best_case_function"] = analysis_result.best_case.function
            data["best_case_explanation"] = analysis_result.best_case.explanation
        
        if analysis_result.worst_case:
            data["worst_case_function"] = analysis_result.worst_case.function
            data["worst_case_explanation"] = analysis_result.worst_case.explanation
        
        if analysis_result.average_case:
            data["average_case_function"] = analysis_result.average_case.function
            data["average_case_explanation"] = analysis_result.average_case.explanation
    else:
        # Caso unificado
        if analysis_result.unified_case:
            data["unified_function"] = analysis_result.unified_case.function
            data["unified_explanation"] = analysis_result.unified_case.explanation
            
            

    if resolution_result:
        phase2_data = extract_phase2_data(resolution_result)
        data.update(phase2_data) 
    
    return data


def reconstruct_analysis(cached_data: dict):
    """
    Reconstruye el objeto de análisis desde datos de caché
    
    Args:
        cached_data: Datos desde Supabase
        
    Returns:
        RecursiveExtraction o IterativeExtraction reconstruido
    """
    from app.analysis.schemas_extraction import (
        RecursiveExtraction,
        IterativeExtraction,
        ExtractedCase,
        UnifiedCase
    )
    
    # Determinar tipo
    is_recursive = cached_data["algorithm_type"] == "RECURSIVE"
    
    # Construir casos
    if cached_data["has_different_cases"]:
        # Casos individuales
        best_case = ExtractedCase(
            case_type="best",
            condition="unknown",
            exists=True,
            function=cached_data["best_case_function"] or "",
            explanation=cached_data["best_case_explanation"] or ""
        )
        
        worst_case = ExtractedCase(
            case_type="worst",
            condition="unknown",
            exists=True,
            function=cached_data["worst_case_function"] or "",
            explanation=cached_data["worst_case_explanation"] or ""
        )
        
        average_case = None
        if cached_data.get("average_case_function"):
            average_case = ExtractedCase(
                case_type="average",
                condition="unknown",
                exists=True,
                function=cached_data["average_case_function"],
                explanation=cached_data["average_case_explanation"] or ""
            )
        
        if is_recursive:
            return RecursiveExtraction(
                algorithm_name=cached_data["algorithm_name"],
                algorithm_type="RECURSIVE",
                recursive_calls_count=1,
                base_case_condition="unknown",
                has_different_cases=True,
                unified_case=None,
                best_case=best_case,
                worst_case=worst_case,
                average_case=average_case
            )
        else:
            return IterativeExtraction(
                algorithm_name=cached_data["algorithm_name"],
                algorithm_type="ITERATIVE",
                loops=[],
                max_nesting=0,
                has_different_cases=True,
                unified_case=None,
                best_case=best_case,
                worst_case=worst_case,
                average_case=average_case
            )
    else:
        # Caso unificado
        unified_case = UnifiedCase(
            function=cached_data["unified_function"] or "",
            applies_to=["best", "worst", "average"],
            explanation=cached_data["unified_explanation"] or ""
        )
        
        if is_recursive:
            return RecursiveExtraction(
                algorithm_name=cached_data["algorithm_name"],
                algorithm_type="RECURSIVE",
                recursive_calls_count=1,
                base_case_condition="unknown",
                has_different_cases=False,
                unified_case=unified_case,
                best_case=None,
                worst_case=None,
                average_case=None
            )
        else:
            return IterativeExtraction(
                algorithm_name=cached_data["algorithm_name"],
                algorithm_type="ITERATIVE",
                loops=[],
                max_nesting=0,
                has_different_cases=False,
                unified_case=unified_case,
                best_case=None,
                worst_case=None,
                average_case=None
            )
            
def extract_phase2_data(resolution) -> dict:
    """
    Extrae datos  para guardar en caché
    Guarda en columnas separadas Y en JSON completo
    
    Args:
        resolution: AlgorithmResolution desde ResolverAgent
        
    Returns:
        Dict con datos para Supabase
    """
    data = {}
    
    if resolution.has_different_cases:
        # ===== CASOS DIFERENTES =====
        
        # Mejor caso
        if resolution.best_case:
            res = resolution.best_case.resolution
            
            # Columnas separadas
            data["best_case_O"] = res.O
            data["best_case_Omega"] = res.Omega
            data["best_case_Theta"] = res.Theta
            data["best_case_method"] = res.method
            
            # JSON completo
            data["best_case_resolved"] = json.dumps({
                "O": res.O,
                "Omega": res.Omega,
                "Theta": res.Theta,
                "is_tight_bound": res.is_tight_bound,
                "method": res.method,
                "steps": res.steps,
                "explanation": res.explanation
            })
        
        # Peor caso
        if resolution.worst_case:
            res = resolution.worst_case.resolution
            
            data["worst_case_O"] = res.O
            data["worst_case_Omega"] = res.Omega
            data["worst_case_Theta"] = res.Theta
            data["worst_case_method"] = res.method
            
            data["worst_case_resolved"] = json.dumps({
                "O": res.O,
                "Omega": res.Omega,
                "Theta": res.Theta,
                "is_tight_bound": res.is_tight_bound,
                "method": res.method,
                "steps": res.steps,
                "explanation": res.explanation
            })
        
        # Caso promedio
        if resolution.average_case:
            res = resolution.average_case.resolution
            
            data["average_case_O"] = res.O
            data["average_case_Omega"] = res.Omega
            data["average_case_Theta"] = res.Theta
            data["average_case_method"] = res.method
            
            data["average_case_resolved"] = json.dumps({
                "O": res.O,
                "Omega": res.Omega,
                "Theta": res.Theta,
                "is_tight_bound": res.is_tight_bound,
                "method": res.method,
                "steps": res.steps,
                "explanation": res.explanation
            })
    
    else:
        # ===== CASO UNIFICADO =====
        
        if resolution.unified_case:
            res = resolution.unified_case.resolution
            
            # Columnas separadas
            data["unified_case_O"] = res.O
            data["unified_case_Omega"] = res.Omega
            data["unified_case_Theta"] = res.Theta
            data["unified_case_method"] = res.method
            
            # JSON completo en resolution_method
            data["resolution_method"] = json.dumps({
                "O": res.O,
                "Omega": res.Omega,
                "Theta": res.Theta,
                "is_tight_bound": res.is_tight_bound,
                "method": res.method,
                "steps": res.steps,
                "explanation": res.explanation
            })
    
    return data
            
        