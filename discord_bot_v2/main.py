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
    "commands.perfil",
    # "commands.aventura",
    # "commands.inventario",
    # "commands.equipar",
    # "commands.loja",
]

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Bot online: {bot.user} (ID: {bot.user.id})")
    print(f"📡 Servidores conectados: {len(bot.guilds)}")
    try:
        synced = await bot.tree.sync()
        print(f"🔄 Slash commands sincronizados: {len(synced)}")
    except Exception as e:
        print(f"❌ Erro ao sincronizar commands: {e}")


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
