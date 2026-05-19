"""
combat.py — Lógica de combate por turnos.

Responsável por calcular dano, aplicar defesa, verificar
condições de vitória/derrota e montar o estado do combate.
"""

import random
from utils.player import buscar_stats_completos

# ── Constantes ────────────────────────────────────────────

CHANCE_CRITICO   = 15   # % de chance de acerto crítico
MULT_CRITICO     = 1.75 # multiplicador de dano crítico
CHANCE_ESQUIVA   = 8    # % de chance de esquivar do ataque inimigo

XP_DERROTA       = 5    # XP de consolação ao perder


def iniciar_combate(user_id: int, slime: dict) -> dict:
    """
    Monta o estado inicial do combate.
    Retorna o estado completo que será mantido na View.
    """
    from utils.classes import CLASSES
    stats = buscar_stats_completos(user_id)
    classe = stats.get("classe")
    classe_emoji = CLASSES[classe]["emoji"] if classe and classe in CLASSES else "🧙"

    return {
        "user_id":      user_id,
        "turno":        1,
        "finalizado":   False,
        "vitoria":      False,
        "buffs":        {},

        # jogador
        "jogador_hp":       stats["hp_total"],
        "jogador_hp_max":   stats["hp_total"],
        "jogador_atk":      stats["atk_total"],
        "jogador_defesa":   stats["defesa_total"],
        "dano_total":       0,

        # classe
        "classe":       classe,
        "classe_emoji": classe_emoji,
        "nivel":        stats["nivel"],

        # slime
        "slime":        slime,
        "slime_hp":     slime["hp_atual"],
        "slime_hp_max": slime["hp_max"],

        # log do último turno
        "log": [f"Um **{slime['emoji']} {slime['nome']}** apareceu!"],
    }


def processar_turno_ataque(estado: dict) -> dict:
    """
    Processa um turno onde o jogador ataca.
    Retorna o estado atualizado com o log do turno.
    """
    log = []

    # ── Ataque do jogador ─────────────────────────────────
    critico = random.randint(1, 100) <= CHANCE_CRITICO
    dano_base = max(1, estado["jogador_atk"] - estado["slime"]["defesa"])
    dano = int(dano_base * MULT_CRITICO) if critico else dano_base
    dano = max(1, dano + random.randint(-2, 2))  # leve variação

    estado["slime_hp"] = max(0, estado["slime_hp"] - dano)
    estado["dano_total"] += dano

    if critico:
        log.append(f"💥 **CRÍTICO!** Você causou **{dano}** de dano!")
    else:
        log.append(f"⚔️ Você atacou e causou **{dano}** de dano.")

    # ── Verifica morte do slime ───────────────────────────
    if estado["slime_hp"] <= 0:
        estado["finalizado"] = True
        estado["vitoria"] = True
        log.append(f"💀 O **{estado['slime']['nome']}** foi derrotado!")
        estado["log"] = log
        return estado

    # ── Contra-ataque do slime ────────────────────────────
    esquivou = random.randint(1, 100) <= CHANCE_ESQUIVA
    if esquivou:
        log.append(f"🌀 Você esquivou do ataque do **{estado['slime']['nome']}**!")
    else:
        dano_slime = max(1, estado["slime"]["atk"] - estado["jogador_defesa"])
        dano_slime = max(1, dano_slime + random.randint(-1, 3))
        estado["jogador_hp"] = max(0, estado["jogador_hp"] - dano_slime)
        log.append(f"🟢 O **{estado['slime']['nome']}** atacou e causou **{dano_slime}** de dano.")

    # ── Verifica morte do jogador ─────────────────────────
    if estado["jogador_hp"] <= 0:
        estado["finalizado"] = True
        estado["vitoria"] = False
        log.append("💀 Você foi derrotado...")

    estado["turno"] += 1
    estado["log"] = log
    return estado


def processar_fuga(estado: dict) -> dict:
    """
    Tenta fugir do combate. 50% de chance de sucesso.
    Se falhar, o slime ataca.
    """
    log = []
    fugiu = random.randint(1, 100) <= 50

    if fugiu:
        estado["finalizado"] = True
        estado["vitoria"] = False
        log.append("🏃 Você fugiu do combate!")
    else:
        log.append("❌ Fuga falhou!")
        dano_slime = max(1, estado["slime"]["atk"] - estado["jogador_defesa"])
        estado["jogador_hp"] = max(0, estado["jogador_hp"] - dano_slime)
        log.append(f"🟢 O **{estado['slime']['nome']}** aproveitou e causou **{dano_slime}** de dano.")

        if estado["jogador_hp"] <= 0:
            estado["finalizado"] = True
            estado["vitoria"] = False
            log.append("💀 Você foi derrotado...")

    estado["turno"] += 1
    estado["log"] = log
    return estado


def barra_hp(hp_atual: int, hp_max: int, tamanho: int = 10) -> str:
    """Gera uma barra visual de HP."""
    preenchido = int((hp_atual / hp_max) * tamanho)
    preenchido = max(0, min(preenchido, tamanho))
    return "❤️" * preenchido + "🖤" * (tamanho - preenchido)


def _calcular_dano_jogador(estado: dict, penalidade_def: float = 1.0) -> int:
    """
    Helper usado pelas habilidades para calcular dano do jogador.
    penalidade_def reduz a defesa do inimigo considerada (ex: 0.5 = ignora metade).
    """
    critico = random.randint(1, 100) <= CHANCE_CRITICO
    buffs = estado.get("buffs", {})

    # chance extra de crítico por buffs
    bonus_critico = sum(b.get("bonus_critico", 0) for b in buffs.values())
    if bonus_critico:
        critico = random.randint(1, 100) <= (CHANCE_CRITICO + bonus_critico)

    # crítico garantido por buff
    if any(b.get("critico") for b in buffs.values()):
        critico = True

    defesa_considerada = int(estado["slime"]["defesa"] * penalidade_def)
    dano_base = max(1, estado["jogador_atk"] - defesa_considerada)
    dano = int(dano_base * MULT_CRITICO) if critico else dano_base
    dano = max(1, dano + random.randint(-1, 2))

    # dano fixo extra por buffs (ex: marca do caçador)
    bonus_fixo = sum(b.get("bonus_dano_fixo", 0) for b in buffs.values())
    dano += bonus_fixo

    return dano
