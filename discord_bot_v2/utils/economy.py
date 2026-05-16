"""
economy.py — Lógica de compra e venda de itens.
"""

from utils.items import buscar_item, ITENS, itens_por_tipo
from database import repository as repo

PERCENTUAL_VENDA = 0.4  # jogador recebe 40% do preço base ao vender


def calcular_preco_venda(item_id: str) -> int:
    item = buscar_item(item_id)
    if not item:
        return 0
    return max(1, int(item["preco"] * PERCENTUAL_VENDA))


def comprar_item(user_id: int, item_id: str) -> dict:
    """
    Processa a compra de um item.
    Retorna dict com: sucesso (bool), mensagem (str), preco (int).
    """
    item = buscar_item(item_id)
    if not item:
        return {"sucesso": False, "mensagem": "Item não encontrado.", "preco": 0}

    preco = item["preco"]
    player = repo.buscar_player(user_id)
    if not player:
        return {"sucesso": False, "mensagem": "Jogador não registrado.", "preco": preco}

    if player["ouro"] < preco:
        falta = preco - player["ouro"]
        return {
            "sucesso": False,
            "mensagem": f"Ouro insuficiente. Faltam **{falta}** 💰.",
            "preco": preco,
        }

    repo.remover_ouro(user_id, preco)
    repo.adicionar_item(user_id, item_id, 1)

    return {"sucesso": True, "mensagem": "Compra realizada!", "preco": preco}


def vender_item(user_id: int, item_id: str, quantidade: int = 1) -> dict:
    """
    Processa a venda de um item do inventário.
    Retorna dict com: sucesso (bool), mensagem (str), ouro_ganho (int).
    """
    item = buscar_item(item_id)
    if not item:
        return {"sucesso": False, "mensagem": "Item não encontrado.", "ouro_ganho": 0}

    removeu = repo.remover_item(user_id, item_id, quantidade)
    if not removeu:
        return {
            "sucesso": False,
            "mensagem": f"Você não possui **{quantidade}x {item['nome']}** no inventário.",
            "ouro_ganho": 0,
        }

    ouro_ganho = calcular_preco_venda(item_id) * quantidade
    repo.adicionar_ouro(user_id, ouro_ganho)

    return {"sucesso": True, "mensagem": "Venda realizada!", "ouro_ganho": ouro_ganho}


def itens_da_loja() -> dict[str, list[dict]]:
    """
    Retorna os itens disponíveis na loja agrupados por tipo.
    Exclui consumíveis de uma seção separada para melhor organização.
    """
    grupos = {
        "arma":      [],
        "armadura":  [],
        "acessorio": [],
        "consumivel":[],
    }
    for item_id, dados in ITENS.items():
        tipo = dados.get("tipo")
        if tipo in grupos:
            grupos[tipo].append({"item_id": item_id, **dados})

    # ordena cada grupo por preço
    for tipo in grupos:
        grupos[tipo].sort(key=lambda x: x["preco"])

    return grupos
