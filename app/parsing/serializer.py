"""
Serializador de AST a estructuras JSON-compatibles.

Convierte instancias de dataclasses de nodos del AST a dicts anidados con
información del tipo de nodo y sus campos, listo para ser retornado por la API.
"""

from __future__ import annotations

from dataclasses import is_dataclass, fields
from typing import Any

try:
    from lark import Token  # type: ignore
except Exception:  # pragma: no cover
    Token = None  # type: ignore


def ast_to_dict(obj: Any) -> Any:
    """
    Serializa un nodo del AST (o estructura anidada) a un objeto JSON-serializable.

    - Para dataclasses: incluye la clave "type" con el nombre de clase y
      serializa recursivamente sus campos.
    - Para listas/tuplas: serializa cada elemento.
    - Para tokens de Lark (si aparecen): usa `.value` como representación.
    - Para primitivos: retorna tal cual.
    """
    # Dataclasses (nuestros nodos AST son dataclasses)
    if is_dataclass(obj):
        data: dict[str, Any] = {"type": obj.__class__.__name__}
        for f in fields(obj):
            value = getattr(obj, f.name)
            data[f.name] = ast_to_dict(value)
        return data

    # Listas o tuplas
    if isinstance(obj, (list, tuple)):
        return [ast_to_dict(x) for x in obj]

    # Token de Lark (por seguridad, normalmente el AST ya no contiene Tokens)
    if Token is not None and isinstance(obj, Token):  # type: ignore
        return obj.value

    # Primitivos y otros tipos (None, str, int, float, bool, dict, ...)
    if isinstance(obj, dict):
        return {k: ast_to_dict(v) for k, v in obj.items()}

    return obj

