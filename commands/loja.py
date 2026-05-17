"""
loja.py — Comandos /loja e /vender.
"""

import discord
from discord.ext import commands
from discord import app_commands

from database import repository as repo
from utils.economy import comprar_item, vender_item, calcular_preco_venda, itens_da_loja
from utils.items import buscar_item, RARIDADE_EMOJI, RARIDADE_COR
from utils.embeds import embed_erro, embed_sucesso, embed_aviso, COR_LOOT

ITENS_POR_PAGINA = 6

SECOES = {
    "armas":       ("🗡️", "arma"),
    "armaduras":   ("🛡️", "armadura"),
    "acessorios":  ("📿", "acessorio"),
    "consumiveis": ("🧪", "consumivel"),
}


def build_embed_loja(secao: str, pagina: int, total_paginas: int) -> discord.Embed:
    emoji, tipo = SECOES[secao]
    loja = itens_da_loja()
    itens = loja.get(tipo, [])

    embed = discord.Embed(
        title=f"🏪 Loja — {emoji} {secao.capitalize()}",
        description="Use `/loja comprar <item_id>` para comprar um item.",
        color=COR_LOOT,
    )

    inicio = pagina * ITENS_POR_PAGINA
    fim = inicio + ITENS_POR_PAGINA
    pagina_itens = itens[inicio:fim]

    if not pagina_itens:
        embed.description = "*Nenhum item disponível nesta seção.*"
        return embed

    for item in pagina_itens:
        raridade = item.get("raridade", "comum")
        emoji_r = RARIDADE_EMOJI.get(raridade, "⚪")

        stats = []
        if item.get("atk"):    stats.append(f"⚔️ +{item['atk']} ATK")
        if item.get("defesa"): stats.append(f"🛡️ +{item['defesa']} DEF")
        if item.get("hp"):     stats.append(f"❤️ +{item['hp']} HP")
        if item.get("cura"):   stats.append(f"💊 Cura {item['cura']} HP")
        stats_txt = "  ".join(stats) if stats else "Sem bônus"

        embed.add_field(
            name=f"{emoji_r} {item['nome']}  —  💰 {item['preco']}",
            value=f"`{item['item_id']}`\n{stats_txt}",
            inline=False,
        )

    embed.set_footer(text=f"Página {pagina + 1}/{total_paginas}  •  RPG Bot V2")
    return embed


class LojaView(discord.ui.View):
    def __init__(self, secao: str):
        super().__init__(timeout=90)
        self.secao = secao
        self.pagina = 0
        self._atualizar_botoes()

    @property
    def _itens_secao(self) -> list:
        _, tipo = SECOES[self.secao]
        return itens_da_loja().get(tipo, [])

    @property
    def total_paginas(self) -> int:
        return max(1, -(-len(self._itens_secao) // ITENS_POR_PAGINA))

    def _atualizar_botoes(self):
        self.anterior.disabled = self.pagina == 0
        self.proximo.disabled  = self.pagina >= self.total_paginas - 1

    def build_embed(self) -> discord.Embed:
        return build_embed_loja(self.secao, self.pagina, self.total_paginas)

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def anterior(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.pagina -= 1
        self._atualizar_botoes()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def proximo(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.pagina += 1
        self._atualizar_botoes()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)


class LojaCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ── /loja ─────────────────────────────────────────────

    @app_commands.command(name="loja", description="Veja os itens disponíveis na loja.")
    @app_commands.describe(secao="Categoria de itens")
    @app_commands.choices(secao=[
        app_commands.Choice(name="🗡️ Armas",        value="armas"),
        app_commands.Choice(name="🛡️ Armaduras",    value="armaduras"),
        app_commands.Choice(name="📿 Acessórios",   value="acessorios"),
        app_commands.Choice(name="🧪 Consumíveis",  value="consumiveis"),
    ])
    async def loja(self, interaction: discord.Interaction, secao: str = "armas"):
        await interaction.response.defer()

        if not repo.buscar_player(interaction.user.id):
            await interaction.followup.send(
                embed=embed_erro("❌ Não registrado", "Use `/registrar` primeiro."),
                ephemeral=True,
            )
            return

        player = repo.buscar_player(interaction.user.id)
        view = LojaView(secao)
        embed = view.build_embed()
        embed.set_author(name=f"💰 Seu saldo: {player['ouro']} ouro")
        await interaction.followup.send(embed=embed, view=view)

    # ── /comprar ──────────────────────────────────────────

    @app_commands.command(name="comprar", description="Compra um item da loja.")
    @app_commands.describe(item_id="ID do item (visível na loja)")
    async def comprar(self, interaction: discord.Interaction, item_id: str):
        await interaction.response.defer(ephemeral=True)

        user_id = interaction.user.id
        if not repo.buscar_player(user_id):
            await interaction.followup.send(
                embed=embed_erro("❌ Não registrado", "Use `/registrar` primeiro.")
            )
            return

        resultado = comprar_item(user_id, item_id)

        if not resultado["sucesso"]:
            await interaction.followup.send(
                embed=embed_erro("❌ Compra falhou", resultado["mensagem"])
            )
            return

        item = buscar_item(item_id)
        player = repo.buscar_player(user_id)
        raridade = item.get("raridade", "comum")
        emoji = RARIDADE_EMOJI.get(raridade, "⚪")

        await interaction.followup.send(
            embed=embed_sucesso(
                "✅ Compra realizada!",
                f"{emoji} **{item['nome']}** adquirido por **{resultado['preco']} 💰**.\n"
                f"Saldo restante: **{player['ouro']} 💰**"
            )
        )

    # ── /vender ───────────────────────────────────────────

    @app_commands.command(name="vender", description="Vende um item do inventário.")
    @app_commands.describe(
        item_id="ID do item a vender",
        quantidade="Quantidade a vender (padrão: 1)",
    )
    async def vender(
        self,
        interaction: discord.Interaction,
        item_id: str,
        quantidade: int = 1,
    ):
        await interaction.response.defer(ephemeral=True)

        user_id = interaction.user.id
        if not repo.buscar_player(user_id):
            await interaction.followup.send(
                embed=embed_erro("❌ Não registrado", "Use `/registrar` primeiro.")
            )
            return

        if quantidade < 1:
            await interaction.followup.send(
                embed=embed_aviso("⚠️ Quantidade inválida", "A quantidade deve ser pelo menos 1.")
            )
            return

        resultado = vender_item(user_id, item_id, quantidade)

        if not resultado["sucesso"]:
            await interaction.followup.send(
                embed=embed_erro("❌ Venda falhou", resultado["mensagem"])
            )
            return

        item = buscar_item(item_id)
        player = repo.buscar_player(user_id)
        preco_unitario = calcular_preco_venda(item_id)

        desc = (
            f"**{item['nome']}** `x{quantidade}` vendido(s) por "
            f"**{resultado['ouro_ganho']} 💰**"
        )
        if quantidade > 1:
            desc += f"\n*(💰 {preco_unitario} por unidade)*"
        desc += f"\nSaldo atual: **{player['ouro']} 💰**"

        await interaction.followup.send(embed=embed_sucesso("✅ Venda realizada!", desc))


async def setup(bot: commands.Bot):
    await bot.add_cog(LojaCog(bot))
