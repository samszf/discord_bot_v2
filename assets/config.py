"""
assets/config.py — URLs centralizadas de todos os assets visuais do bot.

Como usar:
1. O designer sobe as imagens na pasta assets/ do repositório
2. Copie a URL raw do GitHub de cada imagem:
   https://raw.githubusercontent.com/samszf/discord_bot_v2/main/assets/pasta/arquivo.png
3. Preencha os campos abaixo
4. Faça o commit — o bot já usa as imagens automaticamente

Deixe como None enquanto a imagem não estiver pronta.
O bot ignora campos None e continua funcionando normalmente.
"""

# ── IDENTIDADE DO BOT ─────────────────────────────────────
# assets/ui/logo.png
# assets/ui/banner.png

LOGO_BOT     = None
BANNER_GERAL = None


# ── SLIMES ────────────────────────────────────────────────
# assets/slimes/slime_1.png → Slime Comum
# assets/slimes/slime_2.png → Slime Reforçado
# assets/slimes/slime_3.png → Slime Raro
# assets/slimes/slime_4.png → Slime Mutante
# assets/slimes/slime_5.png → Slime Elite
# assets/slimes/slime_6.png → Slime Ancestral
# assets/slimes/slime_7.png → Cubo Gelatinoso Supremo

SLIMES = {
    1: https://raw.githubusercontent.com/samszf/discord_bot_v2/refs/heads/main/assets/slimes/slime_1.png,
    2: https://raw.githubusercontent.com/samszf/discord_bot_v2/refs/heads/main/assets/slimes/slime_2.png,
    3: https://raw.githubusercontent.com/samszf/discord_bot_v2/refs/heads/main/assets/slimes/slime_3.png,
    4: https://raw.githubusercontent.com/samszf/discord_bot_v2/refs/heads/main/assets/slimes/slime_4.png,
    5: https://raw.githubusercontent.com/samszf/discord_bot_v2/refs/heads/main/assets/slimes/slime_5.png,
    6: https://raw.githubusercontent.com/samszf/discord_bot_v2/refs/heads/main/assets/slimes/slime_6.png,
    7: https://raw.githubusercontent.com/samszf/discord_bot_v2/refs/heads/main/assets/slimes/slime_7.png,
}


# ── RESULTADOS DE BATALHA ─────────────────────────────────
# assets/ui/vitoria.png
# assets/ui/derrota.png

BANNER_VITORIA = None
BANNER_DERROTA = None


# ── RARIDADES ─────────────────────────────────────────────
# assets/raridades/comum.png
# assets/raridades/incomum.png
# assets/raridades/raro.png
# assets/raridades/epico.png
# assets/raridades/lendario.png
# assets/raridades/divino.png

RARIDADES = {
    "comum":    None,
    "incomum":  None,
    "raro":     None,
    "epico":    None,
    "lendario": None,
    "divino":   None,
}


# ── SLOTS DE EQUIPAMENTO ──────────────────────────────────
# assets/ui/slot_arma.png
# assets/ui/slot_armadura.png
# assets/ui/slot_acessorio.png

SLOTS = {
    "arma":      None,
    "armadura":  None,
    "acessorio": None,
}


# ── STATS ─────────────────────────────────────────────────
# assets/ui/stat_hp.png
# assets/ui/stat_atk.png
# assets/ui/stat_defesa.png
# assets/ui/stat_xp.png
# assets/ui/stat_ouro.png

STATS = {
    "hp":     None,
    "atk":    None,
    "defesa": None,
    "xp":     None,
    "ouro":   None,
}


# ── CLASSES ───────────────────────────────────────────────
# assets/classes/guerreiro.png
# assets/classes/mago.png
# ... etc

CLASSES = {
    "Guerreiro":   None,
    "Mago":        None,
    "Barbaro":     None,
    "Paladino":    None,
    "Clerigo":     None,
    "Ladino":      None,
    "Monge":       None,
    "Bardo":       None,
    "Druida":      None,
    "Feiticeiro":  None,
    "Bruxo":       None,
    "Patrulheiro": None,
    "Artifice":    None,
}


# ── ITENS ─────────────────────────────────────────────────
# assets/itens/<item_id>.png

ITENS = {
    # armas
    "espada_enferrujada": None,
    "adaga_afiada":       None,
    "espada_longa":       None,
    "machado_guerra":     None,
    "lamina_abissal":     None,
    "espadao_divino":     None,
    # armaduras
    "roupa_surrada":      None,
    "gibao_couro":        None,
    "cota_malha":         None,
    "armadura_placas":    None,
    "manto_sombrio":      None,
    "aegis_celestial":    None,
    # acessorios
    "amuleto_madeira":    None,
    "anel_prata":         None,
    "colar_rubi":         None,
    "bracelete_titanio":  None,
    "orbe_arcano":        None,
    "coroa_eternidade":   None,
    # consumiveis
    "pocao_vida":         None,
    "pocao_vida_maior":   None,
    "elixir_poder":       None,
}


# ── Helpers ────────────────────────────────────────────────

def get_slime(dificuldade: int) -> str | None:
    """Retorna a URL da imagem do slime ou None se não configurada."""
    return SLIMES.get(dificuldade)

def get_classe(classe: str) -> str | None:
    """Retorna a URL da imagem da classe ou None se não configurada."""
    return CLASSES.get(classe)

def get_item(item_id: str) -> str | None:
    """Retorna a URL da imagem do item ou None se não configurada."""
    return ITENS.get(item_id)

def get_raridade(raridade: str) -> str | None:
    """Retorna o ícone de raridade ou None se não configurado."""
    return RARIDADES.get(raridade)
