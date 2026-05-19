"""
habilidade_view.py — Select menu de habilidades durante o combate.
"""

import discord
from utils.habilidades import HABILIDADES
from utils.classes import habilidades_disponiveis


class HabilidadeSelect(discord.ui.Select):
    def __init__(self, classe: str, nivel: int, user_id: int,
                 cooldowns_ativos: set, callback_fn):
        self.user_id = user_id
        self.callback_fn = callback_fn

        disponiveis = habilidades_disponiveis(classe, nivel)
        opcoes = []

        for hab_id in disponiveis:
            hab = HABILIDADES.get(hab_id)
            if not hab:
                continue

            em_cooldown = hab_id in cooldowns_ativos
            label = hab["nome"]
            descricao = hab["descricao"][:100]
            if em_cooldown:
                label = f"[CD] {hab['nome']}"
                descricao = "⏳ Em cooldown"

            opcoes.append(discord.SelectOption(
                label=label,
                value=hab_id,
                description=descricao,
                emoji=hab["emoji"],
            ))

        if not opcoes:
            opcoes = [discord.SelectOption(
                label="Nenhuma habilidade disponível",
                value="none",
                description="Suba de nível para desbloquear habilidades.",
            )]

        super().__init__(
            placeholder="Escolha uma habilidade...",
            min_values=1,
            max_values=1,
            options=opcoes,
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ Este não é o seu combate!", ephemeral=True
            )
            return

        hab_id = self.values[0]
        if hab_id == "none":
            await interaction.response.send_message(
                "❌ Nenhuma habilidade disponível ainda.", ephemeral=True
            )
            return

        await self.callback_fn(interaction, hab_id)


class HabilidadeView(discord.ui.View):
    def __init__(self, classe: str, nivel: int, user_id: int,
                 cooldowns_ativos: set, callback_fn):
        super().__init__(timeout=30)
        self.add_item(HabilidadeSelect(
            classe, nivel, user_id, cooldowns_ativos, callback_fn
        ))
