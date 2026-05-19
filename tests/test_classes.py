"""
test_classes.py — Testes do sistema de classes.
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ["DB_PATH"] = ":memory:"

from database.connection import inicializar_banco, fechar_conexao
from database import repository as repo
from utils.classes import CLASSES, habilidades_disponiveis, bonus_por_nivel, listar_classes
from utils.habilidades import HABILIDADES, executar_habilidade
from utils.combat import iniciar_combate
from utils.slimes import gerar_slime

fechar_conexao()
inicializar_banco()


# ── DEFINIÇÃO DAS CLASSES ──────────────────────────────────

def test_classes_implementadas():
    classes = listar_classes()
    assert "Guerreiro" in classes
    assert "Mago" in classes
    assert "Bárbaro" in classes
    print(f"✅ {len(classes)} classes implementadas: {', '.join(classes)}")

def test_cada_classe_tem_campos_obrigatorios():
    campos = ["emoji", "role", "descricao", "bonus_hp_inicial",
              "bonus_atk_inicial", "bonus_defesa_inicial",
              "crescimento_por_nivel", "habilidades"]
    for nome, dados in CLASSES.items():
        for campo in campos:
            assert campo in dados, f"Classe '{nome}' sem campo '{campo}'"
    print(f"✅ todas as classes têm campos obrigatórios")

def test_cada_classe_tem_4_habilidades():
    for nome, dados in CLASSES.items():
        assert len(dados["habilidades"]) == 4, \
            f"Classe '{nome}' tem {len(dados['habilidades'])} habilidades, esperado 4"
    print("✅ todas as classes têm 4 habilidades")

def test_habilidades_registradas():
    for nome, dados in CLASSES.items():
        for hab_id in dados["habilidades"]:
            assert hab_id in HABILIDADES, \
                f"Habilidade '{hab_id}' da classe '{nome}' não está registrada"
    print(f"✅ todas as habilidades estão registradas ({len(HABILIDADES)} total)")


# ── DESBLOQUEIO DE HABILIDADES ─────────────────────────────

def test_nivel_1_desbloqueia_primeira_habilidade():
    habs = habilidades_disponiveis("Guerreiro", 1)
    assert len(habs) == 1
    assert "segunda_investida" in habs
    print("✅ nível 1 desbloqueia apenas 1ª habilidade")

def test_nivel_3_desbloqueia_segunda():
    habs = habilidades_disponiveis("Guerreiro", 3)
    assert len(habs) == 2
    print("✅ nível 3 desbloqueia 2ª habilidade")

def test_nivel_6_desbloqueia_terceira():
    habs = habilidades_disponiveis("Mago", 6)
    assert len(habs) == 3
    print("✅ nível 6 desbloqueia 3ª habilidade")

def test_nivel_10_desbloqueia_todas():
    habs = habilidades_disponiveis("Bárbaro", 10)
    assert len(habs) == 4
    print("✅ nível 10 desbloqueia todas as 4 habilidades")

def test_classe_inexistente_retorna_vazio():
    habs = habilidades_disponiveis("ClasseInexistente", 10)
    assert habs == []
    print("✅ classe inexistente retorna lista vazia")


# ── BONUS POR NÍVEL ────────────────────────────────────────

def test_bonus_guerreiro():
    b = bonus_por_nivel("Guerreiro")
    assert b["hp"] == 10 and b["atk"] == 3 and b["defesa"] == 2
    print(f"✅ bônus Guerreiro por nível: {b}")

def test_bonus_mago():
    b = bonus_por_nivel("Mago")
    assert b["hp"] == 4 and b["atk"] == 4 and b["defesa"] == 0
    print(f"✅ bônus Mago por nível: {b}")

def test_bonus_barbaro():
    b = bonus_por_nivel("Bárbaro")
    assert b["hp"] == 12 and b["atk"] == 3 and b["defesa"] == 1
    print(f"✅ bônus Bárbaro por nível: {b}")


# ── DEFINIR CLASSE NO BANCO ────────────────────────────────

def test_definir_classe_guerreiro():
    repo.criar_player(7001)
    resultado = repo.definir_classe(7001, "Guerreiro")
    assert resultado is True
    player = repo.buscar_player(7001)
    assert player["classe"] == "Guerreiro"
    assert player["hp_base"] == 100 + 25   # base + bônus guerreiro
    assert player["atk_base"] == 10 + 4
    assert player["defesa_base"] == 5 + 5
    print("✅ definir_classe Guerreiro aplica bônus corretos")

def test_definir_classe_mago():
    repo.criar_player(7002)
    repo.definir_classe(7002, "Mago")
    player = repo.buscar_player(7002)
    assert player["hp_base"] == 100 + 5
    assert player["atk_base"] == 10 + 7
    assert player["defesa_base"] == 5 + 0
    print("✅ definir_classe Mago aplica bônus corretos")

def test_definir_classe_nao_permite_redefinir():
    repo.criar_player(7003)
    assert repo.definir_classe(7003, "Guerreiro") is True
    assert repo.definir_classe(7003, "Mago") is False
    player = repo.buscar_player(7003)
    assert player["classe"] == "Guerreiro"
    print("✅ classe não pode ser redefinida")

def test_definir_classe_inexistente_retorna_false():
    repo.criar_player(7004)
    assert repo.definir_classe(7004, "Ninja") is False
    print("✅ classe inexistente retorna False")


# ── HABILIDADES EM COMBATE ─────────────────────────────────

def _estado_guerreiro():
    repo.criar_player(7010)
    repo.definir_classe(7010, "Guerreiro")
    slime = gerar_slime(1)
    slime["hp_atual"] = 200
    slime["hp_max"] = 200
    slime["atk"] = 5
    return iniciar_combate(7010, slime)

def _estado_mago():
    repo.criar_player(7011)
    repo.definir_classe(7011, "Mago")
    slime = gerar_slime(1)
    slime["hp_atual"] = 200
    slime["hp_max"] = 200
    slime["atk"] = 3
    return iniciar_combate(7011, slime)

def _estado_barbaro():
    repo.criar_player(7012)
    repo.definir_classe(7012, "Bárbaro")
    slime = gerar_slime(1)
    slime["hp_atual"] = 200
    slime["hp_max"] = 200
    slime["atk"] = 5
    return iniciar_combate(7012, slime)

def test_segunda_investida_causa_dano():
    estado = _estado_guerreiro()
    hp_antes = estado["slime_hp"]
    estado = executar_habilidade("segunda_investida", estado)
    assert estado["slime_hp"] < hp_antes
    assert estado["dano_total"] > 0
    print(f"✅ Segunda Investida causou {estado['dano_total']} de dano")

def test_surto_de_acao_requer_nivel_3():
    habs_n1 = habilidades_disponiveis("Guerreiro", 1)
    habs_n3 = habilidades_disponiveis("Guerreiro", 3)
    assert "surto_de_acao" not in habs_n1
    assert "surto_de_acao" in habs_n3
    print("✅ Surto de Ação requer nível 3")

def test_missil_magico_ignora_defesa():
    estado = _estado_mago()
    atk = estado["jogador_atk"]
    estado["slime"]["defesa"] = 999  # defesa absurda
    estado = executar_habilidade("missil_magico", estado)
    dano_esperado = int(atk * 1.5)
    assert estado["dano_total"] >= dano_esperado - 1
    print(f"✅ Míssil Mágico ignorou defesa: {estado['dano_total']} dano")

def test_furia_aumenta_atk():
    estado = _estado_barbaro()
    atk_antes = estado["jogador_atk"]
    estado = executar_habilidade("furia", estado)
    assert estado["jogador_atk"] > atk_antes
    assert "furia" in estado.get("buffs", {})
    print(f"✅ Fúria aumentou ATK: {atk_antes} → {estado['jogador_atk']}")

def test_armadura_arcana_aumenta_def():
    estado = _estado_mago()
    def_antes = estado["jogador_defesa"]
    estado = executar_habilidade("armadura_arcana", estado)
    assert estado["jogador_defesa"] == def_antes + 15
    print(f"✅ Armadura Arcana: DEF {def_antes} → {estado['jogador_defesa']}")

def test_resistencia_brutal_cria_buff():
    estado = _estado_barbaro()
    estado = executar_habilidade("resistencia_brutal", estado)
    assert "resistencia" in estado.get("buffs", {})
    print("✅ Resistência Brutal cria buff corretamente")

def test_estado_tem_classe_e_nivel():
    estado = _estado_guerreiro()
    assert estado["classe"] == "Guerreiro"
    assert estado["nivel"] >= 1
    assert estado["classe_emoji"] == "⚔️"
    print("✅ estado do combate inclui classe e nível")

def test_level_up_usa_crescimento_da_classe():
    repo.criar_player(7020)
    repo.definir_classe(7020, "Bárbaro")
    player_antes = repo.buscar_player(7020)
    from utils.xp import xp_para_nivel
    repo.adicionar_xp(7020, xp_para_nivel(2) + 1)
    player_depois = repo.buscar_player(7020)
    assert player_depois["hp_base"] == player_antes["hp_base"] + 12  # bárbaro ganha 12 HP/nível
    assert player_depois["atk_base"] == player_antes["atk_base"] + 3
    print("✅ level up usa crescimento específico da classe Bárbaro")


# ── Runner ─────────────────────────────────────────────────

if __name__ == "__main__":
    testes = [
        test_classes_implementadas,
        test_cada_classe_tem_campos_obrigatorios,
        test_cada_classe_tem_4_habilidades,
        test_habilidades_registradas,
        test_nivel_1_desbloqueia_primeira_habilidade,
        test_nivel_3_desbloqueia_segunda,
        test_nivel_6_desbloqueia_terceira,
        test_nivel_10_desbloqueia_todas,
        test_classe_inexistente_retorna_vazio,
        test_bonus_guerreiro,
        test_bonus_mago,
        test_bonus_barbaro,
        test_definir_classe_guerreiro,
        test_definir_classe_mago,
        test_definir_classe_nao_permite_redefinir,
        test_definir_classe_inexistente_retorna_false,
        test_segunda_investida_causa_dano,
        test_surto_de_acao_requer_nivel_3,
        test_missil_magico_ignora_defesa,
        test_furia_aumenta_atk,
        test_armadura_arcana_aumenta_def,
        test_resistencia_brutal_cria_buff,
        test_estado_tem_classe_e_nivel,
        test_level_up_usa_crescimento_da_classe,
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
        print(f"✅  TODOS OS {len(testes)} TESTES PASSARAM — Sistema de Classes validado!")
    else:
        print(f"❌  {falhas}/{len(testes)} testes falharam.")
