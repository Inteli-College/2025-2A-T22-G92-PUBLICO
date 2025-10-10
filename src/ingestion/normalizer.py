import re
from unidecode import unidecode

def normalize_text(text):
    """
    Normaliza todos os campos de um dicionário (item):
    - transforma strings em lowercase
    - remove acentos
    - remove caracteres especiais indesejados
    - remove múltiplos espaços consecutivos
    """
    if not isinstance(text, str):
        # Proteção extra para garantir que só processa strings
        return ""
    
    text = text.lower().strip() # lowercase e strip
    text = unidecode(text) # remove acentos

    # Remove longas sequências de pontuação ou caracteres repetidos
    text = re.sub(r'(\.|\s|\-|_){5,}', ' ', text)
    # Remove marcações típicas de final de documento/seção que não são texto
    text = re.sub(r'\(nr\)\s*art\.', ' ', text)
    text = re.sub(r'\"\(nr\)', ' ', text)

    # Remove múltiplos espaços e novas linhas
    text = re.sub(r'\s+', ' ', text).strip()   
    
    return text