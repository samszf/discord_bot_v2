"""
classes.py — Definição das classes disponíveis, bônus por nível e habilidades.

Atualmente implementadas: Guerreiro, Mago, Bárbaro.
Estrutura preparada para receber as 13 classes de D&D.
"""

CLASSES: dict[str, dict] = {

    # ── GUERREIRO ─────────────────────────────────────────
    "Guerreiro": {
        "emoji":       "⚔️",
        "role":        "Tank / DPS",
        "descricao":   "Mestre das armas, resistente e letal em qualquer campo de batalha.",
        "bonus_hp_inicial":      25,
        "bonus_atk_inicial":     4,
        "bonus_defesa_inicial":  5,
        "crescimento_por_nivel": {"hp": 10, "atk": 3, "defesa": 2},
        "habilidades": ["segunda_investida", "surto_de_acao", "postura_defensiva", "campiao_invicto"],
    },

    # ── MAGO ──────────────────────────────────────────────
    "Mago": {
        "emoji":       "🧙",
        "role":        "Mágico / DPS",
        "descricao":   "Estudioso arcano que domina os feitiços mais poderosos do universo.",
        "bonus_hp_inicial":      5,
        "bonus_atk_inicial":     7,
        "bonus_defesa_inicial":  0,
        "crescimento_por_nivel": {"hp": 4, "atk": 4, "defesa": 0},
        "habilidades": ["missil_magico", "bola_de_fogo", "armadura_arcana", "magia_suprema"],
    },

    # ── BÁRBARO ───────────────────────────────────────────
    "Bárbaro": {
        "emoji":       "💢",
        "role":        "Tank / DPS",
        "descricao":   "Guerreiro selvagem que entra em fúria para devastar inimigos.",
        "bonus_hp_inicial":      30,
        "bonus_atk_inicial":     5,
        "bonus_defesa_inicial":  2,
        "crescimento_por_nivel": {"hp": 12, "atk": 3, "defesa": 1},
        "habilidades": ["furia", "ataque_imprudente", "resistencia_brutal", "furia_persistente"],
    },
}


# ── Helpers ────────────────────────────────────────────────

def bonus_por_nivel(classe: str) -> dict:
    """Retorna o crescimento de stats por nível da classe."""
    dados = CLASSES.get(classe)
    if not dados:
        return {"hp": 0, "atk": 0, "defesa": 0}
    return dados["crescimento_por_nivel"]


def habilidades_disponiveis(classe: str, nivel: int) -> list[str]:
    """
    Retorna as habilidades desbloqueadas para a classe no nível informado.
    Desbloqueio: nível 1, 3, 6 e 10.
    """
    dados = CLASSES.get(classe)
    if not dados:
        return []

    niveis_desbloqueio = [1, 3, 6, 10]
    disponiveis = []

    for i, nivel_minimo in enumerate(niveis_desbloqueio):
        if nivel >= nivel_minimo and i < len(dados["habilidades"]):
            disponiveis.append(dados["habilidades"][i])

    return disponiveis


def listar_classes() -> list[str]:
    """Retorna os nomes de todas as classes disponíveis."""
    return list(CLASSES.keys())
