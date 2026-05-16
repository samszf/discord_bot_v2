"""
aventura.py — Comando /aventura.
Inicia um combate procedural contra um slime.
"""

import discord
from discord.ext import commands
from discord import app_commands

from database import repository as repo
from utils.slimes import gerar_slime
from utils.combat import iniciar_combate, barra_hp
from utils.cooldown import verificar_cooldown, registrar_uso
from utils.embeds import embed_erro, embed_aviso
from views.combat_view import CombateView


class AventuraCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="aventura",
        description="Parte em uma aventura e enfrente um slime!"
    )
    async def aventura(self, interaction: discord.Interaction):
        await interaction.response.defer()

        user_id = interaction.user.id

        # ── Verifica registro ──────────────────────────────
        player = repo.buscar_player(user_id)
        if not player:
            embed = embed_erro(
                "❌ Você não está registrado!",
                "Use `/registrar` para criar seu personagem."
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # ── Verifica cooldown ──────────────────────────────
        pode_usar, segundos_restantes = verificar_cooldown(user_id, "aventura")
        if not pode_usar:
            embed = embed_aviso(
                "⏳ Você ainda está se recuperando!",
                f"Aguarde **{segundos_restantes}s** para partir em nova aventura."
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # ── Gera slime e inicia combate ────────────────────
        slime = gerar_slime(player["nivel"])
        estado = iniciar_combate(user_id, slime)

        # ── Registra cooldown ──────────────────────────────
        registrar_uso(user_id, "aventura")

        # ── Monta embed inicial ────────────────────────────
        embed = discord.Embed(
            title=f"⚔️ Aventura — {slime['emoji']} {slime['nome']}",
            description=(
                f"Um **{slime['nome']}** apareceu no seu caminho!\n\n"
                f"**{slime['emoji']} {slime['nome']}**\n"
                f"{barra_hp(slime['hp_atual'], slime['hp_max'])}\n"
                f"`{slime['hp_atual']}/{slime['hp_max']} HP` • "
                f"`{slime['atk']} ATK` • `{slime['defesa']} DEF`\n\n"
                f"**🧙 Seus stats:**\n"
                f"`{estado['jogador_hp']} HP` • "
                f"`{estado['jogador_atk']} ATK` • "
                f"`{estado['jogador_defesa']} DEF`"
            ),
            color=0xE74C3C
        )
        embed.set_footer(text="RPG Bot V2 • Escolha sua ação!")

        view = CombateView(estado, interaction)
        await interaction.followup.send(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(AventuraCog(bot))
