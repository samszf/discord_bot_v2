"""
embeds.py — Funções auxiliares para criar embeds padronizados.
"""

import discord
from datetime import datetime

COR_SUCESSO   = 0x2ECC71  # verde
COR_ERRO      = 0xE74C3C  # vermelho
COR_INFO      = 0x3498DB  # azul
COR_AVISO     = 0xF39C12  # laranja
COR_COMBATE   = 0xE74C3C  # vermelho
COR_LOOT      = 0xF1C40F  # dourado
COR_PERFIL    = 0x9B59B6  # roxo


def embed_base(
    titulo: str,
    descricao: str = "",
    cor: int = COR_INFO
) -> discord.Embed:
    embed = discord.Embed(
        title=titulo,
        description=descricao,
        color=cor,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text="RPG Bot V2")
    return embed


def embed_sucesso(titulo: str, descricao: str = "") -> discord.Embed:
    return embed_base(titulo, descricao, COR_SUCESSO)


def embed_erro(titulo: str, descricao: str = "") -> discord.Embed:
    return embed_base(titulo, descricao, COR_ERRO)


def embed_aviso(titulo: str, descricao: str = "") -> discord.Embed:
    return embed_base(titulo, descricao, COR_AVISO)
