"""
test_fase4.py — Testes da Fase 4: inventário e equipamentos.
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ["DB_PATH"] = ":memory:"

from database.connection import inicializar_banco, fechar_conexao
from database import repository as repo
from utils.items import buscar_item, ITENS, itens_por_tipo

fechar_conexao()
inicializar_banco()

repo.criar_player(5001)
repo.criar_player(5002)


# ── INVENTÁRIO ─────────────────────────────────────────────

def test_inventario_inicial_vazio():
    inv = repo.buscar_inventario(5001)
    assert inv == []
    print("✅ inventário inicial vazio")

def test_adicionar_item_novo():
    repo.adicionar_item(5001, "espada_enferrujada", 1)
    inv = repo.buscar_inventario(5001)
    assert len(inv) == 1
    assert inv[0]["item_id"] == "espada_enferrujada"
    assert inv[0]["quantidade"] == 1
    print("✅ adicionar_item novo")

def test_adicionar_item_empilha():
    repo.adicionar_item(5001, "pocao_vida", 2)
    repo.adicionar_item(5001, "pocao_vida", 3)
    inv = repo.buscar_inventario(5001)
    pocao = next(e for e in inv if e["item_id"] == "pocao_vida")
    assert pocao["quantidade"] == 5
    print("✅ adicionar_item empilha quantidade")

def test_adicionar_multiplos_itens():
    repo.criar_player(5010)
    for item_id in ["espada_enferrujada", "roupa_surrada", "amuleto_madeira"]:
        repo.adicionar_item(5010, item_id, 1)
    inv = repo.buscar_inventario(5010)
    assert len(inv) == 3
    print("✅ múltiplos itens diferentes no inventário")

def test_remover_item_parcial():
    repo.criar_player(5011)
    repo.adicionar_item(5011, "pocao_vida", 5)
    assert repo.remover_item(5011, "pocao_vida", 3) is True
    inv = repo.buscar_inventario(5011)
    assert inv[0]["quantidade"] == 2
    print("✅ remover_item parcial correto")

def test_remover_item_total_remove_linha():
    repo.criar_player(5012)
    repo.adicionar_item(5012, "pocao_vida", 1)
    assert repo.remover_item(5012, "pocao_vida", 1) is True
    assert repo.buscar_inventario(5012) == []
    print("✅ remover_item total remove linha do banco")

def test_remover_item_insuficiente():
    repo.criar_player(5013)
    repo.adicionar_item(5013, "pocao_vida", 1)
    assert repo.remover_item(5013, "pocao_vida", 99) is False
    print("✅ remover_item insuficiente bloqueado")

def test_remover_item_inexistente():
    repo.criar_player(5014)
    assert repo.remover_item(5014, "item_que_nao_existe", 1) is False
    print("✅ remover_item inexistente retorna False")


# ── EQUIPAMENTOS ───────────────────────────────────────────

def test_equipment_inicial_vazio():
    equip = repo.buscar_equipment(5001)
    assert equip["arma"] is None
    assert equip["armadura"] is None
    assert equip["acessorio"] is None
    print("✅ equipment inicial com slots vazios")

def test_equipar_arma():
    repo.atualizar_equipment(5001, "arma", "espada_enferrujada")
    equip = repo.buscar_equipment(5001)
    assert equip["arma"] == "espada_enferrujada"
    print("✅ equipar arma")

def test_equipar_armadura():
    repo.atualizar_equipment(5001, "armadura", "roupa_surrada")
    equip = repo.buscar_equipment(5001)
    assert equip["armadura"] == "roupa_surrada"
    print("✅ equipar armadura")

def test_equipar_acessorio():
    repo.atualizar_equipment(5001, "acessorio", "amuleto_madeira")
    equip = repo.buscar_equipment(5001)
    assert equip["acessorio"] == "amuleto_madeira"
    print("✅ equipar acessório")

def test_desequipar_slot():
    repo.atualizar_equipment(5002, "arma", "espada_enferrujada")
    repo.atualizar_equipment(5002, "arma", None)
    equip = repo.buscar_equipment(5002)
    assert equip["arma"] is None
    print("✅ desequipar slot (None)")

def test_slot_invalido_lanca_erro():
    try:
        repo.atualizar_equipment(5001, "capacete", "item_qualquer")
        assert False, "Deveria ter lançado ValueError"
    except ValueError:
        pass
    print("✅ slot inválido lança ValueError")

def test_trocar_item_equipado():
    repo.criar_player(5015)
    repo.atualizar_equipment(5015, "arma", "espada_enferrujada")
    repo.atualizar_equipment(5015, "arma", "adaga_afiada")
    equip = repo.buscar_equipment(5015)
    assert equip["arma"] == "adaga_afiada"
    print("✅ trocar item equipado substitui corretamente")


# ── FILTRO DE CATEGORIA (lógica do inventario.py) ─────────

def test_filtro_por_tipo_arma():
    armas = itens_por_tipo("arma")
    assert all(v["tipo"] == "arma" for v in armas.values())
    assert len(armas) > 0
    print(f"✅ filtro por tipo 'arma': {len(armas)} itens")

def test_filtro_por_tipo_armadura():
    armaduras = itens_por_tipo("armadura")
    assert all(v["tipo"] == "armadura" for v in armaduras.values())
    print(f"✅ filtro por tipo 'armadura': {len(armaduras)} itens")

def test_filtro_por_tipo_consumivel():
    consumiveis = itens_por_tipo("consumivel")
    assert all(v["tipo"] == "consumivel" for v in consumiveis.values())
    print(f"✅ filtro por tipo 'consumivel': {len(consumiveis)} itens")

def test_itens_equipaveis_tem_slot_valido():
    slots_validos = {"arma", "armadura", "acessorio", "consumivel"}
    for item_id, item in ITENS.items():
        assert item["tipo"] in slots_validos, f"Item '{item_id}' com tipo inválido: {item['tipo']}"
    print(f"✅ todos os {len(ITENS)} itens têm tipo válido")


# ── Runner ─────────────────────────────────────────────────

if __name__ == "__main__":
    testes = [
        test_inventario_inicial_vazio,
        test_adicionar_item_novo,
        test_adicionar_item_empilha,
        test_adicionar_multiplos_itens,
        test_remover_item_parcial,
        test_remover_item_total_remove_linha,
        test_remover_item_insuficiente,
        test_remover_item_inexistente,
        test_equipment_inicial_vazio,
        test_equipar_arma,
        test_equipar_armadura,
        test_equipar_acessorio,
        test_desequipar_slot,
        test_slot_invalido_lanca_erro,
        test_trocar_item_equipado,
        test_filtro_por_tipo_arma,
        test_filtro_por_tipo_armadura,
        test_filtro_por_tipo_consumivel,
        test_itens_equipaveis_tem_slot_valido,
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
        print(f"✅  TODOS OS {len(testes)} TESTES PASSARAM — Fase 4 validada!")
    else:
        print(f"❌  {falhas}/{len(testes)} testes falharam.")
