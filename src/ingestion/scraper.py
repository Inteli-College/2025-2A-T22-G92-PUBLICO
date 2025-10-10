import requests
import os
import json
import time
import base64
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

USER_AGENT_HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def _render_html_to_pdf(driver, timeout = 45):
    """
    Usa o Chrome DevTools Protocol (CDP) para renderizar a página atual em PDF 
    e retornar os bytes do PDF diretamente.
    """
    try:
        # Espera que o corpo da página esteja carregado
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )

        # Tratamento de Cookies
        try:
            # Tenta encontrar o botão "Aceitar cookies" (ou similar) e clica.
            cookie_button_xpath = "//button[contains(text(), 'Aceitar cookies')] | //a[contains(text(), 'Aceitar cookies')]"
            
            print("[SCRAPER][CDP] Tentando encontrar e fechar o banner de cookies...")
            
            # Espera rápida para o botão de cookies, mas não quebra se ele não existir
            cookie_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, cookie_button_xpath))
            )
            
            cookie_button.click()
            print("[SCRAPER][CDP] Banner de cookies fechado com sucesso.")
            
            # Pequeno tempo de espera para o banner desaparecer completamente
            time.sleep(1) 
            
        except Exception:
            # A maioria das URLs não terá esse banner ou o clique falhará, o que é OK.
            print("[SCRAPER][CDP] Banner de cookies não encontrado ou já fechado.")
            pass
        
        # Buffer de 5 segundos extras para o navegador finalizar a formatação final de impressão (após o clique).
        print("[SCRAPER][CDP] Estabilizando a renderização final (5s)...")
        time.sleep(5)
    
    except Exception as e:
        print(f"[SCRAPER][CDP][AVISO] Falha ou timeout na espera inicial: {e}")
        # Continua mesmo com timeout na espera, pois o conteúdo pode ter carregado parcialmente
        pass 
    
    # Parâmetros de criação do PDF
    pdf_options = {
        'printBackground': True, # Inclui cores e imagens de fundo
        'displayHeaderFooter': False # Importante para evitar cabeçalhos
    }
    
    print("[SCRAPER][CDP] Executando Page.printToPDF...")
    
    try:
        # O CDP retorna o PDF codificado em Base64
        result = driver.execute_cdp_cmd("Page.printToPDF", pdf_options)
    
        if 'data' in result:
            pdf_bytes = base64.b64decode(result['data'])
            print(f"[SCRAPER][CDP] Conversão para PDF concluída. Bytes recebidos: {len(pdf_bytes)}")
            return pdf_bytes
        
        print("[SCRAPER][CDP][ERRO] O comando Page.printToPDF não retornou dados.")
        return None
        
    except Exception as e:
        print(f"[SCRAPER][CDP][ERRO] Falha durante a execução do CDP: {e}")
        return None

def url_to_local_pdf(url, output_dir):
    """
    Orquestra o download (se for PDF direto) ou a renderização (se for HTML)
    de uma URL para um arquivo PDF local.
    Retorna o caminho do arquivo PDF salvo.
    """
    # Cria um nome de arquivo previsível para ser procurado depois (usando hash da URL)
    filename_hash = str(hash(url))[:8] 
    output_path = os.path.join(output_dir, f"{filename_hash}.pdf")

    os.makedirs(output_dir, exist_ok=True)
    
    # Tenta download direto (para URLs que retornam PDF bruto)
    pdf_content = None
    try:
        print(f"[SCRAPER][DOWNLOAD] Tentando download direto de: {url}")
        response = requests.get(url, headers=USER_AGENT_HEADER, timeout=30)
        response.raise_for_status()
        
        if response.content.startswith(b'%PDF-'):
            pdf_content = response.content
            print("[SCRAPER][DOWNLOAD] PDF baixado com sucesso.")
        else:
            print("[SCRAPER][DOWNLOAD] Conteúdo não é PDF. Iniciando renderização HTML (CDP)...")
            
    except Exception as e:
        print(f"[SCRAPER][DOWNLOAD][AVISO] Falha no download direto: {e}. Tentando renderização.")
        pass # Continua para a renderização
        
    # Lógica de renderização HTML/Visualizador para PDF
    if pdf_content is None:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"user-agent={USER_AGENT_HEADER['User-Agent']}")
        
        driver = None
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.get(url)
            
            # Chama a função de renderização para obter os bytes do PDF
            pdf_content = _render_html_to_pdf(driver)
            
        except Exception as e:
            print(f"[SCRAPER][RENDER][ERRO] Falha ao renderizar URL para PDF via CDP: {e}")
            
        finally:
            if driver:
                driver.quit()

    # Salvamento local
    if pdf_content:
        with open(output_path, 'wb') as f:
            f.write(pdf_content)
        print(f"[SCRAPER] Aquisição CONCLUÍDA. PDF salvo localmente: {output_path}")
        return output_path
    
    print("[SCRAPER] Falha na aquisição: Não foi possível obter conteúdo PDF por download nem por renderização.")
    return None
