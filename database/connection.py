import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "data/rpg.db")

_connection: sqlite3.Connection | None = None


def get_connection() -> sqlite3.Connection:
    """
    Retorna a conexão singleton com o banco SQLite.
    Cria a conexão na primeira chamada e reutiliza nas seguintes.
    """
    global _connection

    if _connection is None:
        dir_path = os.path.dirname(DB_PATH)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        _connection = sqlite3.connect(DB_PATH, check_same_thread=False)
        _connection.row_factory = sqlite3.Row
        _connection.execute("PRAGMA journal_mode=WAL")
        _connection.execute("PRAGMA foreign_keys=ON")

    return _connection


def inicializar_banco() -> None:
    """Cria todas as tabelas se ainda não existirem."""
    from database.schema import SCHEMA
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.commit()


def fechar_conexao() -> None:
    """Fecha a conexão com o banco. Útil para testes e shutdown."""
    global _connection
    if _connection:
        _connection.close()
        _connection = None
