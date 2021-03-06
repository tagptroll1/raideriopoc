import re
import traceback

from discord import Guild, TextChannel
from discord.ext.commands import Bot, Cog, command
from discord.ext.commands.core import has_guild_permissions

from bot.contants import Emojis, GUILD_ID, BOOSTER_CHANNEL, Roles
from bot.services.raiderio_api import RaiderIOApi


class RaiderIOCog(Cog):
    """Cog related to RaiderIO API"""
    def __init__(self, bot: Bot, api: RaiderIOApi):
        self.bot: Bot = bot
        self.api: RaiderIOApi = api
        self.disabled = True
        self.role_threshhold: int = 1300
        self.reclaim_channel: TextChannel = None
        self.guild: Guild = None
        self.raiderio_regex = re.compile(
            r"https:\/\/raider\.io\/characters\/eu\/(.+)\/([^?.]+)")

        self.roles = {}

    @command()
    @has_guild_permissions(administrator=True)
    async def mythicroles(self, ctx, toggle=None):
        if toggle is None:
            self.disabled = not self.disabled
        else:
            self.disabled = bool(toggle)

        keyword = "Disabled" if self.disabled else "Enabled"
        return await ctx.send(f"{keyword} auto m+ roles")

    def get_and_set_role(self, rolename, id_):
        role = self.roles.get(rolename)
        if not role:
            role = self.guild.get_role(id_)
            self.roles[rolename] = role
        return role

    @staticmethod
    def has_role(member, role):
        return role in member.roles

    def get_roles(self, member, score, spec, faction):
        roles = []

        if faction == "horde":
            booster_role = self.get_and_set_role("booster_H", Roles.HORDE_BOOSTER)
            faction_role = self.get_and_set_role("horde", Roles.HORDE)
        else:
            booster_role = self.get_and_set_role("booster_A", Roles.ALLIANCE_BOOSTER)
            faction_role = self.get_and_set_role("alliance", Roles.ALLIANCE)

        eu_role = self.get_and_set_role("eu_role", Roles.EU)

        if score >= self.role_threshhold and booster_role not in member.roles:
            roles.append(booster_role)

        if faction_role not in member.roles:
            roles.append(faction_role)

        if eu_role not in member.roles:
            roles.append(eu_role)

        return roles

    @Cog.listener()
    async def on_message(self, message):
        if self.disabled:
            return

        if message.channel.id != BOOSTER_CHANNEL:
            return

        if message.author.bot:
            return

        self.guild = message.guild

        match = self.raiderio_regex.findall(message.content)

        if not match:
            print("empty match for " + message.author.name)
            return

        realm = match[0][0]
        char = match[0][1]

        if not (realm and char):
            await message.add_reaction(Emojis.CROSS)
            return

        try:
            resp = await self.api.get_character("eu", realm, char)

            name = resp["name"]
            realm = resp["realm"]
            spec = resp["active_spec_role"]
            faction = resp["faction"]

            if spec == "HEALING":
                spec = "healer"

            score = resp["mythic_plus_scores_by_season"][0]["scores"]["all"]
        except Exception:
            traceback.print_exc()
            return

        if score < self.role_threshhold:
            await message.add_reaction(Emojis.MOCKING)
            return

        roles = self.get_roles(message.author, score, spec, faction)

        if roles:
            await message.author.add_roles(*roles)
            faction_short = "H" if faction == "horde" else "A"
            realm = realm.replace(" ", "")
            await message.author.edit(nick=f"{name}-{realm} [{faction_short}]")
            await message.add_reaction(Emojis.CHECK)
        else:
            await message.add_reaction(Emojis.AWKWARD)

    @command()  # This command is not tested well, might break.
    async def verify(self, ctx, *, url):
        if ctx.guild.id != GUILD_ID and ctx.channel.id != BOOSTER_CHANNEL:
            return

        self.guild = ctx.guild

        match = self.raiderio_regex.findall(url)

        if not match:
            print("empty match for " + ctx.author.name)
            return

        realm = match[0][0]
        char = match[0][1]

        if not (realm and char):
            await ctx.message.add_reaction(Emojis.CROSS)
            return

        try:
            resp = await self.api.get_character("eu", realm, char)

            name = resp["name"]
            realm = resp["realm"]
            spec = resp["active_spec_role"]
            faction = resp["faction"]

            if spec == "HEALING":
                spec = "healer"

            score = resp["mythic_plus_scores_by_season"][0]["scores"]["all"]
        except Exception:
            traceback.print_exc()
            return

        if score < self.role_threshhold:
            await ctx.message.add_reaction(Emojis.MOCKING)
            return

        roles = self.get_roles(ctx.author, score, spec, faction)

        if roles:
            await ctx.author.add_roles(*roles)
            faction_short = "H" if faction == "horde" else "A"
            realm = realm.replace(" ", "")
            await ctx.author.edit(nick=f"{name}-{realm} [{faction_short}]")
            await ctx.message.add_reaction(Emojis.CHECK)
        else:
            await ctx.message.add_reaction(Emojis.AWKWARD)


def setup(bot: Bot) -> None:
    raiderio_api = RaiderIOApi(bot.http_session)
    bot.add_cog(RaiderIOCog(bot, raiderio_api))
