import os
from io import BytesIO
from typing import Optional
from discord.ext.commands.core import has_guild_permissions
import xlsxwriter
import discord
from discord.ext.commands import Bot, Cog, command


class AccountCog(Cog):
    """Cog related to RaiderIO API"""
    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.api_base = os.getenv("apiUrl") or "http://localhost:8000/api/v1"
        self.api_token = os.getenv("apiToken") or ""

    @command()
    @has_guild_permissions(manage_roles=True, administrator=True)
    async def register(self, ctx, member: Optional[discord.User] = None, realm=None, name=None, region="eu"):
        member = member or ctx.author
        if not realm and not name:
            name = member.display_name

            if "[" in name and "]" in name:
                name_realm, faction = name.split()
            else:
                name_realm = name
            name, realm = name_realm.split("-")

        async with self.bot.http_session.post(
            f"{self.api_base}/wowcharacter/register",
            json={
                "account_id": member.id,
                "region": region,
                "realm": realm,
                "name": name
            },
            headers={
                "Authorization": f"Bearer {self.api_token}"
            }
        ) as resp:
            if resp.status == 200 or resp.status == 201:
                await ctx.send("Ok :)")
            else:
                await ctx.send("failed, idk why")

    @command()
    @has_guild_permissions(manage_roles=True, administrator=True)
    async def registerurl(self, ctx, url, member: discord.User = None):
        if member:
            account_id = member.id
        else:
            account_id = ctx.author.id

        async with self.bot.http_session.post(
            f"{self.api_base}/wowcharacter/registerurl",
            json={
                "account_id": account_id,
                "raiderio_url": url
            },
            headers={
                "Authorization": f"Bearer {self.api_token}"
            }
        ) as resp:
            if resp.status == 200 or resp.status == 201:
                await ctx.send("Ok :)")
            else:
                await ctx.send("failed, idk why")

    @command()
    @has_guild_permissions(manage_roles=True, administrator=True)
    async def deduct(self, ctx, member: discord.User,
                     amount: int, *, comment=None):
        if amount > 0:
            amount = -amount

        async with self.bot.http_session.post(
            f"{self.api_base}/transactions",
            json={
                "account_id": member.id,
                "amount": amount,
                "transaction_type": "Strike",
                "comment": comment
            },
            headers={
                "Authorization": f"Bearer {self.api_token}"
            }
        ) as resp:
            if resp.status == 200 or resp.status == 201:
                await ctx.send("Ok :)")
            else:
                await ctx.send("failed, idk why")

    @command()
    async def balance(self, ctx, member: discord.User = None):
        memb = member or ctx.author

        async with self.bot.http_session.get(
            f"{self.api_base}/accounts/{memb.id}/balance",
            headers={
                "Authorization": f"Bearer {self.api_token}"
            }
        ) as resp:
            if resp.status == 200 or resp.status == 201:
                json = await resp.json()
                await ctx.send(json["amount"] or 0)
            else:
                await ctx.send("failed, idk why")

    @command()
    @has_guild_permissions(manage_roles=True, administrator=True)
    async def strikereport(self, ctx):
        async with self.bot.http_session.get(
            f"{self.api_base}/transactions",
            headers={
                "Authorization": f"Bearer {self.api_token}"
            }
        ) as resp:
            if resp.status != 200:
                return await ctx.send("Response failed")
            json = await resp.json()

        col = 0
        row = 0
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        for trans in json:
            if trans["transaction_type"].lower() != "strike":
                continue

            name = trans["wow_character"]["name"]
            realm = trans["wow_character"]["realm"].replace(" ", "")
            faction = "[H]" if trans["wow_character"]["faction"] == "horde" else "[A]"
            amount = trans["amount"]

            worksheet.write(row, col, amount)
            worksheet.write(row, col + 1, name)
            worksheet.write(row, col + 2, f"{realm} {faction}")
            row += 1

        workbook.close()
        output.seek(0)
        await ctx.send("done", file=discord.File(fp=output, filename="strikereport.xlsx"))

    @command()
    @has_guild_permissions(manage_roles=True, administrator=True)
    async def setpaymentcharurl(self, ctx, url, member: discord.User = None):
        member = member or ctx.author
        async with self.bot.http_session.put(
            f"{self.api_base}/wowcharacter/paymentcharacter",
            json={
                "account_id": member.id,
                "raiderio_url": url
            },
            headers={
                "Authorization": f"Bearer {self.api_token}"
            }
        ) as resp:
            if resp.status != 200:
                return await ctx.send("Response failed")
        await ctx.send("done")

    @command()
    @has_guild_permissions(manage_roles=True, administrator=True)
    async def setpaymentchar(self, ctx, char, realm, region, member: discord.User = None):
        member = member or ctx.author
        async with self.bot.http_session.put(
            f"{self.api_base}/wowcharacter/paymentcharacter",
            json={
                "account_id": member.id,
                "name": char,
                "realm": realm,
                "region": region
            },
            headers={
                "Authorization": f"Bearer {self.api_token}"
            }
        ) as resp:
            if resp.status != 200:
                return await ctx.send("Response failed")
        await ctx.send("done")


def setup(bot):
    bot.add_cog(AccountCog(bot))
