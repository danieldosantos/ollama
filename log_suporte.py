import sqlite3
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent

def init_db():
    """Initialize the SQLite database."""
    db_path = BASE_DIR / "db.sqlite"
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            try:
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
            except sqlite3.Error as e:
                logger.error("Erro ao criar tabela de logs: %s", e)
            else:
                conn.commit()
    except sqlite3.Error as e:
        logger.error("Erro ao conectar ao banco de dados: %s", e)

def salvar_log(pergunta, resposta):
    """Save a question/answer pair to the log."""
    db_path = BASE_DIR / "db.sqlite"
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            try:
                cur.execute(
                    "INSERT INTO logs (pergunta, resposta, data) VALUES (?, ?, ?)",
                    (pergunta, resposta, datetime.now().isoformat()),
                )
            except sqlite3.Error as e:
                logger.error("Erro ao registrar log: %s", e)
            else:
                conn.commit()
    except sqlite3.Error as e:
        logger.error("Erro ao conectar ao banco de dados: %s", e)

