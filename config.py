import os

# Base URL for the Ollama service
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Name of the model to use
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

# Enable Flask debug mode when set to a truthy value
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() in ("1", "true", "yes")
