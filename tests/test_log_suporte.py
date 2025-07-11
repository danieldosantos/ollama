import sqlite3
from pathlib import Path
import sys

# Ensure the project root is on the import path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import log_suporte


def test_init_and_salvar_log(tmp_path, monkeypatch):
    # Use a temporary directory for the database file
    monkeypatch.setattr(log_suporte, "BASE_DIR", tmp_path)

    db_file = tmp_path / "db.sqlite"

    # Initialize the database
    log_suporte.init_db()
    assert db_file.exists(), "Database file was not created"

    # Insert a log entry
    pergunta = "Como acessar?"
    resposta = "Use a opção X"
    log_suporte.salvar_log(pergunta, resposta)

    # Verify entry was saved
    with sqlite3.connect(db_file) as conn:
        cur = conn.cursor()
        cur.execute("SELECT pergunta, resposta FROM logs")
        row = cur.fetchone()

    assert row == (pergunta, resposta)
