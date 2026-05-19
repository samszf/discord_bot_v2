import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from database.connection import inicializar_banco

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("PREFIX", "!")

COGS = [
    "commands.registro",
    "commands.admin",
    "commands.perfil",
    "commands.xp_eventos",
    "commands.aventura",
    "commands.inventario",
    "commands.equipar",
    "commands.loja",
]

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Bot online: {bot.user} (ID: {bot.user.id})")
    print(f"📡 Servidores conectados: {len(bot.guilds)}")
    for guild in bot.guilds:
        try:
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            print(f"🔄 Slash commands sincronizados em '{guild.name}': {len(synced)}")
        except Exception as e:
            print(f"❌ Erro ao sincronizar em '{guild.name}': {e}")


@bot.command(name="sync")
@commands.is_owner()
async def sync_commands(ctx: commands.Context):
    """Força a sincronização de slash commands (apenas dono do bot). Uso: !sync"""
    for guild in bot.guilds:
        try:
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            await ctx.send(f"✅ {len(synced)} comando(s) sincronizado(s) em **{guild.name}**.")
        except Exception as e:
            await ctx.send(f"❌ Erro em **{guild.name}**: {e}")


@bot.event
async def on_command_error(ctx: commands.Context, error: Exception):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ Argumento faltando. Use o comando corretamente.")
        return
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Aguarde **{error.retry_after:.1f}s** para usar esse comando novamente.")
        return
    print(f"[ERRO] {error}")
    await ctx.send("❌ Ocorreu um erro inesperado. Tente novamente.")


async def carregar_cogs():
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            print(f"  ✅ Cog carregado: {cog}")
        except Exception as e:
            print(f"  ❌ Falha ao carregar {cog}: {e}")


async def main():
    inicializar_banco()
    print("🗄️  Banco de dados inicializado.")
    async with bot:
        await carregar_cogs()
        await bot.start(TOKEN)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
