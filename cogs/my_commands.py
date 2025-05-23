from discord.ext import commands
import discord

from utils.config import config
from utils.color_printer import cpr


class MyCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.backup_channel_id = config.get("backup_channel_id")

    @commands.hybrid_command(name="ping", description="Check the bot's latency.")
    async def ping(self, ctx: commands.Context):
        await ctx.send(f"Pong! {round(self.bot.latency * 1000)}ms")

    @commands.hybrid_command(name="backup", description="Back up a message.")
    async def backup(self, ctx: commands.Context):
        if ctx.message.reference is None:
            await ctx.send("You must reply to a message to back it up.")
            return
        if ctx.message.reference.resolved is None:
            await ctx.send("The message you replied to could not be resolved.")
            return
        if not isinstance(ctx.message.reference.resolved, discord.Message):
            await ctx.send("The message you replied to is not a message.")
            return
        for reaction in ctx.message.reference.resolved.reactions:
            if reaction.emoji == "📨" and reaction.me:
                await ctx.send(
                    "This message has already been backed up.",
                    delete_after=5,
                    ephemeral=True,
                )
                return

        original_message = ctx.message.reference.resolved

        embed = discord.Embed(
            description=original_message.content,
            color=original_message.author.color,
            timestamp=original_message.created_at,
        )
        embed.set_author(
            name=original_message.author.display_name,
            icon_url=original_message.author.avatar,
        )
        embed.add_field(
            name="Original message",
            value=f"[Jump!]({original_message.jump_url})",
            inline=True,
        )

        embeds = [embed]
        files = []
        for attachment in original_message.attachments:
            if attachment.content_type.startswith("image"):
                new_embed = discord.Embed()
                new_embed.set_image(url=attachment.url)
                embeds.append(new_embed)
            else:
                file = await attachment.to_file()
                files.append(file)

        backup_channel = self.bot.get_channel(self.backup_channel_id)
        if backup_channel is None:
            await ctx.send("The backup channel could not be found.")
            return
        if embeds or files:
            await backup_channel.send(embeds=embeds, files=files)
        await original_message.add_reaction("📨")


async def setup(bot: commands.Bot):
    await bot.add_cog(MyCommands(bot))
    print(cpr.success("Cog loaded: MyCommands"))
