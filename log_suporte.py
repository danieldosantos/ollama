import sqlite3
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def init_db():
    conn = sqlite3.connect(str(BASE_DIR / "db.sqlite"))
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pergunta TEXT,
            resposta TEXT,
            data TEXT
        )
    """)
    conn.commit()
    conn.close()

def salvar_log(pergunta, resposta):
    conn = sqlite3.connect(str(BASE_DIR / "db.sqlite"))
    cur = conn.cursor()
    cur.execute("INSERT INTO logs (pergunta, resposta, data) VALUES (?, ?, ?)",
                (pergunta, resposta, datetime.now().isoformat()))
    conn.commit()
    conn.close()
