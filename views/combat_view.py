"""
combat_view.py — Botões interativos do combate por turnos.
"""

import discord
from utils.combat import processar_turno_ataque, processar_fuga, barra_hp
from utils.loot import sortear_loot, sortear_ouro
from utils.items import nome_item, RARIDADE_EMOJI, buscar_item
from utils.levelup import notificar_levelup
from database import repository as repo


def build_embed_combate(estado: dict) -> discord.Embed:
    """Monta o embed do estado atual do combate."""
    slime = estado["slime"]
    cor = 0xE74C3C if estado["jogador_hp"] < estado["jogador_hp_max"] * 0.3 else 0x3498DB

    embed = discord.Embed(
        title=f"{slime['emoji']} {slime['nome']} — Turno {estado['turno']}",
        color=cor
    )

    # HP do slime
    barra_s = barra_hp(estado["slime_hp"], estado["slime_hp_max"])
    embed.add_field(
        name=f"{slime['emoji']} {slime['nome']}",
        value=f"{barra_s}\n`{estado['slime_hp']}/{estado['slime_hp_max']} HP`",
        inline=True
    )

    # HP do jogador
    barra_j = barra_hp(estado["jogador_hp"], estado["jogador_hp_max"])
    embed.add_field(
        name="🧙 Você",
        value=f"{barra_j}\n`{estado['jogador_hp']}/{estado['jogador_hp_max']} HP`",
        inline=True
    )

    # log do último turno
    if estado["log"]:
        embed.add_field(
            name="📜 Último turno",
            value="\n".join(estado["log"]),
            inline=False
        )

    embed.set_footer(text="RPG Bot V2 • Use os botões abaixo para agir")
    return embed


def build_embed_resultado(estado: dict, xp_ganho: int, ouro_ganho: int, item_drop: str | None) -> discord.Embed:
    """Monta o embed de resultado final do combate."""
    if estado["vitoria"]:
        embed = discord.Embed(
            title="🏆 Vitória!",
            description=f"Você derrotou o **{estado['slime']['emoji']} {estado['slime']['nome']}**!",
            color=0x2ECC71
        )
        embed.add_field(name="✨ XP ganho",   value=f"`+{xp_ganho} XP`",   inline=True)
        embed.add_field(name="💰 Ouro ganho", value=f"`+{ouro_ganho} 💰`", inline=True)
        embed.add_field(name="💥 Dano total", value=f"`{estado['dano_total']}`", inline=True)

        if item_drop:
            item = buscar_item(item_drop)
            raridade = item.get("raridade", "comum") if item else "comum"
            emoji = RARIDADE_EMOJI.get(raridade, "⚪")
            embed.add_field(
                name="🎁 Item dropado!",
                value=f"{emoji} **{nome_item(item_drop)}**",
                inline=False
            )
        else:
            embed.add_field(name="🎁 Loot", value="*Nenhum item dropou.*", inline=False)

    else:
        embed = discord.Embed(
            title="💀 Derrota!",
            description="Você foi derrotado ou fugiu do combate.",
            color=0xE74C3C
        )
        embed.add_field(name="✨ XP de consolação", value=f"`+{xp_ganho} XP`", inline=True)
        embed.add_field(name="💥 Dano causado",     value=f"`{estado['dano_total']}`", inline=True)

    embed.set_footer(text="RPG Bot V2 • Use /aventura para batalhar novamente")
    return embed


class CombateView(discord.ui.View):
    def __init__(self, estado: dict, interaction_original: discord.Interaction):
        super().__init__(timeout=120)
        self.estado = estado
        self.interaction_original = interaction_original
        self.finalizado = False

    async def _atualizar_embed(self, interaction: discord.Interaction):
        """Atualiza o embed do combate após cada ação."""
        embed = build_embed_combate(self.estado)

        if self.estado["finalizado"]:
            await self._finalizar_combate(interaction)
            return

        await interaction.response.edit_message(embed=embed, view=self)

    async def _finalizar_combate(self, interaction: discord.Interaction):
        """Processa o fim do combate: loot, XP, banco e embed final."""
        self.finalizado = True
        self.clear_items()

        estado = self.estado
        user_id = estado["user_id"]
        vitoria = estado["vitoria"]
        slime = estado["slime"]

        # ── Recompensas ───────────────────────────────────
        xp_ganho = slime["xp_recompensa"] if vitoria else 5
        ouro_ganho = sortear_ouro(slime["ouro_min"], slime["ouro_max"]) if vitoria else 0
        item_drop = sortear_loot(slime["raridades"]) if vitoria else None

        # ── Salva no banco ────────────────────────────────
        resultado_xp = repo.adicionar_xp(user_id, xp_ganho)
        if ouro_ganho > 0:
            repo.adicionar_ouro(user_id, ouro_ganho)
        if item_drop:
            repo.adicionar_item(user_id, item_drop)

        repo.atualizar_battle_stats(
            user_id,
            vitoria=vitoria,
            dano_causado=estado["dano_total"],
            slimes_derrotados=1 if vitoria else 0,
        )

        # ── Embed de resultado ────────────────────────────
        embed = build_embed_resultado(estado, xp_ganho, ouro_ganho, item_drop)
        await interaction.response.edit_message(embed=embed, view=self)

        # ── Notifica level up se houver ───────────────────
        if resultado_xp.get("level_up"):
            await notificar_levelup(
                canal=interaction,
                user=interaction.user,
                nivel_antes=resultado_xp["nivel_antes"],
                nivel_depois=resultado_xp["nivel_atual"],
            )

    async def on_timeout(self):
        """Desativa os botões se o combate expirar."""
        self.clear_items()
        try:
            embed = build_embed_combate(self.estado)
            embed.set_footer(text="⏰ Combate encerrado por inatividade.")
            await self.interaction_original.edit_original_response(embed=embed, view=self)
        except Exception:
            pass

    # ── Botões ────────────────────────────────────────────

    @discord.ui.button(label="⚔️ Atacar", style=discord.ButtonStyle.danger)
    async def atacar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.estado["user_id"]:
            await interaction.response.send_message("❌ Este não é o seu combate!", ephemeral=True)
            return
        if self.finalizado:
            return

        self.estado = processar_turno_ataque(self.estado)
        await self._atualizar_embed(interaction)

    @discord.ui.button(label="🏃 Fugir", style=discord.ButtonStyle.secondary)
    async def fugir(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.estado["user_id"]:
            await interaction.response.send_message("❌ Este não é o seu combate!", ephemeral=True)
            return
        if self.finalizado:
            return

        self.estado = processar_fuga(self.estado)
        await self._atualizar_embed(interaction)
