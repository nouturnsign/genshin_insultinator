import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from fuzzysearch import find_near_matches

load_dotenv()
DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(
    command_prefix=">", 
    help_command=commands.DefaultHelpCommand(no_category="Commands"),
    description=">help",
    intents=intents, 
)

logger = logging.getLogger("discord")
member_id_cache = set()

@bot.event
async def on_message(message: discord.Message):
    if not bot.is_ready():
        return 
    
    if message.author.bot:
        return 
    
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return 
    
    if message.author.id in member_id_cache and "genshin" in message.content:
        author = message.author
        gif_url = get_gif_url()
        channel = message.channel
        hook = await channel.create_webhook(name="Genshinsultinator hook")
        avatar_url = None
        if author.avatar is not None:
            avatar_url = author.avatar.url
        await hook.send(
            gif_url,
            username=author.display_name,
            avatar_url=avatar_url,
        )
        await hook.delete()
    
@bot.event
async def on_command_error(ctx: commands.Context, error: commands.errors.CommandError):
    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send(f"Command not found. Try using `{bot.command_prefix}help`")
    logger.error(f"Error: {error}")
    
@bot.command()
async def add(ctx: commands.Context, *names: str):
    """Add a member to the insultinator."""
    guild = ctx.guild
    if guild is None:
        logger.warning("Could not find guild")
        return
    
    for name in names:
        member = guild.get_member_named(name)
        if member is None:
            await ctx.send(f"Failed to add member with name {name}")
        else:
            member_id_cache.add(member.id)
            await ctx.send(f"Successfully added {member.name}#{member.discriminator}")
    
def contains_genshin(content: str) -> bool:
    return len(find_near_matches("genshin", content.lower(), max_l_dist=1)) > 0
    
def get_gif_url() -> str:
    return "https://tenor.com/view/genshin-impact-walter-white-funny-museum-gif-20562746"
    
bot.run(DISCORD_TOKEN)