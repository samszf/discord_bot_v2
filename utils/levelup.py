"""
levelup.py — Lógica de level up e notificações.
"""


def calcular_levelup(nivel_antes: int, nivel_depois: int) -> dict:
    """
    Calcula os bônus ganhos ao subir de nível.
    Retorna dict com os ganhos totais.
    """
    niveis_ganhos = nivel_depois - nivel_antes
    return {
        "niveis_ganhos": niveis_ganhos,
        "bonus_hp":      niveis_ganhos * 10,
        "bonus_atk":     niveis_ganhos * 2,
        "bonus_defesa":  niveis_ganhos * 1,
    }


async def notificar_levelup(canal, user, nivel_antes: int, nivel_depois: int) -> None:
    """
    Envia uma mensagem de parabéns ao jogador que subiu de nível.
    Funciona tanto em canal quanto em interaction do discord.py.
    """
    import discord

    ganhos = calcular_levelup(nivel_antes, nivel_depois)

    embed = discord.Embed(
        title="🎉 LEVEL UP!",
        description=(
            f"Parabéns, **{user.display_name}**!\n"
            f"Você subiu do nível **{nivel_antes}** para o nível **{nivel_depois}**!\n\n"
            f"**Bônus ganhos:**\n"
            f"❤️ +{ganhos['bonus_hp']} HP\n"
            f"⚔️ +{ganhos['bonus_atk']} ATK\n"
            f"🛡️ +{ganhos['bonus_defesa']} DEF"
        ),
        color=0xF1C40F
    )
    embed.set_thumbnail(url=user.display_avatar.url)

    if isinstance(canal, discord.Interaction):
        await canal.followup.send(embed=embed)
    else:
        await canal.send(embed=embed)
