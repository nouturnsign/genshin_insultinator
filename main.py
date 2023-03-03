from typing import Callable, Dict, Iterator, Optional, Set

import asyncio
import os
import random

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

member_cache: Set[discord.Member] = set()
webhook_cache: Dict[discord.abc.MessageableChannel, discord.Webhook] = dict()
gif_cache = [
    "https://tenor.com/view/genshin-genshin-impact-gif-22076439",
    "https://tenor.com/view/genshin-impact-walter-white-funny-museum-gif-20562746",
    "https://tenor.com/view/genshin-impact-meme-memes-funny-fat-gif-23970523",
    "https://tenor.com/view/ganyu-ganyu-genshin-ganyu-genshin-impact-genshin-genshin-impact-gif-24744035",
    "https://tenor.com/view/klee-klee-genshin-impact-genshin-impact-genshin-meme-gif-25645250",
    "https://tenor.com/view/genshin-impact-genshin-genshin-meme-genshin-memes-gif-23777472",
    "https://tenor.com/view/genshin-genshin-meme-meme-funny-no-bitches-gif-25083047",
    "https://tenor.com/view/genshin-dream-funny-meme-gif-21901016",
    "https://tenor.com/view/genshin-pov-relatable-gif-25155083",
    "https://tenor.com/view/kazuha-inazuma-genshin-impact-memes-kazuha-genshin-impact-kazuha-inazuma-gif-23310313",
    "https://tenor.com/view/genshin-impact-fans-genshin-meme-george-floyd-genshin-impact-explaining-meme-gif-23922047",
    "https://tenor.com/view/diluc-genshin-impact-genshin-impact-diluc-genshin-meme-genshin-impact-meme-gif-26111438",
    "https://tenor.com/view/genshin-impact-ayaka-genshin-genshin-meme-gif-24799576",
    "https://tenor.com/view/oh-my-goodness-oh-my-goodness-gracious-oh-my-goodness-gracious-meme-itto-arataki-arataki-itto-gif-24181385",
    "https://tenor.com/view/genshin-impact-genshin-vrchat-vrc-vrchat-fliptripp-gif-21325438",
    "https://tenor.com/view/nikocado-avocado-genshin-impact-meme-gif-26538057",
    "https://tenor.com/view/ganyu-genshin-meme-genshin-impact-cocogoat-sad-gif-23308780",
    "https://tenor.com/view/genshin-impact-meme-genshin-impact-players-going-to-bed-gif-25699251",
    "https://tenor.com/view/genshin-impact-noelle-noelle-genshin-cringe-cringe-detected-gif-23973555",
    "https://tenor.com/view/genshin-impact-genshin-meme-memes-funny-gif-26357403",
    "https://tenor.com/view/genshin-genshin-impact-genshin-impact-fan-mihoyo-gif-21922389",
    "https://tenor.com/view/genshin-impact-players-after-not-playing-for-a-day-gif-24104482",
    "https://tenor.com/view/genshin-players-genshin-impact-player-genshin-impact-players-genshin-player-zy0x-gif-24714837",
    "https://tenor.com/view/pov-you-dont-play-genshin-impact-genshin-impact-gif-22769513",
    "https://tenor.com/view/genshin-impact-player-when-gif-22673256",
    "https://tenor.com/view/genshin-impact-gif-23394265",
    "https://tenor.com/view/genshin-genshin-impact-players-when-gambling-venezuela-gif-22448227",
    "https://tenor.com/view/genshin-genshin-impact-paimon-paimon-food-gif-18876173",
    "https://tenor.com/view/genshin-impact-genshin-genshin-impact-players-anime-coom-gif-26171509",
    "https://tenor.com/view/swag-city-note-discord-genshin-impact-gif-18759787",
    "https://tenor.com/view/kizuna-ai-genshin-players-genshin-impact-gif-25084264",
    "https://tenor.com/view/genshin-gif-20317024",
    "https://tenor.com/view/dad-i-like-genshin-genshin-impact-dad-i-like-genshin-impact-gif-24535079",
    "https://tenor.com/view/genshin-impact-nerd-nerd-emoji-genshin-gif-23413935",
]

@bot.event
async def on_message(message: discord.Message):
    if not bot.is_ready():
        return 
    if message.author.bot:
        return 
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return 
    
    if message.author in member_cache and contains_genshin(message.content):
        gif_url = get_gif_url()
        author = message.author
        username = author.display_name
        avatar_url = None
        if author.avatar is not None:
            avatar_url = author.avatar.url
            
        channel = message.channel
        await retry_webhook_send(3, channel, gif_url, username, avatar_url)
            
async def retry_webhook_send(max_retries: int, channel: discord.abc.MessageableChannel, gif_url: str, username: str, avatar_url: Optional[str]):
    success = False
    for _ in range(max_retries):
        if success:
            break
        if channel not in webhook_cache:
            webhook_cache[channel] = await channel.create_webhook(name="Genshinsultinator webhook")
        webhook = webhook_cache[channel]
        try:
            await webhook.send(
                gif_url,
                username=username,
                avatar_url=avatar_url,
            )
            success = True
        except discord.errors.NotFound:
            webhook_cache[channel] = await channel.create_webhook(name="Genshinsultinator webhook")
        except Exception as exc:
            raise exc 
    
@bot.event
async def on_command_error(ctx: commands.Context, error: commands.errors.CommandError):
    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send(f"Command not found. Try using `{bot.command_prefix}help`")
    print(f"Error: {error}")
    
@bot.command()
async def add(ctx: commands.Context, *names: str):
    """Add a member to the insultinator."""
    guild = ctx.guild
    if guild is None:
        return
    
    for name in names:
        member = guild.get_member_named(name)
        if member is None:
            await ctx.send(f"Failed to add member with name {name}")
        else:
            member_cache.add(member)
            await ctx.send(f"Successfully added {member.name}#{member.discriminator}")
    
def contains_genshin(content: str) -> bool:
    return len(find_near_matches("genshin", content.lower(), max_l_dist=1)) > 0

@bot.command()
async def clear(ctx: commands.Context):
    """Clear existing webhooks."""
    await asyncio.gather(*map(lambda webhook: webhook.delete(), filter(lambda webhook: webhook.guild == ctx.guild, webhook_cache.values())))
    await ctx.send("Cleared webhooks")
    
def gif_generator() -> Iterator[str]:
    previous = random.choice(gif_cache)
    yield previous 
    while True:
        try:
            gif_cache.remove(previous)
            current = random.choice(gif_cache)
            yield current
        except Exception:
            gif_cache.append(previous)
        else:
            previous = current
    
def _make_get_gif_url() -> Callable[[], str]:
    generator = gif_generator()
    def get_gif_url() -> str:
        return next(generator)
    return get_gif_url

_get_gif_url = _make_get_gif_url()
def get_gif_url() -> str:
    return _get_gif_url()

bot.run(DISCORD_TOKEN)