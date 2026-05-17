"""
items.py — Catálogo completo de itens do jogo.

Os itens NÃO são armazenados completos no banco.
O banco guarda apenas o item_id; os atributos vivem aqui.
"""

ITENS: dict[str, dict] = {

    # ── ARMAS ─────────────────────────────────────────────
    "espada_enferrujada": {
        "nome":      "🗡️ Espada Enferrujada",
        "tipo":      "arma",
        "raridade":  "comum",
        "preco":     50,
        "atk":       2,
    },
    "adaga_afiada": {
        "nome":      "🔪 Adaga Afiada",
        "tipo":      "arma",
        "raridade":  "incomum",
        "preco":     120,
        "atk":       5,
    },
    "espada_longa": {
        "nome":      "⚔️ Espada Longa",
        "tipo":      "arma",
        "raridade":  "raro",
        "preco":     300,
        "atk":       10,
    },
    "machado_guerra": {
        "nome":      "🪓 Machado de Guerra",
        "tipo":      "arma",
        "raridade":  "épico",
        "preco":     800,
        "atk":       20,
    },
    "lamina_abissal": {
        "nome":      "🌑 Lâmina Abissal",
        "tipo":      "arma",
        "raridade":  "lendário",
        "preco":     2500,
        "atk":       40,
    },
    "espadao_divino": {
        "nome":      "✨ Espadão Divino",
        "tipo":      "arma",
        "raridade":  "divino",
        "preco":     10000,
        "atk":       80,
    },

    # ── ARMADURAS ─────────────────────────────────────────
    "roupa_surrada": {
        "nome":      "👕 Roupa Surrada",
        "tipo":      "armadura",
        "raridade":  "comum",
        "preco":     40,
        "defesa":    2,
    },
    "gibao_couro": {
        "nome":      "🧥 Gibão de Couro",
        "tipo":      "armadura",
        "raridade":  "incomum",
        "preco":     110,
        "defesa":    5,
    },
    "cota_malha": {
        "nome":      "⛓️ Cota de Malha",
        "tipo":      "armadura",
        "raridade":  "raro",
        "preco":     280,
        "defesa":    10,
    },
    "armadura_placas": {
        "nome":      "🛡️ Armadura de Placas",
        "tipo":      "armadura",
        "raridade":  "épico",
        "preco":     750,
        "defesa":    20,
    },
    "manto_sombrio": {
        "nome":      "🌑 Manto Sombrio",
        "tipo":      "armadura",
        "raridade":  "lendário",
        "preco":     2200,
        "defesa":    38,
    },
    "aegis_celestial": {
        "nome":      "✨ Aegis Celestial",
        "tipo":      "armadura",
        "raridade":  "divino",
        "preco":     9000,
        "defesa":    75,
    },

    # ── ACESSÓRIOS ────────────────────────────────────────
    "amuleto_madeira": {
        "nome":      "📿 Amuleto de Madeira",
        "tipo":      "acessorio",
        "raridade":  "comum",
        "preco":     30,
        "hp":        10,
    },
    "anel_prata": {
        "nome":      "💍 Anel de Prata",
        "tipo":      "acessorio",
        "raridade":  "incomum",
        "preco":     100,
        "hp":        25,
    },
    "colar_rubi": {
        "nome":      "❤️ Colar de Rubi",
        "tipo":      "acessorio",
        "raridade":  "raro",
        "preco":     260,
        "hp":        50,
        "atk":       2,
    },
    "bracelete_titânio": {
        "nome":      "⚙️ Bracelete de Titânio",
        "tipo":      "acessorio",
        "raridade":  "épico",
        "preco":     700,
        "hp":        80,
        "defesa":    5,
    },
    "orbe_arcano": {
        "nome":      "🔮 Orbe Arcano",
        "tipo":      "acessorio",
        "raridade":  "lendário",
        "preco":     2000,
        "hp":        120,
        "atk":       10,
        "defesa":    10,
    },
    "coroa_eternidade": {
        "nome":      "👑 Coroa da Eternidade",
        "tipo":      "acessorio",
        "raridade":  "divino",
        "preco":     8000,
        "hp":        250,
        "atk":       20,
        "defesa":    20,
    },

    # ── CONSUMÍVEIS ───────────────────────────────────────
    "pocao_vida": {
        "nome":      "🧪 Poção de Vida",
        "tipo":      "consumivel",
        "raridade":  "comum",
        "preco":     25,
        "cura":      30,
    },
    "pocao_vida_maior": {
        "nome":      "💊 Poção de Vida Maior",
        "tipo":      "consumivel",
        "raridade":  "incomum",
        "preco":     80,
        "cura":      80,
    },
    "elixir_poder": {
        "nome":      "⚡ Elixir de Poder",
        "tipo":      "consumivel",
        "raridade":  "raro",
        "preco":     200,
        "buff_atk":  5,
        "turnos":    3,
    },
}


# ── Helpers ────────────────────────────────────────────────

RARIDADE_ORDEM = ["comum", "incomum", "raro", "épico", "lendário", "divino"]

RARIDADE_COR = {
    "comum":    0x95A5A6,
    "incomum":  0x2ECC71,
    "raro":     0x3498DB,
    "épico":    0x9B59B6,
    "lendário": 0xF39C12,
    "divino":   0xE74C3C,
}

RARIDADE_EMOJI = {
    "comum":    "⚪",
    "incomum":  "🟢",
    "raro":     "🔵",
    "épico":    "🟣",
    "lendário": "🟠",
    "divino":   "🔴",
}


def buscar_item(item_id: str) -> dict | None:
    """Retorna os dados de um item pelo ID, ou None se não existir."""
    return ITENS.get(item_id)


def nome_item(item_id: str) -> str:
    """Retorna o nome formatado do item ou o próprio ID se não encontrado."""
    item = ITENS.get(item_id)
    return item["nome"] if item else item_id


def itens_por_tipo(tipo: str) -> dict[str, dict]:
    """Retorna todos os itens de um tipo específico."""
    return {k: v for k, v in ITENS.items() if v["tipo"] == tipo}


def itens_por_raridade(raridade: str) -> dict[str, dict]:
    """Retorna todos os itens de uma raridade específica."""
    return {k: v for k, v in ITENS.items() if v["raridade"] == raridade}
