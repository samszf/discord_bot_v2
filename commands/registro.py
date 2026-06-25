"""
registro.py — Comando /registrar com escolha de classe.
"""

import discord
from discord.ext import commands
from discord import app_commands

from utils.player import registrar_jogador
from utils.classes import CLASSES
from utils.embeds import embed_sucesso, embed_erro
from database import repository as repo
from views.classe_view import ClasseView


class RegistroCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="registrar",
        description="Cria seu personagem e entra no mundo do RPG!"
    )
    async def registrar(self, interaction: discord.Interaction):
        # verifica se já está registrado
        if repo.buscar_player(interaction.user.id):
            embed = embed_erro(
                "❌ Já registrado",
                "Você já possui um personagem! Use `/perfil` para ver seus stats."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # pede para escolher a classe
        # divide as 13 classes em dois campos para não ultrapassar o limite do embed
        classes_lista = list(CLASSES.items())
        metade = len(classes_lista) // 2 + len(classes_lista) % 2

        embed_escolha = discord.Embed(
            title="⚔️ Bem-vindo ao RPG!",
            description=(
                f"Olá, **{interaction.user.display_name}**!\n\n"
                "Antes de começar, escolha sua **classe** abaixo.\n"
                "Esta escolha é **permanente** — pense bem!"
            ),
            color=0x9B59B6,
        )
        embed_escolha.add_field(
            name="Classes",
            value="\n".join(
                f"{d['emoji']} **{nome}** — {d['role']}"
                for nome, d in classes_lista[:metade]
            ),
            inline=True,
        )
        embed_escolha.add_field(
            name="\u200b",
            value="\n".join(
                f"{d['emoji']} **{nome}** — {d['role']}"
                for nome, d in classes_lista[metade:]
            ),
            inline=True,
        )
        embed_escolha.set_thumbnail(url=interaction.user.display_avatar.url)
        embed_escolha.set_footer(text="RPG Bot V2 • Menu expira em 60s")

        view = ClasseView()
        await interaction.response.send_message(embed=embed_escolha, view=view)

        # aguarda escolha
        await view.wait()

        if not view.classe_escolhida:
            await interaction.edit_original_response(
                embed=embed_erro("⏰ Tempo esgotado", "Use `/registrar` novamente para criar seu personagem."),
                view=None
            )
            return

        # cria jogador e define classe
        registrar_jogador(interaction.user.id)
        repo.definir_classe(interaction.user.id, view.classe_escolhida)

        player = repo.buscar_player(interaction.user.id)
        dados_classe = CLASSES[view.classe_escolhida]

        embed_final = embed_sucesso(
            f"{dados_classe['emoji']} Personagem criado!",
            f"**{interaction.user.display_name}** entrou no mundo como **{view.classe_escolhida}**!\n\n"
            f"**Stats iniciais:**\n"
            f"❤️ HP: `{player['hp_base']}`\n"
            f"⚔️ ATK: `{player['atk_base']}`\n"
            f"🛡️ DEF: `{player['defesa_base']}`\n"
            f"💰 Ouro: `{player['ouro']}`\n\n"
            f"Use `/perfil` para ver seus stats e `/aventura` para batalhar!"
        )
        embed_final.set_thumbnail(url=interaction.user.display_avatar.url)

        await interaction.edit_original_response(embed=embed_final, view=None)


async def setup(bot: commands.Bot):
    await bot.add_cog(RegistroCog(bot))
