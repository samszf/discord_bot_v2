"""
cooldown.py — Gerenciamento de cooldowns de comandos via banco.
"""

from datetime import datetime, timedelta
from database import repository as repo


COOLDOWNS_SEGUNDOS = {
    "aventura": 30,
}


def verificar_cooldown(user_id: int, comando: str) -> tuple[bool, int]:
    """
    Verifica se o usuário está em cooldown para um comando.
    Retorna (pode_usar: bool, segundos_restantes: int).
    """
    segundos = COOLDOWNS_SEGUNDOS.get(comando, 0)
    if segundos == 0:
        return True, 0

    ultimo = repo.buscar_cooldown(user_id, comando)
    if not ultimo:
        return True, 0

    ultimo_dt = datetime.fromisoformat(ultimo)
    agora = datetime.utcnow()
    delta = agora - ultimo_dt

    if delta >= timedelta(seconds=segundos):
        return True, 0

    restante = segundos - int(delta.total_seconds())
    return False, restante


def registrar_uso(user_id: int, comando: str) -> None:
    """Registra o uso do comando para cooldown."""
    repo.registrar_cooldown(user_id, comando)
