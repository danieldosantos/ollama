# Ollama Documentation Chatbot

This project provides a simple Flask web application that lets you chat in Portuguese with an assistant named **C3PO**. The assistant answers questions based on the contents of `documentacao_estruturada.txt`, using [LangChain](https://python.langchain.com/) and the Ollama `mistral` model. The manual is stored in this file and is automatically loaded when the application starts.

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

Make sure you have the Ollama service running locally with the `mistral` model available.

### Environment variables

The application reads a few settings from environment variables:

```bash
export OLLAMA_BASE_URL="http://localhost:11434"  # URL of the Ollama service
export OLLAMA_MODEL="mistral"                    # Model to load
export FLASK_DEBUG=1                             # Enable Flask debug mode
```

If these variables are not set, the values above are used by default.

## Running the application

Start the Flask server with:
```bash
python app.py
```
The app will be available at `http://127.0.0.1:5000/` by default.

## Web interface

The homepage displays a chat box where you can type a question about the Nexxo platform. When you submit your question, the page shows the assistant's answer below the form. All interactions are stored in `db.sqlite` for later reference.

## Production deployment

For production environments, run the application with a WSGI server such as [Gunicorn](https://gunicorn.org/):

```bash
gunicorn app:app
```

When using Gunicorn, the `if __name__ == "__main__":` block in `app.py` is not executed.
Make sure the environment variable `FLASK_DEBUG` is unset or set to `0` so that debug mode is disabled in production.
