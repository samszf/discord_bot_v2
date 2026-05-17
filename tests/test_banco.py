"""
test_banco.py — Testes da Fase 1: banco, conexão e repository.
"""

import os
import sys
import pytest

# permite importar os módulos do projeto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ["DB_PATH"] = ":memory:"  # banco em memória para testes

from database.connection import inicializar_banco, get_connection
from database import repository as repo


@pytest.fixture(autouse=True)
def setup_banco():
    """Inicializa o banco antes de cada teste."""
    inicializar_banco()


# ── PLAYERS ────────────────────────────────────

def test_criar_player_novo():
    resultado = repo.criar_player(1001)
    assert resultado is True


def test_criar_player_duplicado():
    repo.criar_player(1002)
    resultado = repo.criar_player(1002)
    assert resultado is False


def test_buscar_player_existente():
    repo.criar_player(1003)
    player = repo.buscar_player(1003)
    assert player is not None
    assert player["nivel"] == 1
    assert player["ouro"] == 100


def test_buscar_player_inexistente():
    player = repo.buscar_player(9999)
    assert player is None


def test_atualizar_player():
    repo.criar_player(1004)
    repo.atualizar_player(1004, ouro=500, nivel=3)
    player = repo.buscar_player(1004)
    assert player["ouro"] == 500
    assert player["nivel"] == 3


# ── OURO ───────────────────────────────────────

def test_adicionar_ouro():
    repo.criar_player(1005)
    novo_saldo = repo.adicionar_ouro(1005, 200)
    assert novo_saldo == 300  # 100 inicial + 200


def test_remover_ouro_suficiente():
    repo.criar_player(1006)
    resultado = repo.remover_ouro(1006, 50)
    assert resultado is True
    player = repo.buscar_player(1006)
    assert player["ouro"] == 50


def test_remover_ouro_insuficiente():
    repo.criar_player(1007)
    resultado = repo.remover_ouro(1007, 9999)
    assert resultado is False


# ── INVENTÁRIO ─────────────────────────────────

def test_adicionar_item_novo():
    repo.criar_player(1008)
    repo.adicionar_item(1008, "espada_enferrujada", 1)
    inventario = repo.buscar_inventario(1008)
    assert len(inventario) == 1
    assert inventario[0]["item_id"] == "espada_enferrujada"


def test_adicionar_item_empilha():
    repo.criar_player(1009)
    repo.adicionar_item(1009, "pocao_vida", 2)
    repo.adicionar_item(1009, "pocao_vida", 3)
    inventario = repo.buscar_inventario(1009)
    assert inventario[0]["quantidade"] == 5


def test_remover_item_parcial():
    repo.criar_player(1010)
    repo.adicionar_item(1010, "pocao_vida", 5)
    resultado = repo.remover_item(1010, "pocao_vida", 2)
    assert resultado is True
    inventario = repo.buscar_inventario(1010)
    assert inventario[0]["quantidade"] == 3


def test_remover_item_total():
    repo.criar_player(1011)
    repo.adicionar_item(1011, "espada_enferrujada", 1)
    resultado = repo.remover_item(1011, "espada_enferrujada", 1)
    assert resultado is True
    assert repo.buscar_inventario(1011) == []


def test_remover_item_insuficiente():
    repo.criar_player(1012)
    repo.adicionar_item(1012, "pocao_vida", 1)
    resultado = repo.remover_item(1012, "pocao_vida", 99)
    assert resultado is False


# ── EQUIPAMENTOS ───────────────────────────────

def test_buscar_equipment_inicial():
    repo.criar_player(1013)
    equip = repo.buscar_equipment(1013)
    assert equip is not None
    assert equip["arma"] is None
    assert equip["armadura"] is None


def test_atualizar_equipment():
    repo.criar_player(1014)
    repo.atualizar_equipment(1014, "arma", "espada_enferrujada")
    equip = repo.buscar_equipment(1014)
    assert equip["arma"] == "espada_enferrujada"


def test_slot_invalido():
    repo.criar_player(1015)
    with pytest.raises(ValueError):
        repo.atualizar_equipment(1015, "capacete", "item_qualquer")


# ── COOLDOWNS ──────────────────────────────────

def test_cooldown_inexistente():
    repo.criar_player(1016)
    resultado = repo.buscar_cooldown(1016, "aventura")
    assert resultado is None


def test_registrar_e_buscar_cooldown():
    repo.criar_player(1017)
    repo.registrar_cooldown(1017, "aventura")
    resultado = repo.buscar_cooldown(1017, "aventura")
    assert resultado is not None


# ── BATTLE STATS ───────────────────────────────

def test_battle_stats_inicial():
    repo.criar_player(1018)
    stats = repo.buscar_battle_stats(1018)
    assert stats["vitorias"] == 0
    assert stats["derrotas"] == 0


def test_atualizar_battle_stats_vitoria():
    repo.criar_player(1019)
    repo.atualizar_battle_stats(1019, vitoria=True, dano_causado=150, slimes_derrotados=1)
    stats = repo.buscar_battle_stats(1019)
    assert stats["vitorias"] == 1
    assert stats["dano_total"] == 150
    assert stats["slimes_derrotados"] == 1


def test_atualizar_battle_stats_derrota():
    repo.criar_player(1020)
    repo.atualizar_battle_stats(1020, vitoria=False, dano_causado=40)
    stats = repo.buscar_battle_stats(1020)
    assert stats["derrotas"] == 1
    assert stats["dano_total"] == 40
