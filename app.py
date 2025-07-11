from flask import Flask, render_template, request
from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from log_suporte import init_db, salvar_log
from pathlib import Path
import re
from config import OLLAMA_BASE_URL, OLLAMA_MODEL, FLASK_DEBUG

app = Flask(__name__)
init_db()

# Caminho base
BASE_DIR = Path(__file__).resolve().parent

# Texto completo do manual
arquivo_manual = BASE_DIR / "documentacao_estruturada.txt"
with open(arquivo_manual, "r", encoding="utf-8") as f:
    manual_text = f.read()

# Modelo Ollama
llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)

# Prompt restritivo e direto com o manual incorporado
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
    f"Conteúdo do manual:\n{manual_text}\n\n"
    "Pergunta do usuário: {question}\n\n"
    "Resposta:"
)
prompt = PromptTemplate.from_template(template)

# Rota principal
@app.route("/", methods=["GET", "POST"])
def index():
    resposta = ""
    if request.method == "POST":
        pergunta = request.form["pergunta"]

        raw = llm.invoke(prompt.format(question=pergunta))
        resposta_texto = getattr(raw, "content", str(raw))
        resposta_limpa = re.sub(r"<think>.*?</think>", "", resposta_texto, flags=re.DOTALL).strip()

        if not resposta_limpa:
            resposta_limpa = "Essa informação não está disponível no manual."

        salvar_log(pergunta, resposta_limpa)
        resposta = resposta_limpa

    return render_template("index.html", resposta=resposta)

if __name__ == "__main__":
    app.run(debug=FLASK_DEBUG)
