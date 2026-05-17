"""
loot.py — Sistema de drop de itens por raridade.
"""

import random
from utils.items import ITENS

# ── Pesos de drop por raridade ────────────────────────────

PESOS_RARIDADE = {
    "comum":    60,
    "incomum":  25,
    "raro":     10,
    "épico":    4,
    "lendário": 1,
    "divino":   0.2,
}

# chance de não dropar nada (0-100)
CHANCE_SEM_LOOT = 35


def sortear_loot(raridades_possiveis: list[str]) -> str | None:
    """
    Sorteia um item baseado nas raridades possíveis do slime.
    Retorna o item_id ou None se não dropar nada.
    """
    if random.randint(1, 100) <= CHANCE_SEM_LOOT:
        return None

    # escolhe a raridade alvo
    raridade = random.choice(raridades_possiveis)

    # filtra itens elegíveis (exclui consumíveis do loot de combate)
    elegiveis = [
        item_id for item_id, dados in ITENS.items()
        if dados["raridade"] == raridade and dados["tipo"] != "consumivel"
    ]

    if not elegiveis:
        return None

    return random.choice(elegiveis)


def sortear_ouro(ouro_min: int, ouro_max: int) -> int:
    """Sorteia a quantidade de ouro dentro do range do slime."""
    return random.randint(ouro_min, ouro_max)
