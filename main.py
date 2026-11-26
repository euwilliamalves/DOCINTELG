
import os
from dotenv import load_dotenv

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    CSVLoader
)

from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_core.runnables import (
    RunnablePassthrough,
    RunnableWithMessageHistory,
    RunnableLambda
)

from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


# =========================
# CONFIGURAÇÃO
# =========================

load_dotenv()

key = os.getenv("OPENAI_KEY")

if not key:
    raise ValueError("API indisponível. Verifique sua OPENAI_KEY.")

# CARREGAMENTO DOS DOCUMENTOS
def leitura_documentos(arquivos):
    documentos = []
    for caminho, nome_original in arquivos:
        extensao = os.path.splitext(nome_original)[1].lower()
        if extensao == ".pdf":
            loader = PyPDFLoader(caminho)
        elif extensao == ".docx":
            loader = Docx2txtLoader(caminho)
        elif extensao == ".txt":
            loader = TextLoader(caminho, encoding="utf-8")
        elif extensao == ".csv":
            loader = CSVLoader(caminho, encoding="utf-8")
        else:
            raise ValueError(f"Formato não suportado: {extensao}")
            
        docs = loader.load()
        for doc in docs:
            doc.metadata["source"] = nome_original
        documentos.extend(docs)
    return documentos


# CHUNKING
def chunkenizer(documentos):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n", "\n", ",", ".", ""]
    )
    chunks = splitter.split_documents(documentos)
    for i, doc in enumerate(chunks):
        doc.metadata["doc_id"] = i
    return chunks

# BANCO VETORIAL
def banco_vetorial(documentos):
    if not documentos:
        raise ValueError('Nenhum documento foi carregado.')
    
    chunks = chunkenizer(documentos)

    #Remover chunk sem conteúdo
    chunks = [ doc for doc in chunks if doc.page_content.strip() ]

    if not chunks:
        raise ValueError('Nenhum conteúdo válido foi encontrado para gerar embedding.')
        
    embedding = OpenAIEmbeddings( model = "text-embedding-3-small", api_key = key)

    vector = FAISS.from_documents(documents = chunks, embedding = embedding)
    retriever = vector.as_retriever(search_type = "mmr", search_kwargs = {"k": 5})

    # Retornamos o retriever e não o banco diretamente.
    return retriever


# CONSTRUÇÃO DO RAG
def resposta_chat(retriever):
    store = {}
    def memory(session_id):
        if session_id not in store:
            store[session_id] = InMemoryChatMessageHistory()
        return store[session_id]

    # Formatação dos documentos recuperados
    def format_docs(documentos):
        return "\n\n".join(
            f"Fonte: {doc.metadata.get('source', 'Desconhecida')}\n"
            f"Conteúdo: {doc.page_content}"
            for doc in documentos
        )
    prompt =""" Você é um assistente especializado em análise de documentos.

            Utilize o contexto recuperado para responder às perguntas.

            Regras:
            - Priorize as informações presentes nos documentos.
            - Não invente informações.
            - Se não encontrar a resposta no contexto, informe isso ao usuário.
            - Considere o histórico para compreender perguntas de acompanhamento.

            Contexto:
            {context}
            """
    # Prompt
    template = ChatPromptTemplate.from_messages([
        ("system", prompt),
        MessagesPlaceholder(variable_name="history"),
        ("user", "{input}")
    ])

    # Modelo
    chat = ChatOpenAI( model = "gpt-4o-mini", temperature = 0, api_key = key )

    # Recuperação de contexto
    context = ( RunnableLambda(lambda x: x["input"]) | retriever | RunnableLambda(format_docs) )

    # Composição da chain
    rag_chain = ( RunnablePassthrough.assign( context=context ) | template | chat | StrOutputParser() )
    # Memória conversacional
    memory_list = RunnableWithMessageHistory(rag_chain, memory, history_messages_key="history", input_messages_key="input")

    return memory_list

# EXECUÇÃO DO CHAT
def executar_chat(pergunta, rag, session_id):
    config = {"configurable": { "session_id": session_id }}
    for chunk in rag.stream( {"input": pergunta}, config = config ):
        yield chunk
