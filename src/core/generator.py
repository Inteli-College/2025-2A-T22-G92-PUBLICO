import os
import httpx
import requests
import re
from typing import List, Dict, Any

# A URL da API do TGI (Text Generation Inference) definida no docker-compose
LLM_API_URL = os.getenv("LLM_API_URL", "http://localhost:8080")

class Generator:
    """
    Cliente para chamar o serviço de geração de texto (LLM) que está sendo executado 
    por uma API (TGI - Text Generation Inference).
    """

    def __init__(self, prompt_template: str):
        self.prompt_template = prompt_template
        self.endpoint = f"{LLM_API_URL}/generate"
        print(f"[GENERATOR] Endpoint LLM configurado para: {self.endpoint}")

    async def generate_response(self, contexto: str, pergunta: str) -> str:
        """
        Formata o prompt RAG e chama a API do LLM para gerar a resposta.
        """
        
        # Formata o prompt final RAG
        formatted_prompt = self.prompt_template.format(
            contexto=contexto,
            pergunta=pergunta
        )
        
        # Configura os parâmetros de geração
        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "do_sample": True,
                "temperature": 0.05,  # Baixa temperatura para respostas factuais
                "max_new_tokens": 256,
                "repetition_penalty": 1.03,
                "return_full_text": False,
                "stop_sequences": ["--- CONCLUSAO ---", "No entanto, a resposta", "### RESPOSTA"],
            }
        }
        
        async with httpx.AsyncClient(timeout=500) as client:
            # Faz a chamada POST para a API TGI
            try:
                response = await client.post(f"{LLM_API_URL}/generate", json=payload)
                response.raise_for_status() # Gera exceção para códigos 4xx/5xx

                data = response.json()
                
                # Tenta extrair a resposta de uma lista ou de um objeto único.
                raw_text = None
                if isinstance(data, list) and data and 'generated_text' in data[0]:
                    raw_text = data[0]['generated_text'].strip()
                    print(f"DEBUG: Resposta bruta do LLM: {raw_text}")
                elif isinstance(data, dict) and 'generated_text' in data:
                    raw_text = data['generated_text'].strip()
                    
                if raw_text:
                    text_final = raw_text.strip()
                    
                    # Remover Conclusões e Marcadores de Fim Inesperados
                    end_response_patterns = [
                        r"--- CONCLUSAO ---",
                        r"No entanto, a resposta",
                        r"Desculpe, não encontrei informações relevantes",
                        r"--- CONTEXTO FORNECIDO ---", 
                        r"PERGUNTA DO USUÁRIO:",
                        r"INSTRUÇÕES DE RESPOSTA:",
                        r"### RESPOSTA:",
                    ]    
                    
                    for pattern in end_response_patterns:
                        match = re.search(pattern, text_final, re.IGNORECASE | re.DOTALL) 
                        if match:
                            text_final = text_final[:match.start()].strip()
                            print(f"DEBUG: Padrão de fim '{pattern}' encontrado e texto cortado.")

                    # Remover Repetições do PRÓPRIO PROMPT que o LLM pode ter gerado.
                    prompt_start_patterns = [
                        r"^Você é um assistente de IA imparcial e analítico, especializado em regulamentações financeiras brasileiras.",
                        r"^Sua missão é responder à PERGUNTA DO USUÁRIO com base \*\*EXCLUSIVAMENTE\*\* e \*\*DIRETAMENTE\*\* no CONTEXTO fornecido\.",
                        r"^INSTRUÇÕES DE RESPOSTA:",
                        r"^1\. \*\*Restrição Rigorosa \(Anti-Alucinação\):",
                        r"^2\. \*\*Acurácia e Concisão:",
                        r"^3\. \*\*Rastreabilidade \(Citação Obrigatória\):",
                        r"^4\. \*\*Formato:",
                        r"^--- CONTEXTO FORNECIDO ---", 
                        r"^PERGUNTA DO USUÁRIO:",
                        r"^### RESPOSTA:",
                    ]
                    
                    # Para remover repetições do prompt do INÍCIO da resposta
                    for pattern in prompt_start_patterns:
                        text_final_prev = text_final
                        text_final = re.sub(pattern, '', text_final, 1, flags=re.IGNORECASE | re.DOTALL).strip()
                        if text_final != text_final_prev: # Verifica se houve alguma substituição
                            print(f"DEBUG: Padrão de início '{pattern}' removido do texto.")
                               
                    # Limpeza geral de espaços em branco e quebras de linha extras
                    text_final = re.sub(r'\s*\n\s*\n\s*', '\n\n', text_final) # Reduz múltiplas quebras de linha para duas
                    text_final = text_final.strip() # Remove espaços em branco do início e fim
                            
                    # Se o LLM parou logo após a resposta, isso será a resposta.
                    return text_final
                
                print(f"DEBUG: Formato de resposta do LLM inesperado: {data}")
                return "Erro: Formato de resposta do LLM inválido."

            except requests.exceptions.Timeout:
                return "Erro: O LLM excedeu o tempo limite (Timeout)."
            except requests.exceptions.RequestException as e:
                return f"Erro ao conectar ou receber resposta do LLM: {e}"
            except Exception as e:
                return f"Erro inesperado no gerador: {e}"

# Template RAG
RAG_PROMPT_TEMPLATE = """
Você é um assistente de IA imparcial e analítico, especializado em regulamentações financeiras brasileiras.
Sua missão é responder à PERGUNTA DO USUÁRIO com base **EXCLUSIVAMENTE** e **DIRETAMENTE** no CONTEXTO fornecido.

INSTRUÇÕES DE RESPOSTA:

1.  **Restrição Rigorosa (Anti-Alucinação):** Se o CONTEXTO for insuficiente, não fizer sentido, ou **NÃO CONTIVER A INFORMAÇÃO EXATA E COMPLETA** para a pergunta, você **DEVE** responder: "Desculpe, não encontrei informações relevantes nos documentos fornecidos para responder a essa pergunta específica." **NÃO INVENTE, NÃO ADICIONE E NÃO GENERALIZE INFORMAÇÕES.**

2.  **Acurácia e Concisão:** Revise **TODO** o CONTEXTO cuidadosamente. Formule uma resposta **BREVE, DIRETA, CONCISA** e profissional. Vá direto ao ponto.

3.  **Rastreabilidade (Citação Obrigatória):** Para cada **afirmação factual** na resposta, você **DEVE** incluir a citação exata ([FONTE]) que a suporta. Se não houver fonte no contexto, não responda.

4.  **Formato:** Mantenha a resposta apenas com o texto solicitado, sem introduções ou conclusões desnecessárias.

--- CONTEXTO FORNECIDO ---
{contexto}
----------------------------

PERGUNTA DO USUÁRIO: {pergunta}

### RESPOSTA:
"""

# Inicialização da instância do Gerador
generator = Generator(prompt_template=RAG_PROMPT_TEMPLATE)

# response = generator.generate_response(contexto=contexto_final, pergunta=query)
