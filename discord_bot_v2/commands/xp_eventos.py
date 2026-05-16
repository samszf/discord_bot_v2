"""
xp_eventos.py — Eventos de XP passivo: mensagens de texto e canal de voz.

Responsabilidades:
- on_message: XP por mensagem com cooldown em memória
- task de voz: XP por tick a cada INTERVALO_VOZ_SEG se canal tem >= VOZ_MIN_MEMBROS membros
"""

import time
import discord
from discord.ext import commands, tasks

from database import repository as repo
from utils.xp_passivo import (
    XP_POR_MENSAGEM,
    COOLDOWN_MENSAGEM_SEG,
    XP_POR_TICK_VOZ,
    INTERVALO_VOZ_SEG,
    VOZ_MIN_MEMBROS,
    membros_humanos,
)
from utils.levelup import notificar_levelup


class XPEventosCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # cooldown em memória: {user_id: timestamp_ultimo_xp}
        # não usa banco para não gerar uma query a cada mensagem
        self._cooldown_texto: dict[int, float] = {}

        self.tick_voz.start()

    def cog_unload(self):
        self.tick_voz.cancel()

    # ── XP por mensagem de texto ──────────────────────────

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # ignora bots e mensagens fora de servidor
        if message.author.bot or not message.guild:
            return

        user_id = message.author.id

        # ignora jogadores não registrados silenciosamente
        if not repo.buscar_player(user_id):
            return

        agora = time.time()
        ultimo = self._cooldown_texto.get(user_id, 0)

        # verifica cooldown
        if agora - ultimo < COOLDOWN_MENSAGEM_SEG:
            return

        # atualiza cooldown e concede XP
        self._cooldown_texto[user_id] = agora
        resultado = repo.adicionar_xp(user_id, XP_POR_MENSAGEM)

        if resultado.get("level_up"):
            await notificar_levelup(
                canal=message.channel,
                user=message.author,
                nivel_antes=resultado["nivel_antes"],
                nivel_depois=resultado["nivel_atual"],
            )

    # ── XP por canal de voz ──────────────────────────────

    @tasks.loop(seconds=INTERVALO_VOZ_SEG)
    async def tick_voz(self):
        for guild in self.bot.guilds:
            for canal in guild.voice_channels:
                humanos = membros_humanos(canal)

                # só distribui XP se tiver membros suficientes
                if humanos < VOZ_MIN_MEMBROS:
                    continue

                for membro in canal.members:
                    if membro.bot:
                        continue

                    # ignora jogadores não registrados silenciosamente
                    if not repo.buscar_player(membro.id):
                        continue

                    resultado = repo.adicionar_xp(membro.id, XP_POR_TICK_VOZ)

                    if resultado.get("level_up"):
                        # tenta notificar no canal de texto geral ou sistema do servidor
                        canal_notif = (
                            guild.system_channel
                            or discord.utils.get(guild.text_channels, name="geral")
                            or discord.utils.get(guild.text_channels, name="general")
                        )
                        if canal_notif:
                            await notificar_levelup(
                                canal=canal_notif,
                                user=membro,
                                nivel_antes=resultado["nivel_antes"],
                                nivel_depois=resultado["nivel_atual"],
                            )

    @tick_voz.before_loop
    async def antes_do_tick(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(XPEventosCog(bot))
