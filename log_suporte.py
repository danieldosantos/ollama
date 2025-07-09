import sqlite3
from datetime import datetime

def init_db():
    """Initialize the SQLite database."""
    with sqlite3.connect("db.sqlite") as conn:
        cur = conn.cursor()
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pergunta TEXT,
            resposta TEXT,
            data TEXT
        )
        """
        )

def salvar_log(pergunta, resposta):
    """Save a question/answer pair to the log."""
    with sqlite3.connect("db.sqlite") as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO logs (pergunta, resposta, data) VALUES (?, ?, ?)",
            (pergunta, resposta, datetime.now().isoformat()),
        )
