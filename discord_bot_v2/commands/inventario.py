"""
inventario.py — Comando /inventario com paginação e categorias.
"""

import discord
from discord.ext import commands
from discord import app_commands

from database import repository as repo
from utils.items import buscar_item, RARIDADE_EMOJI, RARIDADE_COR
from utils.embeds import embed_erro, COR_INFO

ITENS_POR_PAGINA = 8

CATEGORIAS = {
    "todos":      ("📦", None),
    "armas":      ("🗡️", "arma"),
    "armaduras":  ("🛡️", "armadura"),
    "acessorios": ("📿", "acessorio"),
    "consumiveis":("🧪", "consumivel"),
}


def build_embed_inventario(
    user: discord.Member,
    itens: list[dict],
    pagina: int,
    total_paginas: int,
    categoria: str,
) -> discord.Embed:
    emoji_cat, _ = CATEGORIAS[categoria]
    embed = discord.Embed(
        title=f"🎒 Inventário de {user.display_name}",
        color=COR_INFO
    )
    embed.set_thumbnail(url=user.display_avatar.url)

    if not itens:
        embed.description = "*Nenhum item encontrado nesta categoria.*"
        return embed

    inicio = pagina * ITENS_POR_PAGINA
    fim = inicio + ITENS_POR_PAGINA
    pagina_itens = itens[inicio:fim]

    linhas = []
    for entrada in pagina_itens:
        item = buscar_item(entrada["item_id"])
        if not item:
            continue
        raridade = item.get("raridade", "comum")
        emoji = RARIDADE_EMOJI.get(raridade, "⚪")

        stats = []
        if item.get("atk"):     stats.append(f"⚔️{item['atk']}")
        if item.get("defesa"):  stats.append(f"🛡️{item['defesa']}")
        if item.get("hp"):      stats.append(f"❤️{item['hp']}")
        if item.get("cura"):    stats.append(f"💊{item['cura']}")
        stats_txt = "  ".join(stats) if stats else ""

        qtd = f" `x{entrada['quantidade']}`" if entrada["quantidade"] > 1 else ""
        linhas.append(f"{emoji} **{item['nome']}**{qtd}  {stats_txt}")

    embed.description = "\n".join(linhas)
    embed.set_footer(text=f"Página {pagina + 1}/{total_paginas}  •  {emoji_cat} {categoria.capitalize()}  •  RPG Bot V2")
    return embed


class InventarioView(discord.ui.View):
    def __init__(self, user: discord.Member, itens_completos: list[dict], categoria: str):
        super().__init__(timeout=90)
        self.user = user
        self.itens_completos = itens_completos
        self.categoria = categoria
        self.pagina = 0
        self._atualizar_botoes()

    @property
    def total_paginas(self) -> int:
        return max(1, -(-len(self.itens_completos) // ITENS_POR_PAGINA))

    def _atualizar_botoes(self):
        self.anterior.disabled = self.pagina == 0
        self.proximo.disabled = self.pagina >= self.total_paginas - 1

    def build_embed(self) -> discord.Embed:
        return build_embed_inventario(
            self.user,
            self.itens_completos,
            self.pagina,
            self.total_paginas,
            self.categoria,
        )

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def anterior(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("❌ Este não é o seu inventário!", ephemeral=True)
            return
        self.pagina -= 1
        self._atualizar_botoes()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def proximo(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("❌ Este não é o seu inventário!", ephemeral=True)
            return
        self.pagina += 1
        self._atualizar_botoes()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)


class InventarioCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="inventario", description="Veja os itens do seu inventário.")
    @app_commands.describe(categoria="Filtrar por categoria de item")
    @app_commands.choices(categoria=[
        app_commands.Choice(name="📦 Todos",        value="todos"),
        app_commands.Choice(name="🗡️ Armas",        value="armas"),
        app_commands.Choice(name="🛡️ Armaduras",    value="armaduras"),
        app_commands.Choice(name="📿 Acessórios",   value="acessorios"),
        app_commands.Choice(name="🧪 Consumíveis",  value="consumiveis"),
    ])
    async def inventario(
        self,
        interaction: discord.Interaction,
        categoria: str = "todos",
    ):
        await interaction.response.defer()

        player = repo.buscar_player(interaction.user.id)
        if not player:
            await interaction.followup.send(
                embed=embed_erro("❌ Não registrado", "Use `/registrar` primeiro."),
                ephemeral=True
            )
            return

        todos = repo.buscar_inventario(interaction.user.id)

        _, tipo_filtro = CATEGORIAS.get(categoria, (None, None))
        if tipo_filtro:
            filtrados = [
                e for e in todos
                if (buscar_item(e["item_id"]) or {}).get("tipo") == tipo_filtro
            ]
        else:
            filtrados = todos

        view = InventarioView(interaction.user, filtrados, categoria)
        await interaction.followup.send(embed=view.build_embed(), view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(InventarioCog(bot))
