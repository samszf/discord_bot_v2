"""
test_fase5.py — Testes da Fase 5: loja e economia.
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ["DB_PATH"] = ":memory:"

from database.connection import inicializar_banco, fechar_conexao
from database import repository as repo
from utils.economy import comprar_item, vender_item, calcular_preco_venda, itens_da_loja
from utils.items import buscar_item

fechar_conexao()
inicializar_banco()

repo.criar_player(6001)  # jogador padrão com 100 ouro
repo.criar_player(6002)  # jogador para testes de saldo insuficiente


# ── PREÇO DE VENDA ─────────────────────────────────────────

def test_preco_venda_menor_que_compra():
    preco_compra = buscar_item("espada_enferrujada")["preco"]
    preco_venda  = calcular_preco_venda("espada_enferrujada")
    assert preco_venda < preco_compra
    print(f"✅ preço de venda ({preco_venda}) < preço de compra ({preco_compra})")

def test_preco_venda_minimo_um():
    preco = calcular_preco_venda("espada_enferrujada")
    assert preco >= 1
    print("✅ preço de venda mínimo é 1")

def test_preco_venda_item_inexistente():
    preco = calcular_preco_venda("item_fake")
    assert preco == 0
    print("✅ preço de venda de item inexistente retorna 0")


# ── COMPRA ─────────────────────────────────────────────────

def test_comprar_item_com_saldo_suficiente():
    # espada_enferrujada custa 50, jogador tem 100
    resultado = comprar_item(6001, "espada_enferrujada")
    assert resultado["sucesso"] is True
    inv = repo.buscar_inventario(6001)
    assert any(e["item_id"] == "espada_enferrujada" for e in inv)
    print("✅ comprar_item com saldo suficiente")

def test_comprar_debita_ouro():
    repo.criar_player(6010)
    saldo_antes = repo.buscar_player(6010)["ouro"]  # 100
    comprar_item(6010, "espada_enferrujada")         # custa 50
    saldo_depois = repo.buscar_player(6010)["ouro"]
    assert saldo_depois == saldo_antes - 50
    print(f"✅ comprar_item debita ouro corretamente ({saldo_antes} → {saldo_depois})")

def test_comprar_item_saldo_insuficiente():
    # lamina_abissal custa 2500, jogador 6002 tem 100
    resultado = comprar_item(6002, "lamina_abissal")
    assert resultado["sucesso"] is False
    assert "insuficiente" in resultado["mensagem"].lower() or "faltam" in resultado["mensagem"].lower()
    print("✅ comprar_item bloqueado por saldo insuficiente")

def test_comprar_item_inexistente():
    resultado = comprar_item(6001, "item_que_nao_existe")
    assert resultado["sucesso"] is False
    print("✅ comprar_item inexistente bloqueado")

def test_comprar_nao_debita_se_falhar():
    saldo_antes = repo.buscar_player(6002)["ouro"]
    comprar_item(6002, "lamina_abissal")
    saldo_depois = repo.buscar_player(6002)["ouro"]
    assert saldo_antes == saldo_depois
    print("✅ comprar_item não debita ouro se falhar")

def test_comprar_multiplas_vezes_empilha():
    repo.criar_player(6011)
    repo.atualizar_player(6011, ouro=1000)
    comprar_item(6011, "pocao_vida")
    comprar_item(6011, "pocao_vida")
    inv = repo.buscar_inventario(6011)
    pocao = next(e for e in inv if e["item_id"] == "pocao_vida")
    assert pocao["quantidade"] == 2
    print("✅ comprar múltiplas vezes empilha no inventário")


# ── VENDA ──────────────────────────────────────────────────

def test_vender_item_existente():
    repo.criar_player(6020)
    repo.adicionar_item(6020, "espada_enferrujada", 1)
    resultado = vender_item(6020, "espada_enferrujada", 1)
    assert resultado["sucesso"] is True
    assert resultado["ouro_ganho"] > 0
    print(f"✅ vender_item existente: ganhou {resultado['ouro_ganho']} ouro")

def test_vender_credita_ouro():
    repo.criar_player(6021)
    repo.adicionar_item(6021, "espada_enferrujada", 1)
    saldo_antes = repo.buscar_player(6021)["ouro"]
    resultado = vender_item(6021, "espada_enferrujada", 1)
    saldo_depois = repo.buscar_player(6021)["ouro"]
    assert saldo_depois == saldo_antes + resultado["ouro_ganho"]
    print(f"✅ vender_item credita ouro ({saldo_antes} → {saldo_depois})")

def test_vender_remove_do_inventario():
    repo.criar_player(6022)
    repo.adicionar_item(6022, "espada_enferrujada", 1)
    vender_item(6022, "espada_enferrujada", 1)
    inv = repo.buscar_inventario(6022)
    assert not any(e["item_id"] == "espada_enferrujada" for e in inv)
    print("✅ vender_item remove item do inventário")

def test_vender_quantidade_parcial():
    repo.criar_player(6023)
    repo.adicionar_item(6023, "pocao_vida", 5)
    resultado = vender_item(6023, "pocao_vida", 3)
    assert resultado["sucesso"] is True
    inv = repo.buscar_inventario(6023)
    pocao = next(e for e in inv if e["item_id"] == "pocao_vida")
    assert pocao["quantidade"] == 2
    print("✅ vender_item quantidade parcial correto")

def test_vender_item_sem_ter():
    resultado = vender_item(6001, "lamina_abissal", 1)
    assert resultado["sucesso"] is False
    print("✅ vender_item sem ter no inventário bloqueado")

def test_vender_quantidade_maior_que_tem():
    repo.criar_player(6024)
    repo.adicionar_item(6024, "pocao_vida", 2)
    resultado = vender_item(6024, "pocao_vida", 99)
    assert resultado["sucesso"] is False
    print("✅ vender_item quantidade maior que possui bloqueado")

def test_vender_multiplica_ouro_por_quantidade():
    repo.criar_player(6025)
    repo.adicionar_item(6025, "pocao_vida", 4)
    preco_unit = calcular_preco_venda("pocao_vida")
    resultado = vender_item(6025, "pocao_vida", 4)
    assert resultado["ouro_ganho"] == preco_unit * 4
    print(f"✅ vender múltiplos multiplica ouro: {preco_unit} x 4 = {resultado['ouro_ganho']}")


# ── CATÁLOGO DA LOJA ───────────────────────────────────────

def test_loja_tem_todas_categorias():
    loja = itens_da_loja()
    assert "arma" in loja
    assert "armadura" in loja
    assert "acessorio" in loja
    assert "consumivel" in loja
    print("✅ loja tem todas as categorias")

def test_loja_ordenada_por_preco():
    loja = itens_da_loja()
    for tipo, itens in loja.items():
        precos = [i["preco"] for i in itens]
        assert precos == sorted(precos), f"Categoria '{tipo}' não está ordenada por preço"
    print("✅ todos os itens da loja ordenados por preço crescente")

def test_loja_itens_tem_item_id():
    loja = itens_da_loja()
    for tipo, itens in loja.items():
        for item in itens:
            assert "item_id" in item, f"Item sem item_id na categoria '{tipo}'"
    print("✅ todos os itens da loja têm item_id")


# ── Runner ─────────────────────────────────────────────────

if __name__ == "__main__":
    testes = [
        test_preco_venda_menor_que_compra,
        test_preco_venda_minimo_um,
        test_preco_venda_item_inexistente,
        test_comprar_item_com_saldo_suficiente,
        test_comprar_debita_ouro,
        test_comprar_item_saldo_insuficiente,
        test_comprar_item_inexistente,
        test_comprar_nao_debita_se_falhar,
        test_comprar_multiplas_vezes_empilha,
        test_vender_item_existente,
        test_vender_credita_ouro,
        test_vender_remove_do_inventario,
        test_vender_quantidade_parcial,
        test_vender_item_sem_ter,
        test_vender_quantidade_maior_que_tem,
        test_vender_multiplica_ouro_por_quantidade,
        test_loja_tem_todas_categorias,
        test_loja_ordenada_por_preco,
        test_loja_itens_tem_item_id,
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
        print(f"✅  TODOS OS {len(testes)} TESTES PASSARAM — Fase 5 validada!")
    else:
        print(f"❌  {falhas}/{len(testes)} testes falharam.")
