# Ollama Documentation Chatbot

This project provides a simple Flask web application that lets you chat in Portuguese with an assistant named **C3PO**. The assistant answers questions based on the contents of `documentacao_estruturada.txt`, using [LangChain](https://python.langchain.com/) and the Ollama `gemma:2b` model. The manual is stored in this file and is automatically loaded when the application starts.

## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use .venv\Scripts\activate
   ```
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

Make sure you have the Ollama service running locally with the `gemma:2b` model available.

## Running the application

Start the Flask server with:
```bash
python app.py
```
The app will be available at `http://127.0.0.1:5000/` by default.

## Web interface

The homepage displays a chat box where you can type a question about the Nexxo platform. When you submit your question, the page shows the assistant's answer below the form. All interactions are stored in `db.sqlite` for later reference.
