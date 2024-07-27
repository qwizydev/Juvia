import discord
import requests
from discord.ext import commands
import asyncio
from juvia_dictionary import *
from tools.favorites import *
from tools.fetch import *


class Api(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.waifu_pics_api = "https://waifu.pics/api"
        self.cat_api = "https://api.thecatapi.com/v1/images/search?limit="
        self.heart_emojis = ["❤️", "🧡", "💛", "💚", "💙"]

    async def send_images_with_reactions(self, ctx, image_urls):
        messages = []
        for idx, image_url in enumerate(image_urls):
            message = await ctx.send(f"{image_url}")
            await message.add_reaction(self.heart_emojis[idx % len(self.heart_emojis)])
            messages.append(message)
        return messages

    def check_reaction(self, reaction, user, ctx, messages):
        return (
            user == ctx.author
            and str(reaction.emoji) in self.heart_emojis
            and reaction.message.id in [msg.id for msg in messages]
        )

    async def wait_for_reaction(self, ctx, messages):
        try:
            reaction, user = await self.bot.wait_for(
                "reaction_add",
                timeout=60.0,
                check=lambda r, u: self.check_reaction(r, u, ctx, messages),
            )
        except asyncio.TimeoutError:
            pass
        else:
            idx = self.heart_emojis.index(str(reaction.emoji))
            return idx
        return None

    async def show_favorites(self, ctx, api_name, page=1):
        favorites = get_user_favorites(str(ctx.author.id))
        if api_name not in favorites or len(favorites[api_name]) == 0:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{botemojis.get('approve')} {ctx.author.mention} you have **no favorites**.. *yet*",
                    color=botcolors.get("juv"),
                )
            )
            return

        per_page = 10
        pages = (len(favorites[api_name]) - 1) // per_page + 1

        if page < 1 or page > pages:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{botemojis.get('decline')} {ctx.author.mention} **invalid** page number",
                    color=botcolors.get("juv"),
                )
            )
            return

        start = (page - 1) * per_page
        end = start + per_page
        favorite_images = favorites[api_name][start:end]

        desc = ""
        for indx, img in enumerate(favorite_images):
            desc += f"> `{indx+1}.` **{img}**\n"

        desc += "> \n"
        desc += "> -# to add an image to favs, react with the heart emoji an image!"

        await ctx.send(
            embed=discord.Embed(
                title=f"{ctx.author} {api_name} favs page {page}/{pages}",
                description=desc,
                color=botcolors.get("juv"),
            ).set_thumbnail(url=ctx.author.avatar.url)
        )

    @commands.hybrid_group(name="api", invoke_without_command=True)
    async def api(self, ctx):
        await ctx.send(
            embed=await fetch_help_embed(
                ctx,
                "api",
                "fetch content from our api's",
                ",api <api> [arg1] [arg2]",
                ",api waifupics sfw",
            )
        )

    @api.command(name="wp", description="fetch content from waifu.pics api")
    async def waifupics(self, ctx, type=None, tag=None, amount: int = 1):
        if type == "fav":
            await self.show_favorites(ctx, "waifupics")
            return

        if type == "tags" or type == "tag":
            if tag == "sfw":
                await ctx.send(
                    embed=await fetch_api_help(
                        ctx,
                        "waifu.pics",
                        [
                            "waifu",
                            "neko",
                            "shinobu",
                            "megumin",
                            "bully",
                            "cuddle",
                            "cry",
                            "hug",
                            "awoo",
                            "kiss",
                            "lick",
                            "pat",
                            "smug",
                            "bonk",
                            "yeet",
                            "blush",
                            "smile",
                            "wave",
                            "highfive",
                            "handhold",
                            "nom",
                            "bite",
                            "glomp",
                            "slap",
                            "kill",
                            "kick",
                            "happy",
                            "wink",
                            "poke",
                            "dance",
                            "cringe",
                        ],
                    )
                )
                return

            elif tag == "nsfw":
                await ctx.send(
                    embed=await fetch_api_help(
                        ctx, "waifu.pics", ["waifu", "neko", "trap", "blowjob"]
                    )
                )
                return

            else:
                await ctx.send(
                    embed=discord.Embed(
                        description=f"{botemojis.get('decline')} {ctx.author.mention}: **invalid** choice of type! you can only view tags for **sfw** and **nsfw**",
                        color=botcolors.get("juv"),
                    )
                )
                return

        if type is None:
            await ctx.send(
                embed=await fetch_help_embed(
                    ctx,
                    "api waifupics",
                    "fetch content from waifu.pics api",
                    ",api waifupics <type> [tag] [amount]",
                    ",api waifupics sfw waifu 5",
                )
            )
            return

        if type == "sfw" or type == "nsfw":
            pass

        else:
            if type is None:
                await ctx.send(
                    embed=await fetch_help_embed(
                        ctx,
                        "api waifupics",
                        "fetch content from waifu.pics api",
                        ",api waifupics <type> [tag] [amount]",
                        ",api waifupics sfw waifu 5",
                    )
                )
                return

        if tag is None:
            tag = "waifu"

        if type is not None and tag is not None:
            try:
                tag = int(tag)
                amount = tag
                tag = "waifu"
            except ValueError:
                tag = tag

        if amount > 5:
            amount = 5

        image_urls = []
        for _ in range(amount):
            try:
                r = requests.get(f"https://api.waifu.pics/{type}/{tag}")
                data = r.json()
                image_urls.append(data["url"])
            except:
                await ctx.send(
                    embed=discord.Embed(
                        description=f"{botemojis.get('decline')} {ctx.author.mention}: **invalid tag!** run `api waifupics tags` for a **list of tags**",
                        color=botcolors.get("juv"),
                    )
                )
                return

        messages = await self.send_images_with_reactions(ctx, image_urls)

        idx = await self.wait_for_reaction(ctx, messages)
        if idx is not None:
            add_favorite(str(ctx.author.id), "waifupics", image_urls[idx])
            favorites = get_user_favorites(str(ctx.author.id))
            embed = discord.Embed(
                description=f'{botemojis.get("approve")} {ctx.author.mention}: the image has been added to **your favorites**\n> current favorites: `{len(favorites["waifupics"])}` images',
                color=botcolors.get("juv"),
            )
            await ctx.send(embed=embed)

    @api.command(name="cat", description="fetch a random cat image")
    async def cat(self, ctx, subcommand=None, amount: int = 1):
        if subcommand == "fav":
            await self.show_favorites(ctx, "cats")
            return

        if amount > 10:
            amount = 10

        r = requests.get(f"{self.cat_api}{amount}")
        data = r.json()
        image_urls = [data[i]["url"] for i in range(amount)]

        messages = await self.send_images_with_reactions(ctx, image_urls)

        idx = await self.wait_for_reaction(ctx, messages)
        if idx is not None:
            add_favorite(str(ctx.author.id), "cats", image_urls[idx])
            favorites = get_user_favorites(str(ctx.author.id))
            embed = discord.Embed(
                description=f'{botemojis.get("approve")} {ctx.author.mention}: the image has been added to **your favorites**\n> current favorites: `{len(favorites["cats"])}` images',
                color=botcolors.get("juv"),
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Api(bot))
