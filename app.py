from flask import Flask, render_template, request
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain_core.vectorstores import VectorStoreRetriever
from log_suporte import init_db, salvar_log
from pathlib import Path
import re
import numpy as np
from collections import Counter

# Compatibilidade com NumPy 2.x
if not hasattr(np, "float_"):
    np.float_ = np.float64

app = Flask(__name__)
init_db()

# Caminho base
BASE_DIR = Path(__file__).resolve().parent
CHROMA_PATH = BASE_DIR / "chroma_db"

# Carrega todo o conteúdo do manual e cria documentos completos por linha
arquivo_manual = BASE_DIR / "documentacao_estruturada.txt"

def carregar_documentos(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        texto = f.read()

    documentos = []
    secao_atual = "Geral"
    for linha in texto.splitlines():
        linha = linha.strip()
        if not linha:
            continue
        if linha.startswith("##"):
            secao_atual = linha.replace("#", "").strip()
            continue
        documentos.append(Document(page_content=linha, metadata={"secao": secao_atual}))
    return documentos

# Documentos com metadados de seção
documentos_com_metadata = carregar_documentos(arquivo_manual)

# Embeddings e persistência com Chroma
embedding = OllamaEmbeddings(model="mistral")
db = Chroma.from_documents(documentos_com_metadata, embedding, persist_directory=str(CHROMA_PATH))

# Modelo Ollama
llm = ChatOllama(model="mistral", base_url="http://localhost:11434")

# Prompt restritivo e direto
template = (
    "Você é C3PO, o assistente virtual da plataforma Nexxo.\n"
    "Sua única função é responder com base **exclusivamente** no conteúdo fornecido abaixo, extraído do manual oficial da plataforma.\n\n"
    "REGRAS ESTRITAS:\n"
    "- NÃO invente, deduza ou complemente nenhuma informação.\n"
    "- NÃO resuma nem reformule instruções: reproduza-as exatamente como aparecem.\n"
    "- NÃO use conhecimento externo, senso comum ou linguagem genérica.\n"
    "- Se a pergunta exigir um passo a passo, transcreva fielmente os passos do conteúdo.\n"
    "- Se o conteúdo não contiver a resposta, diga apenas: **'Essa informação não está disponível no manual.'**\n"
    "- A resposta deve estar em **português do Brasil**, com foco em **clareza e fidelidade textual**.\n\n"
    "Conteúdo do manual:\n{context}\n\n"
    "Pergunta do usuário: {question}\n\n"
    "Resposta:"
)
prompt = PromptTemplate.from_template(template)

# Filtro opcional por palavras-chave
def aplicar_filtro_secao(pergunta):
    filtros = {
        "frete": "Publicação de Nova Carga",
        "motorista": "Seleção de Motoristas",
        "negociação": "Acompanhamento de Frete e Negociação",
        "notificação": "Notificações e Comunicação com Motoristas",
        "comunicação": "Notificações e Comunicação com Motoristas",
        "whatsapp": "Notificações e Comunicação com Motoristas",
        "transportador": "Cadastro de Novos Transportadores",
        "suporte": "Suporte Oficial"
    }
    for palavra, secao in filtros.items():
        if palavra in pergunta.lower():
            return {"secao": secao}
    return {}

# Cadeia QA base
qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=VectorStoreRetriever(vectorstore=db, search_kwargs={"k": 8}),
    chain_type="stuff",
    chain_type_kwargs={"prompt": prompt},
    return_source_documents=True
)

# Rota principal
@app.route("/", methods=["GET", "POST"])
def index():
    resposta = ""
    if request.method == "POST":
        pergunta = request.form["pergunta"]

        filtro = aplicar_filtro_secao(pergunta)
        retriever = VectorStoreRetriever(vectorstore=db, search_kwargs={"k": 8, "filter": filtro} if filtro else {"k": 8})
        qa.retriever = retriever

        resultado = qa.invoke({"query": pergunta})
        resposta_texto = resultado.get("result", "")
        resposta_limpa = re.sub(r"<think>.*?</think>", "", resposta_texto, flags=re.DOTALL).strip()

        fontes = resultado.get("source_documents", [])
        secoes = [f.metadata.get("secao", "Desconhecida") for f in fontes]
        secao_dominante = Counter(secoes).most_common(1)[0][0] if secoes else "Desconhecida"

        if not fontes or not resposta_limpa:
            resposta_limpa = "Essa informação não está disponível no manual."

        salvar_log(pergunta, f"[SEÇÃO: {secao_dominante}]\n{resposta_limpa}")
        resposta = resposta_limpa

    return render_template("index.html", resposta=resposta)

if __name__ == "__main__":
    app.run(debug=True)
