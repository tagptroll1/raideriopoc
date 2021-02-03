from discord import Member, Role
from discord.ext import tasks
from discord.ext.commands import Bot, Cog, command

from bot.contants import GUILD_ID, ROLE_ID
from bot.services.raiderio_api import RaiderIOApi


class RaiderIOCog(Cog):
    """Cog related to RaiderIO API"""
    def __init__(self, bot: Bot, api: RaiderIOApi):
        self.bot: Bot = bot
        self.api: RaiderIOApi = api
        self.role_threshhold: int = 950

        self.background_task.start()

    @command()
    async def score(self, ctx, realm: str, name: str):
        async with ctx.typing():
            character = await self.api.get_character("eu", realm, name)
            score = self.api.get_character_score(character)
            await ctx.send(f"{character['name']}-{character['realm']} {score}")

    @tasks.loop(seconds=30)
    async def background_task(self):
        guild = await self.bot.fetch_guild(GUILD_ID)

        if not guild:
            return

        async for member in guild.fetch_members():

            for role in member.roles:
                if role.id == ROLE_ID:
                    await self.confirm_role(member, role)

    async def confirm_role(self, member: Member, role: Role) -> None:
        name = member.display_name.split("-")

        # it has 2 parts
        if len(name) == 2:
            character = await self.api.get_character("eu", name[1], name[0])
            score = self.api.get_character_score(character)

            if (score < self.role_threshhold):
                await member.remove_roles(role)
                print(f"removed role from {member}, score was {score}")


def setup(bot: Bot) -> None:
    raiderio_api = RaiderIOApi(bot.http_session)
    bot.add_cog(RaiderIOCog(bot, raiderio_api))
