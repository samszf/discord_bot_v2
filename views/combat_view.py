"""
combat_view.py — Botões interativos do combate por turnos.
"""

import discord
from utils.combat import processar_turno_ataque, processar_fuga, barra_hp
from utils.habilidades import HABILIDADES, executar_habilidade
from utils.classes import habilidades_disponiveis
from utils.loot import sortear_loot, sortear_ouro
from utils.items import nome_item, RARIDADE_EMOJI, buscar_item
from utils.levelup import notificar_levelup
from database import repository as repo


def build_embed_combate(estado: dict) -> discord.Embed:
    slime = estado["slime"]
    cor = 0xE74C3C if estado["jogador_hp"] < estado["jogador_hp_max"] * 0.3 else 0x3498DB

    embed = discord.Embed(
        title=f"{slime['emoji']} {slime['nome']} — Turno {estado['turno']}",
        color=cor
    )

    barra_s = barra_hp(estado["slime_hp"], estado["slime_hp_max"])
    embed.add_field(
        name=f"{slime['emoji']} {slime['nome']}",
        value=f"{barra_s}\n`{estado['slime_hp']}/{estado['slime_hp_max']} HP`",
        inline=True
    )

    barra_j = barra_hp(estado["jogador_hp"], estado["jogador_hp_max"])

    # mostra classe no nome do jogador se tiver
    classe = estado.get("classe")
    classe_txt = f" [{estado['classe_emoji']} {classe}]" if classe else ""
    embed.add_field(
        name=f"🧙 Você{classe_txt}",
        value=f"{barra_j}\n`{estado['jogador_hp']}/{estado['jogador_hp_max']} HP`",
        inline=True
    )

    # buffs ativos
    buffs = estado.get("buffs", {})
    if buffs:
        nomes_buffs = []
        for k, v in buffs.items():
            turnos = v.get("turnos", 0)
            nomes_buffs.append(f"`{k}` ({turnos}t)")
        embed.add_field(
            name="✨ Buffs ativos",
            value="  ".join(nomes_buffs),
            inline=False
        )

    if estado["log"]:
        embed.add_field(
            name="📜 Último turno",
            value="\n".join(estado["log"]),
            inline=False
        )

    embed.set_footer(text="RPG Bot V2 • Use os botões abaixo para agir")
    return embed


def build_embed_resultado(estado: dict, xp_ganho: int,
                          ouro_ganho: int, item_drop: str | None) -> discord.Embed:
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
        # cooldowns de habilidades: {hab_id: turnos_restantes}
        self._cooldowns: dict[str, int] = {}
        # atualiza botão de habilidade baseado na classe
        self._atualizar_botao_habilidade()

    def _atualizar_botao_habilidade(self):
        """Habilita ou desabilita o botão de habilidade conforme a classe."""
        tem_classe = bool(self.estado.get("classe"))
        self.habilidade.disabled = not tem_classe

    def _cooldowns_ativos(self) -> set:
        return {hab_id for hab_id, t in self._cooldowns.items() if t > 0}

    def _decrementar_cooldowns(self):
        for hab_id in list(self._cooldowns):
            self._cooldowns[hab_id] = max(0, self._cooldowns[hab_id] - 1)

    async def _atualizar_embed(self, interaction: discord.Interaction):
        embed = build_embed_combate(self.estado)
        if self.estado["finalizado"]:
            await self._finalizar_combate(interaction)
            return
        self._decrementar_cooldowns()
        await interaction.response.edit_message(embed=embed, view=self)

    async def _finalizar_combate(self, interaction: discord.Interaction):
        self.finalizado = True
        self.clear_items()

        estado = self.estado
        user_id = estado["user_id"]
        vitoria = estado["vitoria"]
        slime = estado["slime"]

        xp_ganho    = slime["xp_recompensa"] if vitoria else 5
        ouro_ganho  = sortear_ouro(slime["ouro_min"], slime["ouro_max"]) if vitoria else 0
        item_drop   = sortear_loot(slime["raridades"]) if vitoria else None

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

        embed = build_embed_resultado(estado, xp_ganho, ouro_ganho, item_drop)
        await interaction.response.edit_message(embed=embed, view=self)

        if resultado_xp.get("level_up"):
            await notificar_levelup(
                canal=interaction,
                user=interaction.user,
                nivel_antes=resultado_xp["nivel_antes"],
                nivel_depois=resultado_xp["nivel_atual"],
            )

    async def on_timeout(self):
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

    @discord.ui.button(label="✨ Habilidade", style=discord.ButtonStyle.primary)
    async def habilidade(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.estado["user_id"]:
            await interaction.response.send_message("❌ Este não é o seu combate!", ephemeral=True)
            return
        if self.finalizado:
            return

        from views.habilidade_view import HabilidadeView

        classe = self.estado.get("classe")
        nivel  = self.estado.get("nivel", 1)

        view = HabilidadeView(
            classe=classe,
            nivel=nivel,
            user_id=self.estado["user_id"],
            cooldowns_ativos=self._cooldowns_ativos(),
            callback_fn=self._usar_habilidade,
        )
        await interaction.response.send_message(
            "✨ Escolha sua habilidade:", view=view, ephemeral=True
        )

    async def _usar_habilidade(self, interaction: discord.Interaction, hab_id: str):
        """Callback chamado pelo HabilidadeView ao selecionar uma habilidade."""
        if hab_id in self._cooldowns_ativos():
            await interaction.response.send_message(
                "⏳ Esta habilidade está em cooldown!", ephemeral=True
            )
            return

        hab = HABILIDADES.get(hab_id)
        if not hab:
            return

        self.estado = executar_habilidade(hab_id, self.estado)

        # registra cooldown
        self._cooldowns[hab_id] = hab["cooldown_turnos"]

        # atualiza a mensagem principal do combate
        embed = build_embed_combate(self.estado)
        if self.estado["finalizado"]:
            await self._finalizar_combate(interaction)
        else:
            self._decrementar_cooldowns()
            await interaction.response.edit_message(
                content=None, embed=embed, view=self
            )

    @discord.ui.button(label="🏃 Fugir", style=discord.ButtonStyle.secondary)
    async def fugir(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.estado["user_id"]:
            await interaction.response.send_message("❌ Este não é o seu combate!", ephemeral=True)
            return
        if self.finalizado:
            return
        self.estado = processar_fuga(self.estado)
        await self._atualizar_embed(interaction)
