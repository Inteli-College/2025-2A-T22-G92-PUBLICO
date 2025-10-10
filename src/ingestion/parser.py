from pypdf import PdfReader
import os
from io import BytesIO

def extract_text_from_local_pdf(file_path):
    """
    Realiza a raspagem do texto de um arquivo PDF já salvo localmente.
    """
    if not os.path.exists(file_path):
        print(f"[PARSER][ERRO] Arquivo PDF não encontrado no caminho: {file_path}")
        return None
        
    try:
        print(f"[PARSER] Extraindo texto do arquivo local: {os.path.basename(file_path)}")
        reader = PdfReader(file_path)
        
        text = ""
        for page in reader.pages:
            # Garante que o texto de diferentes páginas seja separado
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n" 
        
        extracted_text = text.strip()
        print(f"[PARSER] Extração concluída. Total de caracteres: {len(extracted_text)}")
        return extracted_text
        
    except Exception as e:
        print(f"[PARSER][ERRO EXTRAÇÃO] Falha ao ler PDF local {file_path}: {e}")
        return None
