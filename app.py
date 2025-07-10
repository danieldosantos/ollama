from flask import Flask, render_template, request
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from log_suporte import init_db, salvar_log
from pathlib import Path
import re
import numpy as np

# Compatibilidade com NumPy 2.x e chromadb
if not hasattr(np, "float_"):
    np.float_ = np.float64

app = Flask(__name__)
init_db()

# Caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent

# 1. Carrega o conteúdo do .txt estruturado
documento = BASE_DIR / "documentacao_estruturada.txt"
loader = TextLoader(str(documento), encoding="utf-8")
docs = loader.load()

# 2. Split em chunks maiores com separador de parágrafo
splitter = CharacterTextSplitter(separator="\n\n", chunk_size=1500, chunk_overlap=300)
chunks = splitter.split_documents(docs)

# 3. Embeddings e armazenamento vetorial com persistência
embedding = OllamaEmbeddings(model="gemma:2b")
db = Chroma.from_documents(chunks, embedding, persist_directory=str(BASE_DIR / "chroma_db"))
db.persist()

# 4. Retriever otimizado
retriever = db.as_retriever(search_kwargs={"k": 20})
llm = ChatOllama(model="gemma:2b", base_url="http://localhost:11434")

# 5. Prompt reforçado
template = (
    "Você é C3PO, o assistente virtual da plataforma Nexxo.\n"
    "Responda sempre em português do Brasil, de forma clara, direta e objetiva.\n"
    "Use SOMENTE o conteúdo abaixo (extraído do manual oficial) para responder com exatidão.\n"
    "NUNCA diga que a informação está no manual. NUNCA diga para consultar o manual.\n"
    "Se a resposta estiver no texto, transcreva exatamente como está.\n"
    "Se for um passo a passo, reproduza fielmente, sem alterar ou resumir.\n\n"
    "Exemplo:\n"
    "Pergunta: Como cadastrar um novo frete na plataforma?\n"
    "Resposta: PUBLICANDO UMA NOVA CARGA\n"
    "1. Menu à esquerda > \"Fretes\" > \"Criar Frete\" ou \"Novo Frete\".\n"
    "2. Origem da Carga: \"Parada 1\" + endereço + tipo + operação.\n"
    "...\n"
    "(etc)\n\n"
    "Contexto:\n{context}\n\n"
    "Pergunta: {question}\n"
    "Resposta:"
)
prompt = PromptTemplate.from_template(template)

qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff",
    chain_type_kwargs={"prompt": prompt}
)

# 6. Rota principal
@app.route("/", methods=["GET", "POST"])
def index():
    resposta = ""
    if request.method == "POST":
        pergunta = request.form["pergunta"]
        resultado = qa.invoke(pergunta)
        resposta_texto = resultado.get("result", "")
        resposta = re.sub(r"<think>.*?</think>", "", resposta_texto, flags=re.DOTALL).strip()
        salvar_log(pergunta, resposta)
    return render_template("index.html", resposta=resposta)

if __name__ == "__main__":
    app.run(debug=True)
