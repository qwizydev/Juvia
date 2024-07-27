import discord
from discord.ext import commands
import json
import os
from juvia_dictionary import *
from tools.fetch import *
from juvia_buttons import *


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="setup",
        description="Sets up the mute, image mute, and jail roles and channels.",
    )
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx, action=None):

        with open("roles.json", "r") as f:
            roles = json.load(f)

        if action == "clear":
            with open("roles.json", "r") as f:
                roles = json.load(f)

            if str(ctx.guild.id) in roles:
                mutedRole = ctx.guild.get_role(roles[str(ctx.guild.id)]["mutedRole"])
                imageMutedRole = ctx.guild.get_role(
                    roles[str(ctx.guild.id)]["imageMutedRole"]
                )
                jailedRole = ctx.guild.get_role(roles[str(ctx.guild.id)]["jailedRole"])
                jailChannel = ctx.guild.get_channel(
                    roles[str(ctx.guild.id)]["jailChannel"]
                )

                await mutedRole.delete()
                await imageMutedRole.delete()
                await jailedRole.delete()
                await jailChannel.delete()

                del roles[str(ctx.guild.id)]
                with open("roles.json", "w") as f:
                    json.dump(roles, f, indent=4)

                await ctx.send(
                    embed=discord.Embed(
                        description=f"{botemojis.get('approve')} {ctx.author.mention}: the **moderation setup** has been **cleared**",
                        color=botcolors.get("juv"),
                    )
                )
            else:
                await ctx.send(
                    embed=discord.Embed(
                        description=f"{botemojis.get('warning')} {ctx.author.mention}: the **moderation setup** has not been **set up** yet",
                        color=botcolors.get("juv"),
                    )
                )
            return

        if str(ctx.guild.id) in roles:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{botemojis.get('warning')} {ctx.author.mention}: the **moderation setup** has already been **completed**",
                    color=botcolors.get("juv"),
                )
            )

        await ctx.typing()

        guild = ctx.guild
        mutedRole = await guild.create_role(name="muted")
        imageMutedRole = await guild.create_role(name="imuted")
        jailedRole = await guild.create_role(name="jailed")
        jailChannel = await guild.create_text_channel("jail")

        for channel in guild.channels:
            await channel.set_permissions(
                mutedRole,
                send_messages=False,
                add_reactions=False,
                create_public_threads=False,
                create_private_threads=False,
            )
            await channel.set_permissions(
                imageMutedRole, embed_links=False, attach_files=False
            )
            await channel.set_permissions(jailedRole, read_messages=False)

        await jailChannel.set_permissions(
            jailedRole, read_messages=True, send_messages=True
        )

        roles[str(guild.id)] = {
            "mutedRole": mutedRole.id,
            "imageMutedRole": imageMutedRole.id,
            "jailedRole": jailedRole.id,
            "jailChannel": jailChannel.id,
        }

        with open("roles.json", "w") as f:
            json.dump(roles, f, indent=4)

        await ctx.send(
            embed=discord.Embed(
                description=f"{botemojis.get('approve')} {ctx.author.mention}: the **moderation setup** has been **completed**",
                color=botcolors.get("juv"),
            )
        )

    @commands.hybrid_command(name="jail", description="Jails a user.")
    @commands.has_permissions(manage_roles=True)
    async def jail(self, ctx, member=None, *, reason=None):
        if member is None:
            await ctx.send(
                embed=await fetch_help_embed(
                    ctx,
                    "jail",
                    "Jails a user.",
                    ",jail <member> [reason]",
                    ",jail qwizle Spamming",
                )
            )
            return

        member = await fetch_member(ctx, member)
        if member is None:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{botemojis.get('warning')} {ctx.author.mention}: **Couldn't find** the user `{member}`",
                    color=botcolors.get("juv"),
                )
            )
            return

        with open("roles.json", "r") as f:
            roles = json.load(f)

        jailedRole = ctx.guild.get_role(roles[str(ctx.guild.id)]["jailedRole"])
        jailChannel = ctx.guild.get_channel(roles[str(ctx.guild.id)]["jailChannel"])

        if jailedRole in member.roles:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{botemojis.get('warning')} {ctx.author.mention}: {member.mention} is already jailed.",
                    color=botcolors.get("juv"),
                )
            )
            return

        roles[str(ctx.guild.id)][str(member.id)] = [role.id for role in member.roles]

        try:
            await member.remove_roles(*member.roles)
        except:
            pass
        await member.add_roles(jailedRole)

        with open("roles.json", "w") as f:
            json.dump(roles, f, indent=4)

        await ctx.send(
            embed=discord.Embed(
                description=f"{botemojis.get('approve')} {ctx.author.mention}: {member.mention} has been **jailed**",
                color=botcolors.get("juv"),
            )
        )
        await jailChannel.send(
            f"{member.mention} you have been jailed, for the reason: **{reason}**, please wait for a staff member to free yo ass"
        )

        embed = create_punishment_embed("jailed", ctx.guild.name, ctx.author, reason)
        await member.send(embed=embed)

    @commands.hybrid_command(name="unjail", description="Unjails a user.")
    @commands.has_permissions(manage_roles=True)
    async def unjail(self, ctx, member=None):
        if member is None:
            await ctx.send(
                embed=await fetch_help_embed(
                    ctx,
                    "unjail",
                    "Unjails a user.",
                    ",unjail <member>",
                    ",unjail qwizle",
                )
            )
            return

        member = await fetch_member(ctx, member)
        if member is None:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{botemojis.get('warning')} {ctx.author.mention}: **Couldn't find** the user `{member}`",
                    color=botcolors.get("juv"),
                )
            )
            return

        with open("roles.json", "r") as f:
            roles = json.load(f)

        jailedRole = ctx.guild.get_role(roles[str(ctx.guild.id)]["jailedRole"])
        jailChannel = ctx.guild.get_channel(roles[str(ctx.guild.id)]["jailChannel"])

        if jailedRole not in member.roles:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{botemojis.get('warning')} {ctx.author.mention}: {member.mention} is not jailed.",
                    color=botcolors.get("juv"),
                )
            )
            return

        oldRoles = [
            ctx.guild.get_role(role)
            for role in roles[str(ctx.guild.id)][str(member.id)]
        ]

        await member.remove_roles(jailedRole)

        try:
            await member.add_roles(*oldRoles)
        except:
            pass

        del roles[str(ctx.guild.id)][str(member.id)]

        with open("roles.json", "w") as f:
            json.dump(roles, f, indent=4)

        await ctx.send(
            embed=discord.Embed(
                description=f"{botemojis.get('approve')} {ctx.author.mention}: **Unjailed** {member.mention}.",
                color=botcolors.get("juv"),
            )
        )
        await jailChannel.send(
            embed=discord.Embed(
                description=f"{member.mention} has been unjailed.",
                color=botcolors.get("juv"),
            )
        )

        embed = create_punishment_embed(
            "unjailed", ctx.guild.name, ctx.author, "No reason provided"
        )
        await member.send(embed=embed)

    @commands.hybrid_command(name="mute", description="Mutes a user.")
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member=None, *, reason=None):
        if member is None:
            await ctx.send(
                embed=await fetch_help_embed(
                    ctx,
                    "mute",
                    "Mutes a user.",
                    ",mute <member> [reason]",
                    ",mute qwizle Spamming",
                )
            )
            return

        member = await fetch_member(ctx, member)
        if member is None:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{botemojis.get('warning')} {ctx.author.mention}: **Couldn't find** the user `{member}`",
                    color=botcolors.get("juv"),
                )
            )
            return

        with open("roles.json", "r") as f:
            roles = json.load(f)

        mutedRole = ctx.guild.get_role(roles[str(ctx.guild.id)]["mutedRole"])

        if mutedRole in member.roles:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{botemojis.get('warning')} {ctx.author.mention}: {member.mention} is already muted.",
                    color=botcolors.get("juv"),
                )
            )
            return

        await member.add_roles(mutedRole)
        await ctx.send(
            embed=discord.Embed(
                description=f"{botemojis.get('approve')} {ctx.author.mention}: **Muted** {member.mention}.",
                color=botcolors.get("juv"),
            )
        )

        embed = create_punishment_embed("muted", ctx.guild.name, ctx.author, reason)
        await member.send(embed=embed)

    @commands.hybrid_command(name="unmute", description="Unmutes a user.")
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member=None):
        if member is None:
            await ctx.send(
                embed=await fetch_help_embed(
                    ctx,
                    "unmute",
                    "Unmutes a user.",
                    ",unmute <member>",
                    ",unmute qwizle",
                )
            )
            return

        member = await fetch_member(ctx, member)
        if member is None:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{botemojis.get('warning')} {ctx.author.mention}: **Couldn't find** the user `{member}`",
                    color=botcolors.get("juv"),
                )
            )
            return

        with open("roles.json", "r") as f:
            roles = json.load(f)

        mutedRole = ctx.guild.get_role(roles[str(ctx.guild.id)]["mutedRole"])

        if mutedRole not in member.roles:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{botemojis.get('warning')} {ctx.author.mention}: {member.mention} is not muted.",
                    color=botcolors.get("juv"),
                )
            )
            return

        await member.remove_roles(mutedRole)
        await ctx.send(
            embed=discord.Embed(
                description=f"{botemojis.get('approve')} {ctx.author.mention}: **Unmuted** {member.mention}.",
                color=botcolors.get("juv"),
            )
        )

        embed = create_punishment_embed(
            "unmuted", ctx.guild.name, ctx.author, "No reason provided"
        )
        await member.send(embed=embed)

    @commands.hybrid_command(name="imute", description="Image mutes a user.")
    @commands.has_permissions(manage_roles=True)
    async def imute(self, ctx, member=None, *, reason=None):
        if member is None:
            await ctx.send(
                embed=await fetch_help_embed(
                    ctx,
                    "imute",
                    "Image mutes a user.",
                    ",imute <member> [reason]",
                    ",imute qwizle Spamming",
                )
            )
            return

        member = await fetch_member(ctx, member)
        if member is None:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{botemojis.get('warning')} {ctx.author.mention}: **Couldn't find** the user `{member}`",
                    color=botcolors.get("juv"),
                )
            )
            return

        with open("roles.json", "r") as f:
            roles = json.load(f)

        imageMutedRole = ctx.guild.get_role(roles[str(ctx.guild.id)]["imageMutedRole"])

        if imageMutedRole in member.roles:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{botemojis.get('warning')} {ctx.author.mention}: {member.mention} is already image muted.",
                    color=botcolors.get("juv"),
                )
            )
            return

        await member.add_roles(imageMutedRole)
        await ctx.send(
            embed=discord.Embed(
                description=f"{botemojis.get('approve')} {ctx.author.mention}: **Image muted** {member.mention}.",
                color=botcolors.get("juv"),
            )
        )

        embed = create_punishment_embed(
            "image muted", ctx.guild.name, ctx.author, reason
        )
        await member.send(embed=embed)

    @commands.hybrid_command(
        name="iunmute", description="Unmutes a user from image mute."
    )
    @commands.has_permissions(manage_roles=True)
    async def iunmute(self, ctx, member=None):
        if member is None:
            await ctx.send(
                embed=await fetch_help_embed(
                    ctx,
                    "iunmute",
                    "Unmutes a user from image mute.",
                    ",iunmute <member>",
                    ",iunmute qwizle",
                )
            )
            return

        member = await fetch_member(ctx, member)
        if member is None:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{botemojis.get('warning')} {ctx.author.mention}: **Couldn't find** the user `{member}`",
                    color=botcolors.get("juv"),
                )
            )
            return

        with open("roles.json", "r") as f:
            roles = json.load(f)

        imageMutedRole = ctx.guild.get_role(roles[str(ctx.guild.id)]["imageMutedRole"])

        if imageMutedRole not in member.roles:
            await ctx.send(
                embed=discord.Embed(
                    description=f"{botemojis.get('warning')} {ctx.author.mention}: {member.mention} is not image muted.",
                    color=botcolors.get("juv"),
                )
            )
            return

        await member.remove_roles(imageMutedRole)
        await ctx.send(
            embed=discord.Embed(
                description=f"{botemojis.get('approve')} {ctx.author.mention}: **Unmuted** from image mute {member.mention}.",
                color=botcolors.get("juv"),
            )
        )

        embed = create_punishment_embed(
            "unmuted from image mute", ctx.guild.name, ctx.author, "No reason provided"
        )
        await member.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
