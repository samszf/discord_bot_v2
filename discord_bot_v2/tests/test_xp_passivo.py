"""
test_xp_passivo.py — Testes do sistema de XP passivo.
"""

import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ["DB_PATH"] = ":memory:"

from database.connection import inicializar_banco, fechar_conexao
from database import repository as repo
from utils.xp_passivo import (
    canal_voz_valido,
    membros_humanos,
    XP_POR_MENSAGEM,
    XP_POR_TICK_VOZ,
    COOLDOWN_MENSAGEM_SEG,
    VOZ_MIN_MEMBROS,
)
from utils.xp import xp_para_nivel

fechar_conexao()
inicializar_banco()


# ── Configurações ─────────────────────────────────────────

def test_xp_mensagem_menor_que_batalha():
    """XP de texto deve ser menor que o ganho típico de batalha."""
    xp_batalha_tipico = 30
    assert XP_POR_MENSAGEM < xp_batalha_tipico
    print(f"✅ XP de mensagem ({XP_POR_MENSAGEM}) < XP de batalha típico ({xp_batalha_tipico})")

def test_xp_voz_menor_que_batalha():
    xp_batalha_tipico = 30
    assert XP_POR_TICK_VOZ < xp_batalha_tipico
    print(f"✅ XP de voz por tick ({XP_POR_TICK_VOZ}) < XP de batalha típico ({xp_batalha_tipico})")

def test_cooldown_configurado():
    assert COOLDOWN_MENSAGEM_SEG >= 30
    print(f"✅ Cooldown de mensagem configurado: {COOLDOWN_MENSAGEM_SEG}s")

def test_voz_min_membros():
    assert VOZ_MIN_MEMBROS >= 2
    print(f"✅ Mínimo de membros em voz: {VOZ_MIN_MEMBROS}")


# ── Lógica de canal de voz ────────────────────────────────

def test_canal_voz_valido_suficiente():
    assert canal_voz_valido(2) is True
    assert canal_voz_valido(5) is True
    print("✅ canal_voz_valido com membros suficientes")

def test_canal_voz_invalido_insuficiente():
    assert canal_voz_valido(0) is False
    assert canal_voz_valido(1) is False
    print("✅ canal_voz_valido bloqueado com 1 membro")


# ── Cooldown em memória (simula o comportamento do cog) ───

def test_cooldown_bloqueia_xp_rapido():
    """Simula o cooldown em memória que o cog usa."""
    cooldown: dict[int, float] = {}
    user_id = 3001
    repo.criar_player(user_id)

    xp_antes = repo.buscar_player(user_id)["xp"]

    # primeira mensagem — deve ganhar XP
    agora = time.time()
    ultimo = cooldown.get(user_id, 0)
    if agora - ultimo >= COOLDOWN_MENSAGEM_SEG:
        cooldown[user_id] = agora
        repo.adicionar_xp(user_id, XP_POR_MENSAGEM)

    xp_apos_primeira = repo.buscar_player(user_id)["xp"]
    assert xp_apos_primeira == xp_antes + XP_POR_MENSAGEM

    # segunda mensagem imediata — deve ser bloqueada pelo cooldown
    agora2 = time.time()
    ultimo2 = cooldown.get(user_id, 0)
    if agora2 - ultimo2 >= COOLDOWN_MENSAGEM_SEG:
        repo.adicionar_xp(user_id, XP_POR_MENSAGEM)

    xp_apos_segunda = repo.buscar_player(user_id)["xp"]
    assert xp_apos_segunda == xp_apos_primeira  # não mudou
    print("✅ cooldown bloqueia XP imediato de texto")


def test_cooldown_libera_apos_tempo(monkeypatch_time=None):
    """Simula que o cooldown expirou e o XP é concedido novamente."""
    cooldown: dict[int, float] = {}
    user_id = 3002
    repo.criar_player(user_id)

    # simula primeiro uso há COOLDOWN + 1 segundos atrás
    cooldown[user_id] = time.time() - (COOLDOWN_MENSAGEM_SEG + 1)

    agora = time.time()
    ultimo = cooldown.get(user_id, 0)
    xp_antes = repo.buscar_player(user_id)["xp"]

    if agora - ultimo >= COOLDOWN_MENSAGEM_SEG:
        cooldown[user_id] = agora
        repo.adicionar_xp(user_id, XP_POR_MENSAGEM)

    xp_depois = repo.buscar_player(user_id)["xp"]
    assert xp_depois == xp_antes + XP_POR_MENSAGEM
    print("✅ cooldown liberado após tempo correto")


# ── XP passivo não atrapalha level up ─────────────────────

def test_xp_passivo_acumula_e_sobe_nivel():
    """Garante que XP passivo acumulado eventualmente causa level up."""
    user_id = 3003
    repo.criar_player(user_id)

    xp_necessario = xp_para_nivel(2)
    ticks = (xp_necessario // XP_POR_MENSAGEM) + 1

    resultado = None
    for _ in range(ticks):
        resultado = repo.adicionar_xp(user_id, XP_POR_MENSAGEM)

    assert resultado["nivel_atual"] >= 2
    print(f"✅ XP passivo acumulado causa level up após {ticks} ticks")

def test_xp_voz_acumula_corretamente():
    user_id = 3004
    repo.criar_player(user_id)

    for _ in range(3):
        repo.adicionar_xp(user_id, XP_POR_TICK_VOZ)

    player = repo.buscar_player(user_id)
    assert player["xp"] >= XP_POR_TICK_VOZ * 3
    print(f"✅ XP de voz acumula corretamente ({XP_POR_TICK_VOZ * 3} XP em 3 ticks)")


# ── Runner ────────────────────────────────────────────────

if __name__ == "__main__":
    testes = [
        test_xp_mensagem_menor_que_batalha,
        test_xp_voz_menor_que_batalha,
        test_cooldown_configurado,
        test_voz_min_membros,
        test_canal_voz_valido_suficiente,
        test_canal_voz_invalido_insuficiente,
        test_cooldown_bloqueia_xp_rapido,
        test_cooldown_libera_apos_tempo,
        test_xp_passivo_acumula_e_sobe_nivel,
        test_xp_voz_acumula_corretamente,
    ]

    falhas = 0
    for teste in testes:
        try:
            teste()
        except Exception as e:
            print(f"❌ {teste.__name__}: {e}")
            falhas += 1

    print()
    if falhas == 0:
        print(f"✅  TODOS OS {len(testes)} TESTES PASSARAM — XP Passivo validado!")
    else:
        print(f"❌  {falhas}/{len(testes)} testes falharam.")
