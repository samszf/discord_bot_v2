"""
habilidades.py — Habilidades ativas das classes.

Cada habilidade recebe e retorna o estado do combate.
Estrutura preparada para receber as 13 classes futuramente.
"""

import random


HABILIDADES: dict[str, dict] = {}


def registrar(hab_id: str, nome: str, emoji: str,
              descricao: str, nivel_minimo: int, cooldown_turnos: int):
    """Decorator para registrar uma habilidade no catálogo."""
    def decorator(fn):
        HABILIDADES[hab_id] = {
            "id":              hab_id,
            "nome":            nome,
            "emoji":           emoji,
            "descricao":       descricao,
            "nivel_minimo":    nivel_minimo,
            "cooldown_turnos": cooldown_turnos,
            "efeito":          fn,
        }
        return fn
    return decorator


def executar_habilidade(hab_id: str, estado: dict) -> dict:
    """
    Executa uma habilidade no estado do combate.
    Não decrementa buffs aqui — o decremento ocorre no turno seguinte via combat_view.
    """
    hab = HABILIDADES.get(hab_id)
    if not hab:
        estado["log"] = ["❌ Habilidade não encontrada."]
        return estado

    return hab["efeito"](estado)


def _decrementar_buffs(estado: dict) -> None:
    """Decrementa os turnos de buffs ativos e remove os expirados."""
    buffs = estado.get("buffs", {})
    expirados = [k for k, v in buffs.items() if v.get("turnos", 0) <= 1]
    for k in expirados:
        buffs.pop(k)
    for v in buffs.values():
        if "turnos" in v:
            v["turnos"] -= 1


# ══════════════════════════════════════════
# GUERREIRO
# ══════════════════════════════════════════

@registrar("segunda_investida", "Segunda Investida", "⚔️",
           "Ataca duas vezes no mesmo turno.",
           nivel_minimo=1, cooldown_turnos=3)
def segunda_investida(estado: dict) -> dict:
    from utils.combat import _calcular_dano_jogador
    log = ["⚔️ **Segunda Investida!** Dois ataques precisos!"]
    for i in range(2):
        dano = _calcular_dano_jogador(estado)
        estado["slime_hp"] = max(0, estado["slime_hp"] - dano)
        estado["dano_total"] += dano
        log.append(f"  ↳ Golpe {i + 1}: **{dano}** de dano.")
        if estado["slime_hp"] <= 0:
            break
    if estado["slime_hp"] <= 0:
        estado["finalizado"] = True
        estado["vitoria"] = True
        log.append(f"💀 O **{estado['slime']['nome']}** foi derrotado!")
    else:
        dano_slime = max(1, estado["slime"]["atk"] - estado["jogador_defesa"])
        estado["jogador_hp"] = max(0, estado["jogador_hp"] - dano_slime)
        log.append(f"🟢 Inimigo contra-atacou: **{dano_slime}** de dano.")
        if estado["jogador_hp"] <= 0:
            estado["finalizado"] = True
            estado["vitoria"] = False
            log.append("💀 Você foi derrotado...")
    estado["turno"] += 1
    estado["log"] = log
    return estado


@registrar("surto_de_acao", "Surto de Ação", "💨",
           "Ataca três vezes no mesmo turno.",
           nivel_minimo=3, cooldown_turnos=6)
def surto_de_acao(estado: dict) -> dict:
    from utils.combat import _calcular_dano_jogador
    log = ["💨 **Surto de Ação!** Três golpes fulminantes!"]
    for i in range(3):
        dano = _calcular_dano_jogador(estado)
        estado["slime_hp"] = max(0, estado["slime_hp"] - dano)
        estado["dano_total"] += dano
        log.append(f"  ↳ Golpe {i + 1}: **{dano}** de dano.")
        if estado["slime_hp"] <= 0:
            break
    if estado["slime_hp"] <= 0:
        estado["finalizado"] = True
        estado["vitoria"] = True
        log.append(f"💀 O **{estado['slime']['nome']}** foi derrotado!")
    else:
        dano_slime = max(1, estado["slime"]["atk"] - estado["jogador_defesa"])
        estado["jogador_hp"] = max(0, estado["jogador_hp"] - dano_slime)
        log.append(f"🟢 Inimigo contra-atacou: **{dano_slime}** de dano.")
        if estado["jogador_hp"] <= 0:
            estado["finalizado"] = True
            estado["vitoria"] = False
            log.append("💀 Você foi derrotado...")
    estado["turno"] += 1
    estado["log"] = log
    return estado


@registrar("postura_defensiva", "Postura Defensiva", "🛡️",
           "+20 DEF por 3 turnos.",
           nivel_minimo=6, cooldown_turnos=4)
def postura_defensiva(estado: dict) -> dict:
    estado.setdefault("buffs", {})
    estado["buffs"]["postura_def"] = {"bonus_def": 20, "turnos": 3}
    estado["jogador_defesa"] += 20
    estado["log"] = ["🛡️ **Postura Defensiva!** +20 DEF por 3 turnos!"]
    return estado


@registrar("campiao_invicto", "Campeão Invicto", "👑",
           "4 ataques consecutivos, regenerando 10% HP por golpe.",
           nivel_minimo=10, cooldown_turnos=8)
def campiao_invicto(estado: dict) -> dict:
    from utils.combat import _calcular_dano_jogador
    log = ["👑 **Campeão Invicto!** Quatro golpes com regeneração!"]
    for i in range(4):
        dano = _calcular_dano_jogador(estado)
        estado["slime_hp"] = max(0, estado["slime_hp"] - dano)
        estado["dano_total"] += dano
        cura = int(estado["jogador_hp_max"] * 0.10)
        estado["jogador_hp"] = min(estado["jogador_hp_max"], estado["jogador_hp"] + cura)
        log.append(f"  ↳ Golpe {i + 1}: **{dano}** dano | +{cura} HP")
        if estado["slime_hp"] <= 0:
            break
    if estado["slime_hp"] <= 0:
        estado["finalizado"] = True
        estado["vitoria"] = True
        log.append(f"💀 O **{estado['slime']['nome']}** foi derrotado!")
    estado["turno"] += 1
    estado["log"] = log
    return estado


# ══════════════════════════════════════════
# MAGO
# ══════════════════════════════════════════

@registrar("missil_magico", "Míssil Mágico", "🔮",
           "Dano mágico garantido de 1.5x ATK, ignora defesa.",
           nivel_minimo=1, cooldown_turnos=2)
def missil_magico(estado: dict) -> dict:
    dano = max(1, int(estado["jogador_atk"] * 1.5))
    estado["slime_hp"] = max(0, estado["slime_hp"] - dano)
    estado["dano_total"] += dano
    log = [f"🔮 **Míssil Mágico!** **{dano}** de dano mágico (ignora defesa)!"]
    if estado["slime_hp"] <= 0:
        estado["finalizado"] = True
        estado["vitoria"] = True
        log.append(f"💀 O **{estado['slime']['nome']}** foi derrotado!")
    else:
        dano_slime = max(1, estado["slime"]["atk"] - estado["jogador_defesa"])
        estado["jogador_hp"] = max(0, estado["jogador_hp"] - dano_slime)
        log.append(f"🟢 Inimigo contra-atacou: **{dano_slime}** de dano.")
        if estado["jogador_hp"] <= 0:
            estado["finalizado"] = True
            estado["vitoria"] = False
            log.append("💀 Você foi derrotado...")
    estado["turno"] += 1
    estado["log"] = log
    return estado


@registrar("bola_de_fogo", "Bola de Fogo", "🎆",
           "Explosão de fogo: 3x ATK, ignora 50% da defesa.",
           nivel_minimo=3, cooldown_turnos=4)
def bola_de_fogo(estado: dict) -> dict:
    dano = max(1, estado["jogador_atk"] * 3 - estado["slime"]["defesa"] // 2)
    estado["slime_hp"] = max(0, estado["slime_hp"] - dano)
    estado["dano_total"] += dano
    log = [f"🎆 **Bola de Fogo!** **{dano}** de dano de fogo!"]
    if estado["slime_hp"] <= 0:
        estado["finalizado"] = True
        estado["vitoria"] = True
        log.append(f"💀 O **{estado['slime']['nome']}** foi derrotado!")
    else:
        dano_slime = max(1, estado["slime"]["atk"] - estado["jogador_defesa"])
        estado["jogador_hp"] = max(0, estado["jogador_hp"] - dano_slime)
        log.append(f"🟢 Inimigo contra-atacou: **{dano_slime}** de dano.")
        if estado["jogador_hp"] <= 0:
            estado["finalizado"] = True
            estado["vitoria"] = False
            log.append("💀 Você foi derrotado...")
    estado["turno"] += 1
    estado["log"] = log
    return estado


@registrar("armadura_arcana", "Armadura Arcana", "🔷",
           "+15 DEF por 4 turnos.",
           nivel_minimo=6, cooldown_turnos=5)
def armadura_arcana(estado: dict) -> dict:
    estado["jogador_defesa"] += 15
    estado.setdefault("buffs", {})
    estado["buffs"]["armadura_arcana"] = {"bonus_def": 15, "turnos": 4}
    estado["log"] = ["🔷 **Armadura Arcana!** +15 DEF por 4 turnos!"]
    return estado


@registrar("magia_suprema", "Magia Suprema", "⚡",
           "Poder absoluto: 8x ATK, ignora toda a defesa.",
           nivel_minimo=10, cooldown_turnos=10)
def magia_suprema(estado: dict) -> dict:
    dano = max(1, estado["jogador_atk"] * 8)
    estado["slime_hp"] = max(0, estado["slime_hp"] - dano)
    estado["dano_total"] += dano
    log = [f"⚡ **MAGIA SUPREMA!** **{dano}** de dano absoluto (ignora defesa)!"]
    if estado["slime_hp"] <= 0:
        estado["finalizado"] = True
        estado["vitoria"] = True
        log.append(f"💀 O **{estado['slime']['nome']}** foi derrotado!")
    else:
        dano_slime = max(1, estado["slime"]["atk"] - estado["jogador_defesa"])
        estado["jogador_hp"] = max(0, estado["jogador_hp"] - dano_slime)
        log.append(f"🟢 Inimigo contra-atacou: **{dano_slime}** de dano.")
        if estado["jogador_hp"] <= 0:
            estado["finalizado"] = True
            estado["vitoria"] = False
            log.append("💀 Você foi derrotado...")
    estado["turno"] += 1
    estado["log"] = log
    return estado


# ══════════════════════════════════════════
# BÁRBARO
# ══════════════════════════════════════════

@registrar("furia", "Fúria", "💢",
           "+75% ATK por 3 turnos. Entra em modo berserk!",
           nivel_minimo=1, cooldown_turnos=5)
def furia(estado: dict) -> dict:
    bonus = int(estado["jogador_atk"] * 0.75)
    estado["jogador_atk"] += bonus
    estado.setdefault("buffs", {})
    estado["buffs"]["furia"] = {"bonus_atk": bonus, "turnos": 3}
    estado["log"] = [f"💢 **FÚRIA!** ATK aumentou em **{bonus}** por 3 turnos!"]
    return estado


@registrar("ataque_imprudente", "Ataque Imprudente", "⚡",
           "Dois golpes devastadores, mas DEF reduzida no contra-ataque.",
           nivel_minimo=3, cooldown_turnos=3)
def ataque_imprudente(estado: dict) -> dict:
    from utils.combat import _calcular_dano_jogador
    log = ["⚡ **Ataque Imprudente!** Dois golpes sem defesa!"]
    for i in range(2):
        dano = _calcular_dano_jogador(estado)
        estado["slime_hp"] = max(0, estado["slime_hp"] - dano)
        estado["dano_total"] += dano
        log.append(f"  ↳ Golpe {i + 1}: **{dano}** de dano.")
        if estado["slime_hp"] <= 0:
            break
    if estado["slime_hp"] <= 0:
        estado["finalizado"] = True
        estado["vitoria"] = True
        log.append(f"💀 O **{estado['slime']['nome']}** foi derrotado!")
    else:
        # defesa reduzida a 50% no contra-ataque
        dano_slime = max(1, estado["slime"]["atk"] - estado["jogador_defesa"] // 2)
        estado["jogador_hp"] = max(0, estado["jogador_hp"] - dano_slime)
        log.append(f"🟢 Inimigo contra-atacou com DEF reduzida: **{dano_slime}** de dano.")
        if estado["jogador_hp"] <= 0:
            estado["finalizado"] = True
            estado["vitoria"] = False
            log.append("💀 Você foi derrotado...")
    estado["turno"] += 1
    estado["log"] = log
    return estado


@registrar("resistencia_brutal", "Resistência Brutal", "🛡️",
           "Reduz o próximo dano recebido em 80%.",
           nivel_minimo=6, cooldown_turnos=4)
def resistencia_brutal(estado: dict) -> dict:
    estado.setdefault("buffs", {})
    estado["buffs"]["resistencia"] = {"reducao_dano_pct": 0.80, "turnos": 1}
    estado["log"] = ["🛡️ **Resistência Brutal!** Próximo golpe causará apenas 20% de dano!"]
    return estado


@registrar("furia_persistente", "Fúria Persistente", "🔥",
           "+100% ATK e +50% DEF por 2 turnos. Modo berserk total.",
           nivel_minimo=10, cooldown_turnos=8)
def furia_persistente(estado: dict) -> dict:
    bonus_atk = estado["jogador_atk"]
    bonus_def = estado["jogador_defesa"] // 2
    estado["jogador_atk"] += bonus_atk
    estado["jogador_defesa"] += bonus_def
    estado.setdefault("buffs", {})
    estado["buffs"]["furia_persistente"] = {
        "bonus_atk": bonus_atk,
        "bonus_def": bonus_def,
        "turnos": 2
    }
    estado["log"] = [f"🔥 **FÚRIA PERSISTENTE!** +{bonus_atk} ATK e +{bonus_def} DEF por 2 turnos!"]
    return estado
