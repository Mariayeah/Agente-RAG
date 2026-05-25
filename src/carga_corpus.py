"""
Modulo para la carga del corpus DNI.
"""

from pathlib import Path


def cargar_corpus(ruta="base conocimiento"):
    """
    Carga todos los documentos .txt de la carpeta especificada.
    
    Args:
        ruta: Ruta a la carpeta con los documentos (por defecto "base conocimiento")
    
    Returns:
        Lista de diccionarios con {"nombre": str, "texto": str}
    """
    carpeta = Path(ruta)
    
    if not carpeta.exists():
        raise FileNotFoundError(f"La carpeta '{carpeta}' no existe")
    
    documentos = []
    archivos = sorted(carpeta.glob("*.txt"))
    
    if not archivos:
        raise FileNotFoundError(f"No se encontraron archivos .txt en '{carpeta}'")
    
    for archivo in archivos:
        texto = archivo.read_text(encoding="utf-8")
        documentos.append({
            "nombre": archivo.name,
            "texto": texto
        })
        print(f"  - Cargado: {archivo.name}")
    
    return documentos