import pip._vendor.requests as requests
import aiohttp, random, asyncio, json, os
import discord, datetime
from discord.ext import commands
from discord import app_commands
from colorthief import ColorThief
import urllib3
from tools.fetch import *
from juvia_dictionary import *


api_key = "bcf19b3d31930c41f130a836b6ad4e3b"


def download_image(url, save_as):
    http = urllib3.PoolManager()
    response = http.request("GET", url)
    with open(save_as, "wb") as file:
        file.write(response.data)


def rgb_to_hex(r, g, b):
    return "{:02x}{:02x}{:02x}".format(r, g, b)


def load_user_data():
    if os.path.exists("lastfm.json"):
        try:
            with open("lastfm.json", "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading user data: {e}")
            return {}
    return {}


def save_user_data(user_data):
    try:
        with open("lastfm.json", "w") as f:
            json.dump(user_data, f, indent=4)
    except Exception as e:
        print(f"Error saving user data: {e}")


class LastFm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = "lastfm.json"
        self.user_data = load_user_data()

    @commands.hybrid_command()
    async def lastfm(self, ctx, action: str = None, username: str = None):

        if action is None:
            await ctx.send(
                embed=await fetch_help_embed(
                    ctx,
                    "lastfm",
                    "set or remove lastfm username",
                    ",lastfm <action>",
                    ",lastfm set qwizle",
                )
            )
            return

        user_data = load_user_data()

        if action.lower() == "set":
            if username is None:
                await ctx.send(
                    embed=await fetch_help_embed(
                        ctx,
                        "lastfm set",
                        "set lastfm username",
                        ",lastfm set <username>",
                        ",lastfm set qwizle",
                    )
                )
                return

            if str(ctx.author.id) in user_data:
                embed = discord.Embed(
                    description=f'{botemojis.get("warning")} {ctx.author.mention}: you have already set a **lastfm username**',
                    color=botcolors.get("juv"),
                )
                await ctx.send(embed=embed)

            else:
                user_data[str(ctx.author.id)] = username
                save_user_data(user_data)

                embed = discord.Embed(
                    description=f"{botemojis.get('approve')} {ctx.author.mention}: set your **lastfm username** to **{username}**",
                    color=botcolors.get("juv"),
                )
                await ctx.send(embed=embed)

        elif action.lower() == "remove":
            if str(ctx.author.id) in user_data:
                user_data.pop(str(ctx.author.id), None)
                save_user_data(user_data)

                embed = discord.Embed(
                    description=f"{botemojis.get('approve')} {ctx.author.mention}: removed your **lastfm username**",
                    color=botcolors.get("juv"),
                )
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    description=f'{botemojis.get("warning")} {ctx.author.mention}: you haven\'t set a **lastfm username** yet',
                    color=botcolors.get("juv"),
                )
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                description=f'{botemojis.get("warning")} {ctx.author.mention}: **invalid action**, choose between **set** and **remove**',
                color=botcolors.get("juv"),
            )
            await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="fm", description="Get information about the user's current playing track!"
    )
    async def now_playing(self, ctx):

        user_data = load_user_data()
        user_id_str = str(ctx.author.id)

        if user_id_str not in user_data:
            embed = discord.Embed(
                description=f'{botemojis.get("warning")} {ctx.author.mention}: please set a **lastfm user** using the command `lastfm set <username>`',
                color=botcolors.get("juv"),
            )
            await ctx.send(embed=embed)
            return

        lastfm_username = user_data[user_id_str]
        now_playing_url = f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={lastfm_username}&api_key={api_key}&format=json&limit=1"
        user_info_url = f"http://ws.audioscrobbler.com/2.0/?method=user.getinfo&user={lastfm_username}&api_key={api_key}&format=json"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(now_playing_url) as response:
                    data = await response.json()

                if "recenttracks" not in data or "track" not in data["recenttracks"]:
                    await ctx.send("Couldn't fetch the currently playing track.")
                    return

                track_info = data["recenttracks"]["track"][0]
                track_name = track_info["name"]
                artist_name = track_info["artist"]["#text"]

                artist_info_url = f"http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&artist={artist_name}&api_key={api_key}&format=json"
                async with session.get(artist_info_url) as response:
                    artist_data = await response.json()
                    artist_image_url = (
                        artist_data["artist"]["image"][-1]["#text"]
                        if artist_data["artist"]["image"]
                        else None
                    )

                album_name = track_info["album"]["#text"]
                album_art = (
                    track_info["image"][-1]["#text"] if track_info["image"] else None
                )

                if album_art:
                    download_image(album_art, "image.jpg")
                    color_thief = ColorThief("image.jpg")
                    dominant_color = color_thief.get_color(quality=1)
                    a, b, c = dominant_color #stole from chatgbt 

                async with session.get(user_info_url) as response:
                    user_data = await response.json()
                    total_scrobbles = user_data["user"]["playcount"]

                track_info_url = f"http://ws.audioscrobbler.com/2.0/?method=track.getInfo&user={lastfm_username}&api_key={api_key}&artist={artist_name}&track={track_name}&format=json"
                async with session.get(track_info_url) as response:
                    track_data = await response.json()

                try:
                    track_play_count = track_data["track"]["userplaycount"]
                except KeyError:
                    track_play_count = "not telling :3"

        except Exception as e:
            return

        faces = [">c<", ">0<", ">n<", ">x<", ">w<", ">o<", ">v<", ">~<"]

        embed = discord.Embed(color=int(rgb_to_hex(a, b, c), 16))
        embed.set_author(
            name=f"{ctx.author} ~ now playing!! ... {faces[random.randint(0, 7)]}",
            icon_url=ctx.author.avatar.url,
        )
        embed.add_field(
            name="Track",
            value=f"[{track_name}](https://www.last.fm/music/{artist_name.replace(' ', '+')}/_/{track_name.replace(' ', '+')})",
            inline=True,
        )
        embed.add_field(
            name="Artist",
            value=f"[{artist_name}](https://www.last.fm/music/{artist_name.replace(' ', '+')})",
            inline=True,
        )
        embed.set_footer(
            text=f"{str(ctx.author).capitalize()}'s Playcount: {track_play_count} ∙ Total Scrobbles: {total_scrobbles} {faces[random.randint(0, 7)]}",
            icon_url="https://cdn.discordapp.com/attachments/1265643693046628383/1265646048609833071/JvasUbf.png?ex=66a2443c&is=66a0f2bc&hm=dc1d59fcc39b0d25da515fff213284cbe8b6818ad950aa6f072e635577f3d88a&",
        )
        embed.timestamp = datetime.datetime.now()

        if album_art:
            embed.set_thumbnail(url=album_art)

        message = await ctx.send(embed=embed)

        try:
            await message.add_reaction("<a:firey:1250887295456907327>")
            await message.add_reaction("<:trash_can:1250886184566132818>")
        except:
            pass


async def setup(bot):
    await bot.add_cog(LastFm(bot))
