"""
repository.py — Centraliza todo acesso ao banco de dados.

Regra: nenhum outro módulo deve importar sqlite3 ou get_connection diretamente.
Todo SQL passa por aqui.
"""

from database.connection import get_connection


# ─────────────────────────────────────────
# PLAYERS
# ─────────────────────────────────────────

def criar_player(user_id: int) -> bool:
    """
    Cria um novo jogador. Retorna True se criou, False se já existe.
    Também inicializa equipment e battle_stats automaticamente.
    """
    with get_connection() as conn:
        player = conn.execute(
            "SELECT user_id FROM players WHERE user_id = ?", (user_id,)
        ).fetchone()

        if player:
            return False

        conn.execute(
            "INSERT INTO players (user_id) VALUES (?)", (user_id,)
        )
        conn.execute(
            "INSERT INTO equipment (user_id) VALUES (?)", (user_id,)
        )
        conn.execute(
            "INSERT INTO battle_stats (user_id) VALUES (?)", (user_id,)
        )
        return True


def buscar_player(user_id: int) -> dict | None:
    """Retorna os dados do jogador ou None se não existir."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM players WHERE user_id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None


def atualizar_player(user_id: int, **campos) -> None:
    """
    Atualiza campos do jogador dinamicamente.
    Exemplo: atualizar_player(123, xp=50, ouro=200)
    """
    if not campos:
        return
    set_clause = ", ".join(f"{col} = ?" for col in campos)
    valores = list(campos.values()) + [user_id]
    with get_connection() as conn:
        conn.execute(
            f"UPDATE players SET {set_clause} WHERE user_id = ?", valores
        )


# ─────────────────────────────────────────
# XP E NÍVEL
# ─────────────────────────────────────────

def adicionar_xp(user_id: int, xp: int) -> dict:
    """
    Adiciona XP ao jogador e verifica level up.
    Retorna dict com: xp_atual, nivel_atual, level_up (bool), niveis_ganhos (int).
    """
    from utils.xp import xp_para_nivel

    player = buscar_player(user_id)
    if not player:
        return {}

    novo_xp = player["xp"] + xp
    nivel_atual = player["nivel"]
    niveis_ganhos = 0

    while novo_xp >= xp_para_nivel(nivel_atual + 1):
        novo_xp -= xp_para_nivel(nivel_atual + 1)
        nivel_atual += 1
        niveis_ganhos += 1

    atualizar_player(user_id, xp=novo_xp, nivel=nivel_atual)

    return {
        "xp_atual": novo_xp,
        "nivel_atual": nivel_atual,
        "level_up": niveis_ganhos > 0,
        "niveis_ganhos": niveis_ganhos,
    }


# ─────────────────────────────────────────
# OURO
# ─────────────────────────────────────────

def adicionar_ouro(user_id: int, quantidade: int) -> int:
    """Adiciona ouro. Retorna o novo saldo."""
    player = buscar_player(user_id)
    novo_saldo = player["ouro"] + quantidade
    atualizar_player(user_id, ouro=novo_saldo)
    return novo_saldo


def remover_ouro(user_id: int, quantidade: int) -> bool:
    """
    Remove ouro se houver saldo suficiente.
    Retorna True se conseguiu, False se saldo insuficiente.
    """
    player = buscar_player(user_id)
    if player["ouro"] < quantidade:
        return False
    atualizar_player(user_id, ouro=player["ouro"] - quantidade)
    return True


# ─────────────────────────────────────────
# INVENTÁRIO
# ─────────────────────────────────────────

def buscar_inventario(user_id: int) -> list[dict]:
    """Retorna todos os itens do inventário do jogador."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM inventory WHERE user_id = ? ORDER BY item_id",
            (user_id,)
        ).fetchall()
        return [dict(row) for row in rows]


def adicionar_item(user_id: int, item_id: str, quantidade: int = 1) -> None:
    """Adiciona item ao inventário. Empilha se já existir."""
    with get_connection() as conn:
        existente = conn.execute(
            "SELECT id, quantidade FROM inventory WHERE user_id = ? AND item_id = ?",
            (user_id, item_id)
        ).fetchone()

        if existente:
            conn.execute(
                "UPDATE inventory SET quantidade = quantidade + ? WHERE id = ?",
                (quantidade, existente["id"])
            )
        else:
            conn.execute(
                "INSERT INTO inventory (user_id, item_id, quantidade) VALUES (?, ?, ?)",
                (user_id, item_id, quantidade)
            )


def remover_item(user_id: int, item_id: str, quantidade: int = 1) -> bool:
    """
    Remove quantidade de um item do inventário.
    Retorna True se conseguiu, False se não tem quantidade suficiente.
    """
    with get_connection() as conn:
        existente = conn.execute(
            "SELECT id, quantidade FROM inventory WHERE user_id = ? AND item_id = ?",
            (user_id, item_id)
        ).fetchone()

        if not existente or existente["quantidade"] < quantidade:
            return False

        if existente["quantidade"] == quantidade:
            conn.execute("DELETE FROM inventory WHERE id = ?", (existente["id"],))
        else:
            conn.execute(
                "UPDATE inventory SET quantidade = quantidade - ? WHERE id = ?",
                (quantidade, existente["id"])
            )
        return True


# ─────────────────────────────────────────
# EQUIPAMENTOS
# ─────────────────────────────────────────

def buscar_equipment(user_id: int) -> dict | None:
    """Retorna os equipamentos do jogador."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM equipment WHERE user_id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None


def atualizar_equipment(user_id: int, slot: str, item_id: str | None) -> None:
    """
    Equipa ou desequipa um item em um slot.
    slot deve ser: 'arma', 'armadura' ou 'acessorio'.
    Passar item_id=None para desequipar.
    """
    slots_validos = {"arma", "armadura", "acessorio"}
    if slot not in slots_validos:
        raise ValueError(f"Slot inválido: '{slot}'. Use: {slots_validos}")

    with get_connection() as conn:
        conn.execute(
            f"UPDATE equipment SET {slot} = ? WHERE user_id = ?",
            (item_id, user_id)
        )


# ─────────────────────────────────────────
# COOLDOWNS
# ─────────────────────────────────────────

def buscar_cooldown(user_id: int, comando: str) -> str | None:
    """Retorna o timestamp do último uso ou None."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT ultimo_uso FROM cooldowns WHERE user_id = ? AND comando = ?",
            (user_id, comando)
        ).fetchone()
        return row["ultimo_uso"] if row else None


def registrar_cooldown(user_id: int, comando: str) -> None:
    """Registra ou atualiza o timestamp de uso de um comando."""
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO cooldowns (user_id, comando, ultimo_uso)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, comando) DO UPDATE SET ultimo_uso = CURRENT_TIMESTAMP
            """,
            (user_id, comando)
        )


# ─────────────────────────────────────────
# BATTLE STATS
# ─────────────────────────────────────────

def atualizar_battle_stats(
    user_id: int,
    vitoria: bool,
    dano_causado: int = 0,
    slimes_derrotados: int = 0
) -> None:
    """Atualiza as estatísticas de batalha do jogador."""
    with get_connection() as conn:
        if vitoria:
            conn.execute(
                """
                UPDATE battle_stats
                SET vitorias = vitorias + 1,
                    dano_total = dano_total + ?,
                    slimes_derrotados = slimes_derrotados + ?
                WHERE user_id = ?
                """,
                (dano_causado, slimes_derrotados, user_id)
            )
        else:
            conn.execute(
                """
                UPDATE battle_stats
                SET derrotas = derrotas + 1,
                    dano_total = dano_total + ?
                WHERE user_id = ?
                """,
                (dano_causado, user_id)
            )


def buscar_battle_stats(user_id: int) -> dict | None:
    """Retorna as estatísticas de batalha do jogador."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM battle_stats WHERE user_id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None
