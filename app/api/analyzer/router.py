"""
Módulo del enrutador del analizador.

Expone los endpoints para analizar pseudocódigo y verificar
el estado del servicio.
"""

from fastapi import APIRouter, HTTPException
from app.core.analysis_pipeline import analyze_pseudocode_internal
from app.api.analyzer.schemas import AstRequest, AstResponse, NaturalLanguageRequest
from app.analysis.agents.translator_agent import TranslatorAgent


router = APIRouter()



@router.post("/ast", response_model=AstResponse)
def build_ast(req: AstRequest) -> AstResponse:
    """
    Genera el AST, analiza (Fase 1) y resuelve complejidades (Fase 2) con caché
    """
    try:
        # Usar función compartida
        result = analyze_pseudocode_internal(
            pseudocode=req.text,
            natural_description=None  
        )
        
        #Respuesta al llamado
        return AstResponse(
            ast=result["ast"],
            pretty=result["pretty"],
            classification=result["classification"],
            analysis=result["analysis"],
            resolution=result["resolution"]
        )
        
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Error construyendo AST y analizando: {exc}"
        ) from exc

        
@router.post("/natural-to-pseudocode")
def natural_to_pseudocode(req: NaturalLanguageRequest) -> dict:
    """
    Traduce lenguaje natural a pseudocódigo Y lo analiza completamente.
    
    Args:
        req: Objeto con la descripción en lenguaje natural
        
    Returns:
        dict con pseudocode, analysis, resolution, y metadatos de traducción
        
    Raises:
        HTTPException: Si no se puede generar pseudocódigo válido o analizarlo
    """
    try:
        # PASO 1: Traducir descripción natural a pseudocódigo

        translator = TranslatorAgent()
        translation_result = translator.translate(req.description)
        
        if not translation_result["success"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": translation_result["error"],
                    "last_attempt": translation_result.get("last_attempt"),
                    "last_error": translation_result.get("last_error")
                }
            )
        
        pseudocode = translation_result["pseudocode"]
        
        
        # PASO 2: Analizar el pseudocódigo generado
        analysis_result = analyze_pseudocode_internal(
            pseudocode=pseudocode,
            natural_description=req.description
        )
        
        # PASO 3: Devolver resultados
        return {
            "pseudocode": pseudocode,
            "validated": translation_result["validated"],
            "attempts": translation_result["attempts"],
            "confidence": translation_result["confidence"],
            "analysis": analysis_result["analysis"],
            "resolution": analysis_result["resolution"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Error en traducción o análisis: {str(e)}"
        )