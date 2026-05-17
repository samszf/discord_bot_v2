"""
equipar.py — Comandos /equipar e /desequipar.
"""

import discord
from discord.ext import commands
from discord import app_commands

from database import repository as repo
from utils.items import buscar_item, nome_item, RARIDADE_EMOJI
from utils.embeds import embed_erro, embed_sucesso, embed_aviso

SLOT_POR_TIPO = {
    "arma":      "arma",
    "armadura":  "armadura",
    "acessorio": "acessorio",
}


class EquiparCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="equipar", description="Equipa um item do seu inventário.")
    @app_commands.describe(item_id="ID do item a equipar (ex: espada_enferrujada)")
    async def equipar(self, interaction: discord.Interaction, item_id: str):
        await interaction.response.defer(ephemeral=True)

        user_id = interaction.user.id

        if not repo.buscar_player(user_id):
            await interaction.followup.send(
                embed=embed_erro("❌ Não registrado", "Use `/registrar` primeiro.")
            )
            return

        # verifica se o item existe no catálogo
        item = buscar_item(item_id)
        if not item:
            await interaction.followup.send(
                embed=embed_erro("❌ Item inválido", f"O item `{item_id}` não existe.")
            )
            return

        # verifica se o item é equipável
        slot = SLOT_POR_TIPO.get(item["tipo"])
        if not slot:
            await interaction.followup.send(
                embed=embed_aviso(
                    "⚠️ Item não equipável",
                    f"**{item['nome']}** é um **{item['tipo']}** e não pode ser equipado diretamente.\n"
                    f"Consumíveis podem ser usados em batalha."
                )
            )
            return

        # verifica se o jogador tem o item no inventário
        inventario = repo.buscar_inventario(user_id)
        tem_item = any(e["item_id"] == item_id for e in inventario)
        if not tem_item:
            await interaction.followup.send(
                embed=embed_erro(
                    "❌ Item não encontrado",
                    f"Você não possui **{item['nome']}** no inventário."
                )
            )
            return

        # verifica o que está equipado no slot atualmente
        equipment = repo.buscar_equipment(user_id)
        item_atual_id = equipment.get(slot)
        item_atual = buscar_item(item_atual_id) if item_atual_id else None

        # equipa o novo item
        repo.atualizar_equipment(user_id, slot, item_id)

        raridade = item.get("raridade", "comum")
        emoji = RARIDADE_EMOJI.get(raridade, "⚪")

        # monta stats do item
        stats = []
        if item.get("atk"):    stats.append(f"⚔️ +{item['atk']} ATK")
        if item.get("defesa"): stats.append(f"🛡️ +{item['defesa']} DEF")
        if item.get("hp"):     stats.append(f"❤️ +{item['hp']} HP")
        stats_txt = "  ".join(stats) if stats else "Sem bônus de stat"

        descricao = f"{emoji} **{item['nome']}** equipado no slot **{slot}**!\n\n{stats_txt}"

        if item_atual:
            descricao += f"\n\n*Substituiu: {item_atual['nome']}*"

        await interaction.followup.send(
            embed=embed_sucesso("✅ Item equipado!", descricao)
        )

    @app_commands.command(name="desequipar", description="Remove um item equipado.")
    @app_commands.describe(slot="Slot a desequipar")
    @app_commands.choices(slot=[
        app_commands.Choice(name="🗡️ Arma",      value="arma"),
        app_commands.Choice(name="🧥 Armadura",   value="armadura"),
        app_commands.Choice(name="📿 Acessório",  value="acessorio"),
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
                embed=embed_aviso("⚠️ Slot vazio", f"Você não tem nada equipado no slot **{slot}**.")
            )
            return

        item_atual = buscar_item(item_atual_id)
        repo.atualizar_equipment(user_id, slot, None)

        await interaction.followup.send(
            embed=embed_sucesso(
                "✅ Item desequipado!",
                f"**{nome_item(item_atual_id)}** foi removido do slot **{slot}**."
            )
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(EquiparCog(bot))
