"""
player.py — Lógica de criação e gerenciamento de jogadores.
"""

from database import repository as repo
from utils.xp import xp_para_nivel


def registrar_jogador(user_id: int) -> dict:
    """
    Registra um novo jogador.
    Retorna dict com: sucesso (bool), mensagem (str).
    """
    criado = repo.criar_player(user_id)

    if not criado:
        return {
            "sucesso": False,
            "mensagem": "Você já possui um personagem registrado!",
        }

    return {
        "sucesso": True,
        "mensagem": "Personagem criado com sucesso!",
    }


def buscar_stats_completos(user_id: int) -> dict | None:
    """
    Retorna todos os dados do jogador consolidados:
    stats base, equipamentos, bônus de itens e stats finais.
    Retorna None se jogador não existir.
    """
    player = repo.buscar_player(user_id)
    if not player:
        return None

    equipment = repo.buscar_equipment(user_id)
    battle_stats = repo.buscar_battle_stats(user_id)

    bonus = calcular_bonus_equipamentos(equipment)

    return {
        # dados base
        "user_id":    player["user_id"],
        "nivel":      player["nivel"],
        "xp":         player["xp"],
        "xp_proximo": xp_para_nivel(player["nivel"] + 1),
        "ouro":       player["ouro"],
        "classe":     player["classe"],
        "criado_em":  player["criado_em"],

        # stats base
        "hp_base":     player["hp_base"],
        "atk_base":    player["atk_base"],
        "defesa_base": player["defesa_base"],

        # bônus de equipamentos
        "bonus_atk":    bonus["atk"],
        "bonus_defesa": bonus["defesa"],
        "bonus_hp":     bonus["hp"],

        # stats finais
        "hp_total":     player["hp_base"]     + bonus["hp"],
        "atk_total":    player["atk_base"]    + bonus["atk"],
        "defesa_total": player["defesa_base"] + bonus["defesa"],

        # equipamentos
        "arma":      equipment["arma"]      if equipment else None,
        "armadura":  equipment["armadura"]  if equipment else None,
        "acessorio": equipment["acessorio"] if equipment else None,

        # batalhas
        "vitorias":          battle_stats["vitorias"]          if battle_stats else 0,
        "derrotas":          battle_stats["derrotas"]          if battle_stats else 0,
        "slimes_derrotados": battle_stats["slimes_derrotados"] if battle_stats else 0,
        "dano_total":        battle_stats["dano_total"]        if battle_stats else 0,
    }


def calcular_bonus_equipamentos(equipment: dict | None) -> dict:
    """
    Soma os bônus de todos os itens equipados.
    Retorna dict com atk, defesa, hp.
    """
    from utils.items import ITENS

    bonus = {"atk": 0, "defesa": 0, "hp": 0}

    if not equipment:
        return bonus

    for slot in ("arma", "armadura", "acessorio"):
        item_id = equipment.get(slot)
        if item_id and item_id in ITENS:
            item = ITENS[item_id]
            bonus["atk"]    += item.get("atk", 0)
            bonus["defesa"] += item.get("defesa", 0)
            bonus["hp"]     += item.get("hp", 0)

    return bonus
