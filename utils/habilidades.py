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

@registrar("segunda_investida", "Segunda Investida", "⚔",
           "Ataca duas vezes no mesmo turno.",
           nivel_minimo=1, cooldown_turnos=3)
def segunda_investida(estado: dict) -> dict:
    from utils.combat import _calcular_dano_jogador
    log = ["⚔ **Segunda Investida!** Dois ataques precisos!"]
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


@registrar("postura_defensiva", "Postura Defensiva", "🛡",
           "+20 DEF por 3 turnos.",
           nivel_minimo=6, cooldown_turnos=4)
def postura_defensiva(estado: dict) -> dict:
    estado.setdefault("buffs", {})
    estado["buffs"]["postura_def"] = {"bonus_def": 20, "turnos": 3}
    estado["jogador_defesa"] += 20
    estado["log"] = ["🛡 **Postura Defensiva!** +20 DEF por 3 turnos!"]
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


@registrar("resistencia_brutal", "Resistência Brutal", "🛡",
           "Reduz o próximo dano recebido em 80%.",
           nivel_minimo=6, cooldown_turnos=4)
def resistencia_brutal(estado: dict) -> dict:
    estado.setdefault("buffs", {})
    estado["buffs"]["resistencia"] = {"reducao_dano_pct": 0.80, "turnos": 1}
    estado["log"] = ["🛡 **Resistência Brutal!** Próximo golpe causará apenas 20% de dano!"]
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


# ══════════════════════════════════════════
# PALADINO
# ══════════════════════════════════════════

@registrar("imposicao_de_maos", "Imposição de Mãos", "🙏",
           "Cura 40% do HP máximo com toque sagrado.",
           nivel_minimo=1, cooldown_turnos=4)
def imposicao_de_maos(estado: dict) -> dict:
    cura = int(estado["jogador_hp_max"] * 0.40)
    estado["jogador_hp"] = min(estado["jogador_hp_max"], estado["jogador_hp"] + cura)
    estado["log"] = [f"🙏 **Imposição de Mãos!** Você recuperou **{cura} HP**!"]
    return estado


@registrar("golpe_divino", "Golpe Divino", "⚡",
           "Golpe sagrado: 2.5x ATK, ignora 50% da defesa.",
           nivel_minimo=3, cooldown_turnos=3)
def golpe_divino(estado: dict) -> dict:
    dano = max(1, int(estado["jogador_atk"] * 2.5) - estado["slime"]["defesa"] // 2)
    estado["slime_hp"] = max(0, estado["slime_hp"] - dano)
    estado["dano_total"] += dano
    log = [f"⚡ **Golpe Divino!** **{dano}** de dano sagrado!"]
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


@registrar("aura_de_protecao", "Aura de Proteção", "🌟",
           "+20 DEF permanente nesta batalha.",
           nivel_minimo=6, cooldown_turnos=0)
def aura_de_protecao(estado: dict) -> dict:
    estado["jogador_defesa"] += 20
    estado["log"] = ["🌟 **Aura de Proteção!** +20 DEF permanente nesta batalha!"]
    return estado


@registrar("juramento_sagrado", "Juramento Sagrado", "✨",
           "Cura 30% HP e causa 4x ATK de dano sagrado.",
           nivel_minimo=10, cooldown_turnos=8)
def juramento_sagrado(estado: dict) -> dict:
    cura = int(estado["jogador_hp_max"] * 0.30)
    estado["jogador_hp"] = min(estado["jogador_hp_max"], estado["jogador_hp"] + cura)
    dano = max(1, estado["jogador_atk"] * 4 - estado["slime"]["defesa"] // 2)
    estado["slime_hp"] = max(0, estado["slime_hp"] - dano)
    estado["dano_total"] += dano
    log = [f"✨ **Juramento Sagrado!** +{cura} HP e **{dano}** de dano!"]
    if estado["slime_hp"] <= 0:
        estado["finalizado"] = True
        estado["vitoria"] = True
        log.append(f"💀 O **{estado['slime']['nome']}** foi derrotado!")
    estado["turno"] += 1
    estado["log"] = log
    return estado


# ══════════════════════════════════════════
# CLÉRIGO
# ══════════════════════════════════════════

@registrar("palavra_de_cura", "Palavra de Cura", "✝",
           "Cura 30% do HP máximo.",
           nivel_minimo=1, cooldown_turnos=3)
def palavra_de_cura(estado: dict) -> dict:
    cura = int(estado["jogador_hp_max"] * 0.30)
    estado["jogador_hp"] = min(estado["jogador_hp_max"], estado["jogador_hp"] + cura)
    estado["log"] = [f"✝ **Palavra de Cura!** Você recuperou **{cura} HP**!"]
    return estado


@registrar("punir_o_mal", "Punir o Mal", "☀",
           "Dano sagrado: 2x ATK, ignora 50% da defesa inimiga.",
           nivel_minimo=3, cooldown_turnos=3)
def punir_o_mal(estado: dict) -> dict:
    dano = max(1, int(estado["jogador_atk"] * 2) - estado["slime"]["defesa"] // 2)
    estado["slime_hp"] = max(0, estado["slime_hp"] - dano)
    estado["dano_total"] += dano
    log = [f"☀ **Punir o Mal!** **{dano}** de dano sagrado!"]
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


@registrar("escudo_da_fe", "Escudo da Fé", "🌟",
           "+10 DEF permanente nesta batalha.",
           nivel_minimo=6, cooldown_turnos=0)
def escudo_da_fe(estado: dict) -> dict:
    estado["jogador_defesa"] += 10
    estado["log"] = ["🌟 **Escudo da Fé!** +10 DEF permanente nesta batalha!"]
    return estado


@registrar("milagre_divino", "Milagre Divino", "💫",
           "Restaura 100% do HP instantaneamente.",
           nivel_minimo=10, cooldown_turnos=10)
def milagre_divino(estado: dict) -> dict:
    estado["jogador_hp"] = estado["jogador_hp_max"]
    estado["log"] = ["💫 **Milagre Divino!** HP completamente restaurado!"]
    return estado


# ══════════════════════════════════════════
# LADINO
# ══════════════════════════════════════════

@registrar("ataque_furtivo", "Ataque Furtivo", "🗡",
           "35% de crítico — se acertar, causa 3x ATK.",
           nivel_minimo=1, cooldown_turnos=2)
def ataque_furtivo(estado: dict) -> dict:
    critico = random.randint(1, 100) <= 35
    dano_base = max(1, estado["jogador_atk"] - estado["slime"]["defesa"])
    dano = dano_base * 3 if critico else dano_base
    estado["slime_hp"] = max(0, estado["slime_hp"] - dano)
    estado["dano_total"] += dano
    log = [f"🗡 **Ataque Furtivo!** {'💥 CRÍTICO! ' if critico else ''}**{dano}** de dano!"]
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


@registrar("evasao", "Evasão", "💨",
           "Garante esquiva no próximo ataque inimigo.",
           nivel_minimo=3, cooldown_turnos=3)
def evasao(estado: dict) -> dict:
    estado.setdefault("buffs", {})
    estado["buffs"]["evasao"] = {"esquiva_garantida": True, "turnos": 1}
    estado["log"] = ["💨 **Evasão!** O próximo ataque inimigo será esquivado!"]
    return estado


@registrar("golpe_baixo", "Golpe Baixo", "🦵",
           "Atordoa o inimigo: -50% ATK dele por 2 turnos.",
           nivel_minimo=6, cooldown_turnos=4)
def golpe_baixo(estado: dict) -> dict:
    dano = max(1, estado["jogador_atk"] - estado["slime"]["defesa"])
    estado["slime_hp"] = max(0, estado["slime_hp"] - dano)
    estado["dano_total"] += dano
    estado.setdefault("buffs", {})
    estado["buffs"]["inimigo_atordoado"] = {"reducao_atk_pct": 0.5, "turnos": 2}
    log = [f"🦵 **Golpe Baixo!** **{dano}** de dano e inimigo atordoado por 2 turnos!"]
    if estado["slime_hp"] <= 0:
        estado["finalizado"] = True
        estado["vitoria"] = True
        log.append(f"💀 O **{estado['slime']['nome']}** foi derrotado!")
    estado["turno"] += 1
    estado["log"] = log
    return estado


@registrar("morte_subita", "Morte Súbita", "💀",
           "20% de instakill. Se falhar, causa 4x ATK.",
           nivel_minimo=10, cooldown_turnos=8)
def morte_subita(estado: dict) -> dict:
    if random.randint(1, 100) <= 20:
        estado["dano_total"] += estado["slime_hp"]
        estado["slime_hp"] = 0
        estado["finalizado"] = True
        estado["vitoria"] = True
        estado["log"] = ["💀 **MORTE SÚBITA!** Golpe fatal instantâneo!",
                         f"💀 O **{estado['slime']['nome']}** foi derrotado!"]
    else:
        dano = max(1, estado["jogador_atk"] * 4 - estado["slime"]["defesa"])
        estado["slime_hp"] = max(0, estado["slime_hp"] - dano)
        estado["dano_total"] += dano
        log = [f"💀 **Morte Súbita!** Instakill falhou, mas causou **{dano}** de dano!"]
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
# MONGE
# ══════════════════════════════════════════

@registrar("torrente_de_golpes", "Torrente de Golpes", "👊",
           "3 socos de ki consecutivos.",
           nivel_minimo=1, cooldown_turnos=3)
def torrente_de_golpes(estado: dict) -> dict:
    from utils.combat import _calcular_dano_jogador
    log = ["👊 **Torrente de Golpes!** Três socos de ki!"]
    for i in range(3):
        dano = max(1, _calcular_dano_jogador(estado) // 2 + estado["jogador_atk"] // 3)
        estado["slime_hp"] = max(0, estado["slime_hp"] - dano)
        estado["dano_total"] += dano
        log.append(f"  ↳ Soco {i+1}: **{dano}** de dano.")
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


@registrar("passo_do_vento", "Passo do Vento", "🌬",
           "+40% de esquiva por 2 turnos.",
           nivel_minimo=3, cooldown_turnos=3)
def passo_do_vento(estado: dict) -> dict:
    estado.setdefault("buffs", {})
    estado["buffs"]["passo_vento"] = {"bonus_esquiva": 40, "turnos": 2}
    estado["log"] = ["🌬 **Passo do Vento!** +40% de esquiva por 2 turnos!"]
    return estado


@registrar("ataque_ki", "Ataque de Ki", "☯",
           "Dano de ki: 2.5x ATK, ignora 30% da defesa.",
           nivel_minimo=6, cooldown_turnos=4)
def ataque_ki(estado: dict) -> dict:
    dano = max(1, int(estado["jogador_atk"] * 2.5) - int(estado["slime"]["defesa"] * 0.7))
    estado["slime_hp"] = max(0, estado["slime_hp"] - dano)
    estado["dano_total"] += dano
    log = [f"☯ **Ataque de Ki!** **{dano}** de dano de ki!"]
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


@registrar("corpo_vazio", "Corpo Vazio", "🌑",
           "Imunidade a dano por 1 turno.",
           nivel_minimo=10, cooldown_turnos=8)
def corpo_vazio(estado: dict) -> dict:
    estado.setdefault("buffs", {})
    estado["buffs"]["imune"] = {"imunidade": True, "turnos": 1}
    estado["log"] = ["🌑 **Corpo Vazio!** Você é imune a dano no próximo turno!"]
    return estado


# ══════════════════════════════════════════
# BARDO
# ══════════════════════════════════════════

@registrar("inspiracao_bardica", "Inspiração Bárdica", "🎵",
           "+30% ATK e +20% de esquiva por 2 turnos.",
           nivel_minimo=1, cooldown_turnos=3)
def inspiracao_bardica(estado: dict) -> dict:
    bonus = int(estado["jogador_atk"] * 0.30)
    estado["jogador_atk"] += bonus
    estado.setdefault("buffs", {})
    estado["buffs"]["inspiracao"] = {"bonus_atk": bonus, "bonus_esquiva": 20, "turnos": 2}
    estado["log"] = [f"🎵 **Inspiração Bárdica!** +{bonus} ATK e +20% esquiva por 2 turnos!"]
    return estado


@registrar("palavra_de_cura_bardo", "Palavra de Cura", "💚",
           "Cura 25% do HP máximo.",
           nivel_minimo=3, cooldown_turnos=4)
def palavra_de_cura_bardo(estado: dict) -> dict:
    cura = int(estado["jogador_hp_max"] * 0.25)
    estado["jogador_hp"] = min(estado["jogador_hp_max"], estado["jogador_hp"] + cura)
    estado["log"] = [f"💚 **Palavra de Cura!** Você recuperou **{cura} HP**!"]
    return estado


@registrar("encantamento", "Encantamento", "✨",
           "Encanta o inimigo: -30% ATK dele por 2 turnos.",
           nivel_minimo=6, cooldown_turnos=5)
def encantamento(estado: dict) -> dict:
    estado.setdefault("buffs", {})
    estado["buffs"]["inimigo_encantado"] = {"reducao_atk_pct": 0.30, "turnos": 2}
    estado["log"] = ["✨ **Encantamento!** Inimigo encantado: -30% ATK por 2 turnos!"]
    return estado


@registrar("cancao_do_descanso", "Canção do Descanso", "🎶",
           "Cura 50% do HP máximo.",
           nivel_minimo=10, cooldown_turnos=8)
def cancao_do_descanso(estado: dict) -> dict:
    cura = int(estado["jogador_hp_max"] * 0.50)
    estado["jogador_hp"] = min(estado["jogador_hp_max"], estado["jogador_hp"] + cura)
    estado["log"] = [f"🎶 **Canção do Descanso!** Você recuperou **{cura} HP**!"]
    return estado


# ══════════════════════════════════════════
# DRUIDA
# ══════════════════════════════════════════

@registrar("forma_selvagem", "Forma Selvagem", "🐻",
           "Recupera HP igual ao HP atual (dobra temporariamente).",
           nivel_minimo=1, cooldown_turnos=5)
def forma_selvagem(estado: dict) -> dict:
    bonus = estado["jogador_hp"]
    estado["jogador_hp"] = min(estado["jogador_hp_max"], estado["jogador_hp"] + bonus)
    estado["log"] = [f"🐻 **Forma Selvagem!** Recuperou **{bonus} HP** temporário!"]
    return estado


@registrar("cura_natural", "Cura Natural", "🍃",
           "Cura 20% do HP máximo.",
           nivel_minimo=3, cooldown_turnos=3)
def cura_natural(estado: dict) -> dict:
    cura = int(estado["jogador_hp_max"] * 0.20)
    estado["jogador_hp"] = min(estado["jogador_hp_max"], estado["jogador_hp"] + cura)
    estado["log"] = [f"🍃 **Cura Natural!** Você recuperou **{cura} HP**!"]
    return estado


@registrar("chamado_da_natureza", "Chamado da Natureza", "🌪",
           "Raio da natureza: 3x ATK de dano.",
           nivel_minimo=6, cooldown_turnos=4)
def chamado_da_natureza(estado: dict) -> dict:
    dano = max(1, estado["jogador_atk"] * 3 - estado["slime"]["defesa"])
    estado["slime_hp"] = max(0, estado["slime_hp"] - dano)
    estado["dano_total"] += dano
    log = [f"🌪 **Chamado da Natureza!** **{dano}** de dano de raio!"]
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


@registrar("furia_da_tempestade", "Fúria da Tempestade", "⛈",
           "Tempestade devastadora: 5x ATK de dano.",
           nivel_minimo=10, cooldown_turnos=8)
def furia_da_tempestade(estado: dict) -> dict:
    dano = max(1, estado["jogador_atk"] * 5 - estado["slime"]["defesa"])
    estado["slime_hp"] = max(0, estado["slime_hp"] - dano)
    estado["dano_total"] += dano
    log = [f"⛈ **Fúria da Tempestade!** **{dano}** de dano devastador!"]
    if estado["slime_hp"] <= 0:
        estado["finalizado"] = True
        estado["vitoria"] = True
        log.append(f"💀 O **{estado['slime']['nome']}** foi derrotado!")
    estado["turno"] += 1
    estado["log"] = log
    return estado


# ══════════════════════════════════════════
# FEITICEIRO
# ══════════════════════════════════════════

@registrar("toque_de_chamas", "Toque de Chamas", "🔥",
           "Fogo puro: 2x ATK, ignora toda a defesa.",
           nivel_minimo=1, cooldown_turnos=2)
def toque_de_chamas(estado: dict) -> dict:
    dano = max(1, estado["jogador_atk"] * 2)
    estado["slime_hp"] = max(0, estado["slime_hp"] - dano)
    estado["dano_total"] += dano
    log = [f"🔥 **Toque de Chamas!** **{dano}** de dano de fogo (ignora defesa)!"]
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


@registrar("metamagia", "Metamagia", "✨",
           "+100% dano na próxima habilidade usada.",
           nivel_minimo=3, cooldown_turnos=5)
def metamagia(estado: dict) -> dict:
    estado.setdefault("buffs", {})
    estado["buffs"]["metamagia"] = {"bonus_dano_pct": 1.0, "turnos": 1}
    estado["log"] = ["✨ **Metamagia!** Próxima habilidade causará dano dobrado!"]
    return estado


@registrar("explosao_de_caos", "Explosão de Caos", "💥",
           "Dano caótico aleatório: 1x a 5x ATK.",
           nivel_minimo=6, cooldown_turnos=4)
def explosao_de_caos(estado: dict) -> dict:
    mult = random.uniform(1.0, 5.0)
    dano = max(1, int(estado["jogador_atk"] * mult) - estado["slime"]["defesa"] // 2)
    estado["slime_hp"] = max(0, estado["slime_hp"] - dano)
    estado["dano_total"] += dano
    log = [f"💥 **Explosão de Caos!** {mult:.1f}x → **{dano}** de dano!"]
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


@registrar("surto_de_magia", "Surto de Magia", "🌀",
           "Poder máximo: 8x ATK, ignora toda a defesa.",
           nivel_minimo=10, cooldown_turnos=10)
def surto_de_magia(estado: dict) -> dict:
    dano = max(1, estado["jogador_atk"] * 8)
    estado["slime_hp"] = max(0, estado["slime_hp"] - dano)
    estado["dano_total"] += dano
    log = [f"🌀 **Surto de Magia!** **{dano}** de dano puro!"]
    if estado["slime_hp"] <= 0:
        estado["finalizado"] = True
        estado["vitoria"] = True
        log.append(f"💀 O **{estado['slime']['nome']}** foi derrotado!")
    estado["turno"] += 1
    estado["log"] = log
    return estado


# ══════════════════════════════════════════
# BRUXO
# ══════════════════════════════════════════

@registrar("maldicao_do_hexblade", "Maldição do Hexblade", "👁",
           "Inimigo recebe +30% dano por 3 turnos.",
           nivel_minimo=1, cooldown_turnos=4)
def maldicao_do_hexblade(estado: dict) -> dict:
    estado.setdefault("buffs", {})
    estado["buffs"]["hexblade"] = {"bonus_dano_recebido_pct": 0.30, "turnos": 3}
    estado["log"] = ["👁 **Maldição do Hexblade!** Inimigo recebe +30% dano por 3 turnos!"]
    return estado


@registrar("toque_eldritch", "Toque Eldritch", "🌑",
           "2x ATK de dano, drena 20% como HP.",
           nivel_minimo=3, cooldown_turnos=3)
def toque_eldritch(estado: dict) -> dict:
    dano = max(1, estado["jogador_atk"] * 2 - estado["slime"]["defesa"] // 2)
    estado["slime_hp"] = max(0, estado["slime_hp"] - dano)
    estado["dano_total"] += dano
    cura = int(dano * 0.20)
    estado["jogador_hp"] = min(estado["jogador_hp_max"], estado["jogador_hp"] + cura)
    log = [f"🌑 **Toque Eldritch!** **{dano}** de dano e drenou **{cura} HP**!"]
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


@registrar("olho_do_patrono", "Olho do Patrono", "🔯",
           "Próximo ataque tem crítico garantido.",
           nivel_minimo=6, cooldown_turnos=5)
def olho_do_patrono(estado: dict) -> dict:
    estado.setdefault("buffs", {})
    estado["buffs"]["critico_garantido"] = {"critico": True, "turnos": 1}
    estado["log"] = ["🔯 **Olho do Patrono!** Próximo ataque com crítico garantido!"]
    return estado


@registrar("pacto_de_sangue", "Pacto de Sangue", "🩸",
           "Sacrifica 20% HP para causar 6x ATK de dano.",
           nivel_minimo=10, cooldown_turnos=6)
def pacto_de_sangue(estado: dict) -> dict:
    custo = int(estado["jogador_hp_max"] * 0.20)
    estado["jogador_hp"] = max(1, estado["jogador_hp"] - custo)
    dano = max(1, estado["jogador_atk"] * 6)
    estado["slime_hp"] = max(0, estado["slime_hp"] - dano)
    estado["dano_total"] += dano
    log = [f"🩸 **Pacto de Sangue!** -{custo} HP próprio → **{dano}** de dano!"]
    if estado["slime_hp"] <= 0:
        estado["finalizado"] = True
        estado["vitoria"] = True
        log.append(f"💀 O **{estado['slime']['nome']}** foi derrotado!")
    estado["turno"] += 1
    estado["log"] = log
    return estado


# ══════════════════════════════════════════
# PATRULHEIRO
# ══════════════════════════════════════════

@registrar("marca_do_cacador", "Marca do Caçador", "🏹",
           "+5 dano fixo por ataque por 4 turnos.",
           nivel_minimo=1, cooldown_turnos=3)
def marca_do_cacador(estado: dict) -> dict:
    estado.setdefault("buffs", {})
    estado["buffs"]["marca_cacador"] = {"bonus_dano_fixo": 5, "turnos": 4}
    estado["log"] = ["🏹 **Marca do Caçador!** +5 dano fixo por ataque por 4 turnos!"]
    return estado


@registrar("chuva_de_flechas", "Chuva de Flechas", "🌧",
           "4 flechas disparadas com dano individual.",
           nivel_minimo=3, cooldown_turnos=4)
def chuva_de_flechas(estado: dict) -> dict:
    log = ["🌧 **Chuva de Flechas!** Quatro flechas disparadas!"]
    for i in range(4):
        dano = max(1, estado["jogador_atk"] - estado["slime"]["defesa"] + random.randint(0, 5))
        estado["slime_hp"] = max(0, estado["slime_hp"] - dano)
        estado["dano_total"] += dano
        log.append(f"  ↳ Flecha {i+1}: **{dano}** de dano.")
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


@registrar("sentidos_agucados", "Sentidos Aguçados", "👁",
           "+30% chance de crítico por 3 turnos.",
           nivel_minimo=6, cooldown_turnos=4)
def sentidos_agucados(estado: dict) -> dict:
    estado.setdefault("buffs", {})
    estado["buffs"]["sentidos"] = {"bonus_critico": 30, "turnos": 3}
    estado["log"] = ["👁 **Sentidos Aguçados!** +30% chance de crítico por 3 turnos!"]
    return estado


@registrar("golpe_colossal", "Golpe Colossal", "💫",
           "Golpe preciso letal: 5x ATK de dano.",
           nivel_minimo=10, cooldown_turnos=8)
def golpe_colossal(estado: dict) -> dict:
    dano = max(1, estado["jogador_atk"] * 5 - estado["slime"]["defesa"])
    estado["slime_hp"] = max(0, estado["slime_hp"] - dano)
    estado["dano_total"] += dano
    log = [f"💫 **Golpe Colossal!** **{dano}** de dano letal!"]
    if estado["slime_hp"] <= 0:
        estado["finalizado"] = True
        estado["vitoria"] = True
        log.append(f"💀 O **{estado['slime']['nome']}** foi derrotado!")
    estado["turno"] += 1
    estado["log"] = log
    return estado


# ══════════════════════════════════════════
# ARTÍFICE
# ══════════════════════════════════════════

@registrar("infusao_magica", "Infusão Mágica", "⚙",
           "+10 ATK ou +10 DEF aleatório por 3 turnos.",
           nivel_minimo=1, cooldown_turnos=3)
def infusao_magica(estado: dict) -> dict:
    estado.setdefault("buffs", {})
    if random.randint(0, 1) == 0:
        estado["jogador_atk"] += 10
        estado["buffs"]["infusao_atk"] = {"bonus_atk": 10, "turnos": 3}
        estado["log"] = ["⚙ **Infusão Mágica!** +10 ATK por 3 turnos!"]
    else:
        estado["jogador_defesa"] += 10
        estado["buffs"]["infusao_def"] = {"bonus_def": 10, "turnos": 3}
        estado["log"] = ["⚙ **Infusão Mágica!** +10 DEF por 3 turnos!"]
    return estado


@registrar("torrinha_de_batalha", "Torrinha de Batalha", "🏗",
           "Torrinha ataca automaticamente: +50% ATK por 3 turnos.",
           nivel_minimo=3, cooldown_turnos=5)
def torrinha_de_batalha(estado: dict) -> dict:
    bonus = int(estado["jogador_atk"] * 0.50)
    estado["jogador_atk"] += bonus
    estado.setdefault("buffs", {})
    estado["buffs"]["torrinha"] = {"bonus_atk": bonus, "turnos": 3}
    estado["log"] = [f"🏗 **Torrinha de Batalha!** +{bonus} ATK por 3 turnos!"]
    return estado


@registrar("elixir_do_artificer", "Elixir do Artífice", "🧪",
           "Cura 35% HP e concede +15 ATK por 2 turnos.",
           nivel_minimo=6, cooldown_turnos=5)
def elixir_do_artificer(estado: dict) -> dict:
    cura = int(estado["jogador_hp_max"] * 0.35)
    estado["jogador_hp"] = min(estado["jogador_hp_max"], estado["jogador_hp"] + cura)
    estado["jogador_atk"] += 15
    estado.setdefault("buffs", {})
    estado["buffs"]["elixir"] = {"bonus_atk": 15, "turnos": 2}
    estado["log"] = [f"🧪 **Elixir do Artífice!** +{cura} HP e +15 ATK por 2 turnos!"]
    return estado


@registrar("golem_de_ferro", "Golem de Ferro", "🤖",
           "Golem invocado: +25 DEF e +20 ATK por 2 turnos.",
           nivel_minimo=10, cooldown_turnos=8)
def golem_de_ferro(estado: dict) -> dict:
    estado["jogador_defesa"] += 25
    estado["jogador_atk"] += 20
    estado.setdefault("buffs", {})
    estado["buffs"]["golem"] = {"bonus_def": 25, "bonus_atk": 20, "turnos": 2}
    estado["log"] = ["🤖 **Golem de Ferro!** +25 DEF e +20 ATK por 2 turnos!"]
    return estado
