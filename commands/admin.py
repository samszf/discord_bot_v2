"""
admin.py — Comandos de administração para o dono do bot.

Todos os comandos são restritos ao dono do bot (is_owner).
Prefixo: !admin <comando>

Comandos disponíveis:
  !admin info @usuario         — ver dados completos do jogador
  !admin deletar @usuario      — apagar personagem
  !admin nivel @usuario <n>    — definir nível
  !admin xp @usuario <n>       — adicionar XP
  !admin ouro @usuario <n>     — adicionar ouro
  !admin classe @usuario       — definir/trocar classe (select menu)
  !admin item @usuario <id>    — adicionar item ao inventário
  !admin resetcd @usuario      — resetar todos os cooldowns
  !admin listar                — listar todos os jogadores registrados
"""

import discord
from discord.ext import commands

from database import repository as repo
from database.connection import get_connection
from utils.classes import CLASSES, listar_classes
from utils.items import buscar_item, ITENS


def dono_only():
    async def predicate(ctx: commands.Context) -> bool:
        return await ctx.bot.is_owner(ctx.author)
    return commands.check(predicate)


class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ── !admin ────────────────────────────────────────────

    @commands.group(name="admin", invoke_without_command=True)
    @dono_only()
    async def admin(self, ctx: commands.Context):
        embed = discord.Embed(
            title="🔧 Comandos de Administração",
            color=0xE67E22,
        )
        embed.add_field(
            name="Jogadores",
            value=(
                "`!admin info @usuario` — ver dados do jogador\n"
                "`!admin deletar @usuario` — apagar personagem\n"
                "`!admin listar` — listar todos os jogadores\n"
            ),
            inline=False,
        )
        embed.add_field(
            name="Progressão",
            value=(
                "`!admin nivel @usuario <n>` — definir nível\n"
                "`!admin xp @usuario <n>` — adicionar XP\n"
                "`!admin ouro @usuario <n>` — adicionar ouro\n"
            ),
            inline=False,
        )
        embed.add_field(
            name="Classe e Itens",
            value=(
                "`!admin classe @usuario` — definir/trocar classe\n"
                "`!admin item @usuario <item_id>` — adicionar item\n"
                "`!admin resetcd @usuario` — resetar cooldowns\n"
            ),
            inline=False,
        )
        embed.set_footer(text="⚠️ Apenas o dono do bot pode usar esses comandos.")
        await ctx.send(embed=embed)

    # ── !admin info ───────────────────────────────────────

    @admin.command(name="info")
    @dono_only()
    async def admin_info(self, ctx: commands.Context, usuario: discord.Member):
        player = repo.buscar_player(usuario.id)
        if not player:
            await ctx.send(f"❌ **{usuario.display_name}** não está registrado.")
            return

        equip  = repo.buscar_equipment(usuario.id)
        stats  = repo.buscar_battle_stats(usuario.id)
        inv    = repo.buscar_inventario(usuario.id)

        embed = discord.Embed(
            title=f"🔧 Admin — {usuario.display_name}",
            color=0xE67E22
        )
        embed.add_field(
            name="📊 Dados",
            value=(
                f"ID: `{player['user_id']}`\n"
                f"Nível: `{player['nivel']}`\n"
                f"XP: `{player['xp']}`\n"
                f"Ouro: `{player['ouro']}`\n"
                f"Classe: `{player['classe'] or 'Nenhuma'}`\n"
                f"Criado em: `{player['criado_em']}`"
            ),
            inline=True,
        )
        embed.add_field(
            name="⚔️ Stats",
            value=(
                f"HP: `{player['hp_base']}`\n"
                f"ATK: `{player['atk_base']}`\n"
                f"DEF: `{player['defesa_base']}`"
            ),
            inline=True,
        )
        embed.add_field(
            name="🏆 Batalhas",
            value=(
                f"Vitórias: `{stats['vitorias']}`\n"
                f"Derrotas: `{stats['derrotas']}`\n"
                f"Slimes: `{stats['slimes_derrotados']}`\n"
                f"Dano total: `{stats['dano_total']}`"
            ),
            inline=True,
        )
        embed.add_field(
            name="⚙️ Equipamentos",
            value=(
                f"Arma: `{equip['arma'] or 'Vazio'}`\n"
                f"Armadura: `{equip['armadura'] or 'Vazio'}`\n"
                f"Acessório: `{equip['acessorio'] or 'Vazio'}`"
            ),
            inline=True,
        )
        embed.add_field(
            name=f"🎒 Inventário ({len(inv)} itens)",
            value="\n".join(
                f"`{e['item_id']}` x{e['quantidade']}" for e in inv[:10]
            ) or "*Vazio*",
            inline=False,
        )
        await ctx.send(embed=embed)

    # ── !admin deletar ────────────────────────────────────

    @admin.command(name="deletar")
    @dono_only()
    async def admin_deletar(self, ctx: commands.Context, usuario: discord.Member):
        player = repo.buscar_player(usuario.id)
        if not player:
            await ctx.send(f"❌ **{usuario.display_name}** não está registrado.")
            return

        # confirmação
        embed = discord.Embed(
            title="⚠️ Confirmar exclusão",
            description=(
                f"Tem certeza que deseja apagar o personagem de **{usuario.display_name}**?\n\n"
                f"Classe: `{player['classe'] or 'Nenhuma'}` | Nível: `{player['nivel']}`\n\n"
                "Responda com `sim` em 15 segundos para confirmar."
            ),
            color=0xE74C3C,
        )
        await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.content.lower() == "sim" and m.channel == ctx.channel

        try:
            await self.bot.wait_for("message", check=check, timeout=15)
        except Exception:
            await ctx.send("❌ Exclusão cancelada.")
            return

        with get_connection() as conn:
            conn.execute("DELETE FROM habilidades_cooldown WHERE user_id = ?", (usuario.id,))
            conn.execute("DELETE FROM cooldowns     WHERE user_id = ?", (usuario.id,))
            conn.execute("DELETE FROM battle_stats  WHERE user_id = ?", (usuario.id,))
            conn.execute("DELETE FROM equipment     WHERE user_id = ?", (usuario.id,))
            conn.execute("DELETE FROM inventory     WHERE user_id = ?", (usuario.id,))
            conn.execute("DELETE FROM players       WHERE user_id = ?", (usuario.id,))

        await ctx.send(f"✅ Personagem de **{usuario.display_name}** deletado com sucesso.")

    # ── !admin nivel ──────────────────────────────────────

    @admin.command(name="nivel")
    @dono_only()
    async def admin_nivel(self, ctx: commands.Context, usuario: discord.Member, nivel: int):
        if not repo.buscar_player(usuario.id):
            await ctx.send(f"❌ **{usuario.display_name}** não está registrado.")
            return
        if nivel < 1:
            await ctx.send("❌ Nível mínimo é 1.")
            return

        repo.atualizar_player(usuario.id, nivel=nivel, xp=0)
        await ctx.send(f"✅ Nível de **{usuario.display_name}** definido para `{nivel}`.")

    # ── !admin xp ─────────────────────────────────────────

    @admin.command(name="xp")
    @dono_only()
    async def admin_xp(self, ctx: commands.Context, usuario: discord.Member, quantidade: int):
        if not repo.buscar_player(usuario.id):
            await ctx.send(f"❌ **{usuario.display_name}** não está registrado.")
            return

        resultado = repo.adicionar_xp(usuario.id, quantidade)
        msg = f"✅ +`{quantidade}` XP para **{usuario.display_name}**."
        if resultado.get("level_up"):
            msg += f" 🎉 Subiu para o nível **{resultado['nivel_atual']}**!"
        await ctx.send(msg)

    # ── !admin ouro ───────────────────────────────────────

    @admin.command(name="ouro")
    @dono_only()
    async def admin_ouro(self, ctx: commands.Context, usuario: discord.Member, quantidade: int):
        if not repo.buscar_player(usuario.id):
            await ctx.send(f"❌ **{usuario.display_name}** não está registrado.")
            return

        novo_saldo = repo.adicionar_ouro(usuario.id, quantidade)
        await ctx.send(
            f"✅ +`{quantidade}` 💰 para **{usuario.display_name}**. "
            f"Saldo atual: `{novo_saldo}` 💰."
        )

    # ── !admin classe ─────────────────────────────────────

    @admin.command(name="classe")
    @dono_only()
    async def admin_classe(self, ctx: commands.Context, usuario: discord.Member):
        if not repo.buscar_player(usuario.id):
            await ctx.send(f"❌ **{usuario.display_name}** não está registrado.")
            return

        classes = listar_classes()
        lista = "\n".join(
            f"`{i+1}` — {CLASSES[c]['emoji']} **{c}** ({CLASSES[c]['role']})"
            for i, c in enumerate(classes)
        )
        embed = discord.Embed(
            title=f"🧙 Definir classe — {usuario.display_name}",
            description=f"{lista}\n\nResponda com o **número** da classe em 30 segundos.",
            color=0xE67E22,
        )
        await ctx.send(embed=embed)

        def check(m):
            return (
                m.author == ctx.author
                and m.channel == ctx.channel
                and m.content.isdigit()
                and 1 <= int(m.content) <= len(classes)
            )

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=30)
        except Exception:
            await ctx.send("❌ Tempo esgotado.")
            return

        classe_escolhida = classes[int(msg.content) - 1]

        # força a troca mesmo que já tenha classe (admin override)
        with get_connection() as conn:
            dados = CLASSES[classe_escolhida]
            player = repo.buscar_player(usuario.id)
            conn.execute(
                "UPDATE players SET classe = ?, hp_base = ?, atk_base = ?, defesa_base = ? WHERE user_id = ?",
                (
                    classe_escolhida,
                    player["hp_base"]         + dados["bonus_hp_inicial"],
                    player["atk_base"]        + dados["bonus_atk_inicial"],
                    player["defesa_base"]     + dados["bonus_defesa_inicial"],
                    usuario.id,
                )
            )

        await ctx.send(
            f"✅ Classe de **{usuario.display_name}** definida para "
            f"{CLASSES[classe_escolhida]['emoji']} **{classe_escolhida}**."
        )

    # ── !admin item ───────────────────────────────────────

    @admin.command(name="item")
    @dono_only()
    async def admin_item(self, ctx: commands.Context, usuario: discord.Member, item_id: str, quantidade: int = 1):
        if not repo.buscar_player(usuario.id):
            await ctx.send(f"❌ **{usuario.display_name}** não está registrado.")
            return

        item = buscar_item(item_id)
        if not item:
            ids_validos = ", ".join(list(ITENS.keys())[:10]) + "..."
            await ctx.send(
                f"❌ Item `{item_id}` não existe.\n"
                f"Alguns IDs válidos: `{ids_validos}`"
            )
            return

        repo.adicionar_item(usuario.id, item_id, quantidade)
        await ctx.send(
            f"✅ `{quantidade}x {item['nome']}` adicionado ao inventário de **{usuario.display_name}**."
        )

    # ── !admin resetcd ────────────────────────────────────

    @admin.command(name="resetcd")
    @dono_only()
    async def admin_resetcd(self, ctx: commands.Context, usuario: discord.Member):
        if not repo.buscar_player(usuario.id):
            await ctx.send(f"❌ **{usuario.display_name}** não está registrado.")
            return

        with get_connection() as conn:
            conn.execute("DELETE FROM cooldowns WHERE user_id = ?", (usuario.id,))
            conn.execute("DELETE FROM habilidades_cooldown WHERE user_id = ?", (usuario.id,))

        await ctx.send(f"✅ Todos os cooldowns de **{usuario.display_name}** foram resetados.")

    # ── !admin listar ─────────────────────────────────────

    @admin.command(name="listar")
    @dono_only()
    async def admin_listar(self, ctx: commands.Context):
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT user_id, nivel, classe, ouro FROM players ORDER BY nivel DESC"
            ).fetchall()

        if not rows:
            await ctx.send("Nenhum jogador registrado.")
            return

        linhas = []
        for row in rows:
            membro = ctx.guild.get_member(row["user_id"])
            nome = membro.display_name if membro else f"ID:{row['user_id']}"
            classe = row["classe"] or "Sem classe"
            emoji = CLASSES[classe]["emoji"] if classe in CLASSES else "❓"
            linhas.append(
                f"`Nv.{row['nivel']:>2}` {emoji} **{nome}** — `{classe}` | 💰`{row['ouro']}`"
            )

        embed = discord.Embed(
            title=f"👥 Jogadores registrados ({len(rows)})",
            description="\n".join(linhas),
            color=0xE67E22,
        )
        await ctx.send(embed=embed)

    # ── Erro de permissão ─────────────────────────────────

    @admin.error
    async def admin_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("❌ Apenas o dono do bot pode usar comandos de admin.")


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))
