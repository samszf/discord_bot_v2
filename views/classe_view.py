"""
classe_view.py — Select menu de escolha de classe no /registrar.
"""

import discord
from utils.classes import CLASSES


class ClasseSelect(discord.ui.Select):
    def __init__(self):
        opcoes = [
            discord.SelectOption(
                label=nome,
                value=nome,
                description=dados["descricao"][:100],
                emoji=dados["emoji"],
            )
            for nome, dados in CLASSES.items()
        ]
        super().__init__(
            placeholder="Escolha sua classe...",
            min_values=1,
            max_values=1,
            options=opcoes,
        )

    async def callback(self, interaction: discord.Interaction):
        classe = self.values[0]
        dados = CLASSES[classe]

        self.disabled = True
        self.view.classe_escolhida = classe
        self.view.stop()

        cresc = dados["crescimento_por_nivel"]
        embed = discord.Embed(
            title=f"{dados['emoji']} Classe escolhida: {classe}",
            description=dados["descricao"],
            color=0x2ECC71,
        )
        embed.add_field(
            name="📊 Stats iniciais (bônus)",
            value=(
                f"❤️ +{dados['bonus_hp_inicial']} HP\n"
                f"⚔️ +{dados['bonus_atk_inicial']} ATK\n"
                f"🛡️ +{dados['bonus_defesa_inicial']} DEF"
            ),
            inline=True,
        )
        embed.add_field(
            name="📈 Crescimento por nível",
            value=(
                f"❤️ +{cresc['hp']} HP\n"
                f"⚔️ +{cresc['atk']} ATK\n"
                f"🛡️ +{cresc['defesa']} DEF"
            ),
            inline=True,
        )
        hab_nomes = dados["habilidades"]
        embed.add_field(
            name="✨ Habilidades (nível 1 / 3 / 6 / 10)",
            value=" → ".join(f"`{h}`" for h in hab_nomes),
            inline=False,
        )
        embed.set_footer(text="RPG Bot V2 • Esta escolha é permanente!")

        await interaction.response.edit_message(embed=embed, view=self.view)


class ClasseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.classe_escolhida: str | None = None
        self.add_item(ClasseSelect())

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
