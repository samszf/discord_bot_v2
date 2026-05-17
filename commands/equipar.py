"""
equipar.py — Comandos /equipar e /desequipar.
"""

import discord
from discord.ext import commands
from discord import app_commands

from database import repository as repo
from utils.items import buscar_item, nome_item, RARIDADE_EMOJI
from utils.embeds import embed_erro, embed_sucesso, embed_aviso, COR_INFO
from views.equipar_view import EquiparView


class EquiparCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="equipar", description="Equipa um item do seu inventário.")
    async def equipar(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        user_id = interaction.user.id

        if not repo.buscar_player(user_id):
            await interaction.followup.send(
                embed=embed_erro("❌ Não registrado", "Use `/registrar` primeiro.")
            )
            return

        inventario = repo.buscar_inventario(user_id)

        # filtra apenas itens equipáveis
        equipaveis = [
            e for e in inventario
            if (buscar_item(e["item_id"]) or {}).get("tipo") in ("arma", "armadura", "acessorio")
        ]

        if not equipaveis:
            await interaction.followup.send(
                embed=embed_aviso(
                    "🎒 Inventário vazio",
                    "Você não possui nenhum item equipável.\n"
                    "Aventure-se ou compre itens na `/loja`!"
                )
            )
            return

        view = EquiparView(equipaveis, user_id)

        embed = discord.Embed(
            title="⚙️ Equipar Item",
            description="Selecione um item do menu abaixo para equipar.",
            color=COR_INFO
        )
        embed.set_footer(text="RPG Bot V2 • Menu expira em 60s")

        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name="desequipar", description="Remove um item equipado.")
    @app_commands.describe(slot="Slot a desequipar")
    @app_commands.choices(slot=[
        app_commands.Choice(name="🗡️ Arma",     value="arma"),
        app_commands.Choice(name="🧥 Armadura",  value="armadura"),
        app_commands.Choice(name="📿 Acessório", value="acessorio"),
    ])
    async def desequipar(self, interaction: discord.Interaction, slot: str):
        await interaction.response.defer(ephemeral=True)

        user_id = interaction.user.id

        if not repo.buscar_player(user_id):
            await interaction.followup.send(
                embed=embed_erro("❌ Não registrado", "Use `/registrar` primeiro.")
            )
            return

        equipment = repo.buscar_equipment(user_id)
        item_atual_id = equipment.get(slot)

        if not item_atual_id:
            await interaction.followup.send(
                embed=embed_aviso("⚠️ Slot vazio",
                                  f"Você não tem nada equipado no slot **{slot}**.")
            )
            return

        repo.atualizar_equipment(user_id, slot, None)

        await interaction.followup.send(
            embed=embed_sucesso(
                "✅ Item desequipado!",
                f"**{nome_item(item_atual_id)}** foi removido do slot **{slot}**."
            )
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(EquiparCog(bot))
