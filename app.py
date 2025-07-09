from flask import Flask, render_template, request
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from log_suporte import init_db, salvar_log
import re

app = Flask(__name__)
init_db()

# 1. Carrega o conteúdo do .txt (UTF-8)
loader = TextLoader("documentacao.txt", encoding="utf-8")
docs = loader.load()

# 2. Split em chunks maiores
splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = splitter.split_documents(docs)

# 3. Embeddings e armazenamento vetorial com modelo gemma
embedding = OllamaEmbeddings(model="gemma:2b")
db = Chroma.from_documents(chunks, embedding, persist_directory="chroma_db")

# 4. Modelo e retriever com contexto ampliado
retriever = db.as_retriever(search_kwargs={"k": 8})
llm = ChatOllama(model="gemma:2b", base_url="http://localhost:11434")

# 5. Prompt reforçado
template = (
    "Você é C3PO, o assistente virtual oficial da plataforma Nexxo.\n"
    "Responda sempre em português do Brasil, com clareza e objetividade.\n"
    "Use apenas o conteúdo abaixo (extraído do manual) para responder com precisão.\n"
    "Nunca diga que não sabe ou que o usuário deve consultar o manual. Se a informação estiver no texto, traga-a diretamente.\n\n"
    "Contexto:\n{context}\n\n"
    "Pergunta: {question}\n"
    "Resposta:"
)
prompt = PromptTemplate.from_template(template)

qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
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
