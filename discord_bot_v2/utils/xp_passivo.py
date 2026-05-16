"""
xp_passivo.py — Configurações e lógica de XP passivo.

XP de texto:  fixo por mensagem, com cooldown por usuário.
XP de voz:    fixo a cada intervalo, só com mais alguém no canal.
"""

# ── Configurações ─────────────────────────────────────────

XP_POR_MENSAGEM       = 2      # XP ganho por mensagem de texto
COOLDOWN_MENSAGEM_SEG = 60     # segundos entre ganhos de XP por texto

XP_POR_TICK_VOZ       = 5      # XP ganho por tick em voz
INTERVALO_VOZ_SEG     = 300    # segundos entre ticks de voz (5 min)
VOZ_MIN_MEMBROS       = 2      # mínimo de membros para XP contar

# ── Helpers ───────────────────────────────────────────────

def canal_voz_valido(membros_no_canal: int) -> bool:
    """Retorna True se o canal tem membros suficientes para dar XP."""
    return membros_no_canal >= VOZ_MIN_MEMBROS


def membros_humanos(canal_voz) -> int:
    """Conta membros humanos (não-bots) em um canal de voz."""
    return sum(1 for m in canal_voz.members if not m.bot)
