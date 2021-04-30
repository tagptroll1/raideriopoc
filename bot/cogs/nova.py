import asyncio
from asyncio.tasks import Task
from itertools import chain
from typing import Callable, List

from discord import Message, Embed
from discord.emoji import Emoji
from discord.ext.commands import command
from discord.ext.commands import Bot, Cog

from bot.services.raiderio_api import RaiderIOApi
from bot.contants import Emojis


class NovaCog(Cog):
    """Cog related to RaiderIO API"""
    def __init__(self, bot: Bot, api: RaiderIOApi):
        self.bot = bot
        self.api = api
        self.signed_up = {}

    async def add_reaction_with_listener(self, msg: Message, reaction: str, callback: Callable):
        await msg.add_reaction(reaction)

        done = False
        while not done:
            re, user = await self.bot.wait_for(
                "reaction_add",
                check=lambda r, u: str(r) == reaction and r.message.id == msg.id and not u.bot)

            done = await callback(msg, user)

        if re:
            await re.clear()

    @command()
    async def new_run(self, ctx, faction, *, info=None):
        faction = Emojis.ALLIANCE

        if faction.lower() == "h" or faction.lower() == "horde":
            faction = Emojis.HORDE

        await ctx.message.delete()

        embed = Embed()

        if info:
            embed.description = f"{ctx.author} has started a new run on {faction}\n```\n{info}```"

        embed.add_field(name="📢 Announcer", value=f"- {ctx.author.mention}", inline=False)
        embed.add_field(name=f"{Emojis.DPS} Dps", value="-\n-\n-", inline=False)
        embed.add_field(name=f"{Emojis.HEALER} Healer", value="-", inline=False)
        embed.add_field(name=f"{Emojis.TANK} Tank", value="-", inline=False)
        msg = await ctx.send(embed=embed)

        self.signed_up[msg.id] = {}

        tasks = []
        tasks.append(self.add_reaction_with_listener(msg, Emojis.DPS, self.signup("Dps", 3)))
        tasks.append(self.add_reaction_with_listener(msg, Emojis.HEALER, self.signup("Healer")))
        tasks.append(self.add_reaction_with_listener(msg, Emojis.TANK, self.signup("Tank")))

        self.bot.tasks.update(tasks)
        await asyncio.gather(*tasks)

        for task in tasks:
            self.bot.tasks.remove(task)

    def signup(self, role, amount=1):
        async def wrapper(msg, user):
            if role not in self.signed_up[msg.id]:
                self.signed_up[msg.id][role] = set()

            all_users_signup = chain(*self.signed_up[msg.id].values())

            if user in all_users_signup:
                return False

            embed = msg.embeds[0]
            dic = embed.to_dict()

            for field in dic.get("fields", []):
                if role in field["name"]:
                    field["value"] = field["value"].replace("-", f"+ {user.mention}", 1)
                    break

            self.signed_up[msg.id][role].add(user)
            await msg.edit(embed=Embed.from_dict(dic))
            return len(self.signed_up[msg.id][role]) == amount
        return wrapper


def setup(bot: Bot) -> None:
    raiderio_api = RaiderIOApi(bot.http_session)
    bot.add_cog(NovaCog(bot, raiderio_api))
