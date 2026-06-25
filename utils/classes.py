"""
classes.py — Definição das 13 classes de D&D, bônus por nível e habilidades.
"""

CLASSES: dict[str, dict] = {

    # ── GUERREIRO ─────────────────────────────────────────
    "Guerreiro": {
        "emoji":       "⚔",
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

    # ── PALADINO ──────────────────────────────────────────
    "Paladino": {
        "emoji":       "🛡",
        "role":        "Tank / Suporte",
        "descricao":   "Cavaleiro sagrado que combina força de combate com cura divina.",
        "bonus_hp_inicial":      25,
        "bonus_atk_inicial":     3,
        "bonus_defesa_inicial":  6,
        "crescimento_por_nivel": {"hp": 10, "atk": 2, "defesa": 3},
        "habilidades": ["imposicao_de_maos", "golpe_divino", "aura_de_protecao", "juramento_sagrado"],
    },

    # ── CLÉRIGO ───────────────────────────────────────────
    "Clérigo": {
        "emoji":       "✝",
        "role":        "Suporte / Tank",
        "descricao":   "Servidor divino que cura aliados e castiga inimigos com luz sagrada.",
        "bonus_hp_inicial":      20,
        "bonus_atk_inicial":     2,
        "bonus_defesa_inicial":  5,
        "crescimento_por_nivel": {"hp": 8, "atk": 1, "defesa": 2},
        "habilidades": ["palavra_de_cura", "punir_o_mal", "escudo_da_fe", "milagre_divino"],
    },

    # ── LADINO ────────────────────────────────────────────
    "Ladino": {
        "emoji":       "🗡",
        "role":        "DPS",
        "descricao":   "Especialista em ataques precisos e devastadores nas brechas do inimigo.",
        "bonus_hp_inicial":      10,
        "bonus_atk_inicial":     6,
        "bonus_defesa_inicial":  2,
        "crescimento_por_nivel": {"hp": 6, "atk": 4, "defesa": 1},
        "habilidades": ["ataque_furtivo", "evasao", "golpe_baixo", "morte_subita"],
    },

    # ── MONGE ─────────────────────────────────────────────
    "Monge": {
        "emoji":       "👊",
        "role":        "DPS",
        "descricao":   "Mestre das artes marciais que canaliza ki para golpes devastadores.",
        "bonus_hp_inicial":      15,
        "bonus_atk_inicial":     5,
        "bonus_defesa_inicial":  3,
        "crescimento_por_nivel": {"hp": 7, "atk": 3, "defesa": 2},
        "habilidades": ["torrente_de_golpes", "passo_do_vento", "ataque_ki", "corpo_vazio"],
    },

    # ── BARDO ─────────────────────────────────────────────
    "Bardo": {
        "emoji":       "🎵",
        "role":        "Suporte / DPS",
        "descricao":   "Artista versátil que inspira aliados e confunde inimigos com sua música.",
        "bonus_hp_inicial":      10,
        "bonus_atk_inicial":     3,
        "bonus_defesa_inicial":  2,
        "crescimento_por_nivel": {"hp": 7, "atk": 2, "defesa": 1},
        "habilidades": ["inspiracao_bardica", "palavra_de_cura_bardo", "encantamento", "cancao_do_descanso"],
    },

    # ── DRUIDA ────────────────────────────────────────────
    "Druida": {
        "emoji":       "🌿",
        "role":        "Suporte / DPS",
        "descricao":   "Guardião da natureza que assume formas animais e conjura a força da terra.",
        "bonus_hp_inicial":      15,
        "bonus_atk_inicial":     2,
        "bonus_defesa_inicial":  3,
        "crescimento_por_nivel": {"hp": 8, "atk": 2, "defesa": 1},
        "habilidades": ["forma_selvagem", "cura_natural", "chamado_da_natureza", "furia_da_tempestade"],
    },

    # ── FEITICEIRO ────────────────────────────────────────
    "Feiticeiro": {
        "emoji":       "🔥",
        "role":        "Mágico / DPS",
        "descricao":   "Mago nato cujo poder emana do sangue — conjura feitiços devastadores.",
        "bonus_hp_inicial":      5,
        "bonus_atk_inicial":     8,
        "bonus_defesa_inicial":  0,
        "crescimento_por_nivel": {"hp": 5, "atk": 4, "defesa": 0},
        "habilidades": ["toque_de_chamas", "metamagia", "explosao_de_caos", "surto_de_magia"],
    },

    # ── BRUXO ─────────────────────────────────────────────
    "Bruxo": {
        "emoji":       "👁",
        "role":        "Mágico / DPS",
        "descricao":   "Fez um pacto com entidades sombrias em troca de poder devastador.",
        "bonus_hp_inicial":      10,
        "bonus_atk_inicial":     6,
        "bonus_defesa_inicial":  1,
        "crescimento_por_nivel": {"hp": 6, "atk": 4, "defesa": 0},
        "habilidades": ["maldicao_do_hexblade", "toque_eldritch", "olho_do_patrono", "pacto_de_sangue"],
    },

    # ── PATRULHEIRO ───────────────────────────────────────
    "Patrulheiro": {
        "emoji":       "🏹",
        "role":        "DPS",
        "descricao":   "Rastreador habilidoso que marca presas e as caça com precisão mortal.",
        "bonus_hp_inicial":      15,
        "bonus_atk_inicial":     6,
        "bonus_defesa_inicial":  2,
        "crescimento_por_nivel": {"hp": 7, "atk": 3, "defesa": 1},
        "habilidades": ["marca_do_cacador", "chuva_de_flechas", "sentidos_agucados", "golpe_colossal"],
    },

    # ── ARTÍFICE ──────────────────────────────────────────
    "Artífice": {
        "emoji":       "⚙",
        "role":        "Suporte / DPS",
        "descricao":   "Inventor genial que usa engenhos mágicos para combater e apoiar aliados.",
        "bonus_hp_inicial":      15,
        "bonus_atk_inicial":     4,
        "bonus_defesa_inicial":  4,
        "crescimento_por_nivel": {"hp": 7, "atk": 2, "defesa": 2},
        "habilidades": ["infusao_magica", "torrinha_de_batalha", "elixir_do_artificer", "golem_de_ferro"],
    },
}


# ── Helpers ────────────────────────────────────────────────

def bonus_por_nivel(classe: str) -> dict:
    dados = CLASSES.get(classe)
    if not dados:
        return {"hp": 0, "atk": 0, "defesa": 0}
    return dados["crescimento_por_nivel"]


def habilidades_disponiveis(classe: str, nivel: int) -> list[str]:
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
    return list(CLASSES.keys())
