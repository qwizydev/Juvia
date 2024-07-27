import discord
from discord.ext import commands
from tools.fetch import fetch_help_embed
from juvia_dictionary import *
import json, os


class Prefix(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="prefix", invoke_without_command=True)
    async def prefix(self, ctx):

        await ctx.send(
            embed=discord.Embed(
                description=f'{botemojis.get("approve")} {ctx.author.mention}: the **prefix** is **{await self.bot.get_prefix(ctx)}**',
                color=botcolors.get("juv"),
            )
        )

    @prefix.command(name="set")
    async def set_prefix(self, ctx, prefix: str = None):

        with open("prefixes.json", "r") as f:
            prefix_data = json.load(f)

        if prefix is not None:
            pass

        else:
            await ctx.send(
                embed=await fetch_help_embed(
                    ctx,
                    "prefix",
                    "Sets the server prefix",
                    ",prefix set <prefix>",
                    ",prefix set !",
                )
            )
            return

        prefix_data[str(ctx.guild.id)] = str(prefix)
        with open("prefixes.json", "w") as f:
            json.dump(prefix_data, f)

        await ctx.send(
            embed=discord.Embed(
                description=f'{botemojis.get("approve")} {ctx.author.mention}: the **prefix** has been **set** to `{prefix}`',
                color=botcolors.get("juv"),
            )
        )

    @prefix.command(name="remove")
    async def remove_prefix(self, ctx):

        with open("prefixes.json", "r") as f:
            prefix_data = json.load(f)

        with open("prefixes.json", "w") as f:
            prefix_data[str(ctx.guild.id)] = "-"
            json.dump(prefix_data, f)

        await ctx.send(
            embed=discord.Embed(
                description=f'{botemojis.get("approve")} {ctx.author.mention}: the **guild prefix** has been **reverted** back to `-`',
                color=botcolors.get("juv"),
            )
        )


async def setup(bot):
    await bot.add_cog(Prefix(bot))
