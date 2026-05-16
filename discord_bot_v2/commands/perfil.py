"""
perfil.py — Comando /perfil.
"""

import discord
from discord.ext import commands
from discord import app_commands

from utils.player import buscar_stats_completos
from utils.xp import xp_para_nivel
from utils.items import nome_item, RARIDADE_EMOJI, buscar_item
from utils.embeds import embed_erro, COR_PERFIL


def barra_xp(xp_atual: int, xp_necessario: int, tamanho: int = 10) -> str:
    """Gera uma barra de progresso de XP visual."""
    preenchido = int((xp_atual / xp_necessario) * tamanho)
    preenchido = min(preenchido, tamanho)
    return "█" * preenchido + "░" * (tamanho - preenchido)


def formatar_slot(item_id: str | None, slot_nome: str) -> str:
    """Formata um slot de equipamento para exibição."""
    if not item_id:
        return f"*Nenhum*"
    item = buscar_item(item_id)
    if not item:
        return f"*Desconhecido*"
    raridade = item.get("raridade", "comum")
    emoji = RARIDADE_EMOJI.get(raridade, "⚪")
    return f"{emoji} {item['nome']}"


class PerfilCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="perfil",
        description="Exibe o perfil e stats do seu personagem."
    )
    @app_commands.describe(usuario="Ver o perfil de outro jogador (opcional)")
    async def perfil(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member = None
    ):
        await interaction.response.defer()

        alvo = usuario or interaction.user
        stats = buscar_stats_completos(alvo.id)

        if not stats:
            if alvo.id == interaction.user.id:
                msg = "Você ainda não se registrou! Use `/registrar` para começar."
            else:
                msg = f"**{alvo.display_name}** ainda não possui um personagem."
            embed = embed_erro("❌ Personagem não encontrado", msg)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(
            title=f"📜 Perfil de {alvo.display_name}",
            color=COR_PERFIL
        )
        embed.set_thumbnail(url=alvo.display_avatar.url)

        # ── Nível e XP ──────────────────────────────────────
        barra = barra_xp(stats["xp"], stats["xp_proximo"])
        nivel_txt = (
            f"**Nível {stats['nivel']}**\n"
            f"`{barra}` {stats['xp']}/{stats['xp_proximo']} XP"
        )
        if stats["classe"]:
            nivel_txt = f"*{stats['classe']}* — " + nivel_txt

        embed.add_field(name="🏅 Progressão", value=nivel_txt, inline=False)

        # ── Stats ────────────────────────────────────────────
        def fmt_stat(base: int, bonus: int, emoji: str) -> str:
            if bonus > 0:
                return f"{emoji} `{base + bonus}` *(+{bonus})*"
            return f"{emoji} `{base}`"

        stats_txt = (
            f"{fmt_stat(stats['hp_base'],     stats['bonus_hp'],     '❤️ HP')}\n"
            f"{fmt_stat(stats['atk_base'],    stats['bonus_atk'],    '⚔️ ATK')}\n"
            f"{fmt_stat(stats['defesa_base'], stats['bonus_defesa'], '🛡️ DEF')}"
        )
        embed.add_field(name="📊 Stats", value=stats_txt, inline=True)

        # ── Economia ─────────────────────────────────────────
        embed.add_field(
            name="💰 Economia",
            value=f"💰 Ouro: `{stats['ouro']}`",
            inline=True
        )

        embed.add_field(name="\u200b", value="\u200b", inline=False)

        # ── Equipamentos ─────────────────────────────────────
        equip_txt = (
            f"🗡️ Arma: {formatar_slot(stats['arma'], 'arma')}\n"
            f"🧥 Armadura: {formatar_slot(stats['armadura'], 'armadura')}\n"
            f"📿 Acessório: {formatar_slot(stats['acessorio'], 'acessorio')}"
        )
        embed.add_field(name="⚙️ Equipamentos", value=equip_txt, inline=False)

        # ── Batalhas ─────────────────────────────────────────
        total = stats["vitorias"] + stats["derrotas"]
        winrate = (
            f"{int(stats['vitorias'] / total * 100)}%"
            if total > 0 else "—"
        )
        batalhas_txt = (
            f"✅ Vitórias: `{stats['vitorias']}`\n"
            f"❌ Derrotas: `{stats['derrotas']}`\n"
            f"📈 Win rate: `{winrate}`\n"
            f"👾 Slimes derrotados: `{stats['slimes_derrotados']}`\n"
            f"💥 Dano total causado: `{stats['dano_total']}`"
        )
        embed.add_field(name="⚔️ Batalhas", value=batalhas_txt, inline=False)

        embed.set_footer(text="RPG Bot V2")

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(PerfilCog(bot))
