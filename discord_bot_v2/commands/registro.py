"""
registro.py — Comando /registrar.
"""

import discord
from discord.ext import commands
from discord import app_commands

from utils.player import registrar_jogador
from utils.embeds import embed_sucesso, embed_erro


class RegistroCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="registrar",
        description="Cria seu personagem e entra no mundo do RPG!"
    )
    async def registrar(self, interaction: discord.Interaction):
        await interaction.response.defer()

        resultado = registrar_jogador(interaction.user.id)

        if not resultado["sucesso"]:
            embed = embed_erro(
                "❌ Registro falhou",
                resultado["mensagem"]
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        embed = embed_sucesso(
            "⚔️ Bem-vindo ao RPG!",
            f"Olá, **{interaction.user.display_name}**!\n\n"
            f"Seu personagem foi criado com sucesso.\n\n"
            f"**Stats iniciais:**\n"
            f"❤️ HP: `100`\n"
            f"⚔️ ATK: `10`\n"
            f"🛡️ DEF: `5`\n"
            f"💰 Ouro: `100`\n\n"
            f"Use `/perfil` para ver seus stats e `/aventura` para começar a batalhar!"
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(RegistroCog(bot))
