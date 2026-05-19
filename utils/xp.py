"""
xp.py — Fórmulas de progressão de XP e nível.
"""


def xp_para_nivel(nivel: int) -> int:
    """
    Retorna o XP necessário para atingir o nível informado.
    Fórmula: 120 * (nivel ^ 1.8)
    Mais íngreme que a anterior — nível 10 exige ~2x mais esforço,
    mas os primeiros níveis ainda são rápidos para engajar o jogador.
    """
    return int(120 * (nivel ** 1.8))


def xp_total_para_nivel(nivel: int) -> int:
    """Retorna o XP acumulado total necessário para chegar ao nível."""
    return sum(xp_para_nivel(n) for n in range(1, nivel))


def calcular_nivel(xp_total: int) -> tuple[int, int]:
    """
    Dado um XP total acumulado, retorna (nivel, xp_restante_no_nivel).
    """
    nivel = 1
    while xp_total >= xp_para_nivel(nivel + 1):
        xp_total -= xp_para_nivel(nivel + 1)
        nivel += 1
    return nivel, xp_total
