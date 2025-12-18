import os
import requests
import streamlit as st
import pytz
from datetime import datetime

# =========================================
# CONFIGURAÇÃO
# =========================================
BACKEND_API = os.getenv("BACKEND_API", "http://rag-api:8000")
PUBLIC_API_URL = os.getenv("PUBLIC_API_URL", "http://localhost:8000")

def format_date(iso_timestamp):
    """Converte timestamp para uma data amigável do Brasil."""
    try:
        if not iso_timestamp or iso_timestamp == "N/A":
            return "N/A"

        dt_utc = datetime.fromisoformat(iso_timestamp).replace(tzinfo=pytz.utc)
        brt = pytz.timezone('America/Sao_Paulo')
        dt_brt = dt_utc.astimezone(brt)
        return dt_brt.strftime("%d/%m/%Y %H:%M:%S")
    except:
        return iso_timestamp


# =========================================
# ESTADO GLOBAL
# =========================================
st.set_page_config(page_title="RAG BOFA", layout="wide")

if "token" not in st.session_state:
    st.session_state.token = None


# =========================================
# FUNÇÃO LOGIN
# =========================================
def login(username, password):
    try:
        response = requests.post(
            f"{BACKEND_API}/token",
            data={"username": username, "password": password},
            timeout=10
        )
        if response.status_code == 200:
            st.session_state.token = response.json()["access_token"]
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")
    except Exception as e:
        st.error(f"Erro ao conectar: {e}")


# =========================================
# BARRA SUPERIOR (LOGIN + LOGOUT)
# =========================================
st.markdown(
    """
    <style>
        .top-bar {
            display: flex;
            justify-content: flex-end;
            align-items: center;
            padding: 10px 10px 0 0;
        }
        .logout-btn button {
            background-color: #ff4b4b !important;
            color: white !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

with st.container():
    st.markdown('<div class="top-bar">', unsafe_allow_html=True)

    if st.session_state.token is not None:
        if st.button("🔓 Sair", key="logout-btn"):
            st.session_state.token = None
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# =========================================
# TELA DE LOGIN (fora da sidebar)
# =========================================
if st.session_state.token is None:
    st.title("🔐 Acesso ao Sistema")

    st.write("Entre com seu usuário e senha para usar a plataforma.")

    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        login(username, password)

    st.stop()


# =========================================
# SIDEBAR: MENU LIMPO
# =========================================
with st.sidebar:
    st.header("📚 Navegação")

    menu = st.radio(
        "O que deseja fazer?",
        ["Upload de Material", "Chat / Perguntas"],
    )


# =========================================
# =======  ÁREA 1 – UPLOAD  =======
# =========================================
if menu == "Upload de Material":

    st.title("📚 Enviar Materiais")

    tab1, tab2, tab3 = st.tabs(["PDF", "URL Única", "Lista de URLs"])

    # ---------------------- PDF ----------------------
    with tab1:
        st.subheader("Enviar um PDF")

        pdf_file = st.file_uploader("Escolha um arquivo PDF", type=["pdf"])
        cargos_pdf = st.multiselect(
            "Quem pode acessar este documento?",
            ["admin", "gerente", "analista", "aluno"],
            default=["admin"],
        )

        if st.button("Enviar PDF"):
            if pdf_file is None:
                st.error("Selecione um arquivo.")
            else:
                files = {"file": pdf_file}
                data = {"roles_csv": ",".join(cargos_pdf)}
                with st.spinner("Enviando PDF..."):
                    response = requests.post(
                        f"{BACKEND_API}/upload-pdf",
                        files=files,
                        data=data,
                        headers={"Authorization": f"Bearer {st.session_state.token}"}
                    )
                    st.success("PDF enviado!")
                    st.json(response.json())

    # ---------------------- URL Única ----------------------
    with tab2:
        st.subheader("Processar uma URL")

        url = st.text_input("Digite a URL")
        cargos_url = st.multiselect(
            "Quem pode acessar este conteúdo?",
            ["admin", "gerente", "analista", "aluno"],
            default=["admin"],
        )

        if st.button("Enviar URL"):
            if not url.strip():
                st.error("Digite uma URL válida.")
            else:
                payload = {"url": url, "allowed_roles": cargos_url}
                with st.spinner("Processando URL..."):
                    response = requests.post(
                        f"{BACKEND_API}/upload-url",
                        json=payload,
                        headers={"Authorization": f"Bearer {st.session_state.token}"}
                    )
                    st.success("URL enviada!")
                    st.json(response.json())

    # ---------------------- BATCH ----------------------
    with tab3:
        st.subheader("Enviar várias URLs")

        urls_text = st.text_area("Insira uma URL por linha")
        cargos_batch = st.multiselect(
            "Quem pode acessar esses conteúdos?",
            ["admin", "gerente", "analista", "aluno"],
            default=["admin"],
        )

        if st.button("Enviar lista"):
            urls_list = [u.strip() for u in urls_text.split("\n") if u.strip()]

            if not urls_list:
                st.error("Insira ao menos uma URL.")
            else:
                payload = {"urls": urls_list, "allowed_roles": cargos_batch}
                with st.spinner("Enviando..."):
                    response = requests.post(
                        f"{BACKEND_API}/ingest/batch",
                        json=payload,
                        headers={"Authorization": f"Bearer {st.session_state.token}"}
                    )
                    st.success("Envio concluído!")
                    st.json(response.json())


# =========================================
# =======  ÁREA 2 – CHAT =======
# =========================================
if menu == "Chat / Perguntas":

    st.title("💬 Consultar a Base")

    question = st.text_input("Digite sua pergunta:")

    if st.button("Enviar Pergunta"):

        if not question.strip():
            st.error("Digite uma pergunta.")
        else:
            payload = {"query": question}

            with st.spinner("Buscando informações..."):
                response = requests.post(
                    f"{BACKEND_API}/query",
                    json=payload,
                    headers={"Authorization": f"Bearer {st.session_state.token}"}
                )
                data = response.json()

                st.subheader("🧠 Resposta do sistema")
                st.write(data.get("answer", "Sem resposta."))

                with st.expander("🔍 Ver chunks usados na resposta"):
                    # Explicação simples do que são chunks (AGORA dentro do dropdown)
                    st.markdown("""
                    ### 📘 O que são *chunks*?
                    *Chunks* são pequenos pedaços de texto retirados dos arquivos e sites que você enviou.  
                    O sistema divide tudo em partes menores para conseguir encontrar rapidamente **onde está a informação** que responde sua pergunta.

                    Aqui você pode ver exatamente **quais trechos** o sistema usou para montar a resposta.
                    """)

                    # Lista dos chunks retornados
                    for i, chunk in enumerate(data["chunks"], 1):
                        with st.container(border=True):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                source = chunk.get('source', '#')
                                file_on_disk = chunk.get('file_in_storage')
                                name_for_display = chunk.get('display_name')
                                final_link = f"{PUBLIC_API_URL}/files/{file_on_disk}"

                                if source.startswith("http"):
                                    st.markdown(f"🔗 **Fonte Web:** [{name_for_display}]({final_link})")
                                elif file_on_disk:
                                    st.markdown(f"📄 **Arquivo enviado:** [{name_for_display}]({final_link})")
                                else:
                                    st.markdown(f"📝 **Fonte:** {name_for_display}")

                            with col2:
                                st.metric(label="Relevância", value=f"{chunk['score']:.4f}")

                            formatted_date = format_date(chunk.get('last_updated', 'N/A'))
                            st.caption(f"📅 **Atualizado em:** {formatted_date} • 🔖 **Chunk ID:** {chunk.get('chunk_index')}")

                            with st.expander(f"📖 Ver trecho #{i}"):
                                st.text(chunk['chunk'])

