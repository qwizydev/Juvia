import os, json
import discord
import aiohttp, asyncio
import tracemalloc
from discord import app_commands
from discord.ext import commands
from juvia_dictionary import botcolors, botemojis
import termcolor


def get_prefix(bot, message):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
    return prefixes.get(str(message.guild.id), "jv")


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):

        print(f"{termcolor.colored('_____________________________________', 'yellow')}")
        print(
            f"\n{termcolor.colored(self.user.name, 'yellow')} is ready for freaky activies!\nid -> {termcolor.colored(self.user.id, 'red')}\n"
        )
        print(f"{termcolor.colored('_____________________________________', 'red')}")

        await self.load_cogs()
        await bot.tree.sync()
        print(f'{termcolor.colored(f"Synced commands!", "green")}')

    async def on_guild_join(self, guild):
        with open("prefixes.json", "r") as f:
            prefixes = json.load(f)
        prefixes[str(guild.id)] = "jv"
        with open("prefixes.json", "w") as f:
            json.dump(prefixes, f)

    async def on_guild_remove(self, guild):
        with open("prefixes.json", "r") as f:
            prefixes = json.load(f)
        if str(guild.id) in prefixes:
            del prefixes[str(guild.id)]
        with open("prefixes.json", "w") as f:
            json.dump(prefixes, f)

    async def load_cogs(self):
        cogs_dir = os.path.join(os.path.dirname(__file__), "cogs")
        for filename in os.listdir(cogs_dir):
            if filename.endswith(".py"):
                if filename != "__init__.py":
                    await self.load_extension(f"cogs.{filename[:-3]}")
                else:
                    print(f"skipping: ", filename, " reason: init file")

    async def reload_cogs(self):
        cogs_dir = os.path.join(os.path.dirname(__file__), "cogs")
        for filename in os.listdir(cogs_dir):
            if filename.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                except Exception as e:
                    pass
                try:
                    await self.unload_extension(f"cogs.{filename[:-3]}")
                except Exception as e:
                    pass
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                except Exception as e:
                    pass


bot = Bot(
    command_prefix=get_prefix,
    intents=discord.Intents.all(),
    help_command=None,
    strip_after_prefix=True,
    case_insensitive=True,
    allowed_mentions=discord.AllowedMentions(
        everyone=False,
        users=True,
        roles=False,
        replied_user=False,
    ),
)


@bot.command()
async def rc(ctx):
    await bot.reload_cogs()
    await ctx.message.add_reaction("👍")


@bot.command()
async def sync(ctx):
    await bot.tree.sync()
    await ctx.message.add_reaction("👍")


bot.run()
