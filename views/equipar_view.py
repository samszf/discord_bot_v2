"""
equipar_view.py — Select menu para equipar itens do inventário.
"""

import discord
from utils.items import buscar_item, RARIDADE_EMOJI
from utils.embeds import embed_sucesso, embed_erro, embed_aviso
from database import repository as repo

SLOT_POR_TIPO = {
    "arma":      "arma",
    "armadura":  "armadura",
    "acessorio": "acessorio",
}


def build_opcoes(inventario: list[dict]) -> list[discord.SelectOption]:
    """
    Monta as opções do select a partir do inventário.
    Filtra apenas itens equipáveis (arma, armadura, acessório).
    """
    opcoes = []
    vistos = set()  # evita duplicatas do mesmo item

    for entrada in inventario:
        item_id = entrada["item_id"]
        if item_id in vistos:
            continue

        item = buscar_item(item_id)
        if not item or item["tipo"] not in SLOT_POR_TIPO:
            continue

        vistos.add(item_id)
        raridade = item.get("raridade", "comum")
        emoji = RARIDADE_EMOJI.get(raridade, "⚪")

        stats = []
        if item.get("atk"):    stats.append(f"+{item['atk']} ATK")
        if item.get("defesa"): stats.append(f"+{item['defesa']} DEF")
        if item.get("hp"):     stats.append(f"+{item['hp']} HP")
        descricao = "  ".join(stats) if stats else raridade.capitalize()

        opcoes.append(discord.SelectOption(
            label=item["nome"].replace("🗡️", "").replace("🔪", "").replace("⚔️", "")
                              .replace("🪓", "").replace("🌑", "").replace("✨", "")
                              .replace("👕", "").replace("🧥", "").replace("⛓️", "")
                              .replace("🛡️", "").replace("🌑", "").replace("📿", "")
                              .replace("💍", "").replace("❤️", "").replace("⚙️", "")
                              .replace("🔮", "").replace("👑", "").strip(),
            value=item_id,
            description=descricao,
            emoji=emoji,
        ))

    return opcoes


class EquiparSelect(discord.ui.Select):
    def __init__(self, opcoes: list[discord.SelectOption], user_id: int):
        super().__init__(
            placeholder="Escolha um item para equipar...",
            min_values=1,
            max_values=1,
            options=opcoes,
        )
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ Este não é o seu menu!", ephemeral=True
            )
            return

        item_id = self.values[0]
        item = buscar_item(item_id)
        slot = SLOT_POR_TIPO.get(item["tipo"])

        # verifica se ainda tem o item (pode ter vendido entre abrir e equipar)
        inventario = repo.buscar_inventario(self.user_id)
        tem_item = any(e["item_id"] == item_id for e in inventario)
        if not tem_item:
            await interaction.response.edit_message(
                embed=embed_erro("❌ Item não encontrado",
                                 "Você não possui mais esse item no inventário."),
                view=None
            )
            return

        # verifica o que está equipado atualmente no slot
        equipment = repo.buscar_equipment(self.user_id)
        item_atual_id = equipment.get(slot)
        item_atual = buscar_item(item_atual_id) if item_atual_id else None

        # equipa
        repo.atualizar_equipment(self.user_id, slot, item_id)

        raridade = item.get("raridade", "comum")
        emoji = RARIDADE_EMOJI.get(raridade, "⚪")

        stats = []
        if item.get("atk"):    stats.append(f"⚔️ +{item['atk']} ATK")
        if item.get("defesa"): stats.append(f"🛡️ +{item['defesa']} DEF")
        if item.get("hp"):     stats.append(f"❤️ +{item['hp']} HP")
        stats_txt = "  ".join(stats) if stats else "Sem bônus de stat"

        descricao = (
            f"{emoji} **{item['nome']}** equipado no slot **{slot}**!\n\n"
            f"{stats_txt}"
        )
        if item_atual:
            descricao += f"\n\n*Substituiu: {item_atual['nome']}*"

        # desabilita o select após uso
        self.disabled = True
        await interaction.response.edit_message(
            embed=embed_sucesso("✅ Item equipado!", descricao),
            view=self.view
        )


class EquiparView(discord.ui.View):
    def __init__(self, inventario: list[dict], user_id: int):
        super().__init__(timeout=60)
        opcoes = build_opcoes(inventario)

        if opcoes:
            # Discord limita 25 opções por select
            self.add_item(EquiparSelect(opcoes[:25], user_id))

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
