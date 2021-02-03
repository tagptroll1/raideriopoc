from discord.ext.commands import Bot, Cog, command


class BotCog(Cog):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    @command(name="reload", aliases=["r"])
    async def reload_extension(self, ctx, *, extension: str) -> None:
        if not extension.startswith("bot.cogs."):
            extension = "bot.cogs." + extension

        try:
            self.bot.unload_extension(extension)
        except Exception:
            pass  # It's most likely not loaded

        try:
            self.bot.load_extension(extension)
        except Exception as e:
            return await ctx.send(f"Loading {extension} failed:\n``` {e}```")

        await ctx.send("done")

    @command()
    async def shutdown(self, ctx):
        self.bot.close()


def setup(bot: Bot) -> None:
    bot.add_cog(BotCog(bot))
