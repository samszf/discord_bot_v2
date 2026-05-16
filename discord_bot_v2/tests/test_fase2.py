"""
test_fase2.py — Testes da Fase 2: jogador, XP, level up, perfil, items.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ["DB_PATH"] = ":memory:"

from database.connection import inicializar_banco, fechar_conexao
from database import repository as repo
from utils.player import registrar_jogador, buscar_stats_completos, calcular_bonus_equipamentos
from utils.xp import xp_para_nivel, calcular_nivel
from utils.items import buscar_item, nome_item, itens_por_tipo, ITENS
from utils.levelup import calcular_levelup

# reinicia banco a cada execução
fechar_conexao()
inicializar_banco()


# ── REGISTRO ───────────────────────────────────────────────

def test_registrar_novo():
    r = registrar_jogador(2001)
    assert r["sucesso"] is True
    print("✅ registrar_jogador novo")

def test_registrar_duplicado():
    registrar_jogador(2002)
    r = registrar_jogador(2002)
    assert r["sucesso"] is False
    print("✅ registrar_jogador duplicado bloqueado")

def test_registrar_cria_equipment_e_stats():
    registrar_jogador(2003)
    assert repo.buscar_equipment(2003) is not None
    assert repo.buscar_battle_stats(2003) is not None
    print("✅ registrar_jogador cria equipment e battle_stats")


# ── XP E LEVEL UP ──────────────────────────────────────────

def test_xp_para_nivel():
    assert xp_para_nivel(1) == 100
    assert xp_para_nivel(2) > xp_para_nivel(1)
    print("✅ xp_para_nivel crescente")

def test_calcular_nivel():
    nivel, xp_resto = calcular_nivel(0)
    assert nivel == 1
    nivel, _ = calcular_nivel(xp_para_nivel(2) + 1)
    assert nivel == 2
    print("✅ calcular_nivel")

def test_adicionar_xp_sem_levelup():
    registrar_jogador(2010)
    resultado = repo.adicionar_xp(2010, 10)
    assert resultado["level_up"] is False
    assert resultado["xp_atual"] == 10
    print("✅ adicionar_xp sem level up")

def test_adicionar_xp_com_levelup():
    registrar_jogador(2011)
    xp_necessario = xp_para_nivel(2)
    resultado = repo.adicionar_xp(2011, xp_necessario + 5)
    assert resultado["level_up"] is True
    assert resultado["nivel_atual"] == 2
    assert resultado["nivel_antes"] == 1
    assert resultado["niveis_ganhos"] == 1
    print("✅ adicionar_xp com level up")

def test_levelup_aplica_bonus_stats():
    registrar_jogador(2012)
    player_antes = repo.buscar_player(2012)
    xp_necessario = xp_para_nivel(2)
    repo.adicionar_xp(2012, xp_necessario + 1)
    player_depois = repo.buscar_player(2012)
    assert player_depois["hp_base"]     == player_antes["hp_base"]     + 10
    assert player_depois["atk_base"]    == player_antes["atk_base"]    + 2
    assert player_depois["defesa_base"] == player_antes["defesa_base"] + 1
    print("✅ level up aplica bônus de stats no banco")

def test_calcular_levelup_multiplos_niveis():
    ganhos = calcular_levelup(1, 3)
    assert ganhos["niveis_ganhos"] == 2
    assert ganhos["bonus_hp"] == 20
    assert ganhos["bonus_atk"] == 4
    print("✅ calcular_levelup múltiplos níveis")


# ── STATS COMPLETOS ────────────────────────────────────────

def test_buscar_stats_completos_jogador_existente():
    registrar_jogador(2020)
    stats = buscar_stats_completos(2020)
    assert stats is not None
    assert stats["nivel"] == 1
    assert stats["hp_total"] == 100
    assert stats["atk_total"] == 10
    assert stats["defesa_total"] == 5
    assert stats["arma"] is None
    print("✅ buscar_stats_completos retorna dados corretos")

def test_buscar_stats_completos_inexistente():
    stats = buscar_stats_completos(9999)
    assert stats is None
    print("✅ buscar_stats_completos retorna None para inexistente")

def test_stats_com_equipamento():
    registrar_jogador(2021)
    repo.atualizar_equipment(2021, "arma", "espada_enferrujada")
    stats = buscar_stats_completos(2021)
    assert stats["bonus_atk"] == 2
    assert stats["atk_total"] == 12  # 10 base + 2 bônus
    print("✅ stats_completos inclui bônus de equipamento")


# ── ITENS ──────────────────────────────────────────────────

def test_buscar_item_existente():
    item = buscar_item("espada_enferrujada")
    assert item is not None
    assert item["tipo"] == "arma"
    assert item["raridade"] == "comum"
    print("✅ buscar_item existente")

def test_buscar_item_inexistente():
    item = buscar_item("item_que_nao_existe")
    assert item is None
    print("✅ buscar_item inexistente retorna None")

def test_nome_item():
    assert "Espada" in nome_item("espada_enferrujada")
    assert nome_item("xyz") == "xyz"
    print("✅ nome_item")

def test_itens_por_tipo():
    armas = itens_por_tipo("arma")
    assert len(armas) > 0
    assert all(v["tipo"] == "arma" for v in armas.values())
    print("✅ itens_por_tipo")

def test_todos_itens_tem_campos_obrigatorios():
    campos = ["nome", "tipo", "raridade", "preco"]
    for item_id, item in ITENS.items():
        for campo in campos:
            assert campo in item, f"Item '{item_id}' sem campo '{campo}'"
    print(f"✅ todos os {len(ITENS)} itens têm campos obrigatórios")

def test_calcular_bonus_sem_equipamento():
    bonus = calcular_bonus_equipamentos(None)
    assert bonus == {"atk": 0, "defesa": 0, "hp": 0}
    print("✅ calcular_bonus sem equipamento retorna zeros")

def test_calcular_bonus_com_equipamentos():
    equip = {
        "arma":      "espada_enferrujada",   # +2 atk
        "armadura":  "roupa_surrada",         # +2 def
        "acessorio": "amuleto_madeira",       # +10 hp
    }
    bonus = calcular_bonus_equipamentos(equip)
    assert bonus["atk"]    == 2
    assert bonus["defesa"] == 2
    assert bonus["hp"]     == 10
    print("✅ calcular_bonus com equipamentos somados corretamente")


# ── RUNNER ─────────────────────────────────────────────────

if __name__ == "__main__":
    testes = [
        test_registrar_novo,
        test_registrar_duplicado,
        test_registrar_cria_equipment_e_stats,
        test_xp_para_nivel,
        test_calcular_nivel,
        test_adicionar_xp_sem_levelup,
        test_adicionar_xp_com_levelup,
        test_levelup_aplica_bonus_stats,
        test_calcular_levelup_multiplos_niveis,
        test_buscar_stats_completos_jogador_existente,
        test_buscar_stats_completos_inexistente,
        test_stats_com_equipamento,
        test_buscar_item_existente,
        test_buscar_item_inexistente,
        test_nome_item,
        test_itens_por_tipo,
        test_todos_itens_tem_campos_obrigatorios,
        test_calcular_bonus_sem_equipamento,
        test_calcular_bonus_com_equipamentos,
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
        print(f"✅  TODOS OS {len(testes)} TESTES PASSARAM — Fase 2 validada!")
    else:
        print(f"❌  {falhas}/{len(testes)} testes falharam.")
