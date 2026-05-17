"""
test_fase3.py — Testes da Fase 3: slimes, loot, combate, cooldown.
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ["DB_PATH"] = ":memory:"

from database.connection import inicializar_banco, fechar_conexao
from database import repository as repo
from utils.slimes import gerar_slime, SLIMES, _sortear_dificuldade
from utils.loot import sortear_loot, sortear_ouro
from utils.combat import iniciar_combate, processar_turno_ataque, processar_fuga, barra_hp
from utils.cooldown import verificar_cooldown, registrar_uso

fechar_conexao()
inicializar_banco()

# cria um jogador de teste base
repo.criar_player(4001)


# ── SLIMES ────────────────────────────────────────────────

def test_gerar_slime_retorna_campos_obrigatorios():
    slime = gerar_slime(1)
    campos = ["nome", "emoji", "hp_max", "hp_atual", "atk", "defesa",
              "xp_recompensa", "ouro_min", "ouro_max", "raridades", "dificuldade"]
    for c in campos:
        assert c in slime, f"Campo '{c}' ausente no slime"
    print("✅ gerar_slime retorna todos os campos obrigatórios")

def test_gerar_slime_hp_positivo():
    for nivel in [1, 5, 10, 20]:
        slime = gerar_slime(nivel)
        assert slime["hp_max"] > 0
        assert slime["hp_atual"] == slime["hp_max"]
    print("✅ gerar_slime HP sempre positivo")

def test_dificuldade_escala_com_nivel():
    # nível 1 nunca deve gerar dificuldade > 3
    for _ in range(50):
        d = _sortear_dificuldade(1)
        assert d <= 3, f"Nível 1 gerou dificuldade {d}"
    print("✅ dificuldade escalada corretamente para nível 1")

def test_dificuldade_alta_para_nivel_alto():
    # nível 20 deve ser capaz de gerar dificuldades altas
    dificuldades = {_sortear_dificuldade(20) for _ in range(100)}
    assert max(dificuldades) >= 5
    print(f"✅ nível 20 gera dificuldades altas: {sorted(dificuldades)}")

def test_variacao_hp_dentro_do_esperado():
    base_hp = SLIMES[1]["hp_base"]
    for _ in range(30):
        slime = gerar_slime(1)
        if slime["dificuldade"] == 1:
            assert slime["hp_max"] >= int(base_hp * 0.88)
            assert slime["hp_max"] <= int(base_hp * 1.12)
    print("✅ variação de HP dentro de ±10% do base")


# ── LOOT ──────────────────────────────────────────────────

def test_sortear_ouro_dentro_do_range():
    for _ in range(50):
        ouro = sortear_ouro(10, 30)
        assert 10 <= ouro <= 30
    print("✅ sortear_ouro sempre dentro do range")

def test_sortear_loot_retorna_item_ou_none():
    resultados = [sortear_loot(["comum", "incomum"]) for _ in range(50)]
    items = [r for r in resultados if r is not None]
    nones = [r for r in resultados if r is None]
    assert len(items) > 0, "Nunca dropou nenhum item em 50 tentativas"
    print(f"✅ sortear_loot: {len(items)} drops e {len(nones)} sem loot em 50 tentativas")

def test_sortear_loot_item_valido():
    from utils.items import ITENS
    for _ in range(20):
        resultado = sortear_loot(["comum"])
        if resultado:
            assert resultado in ITENS
            assert ITENS[resultado]["tipo"] != "consumivel"
    print("✅ sortear_loot retorna apenas itens válidos e não-consumíveis")


# ── COMBATE ───────────────────────────────────────────────

def _estado_teste():
    slime = gerar_slime(1)
    return iniciar_combate(4001, slime)

def test_iniciar_combate_campos():
    estado = _estado_teste()
    assert estado["turno"] == 1
    assert estado["finalizado"] is False
    assert estado["jogador_hp"] > 0
    assert estado["slime_hp"] > 0
    assert len(estado["log"]) > 0
    print("✅ iniciar_combate estado inicial correto")

def test_ataque_reduz_hp_slime():
    estado = _estado_teste()
    hp_antes = estado["slime_hp"]
    estado = processar_turno_ataque(estado)
    assert estado["slime_hp"] <= hp_antes
    print("✅ processar_turno_ataque reduz HP do slime")

def test_ataque_incrementa_turno():
    estado = _estado_teste()
    if not estado["finalizado"]:
        estado = processar_turno_ataque(estado)
        assert estado["turno"] >= 2
    print("✅ processar_turno_ataque incrementa turno")

def test_ataque_log_preenchido():
    estado = _estado_teste()
    estado = processar_turno_ataque(estado)
    assert len(estado["log"]) > 0
    print("✅ processar_turno_ataque preenche log")

def test_combate_completo_termina():
    """Simula um combate completo até o fim."""
    slime = gerar_slime(1)
    # força slime fraco para garantir que o jogador vence
    slime["hp_atual"] = 10
    slime["hp_max"] = 10
    slime["atk"] = 1
    estado = iniciar_combate(4001, slime)

    for _ in range(50):
        if estado["finalizado"]:
            break
        estado = processar_turno_ataque(estado)

    assert estado["finalizado"] is True
    print(f"✅ combate completo termina (vitória: {estado['vitoria']})")

def test_fuga_muda_estado():
    estado = _estado_teste()
    estado = processar_fuga(estado)
    assert len(estado["log"]) > 0
    assert estado["turno"] >= 2
    print("✅ processar_fuga altera estado corretamente")

def test_fuga_pode_finalizar():
    """Testa que fuga eventualmente finaliza o combate."""
    finalizou = False
    for _ in range(30):
        estado = _estado_teste()
        estado = processar_fuga(estado)
        if estado["finalizado"]:
            finalizou = True
            break
    assert finalizou
    print("✅ processar_fuga pode finalizar o combate")

def test_barra_hp_cheia():
    assert barra_hp(10, 10) == "❤️" * 10
    print("✅ barra_hp cheia correta")

def test_barra_hp_vazia():
    assert barra_hp(0, 10) == "🖤" * 10
    print("✅ barra_hp vazia correta")

def test_barra_hp_parcial():
    barra = barra_hp(5, 10)
    assert "❤️" in barra and "🖤" in barra
    print("✅ barra_hp parcial correta")

def test_dano_total_acumula():
    slime = gerar_slime(1)
    slime["hp_atual"] = 999
    slime["hp_max"] = 999
    slime["atk"] = 0
    estado = iniciar_combate(4001, slime)
    for _ in range(3):
        estado = processar_turno_ataque(estado)
    assert estado["dano_total"] > 0
    print(f"✅ dano_total acumula corretamente: {estado['dano_total']}")


# ── COOLDOWN ──────────────────────────────────────────────

def test_cooldown_inicial_liberado():
    pode, restante = verificar_cooldown(9991, "aventura")
    assert pode is True
    assert restante == 0
    print("✅ cooldown inicial liberado")

def test_cooldown_apos_registro():
    repo.criar_player(9992)
    registrar_uso(9992, "aventura")
    pode, restante = verificar_cooldown(9992, "aventura")
    assert pode is False
    assert restante > 0
    print(f"✅ cooldown ativo após registro ({restante}s restantes)")

def test_cooldown_comando_sem_cooldown():
    pode, restante = verificar_cooldown(9993, "comando_sem_cooldown")
    assert pode is True
    assert restante == 0
    print("✅ comando sem cooldown configurado sempre liberado")


# ── Runner ────────────────────────────────────────────────

if __name__ == "__main__":
    testes = [
        test_gerar_slime_retorna_campos_obrigatorios,
        test_gerar_slime_hp_positivo,
        test_dificuldade_escala_com_nivel,
        test_dificuldade_alta_para_nivel_alto,
        test_variacao_hp_dentro_do_esperado,
        test_sortear_ouro_dentro_do_range,
        test_sortear_loot_retorna_item_ou_none,
        test_sortear_loot_item_valido,
        test_iniciar_combate_campos,
        test_ataque_reduz_hp_slime,
        test_ataque_incrementa_turno,
        test_ataque_log_preenchido,
        test_combate_completo_termina,
        test_fuga_muda_estado,
        test_fuga_pode_finalizar,
        test_barra_hp_cheia,
        test_barra_hp_vazia,
        test_barra_hp_parcial,
        test_dano_total_acumula,
        test_cooldown_inicial_liberado,
        test_cooldown_apos_registro,
        test_cooldown_comando_sem_cooldown,
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
        print(f"✅  TODOS OS {len(testes)} TESTES PASSARAM — Fase 3 validada!")
    else:
        print(f"❌  {falhas}/{len(testes)} testes falharam.")
