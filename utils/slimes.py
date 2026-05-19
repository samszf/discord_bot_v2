"""
slimes.py — Geração procedural de slimes.

7 tipos de dificuldade, cada um com stats escaláveis e loot table própria.
"""

import random

# ── Definição dos tipos de slime ──────────────────────────

SLIMES = {
    1: {
        "nome":      "Slime Comum",
        "emoji":     "🟢",
        "hp_base":   30,
        "atk_base":  5,
        "defesa":    0,
        "xp":        22,
        "ouro":      (3, 8),
        "raridades": ["comum", "comum", "comum", "incomum"],
    },
    2: {
        "nome":      "Slime Reforçado",
        "emoji":     "🔵",
        "hp_base":   55,
        "atk_base":  9,
        "defesa":    2,
        "xp":        42,
        "ouro":      (6, 14),
        "raridades": ["comum", "incomum", "incomum"],
    },
    3: {
        "nome":      "Slime Raro",
        "emoji":     "🟣",
        "hp_base":   90,
        "atk_base":  14,
        "defesa":    4,
        "xp":        75,
        "ouro":      (12, 25),
        "raridades": ["incomum", "raro", "raro"],
    },
    4: {
        "nome":      "Slime Mutante",
        "emoji":     "🟠",
        "hp_base":   140,
        "atk_base":  20,
        "defesa":    7,
        "xp":        127,
        "ouro":      (20, 45),
        "raridades": ["incomum", "raro", "épico"],
    },
    5: {
        "nome":      "Slime Elite",
        "emoji":     "🔴",
        "hp_base":   210,
        "atk_base":  28,
        "defesa":    12,
        "xp":        195,
        "ouro":      (35, 70),
        "raridades": ["raro", "épico", "épico"],
    },
    6: {
        "nome":      "Slime Ancestral",
        "emoji":     "⚫",
        "hp_base":   300,
        "atk_base":  38,
        "defesa":    18,
        "xp":        300,
        "ouro":      (55, 110),
        "raridades": ["épico", "épico", "lendário"],
    },
    7: {
        "nome":      "Cubo Gelatinoso Supremo",
        "emoji":     "💀",
        "hp_base":   450,
        "atk_base":  55,
        "defesa":    25,
        "xp":        525,
        "ouro":      (90, 180),
        "raridades": ["épico", "lendário", "divino"],
    },
}

# ── Geração ───────────────────────────────────────────────

def gerar_slime(nivel_jogador: int) -> dict:
    """
    Gera um slime proceduralmente baseado no nível do jogador.
    Jogadores mais altos encontram slimes mais difíceis com mais frequência.
    Retorna um dict com todos os dados do slime para o combate.
    """
    dificuldade = _sortear_dificuldade(nivel_jogador)
    base = SLIMES[dificuldade]

    # variação aleatória de ±10% nos stats
    variacao = lambda v: int(v * random.uniform(0.90, 1.10))

    hp = variacao(base["hp_base"])

    return {
        "dificuldade":  dificuldade,
        "nome":         base["nome"],
        "emoji":        base["emoji"],
        "hp_max":       hp,
        "hp_atual":     hp,
        "atk":          variacao(base["atk_base"]),
        "defesa":        base["defesa"],
        "xp_recompensa": base["xp"],
        "ouro_min":     base["ouro"][0],
        "ouro_max":     base["ouro"][1],
        "raridades":    base["raridades"],
    }


def _sortear_dificuldade(nivel_jogador: int) -> int:
    """
    Sorteia a dificuldade do slime com pesos baseados no nível do jogador.
    Jogadores de nível alto têm chance de encontrar slimes mais fortes.
    """
    # dificuldade máxima que o jogador pode encontrar
    max_dif = min(7, max(1, (nivel_jogador // 3) + 2))

    # pesos: slimes mais próximos do nível do jogador têm maior chance
    pesos = []
    for d in range(1, max_dif + 1):
        distancia = abs(d - max_dif)
        pesos.append(max(1, 5 - distancia))

    dificuldades = list(range(1, max_dif + 1))
    return random.choices(dificuldades, weights=pesos, k=1)[0]
