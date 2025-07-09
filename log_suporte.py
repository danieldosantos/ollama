import sqlite3
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def init_db():
    """Initialize the SQLite database."""
    db_path = BASE_DIR / "db.sqlite"
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pergunta TEXT,
                resposta TEXT,
                data TEXT
            )
        """)

def salvar_log(pergunta, resposta):
    """Save a question/answer pair to the log."""
    db_path = BASE_DIR / "db.sqlite"
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO logs (pergunta, resposta, data) VALUES (?, ?, ?)",
            (pergunta, resposta, datetime.now().isoformat())
        )

