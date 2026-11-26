
import streamlit as st
import tempfile
import os
import hashlib
import uuid

from main import (
    leitura_documentos,
    banco_vetorial,
    resposta_chat,
    executar_chat
)


# =========================
# CONFIGURAÇÃO
# =========================

st.set_page_config(
    page_title="Assistente Inteligente de Documentos",
    page_icon="🤖",
    layout="centered"
)

st.markdown("""
<style>

.block-container {
    max-width: 1000px;
    padding-top: 2rem;
}

[data-testid="stChatMessage"] {
    background-color: transparent !important;
}

[data-testid="stChatMessageContent"] {
    background-color: transparent !important;
}

</style>
""", unsafe_allow_html=True)


st.title("Geração Aumentada por Recuperação")
st.caption("Assistente Inteligente de Documentos")

# INICIALIZAÇÃO DA SESSÃO

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4().hex

if "banco" not in st.session_state:
    st.session_state.banco = None

if "rag" not in st.session_state:
    st.session_state.rag = None

if "fingerprint" not in st.session_state:
    st.session_state.fingerprint = None

if "nomes_documentos" not in st.session_state:
    st.session_state.nomes_documentos = []

# UPLOAD DOS DOCUMENTOS
documentos = st.file_uploader(
    "📎 Envie seus documentos",
    type=["pdf", "docx", "txt", "csv"],
    accept_multiple_files=True
)


if documentos:
    # Identificação dos arquivos enviados
    hash_arquivos = hashlib.sha256()

    for documento in documentos:

        hash_arquivos.update(documento.name.encode("utf-8"))
        hash_arquivos.update(documento.getvalue())

    fingerprint = hash_arquivos.hexdigest()

    # Evita reconstruir o RAG em cada rerun
    if fingerprint != st.session_state.fingerprint:
        arquivos_temp = []

        try:
            with st.spinner("📚 Processando documentos..."):
                for documento in documentos:

                    extensao = os.path.splitext(documento.name)[1]
                    arquivo_temp = tempfile.NamedTemporaryFile( delete=False, suffix=extensao )

                    arquivo_temp.write(documento.getbuffer())
                    arquivo_temp.close()

                    arquivos_temp.append( (arquivo_temp.name, documento.name) )

                # Carregamento
                docs = leitura_documentos(arquivos_temp)

                # Criação do banco vetorial
                banco = banco_vetorial(docs)

                # Construção da chain com memória
                rag = resposta_chat(banco)

                # Armazenamento na sessão
                st.session_state.banco = banco
                st.session_state.rag = rag
                st.session_state.fingerprint = fingerprint
                st.session_state.nomes_documentos = [ doc.name for doc in documentos ]

                # Nova base de documentos = nova conversa
                st.session_state.messages = []
                st.session_state.session_id = uuid.uuid4().hex
            st.success("✅ Documentos processados com sucesso!")

        finally:
            # Exclusão dos arquivos temporários
            for caminho, nome in arquivos_temp:
                if os.path.exists(caminho):
                    os.remove(caminho)

# MOSTRAR DOCUMENTOS
if st.session_state.nomes_documentos:
    st.sidebar.subheader("📚 Documentos")
    for nome in st.session_state.nomes_documentos:
        st.sidebar.write(f"📄 {nome}")

# HISTÓRICO DO CHAT
user_avatar = "👤"
system_avatar = "🧠"

for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user", avatar=user_avatar):
            st.markdown(message["content"])

    else:
        with st.chat_message("assistant", avatar=system_avatar):
            st.markdown(message["content"])


# INPUT E PROCESSAMENTO
prompt = st.chat_input("Digite sua mensagem...")

if prompt:
    # Mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar=user_avatar):
        st.markdown(prompt)

    # Verificação do banco
    if st.session_state.rag is None:
        resposta = "📎 Primeiro envie pelo menos um documento."
        with st.chat_message("assistant", avatar=system_avatar):
            st.markdown(resposta)

    else:
        with st.chat_message("assistant", avatar=system_avatar):
            resposta = st.write_stream(
                executar_chat(
                    prompt,
                    st.session_state.rag,
                    st.session_state.session_id
                )
            )

    # Armazenamento da resposta
    st.session_state.messages.append({"role": "assistant", "content": resposta })
