"""
checks.py — Decorators e verificações reutilizáveis para commands.
"""

import discord
from discord.ext import commands
from database.repository import buscar_player


def jogador_registrado():
    """
    Decorator que bloqueia o comando se o usuário não estiver registrado.
    Uso: @jogador_registrado()
    """
    async def predicate(ctx: commands.Context) -> bool:
        player = buscar_player(ctx.author.id)
        if not player:
            embed = discord.Embed(
                title="❌ Você não está registrado!",
                description="Use `/registrar` para criar seu personagem.",
                color=0xE74C3C
            )
            await ctx.send(embed=embed)
            return False
        return True
    return commands.check(predicate)
