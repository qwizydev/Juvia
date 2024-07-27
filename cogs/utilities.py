import discord
from discord.ext import commands
from tools.fetch import *
from juvia_dictionary import *
from juvia_buttons import ConfirmationView
from datetime import datetime, timedelta
import os, json


class Utilities(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.afk_file = "afk.json"
        self.load_afk_statuses()

    def format_activity(self, activity):
        activity_type = str(activity.type).split(".")[-1]
        if activity_type == "listening":
            return f"Listening to {activity.name}"
        elif activity_type == "playing":
            return f"Playing {activity.name}"
        elif activity_type == "watching":
            return f"Watching {activity.name}"
        elif activity_type == "streaming":
            return f"Streaming {activity.name}"
        else:
            return f"Activity: {activity.name}"

    def format_duration(self, duration):
        seconds = duration.total_seconds()
        if seconds < 60:
            return f"{int(seconds)} seconds"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            return f"{minutes} minutes"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours} hours and {minutes} minutes"

    def load_afk_statuses(self):
        if os.path.exists(self.afk_file):
            with open(self.afk_file, "r") as f:
                self.afk_users = json.load(f)
        else:
            self.afk_users = {}

    def save_afk_statuses(self):
        with open(self.afk_file, "w") as f:
            json.dump(self.afk_users, f)

    @commands.hybrid_command(name="echo", description="repeat the user's input")
    async def echo(self, ctx, *, message: str = None):

        if message is not None:
            await ctx.send(message)

        else:
            await ctx.send(
                embed=await fetch_help_embed(
                    ctx,
                    "echo",
                    "Repeat user input",
                    ",echo <message>",
                    ",echo hello world!",
                )
            )

    @commands.hybrid_command(
        name="fmember", description="get basic information on the specified user"
    )
    async def fetch_member_user(self, ctx, member: str = None):

        prev_member = member
        if member is not None:
            member = await fetch_member(ctx, member)

            if member is not None:
                edesc = f"{botemojis.get('approve')} {ctx.author.mention}: **fetched** the user **{member.mention}**"
                edesc += f"\n> username: `{member}`"
                edesc += f"\n> display name: `{member.display_name}`"
                edesc += f"\n> id: `{member.id}`"
                if member.bot:
                    edesc += f"\n> bot: `{str(member.bot).lower()}`"
                if member.activity:
                    activity = member.activity
                    formatted_activity = self.format_activity(activity)
                    edesc += f"\n> user activity: `{formatted_activity}`"
                if member in ctx.guild.members:
                    edesc += f"\n> user in server: `True`"
                    edesc += f"\n> user top role: `{member.top_role.name}`"
                edesc += f"\n> user avatar: **[avatar]({member.avatar.url})**"

                await ctx.send(
                    embed=discord.Embed(
                        description=edesc,
                        color=botcolors.get("juv"),
                    ).set_thumbnail(url=member.avatar.url)
                )
            else:
                await ctx.send(
                    embed=discord.Embed(
                        description=f"{botemojis.get('decline')} {ctx.author.mention}: the user **`{prev_member}`** was **not found**",
                        color=botcolors.get("juv"),
                    )
                )

        else:
            await ctx.send(
                embed=await fetch_help_embed(
                    ctx,
                    "Fetch Member",
                    "Fetch a user by name, id, or mention",
                    ",fetchmember <user>",
                    ",fetchmember qwizle",
                )
            )

    @commands.hybrid_group(
        name="nuke",
        description="nuke the specified channel and make a new one",
        invoke_without_command=True,
    )
    async def nuke(self, ctx):
        view = ConfirmationView()
        if ctx.author.guild_permissions.administrator:
            message = await ctx.send(
                embed=discord.Embed(
                    description=f"{botemojis.get('warning')} {ctx.author.mention}: **are you sure** you want to **nuke** the channel **{ctx.channel.name}**?",
                    color=botcolors.get("juv"),
                ),
                view=view,
            )

            await view.wait()
            if view.result:
                pass
            else:
                await message.delete()
                return

        else:
            await ctx.send(
                embed=fetch_help_embed(
                    ctx, "nuke", "nuke a channel", ",nuke (channel)", ",nuke"
                )
            )

        channel = ctx.guild.get_channel(ctx.channel.id)

        channel_name = channel.name
        channel_topic = channel.topic
        channel_position = channel.position
        channel_nsfw = channel.nsfw
        channel_category = channel.category
        channel_permissions = channel.overwrites

        await channel.delete()

        new_channel = await ctx.guild.create_text_channel(
            name=channel_name,
            topic=channel_topic,
            position=channel_position,
            nsfw=channel_nsfw,
            category=channel_category,
        )

        for target, overwrite in channel_permissions.items():
            await new_channel.set_permissions(target, overwrite=overwrite)

        message = await new_channel.send("first lmao")
        await message.add_reaction("😂")

    @nuke.command(name="server", description="nuke the server channels")
    async def server(self, ctx):
        view = ConfirmationView()
        if ctx.author.guild_permissions.administrator:
            message = await ctx.send(
                embed=discord.Embed(
                    description=f"{botemojis.get('warning')} {ctx.author.mention}: **are you sure** you want to nuke **the server?**",
                    color=botcolors.get("juv"),
                ),
                view=view,
            )

            await view.wait()
            if view.result:
                pass
            else:
                await message.delete()
                return

        else:
            await ctx.send(
                embed=fetch_help_embed(
                    ctx, "nuke", "nuke a channel", ",nuke (channel)", ",nuke"
                )
            )

        for channel in ctx.guild.channels:
            channel_name = channel.name
            channel_position = channel.position
            channel_nsfw = channel.nsfw
            channel_category = channel.category
            channel_permissions = channel.overwrites

            if isinstance(channel, discord.TextChannel):
                channel_topic = channel.topic
                channel_slowmode_delay = channel.slowmode_delay
                channel_is_news = channel.is_news()

                await channel.delete()
                new_channel = await ctx.guild.create_text_channel(
                    name=channel_name,
                    topic=channel_topic,
                    position=channel_position,
                    nsfw=channel_nsfw,
                    category=channel_category,
                    slowmode_delay=channel_slowmode_delay,
                )

                for target, overwrite in channel_permissions.items():
                    await new_channel.set_permissions(target, overwrite=overwrite)

                message = await new_channel.send("first lmao")
                await message.add_reaction("😂")

            elif isinstance(channel, discord.VoiceChannel):
                channel_bitrate = channel.bitrate
                channel_user_limit = channel.user_limit

                await channel.delete()
                new_channel = await ctx.guild.create_voice_channel(
                    name=channel_name,
                    position=channel_position,
                    category=channel_category,
                    bitrate=channel_bitrate,
                    user_limit=channel_user_limit,
                )

                for target, overwrite in channel_permissions.items():
                    await new_channel.set_permissions(target, overwrite=overwrite)

            elif isinstance(channel, discord.CategoryChannel):
                pass

    @commands.hybrid_command(name="afk", description="set afk status")
    async def afk(self, ctx, *, message=None):
        user_id = str(ctx.author.id)

        if message is None:
            message = "AFK"

        self.afk_users[user_id] = {
            "time": datetime.now().isoformat(),
            "message": message,
        }

        self.save_afk_statuses()
        embed = discord.Embed(
            description=f"{botemojis.get('approve')} <@{ctx.author.id}>: You're now AFK with the status: **{message}**",
            color=botcolors.get("juv"),
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="set_activity")
    async def set_activity(self, ctx, *, activity_name: str = None):

        if ctx.author.id != 1119566792466104360:
            await ctx.send("fuck off nigga")
            return

        if activity_name is None:
            activity_name = "@ me for help or some idk"

        activity = discord.Streaming(
            name=activity_name, url="https://twitch.tv/discord"
        )
        await self.bot.change_presence(activity=activity)
        await ctx.message.add_reaction("👍")

    @commands.hybrid_command(name="help")
    async def help(self, ctx):
        command_list = []
        for command in self.bot.commands:
            command_list.append(command.name)

        command_list.sort()
        command_list_x = ", ".join(command for command in command_list)

        descx = f"> {botemojis.get("approve")} list of all *current* commands: "
        descx += f"```{command_list_x}```"
        descx += f"\n> -# reminder: this is a work in progress and is subject to change"
        await ctx.send(
            embed=discord.Embed(
                description=descx,
                color=botcolors.get("juv"),
            ).set_author(
                name=f"{self.bot.user.name} bot ", icon_url=self.bot.user.avatar.url
            )
        )

    @commands.Cog.listener()
    async def on_message(self, message):

        bot_mention = f"<@{self.bot.user.id}>"
        if message.content.strip() == bot_mention:

            with open("prefixes.json", "r") as f:
                prefixes = json.load(f)
                prefix = prefixes.get(str(message.guild.id), "jv")

                await message.channel.send(
                    f"{message.author.mention}: run **help** for more commands, join the [juvia support server](https://discord.gg/TFfNYqVBGM)",
                    embed=discord.Embed(
                        description=f"> current guild prefix: `{prefix}`",
                        color=botcolors.get("juv"),
                    ),
                )

        if message.author.bot:
            return

        user_id = str(message.author.id)
        if user_id in self.afk_users:
            afk_info = self.afk_users[user_id]
            afk_time = datetime.fromisoformat(afk_info["time"])
            time_afk = datetime.now() - afk_time

            if time_afk > timedelta(seconds=2):
                self.afk_users.pop(user_id)
                self.save_afk_statuses()
                embed = discord.Embed(
                    description=f":wave: {message.author.mention}: Welcome back, you were away for **{self.format_duration(time_afk)}**",
                    color=botcolors.get("juv"),
                )
                await message.channel.send(embed=embed)

        for mention in message.mentions:
            mention_id = str(mention.id)
            if mention_id in self.afk_users:
                afk_info = self.afk_users[mention_id]
                afk_message = afk_info["message"]
                afk_time = datetime.fromisoformat(afk_info["time"])
                embed = discord.Embed(
                    description=f":zzz: {mention.mention} is AFK: **{afk_message}** - since <t:{int(afk_time.timestamp())}:R>",
                    color=botcolors.get("juv"),
                )
                await message.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Utilities(bot))
