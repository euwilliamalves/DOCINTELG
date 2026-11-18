# 📚 DocIntelG – Consulta Inteligente de Documentos com RAG

## 📌 Sobre o projeto

O DocIntelG é uma aplicação desenvolvida em Python que utiliza a arquitetura Retrieval-Augmented Generation (RAG) para permitir consultas inteligentes sobre documentos PDF.

A solução realiza a extração do conteúdo dos documentos, divide os textos em pequenos fragmentos (*chunks*), gera embeddings e armazena as representações vetoriais utilizando FAISS.

Quando o usuário realiza uma pergunta, a aplicação recupera os trechos mais relevantes do documento e utiliza um modelo de linguagem para elaborar uma resposta baseada no contexto encontrado.

## 🚀 Funcionalidades

- Carregamento e leitura de documentos PDF.
- Extração de conteúdo utilizando PyPDFLoader.
- Divisão de documentos em chunks.
- Geração de embeddings.
- Armazenamento vetorial com FAISS.
- Recuperação de documentos por similaridade semântica.
- Recuperação de contexto utilizando MMR.
- Geração de respostas contextualizadas com LLM.
- Interface interativa desenvolvida com Streamlit.

## 🛠️ Tecnologias utilizadas

- Python
- Streamlit
- LangChain
- OpenAI API
- ChatOpenAI
- OpenAI Embeddings
- FAISS
- PyPDF

## 🧠 Arquitetura RAG

O projeto implementa um fluxo de Retrieval-Augmented Generation dividido em duas etapas principais.

### 1. Indexação dos documentos

1. O usuário disponibiliza um documento PDF.
2. O PyPDFLoader realiza a leitura e extração do conteúdo.
3. O RecursiveCharacterTextSplitter divide o conteúdo em fragmentos.
4. Os embeddings são gerados utilizando o modelo `text-embedding-3-small`.
5. Os vetores são armazenados no FAISS.

### 2. Recuperação e geração de respostas

1. O usuário envia uma pergunta.
2. A pergunta é utilizada para recuperar os trechos relevantes.
3. O FAISS realiza a busca vetorial.
4. O mecanismo MMR seleciona os documentos relevantes, buscando reduzir a redundância.
5. O contexto recuperado é enviado ao LLM.
6. O modelo gera uma resposta baseada nas informações encontradas.

## ⚙️ Configurações utilizadas

| Parâmetro | Configuração |
|---|---|
| Chunk size | 500 |
| Chunk overlap | 100 |
| Embeddings | text-embedding-3-small |
| Recuperação | MMR |
| Quantidade de documentos | 3 |
| Banco vetorial | FAISS |
| Modelo de linguagem | gpt-3.5-turbo |

## 🔎 Estratégia de recuperação

O projeto utiliza Maximum Marginal Relevance (MMR) para selecionar documentos relevantes considerando tanto a similaridade com a pergunta quanto a diversidade dos trechos recuperados.

Essa estratégia ajuda a evitar que a recuperação retorne apenas fragmentos muito semelhantes entre si.

## ⚙️ Como executar o projeto

### 1. Clone o repositório

```bash
git clone [URL DO REPOSITORIO]
cd DocIntelG
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv
```

### 3. Ative o ambiente virtual

Windows:

```bash
venv\Scripts\activate
```

Linux / macOS:

```bash
source venv/bin/activate
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

### 5. Configure a chave da OpenAI

Crie um arquivo `.env`:

```env
OPENAI_KEY=sua_chave_api
```

A aplicação também possui suporte à configuração da chave por meio de `st.secrets`.

### 6. Execute a aplicação

```bash
streamlit run app.py
```

## 🌐 Demonstração

Acesse a aplicação:

[DocIntelG – Aplicação online](https://docintelg.streamlit.app/)

## 🎯 Objetivo do projeto

Aplicar conceitos de RAG, embeddings, bancos vetoriais e LLMs na construção de uma solução capaz de interpretar documentos e responder perguntas utilizando informações recuperadas diretamente das fontes disponibilizadas.

## 👨‍💻 Autor

William Alves

[GitHub](https://github.com/euwilliamalves)
