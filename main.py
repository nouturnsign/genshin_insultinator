from __future__ import annotations

from typing import Callable, Dict, Literal, Iterator, Optional, Set, TYPE_CHECKING

import asyncio
import os
import random

import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import commands
from dotenv import load_dotenv
from fuzzysearch import find_near_matches

load_dotenv()
DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]

if TYPE_CHECKING:
    from collections.abc import Awaitable
    Member = discord.Member
    Webhook = discord.Webhook
    Message = discord.Message
    Context = commands.Context
    MessageableChannel = discord.abc.MessageableChannel

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(
    command_prefix=">", 
    help_command=commands.DefaultHelpCommand(no_category="Commands"),
    description=">help",
    intents=intents, 
)

member_cache: Set[Member] = set()
webhook_cache: Dict[MessageableChannel, Webhook] = dict()
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
    "https://tenor.com/view/high-five-gif-25365854",
    "https://tenor.com/view/genshin-impact-gif-24534282",
    "https://tenor.com/view/genshin-impact-fans-when-they-lose-their-virginity-gif-23661588",
    "https://tenor.com/view/monkey-moments-rezero-genshin-impact-cord-big-chungus-gif-18963645",
    "https://tenor.com/view/genshin-impact-kusanali-genshin-hoyoverse-mihoyo-gif-26501367",
    "https://tenor.com/view/xingqiu-xingqiu-genshin-impact-genshin-meme-genshin-impact-characters-genshin-gif-26237483",
    "https://tenor.com/view/thoma-tohma-genshin-impact-genshin-genshin-thoma-gif-22479292",
    "https://tenor.com/view/genshin-genshin-impact-itto-smelly-shower-gif-24181535",
    "https://tenor.com/view/venti-venti-genshin-genshin-impact-gif-24022682",
    "https://tenor.com/view/genshin-impact-genshin-venti-i-am-going-to-eat-myself-genshin-eat-genshin-myself-gif-24544507",
    "https://tenor.com/view/genshin-impact-gif-23894991",
    "https://tenor.com/view/genshin-impact-omori-kel-ecstatic-gif-20882068",
    "https://tenor.com/view/arataki-itto-itto-genshin-arataki-itto-genshin-genshin-genshin-impact-gif-23413330",
    "https://tenor.com/view/la-noire-genshin-impact-gif-25963082",
    "https://tenor.com/view/delusional-gif-26352196",
    "https://tenor.com/view/genshin-impact-gif-18925768",
    "https://tenor.com/view/fugo-jjba-gif-24703416",
    "https://tenor.com/view/genshin-impact-sad-life-no-father-gif-22434705",
    "https://tenor.com/view/you-deleted-genshin-impact-gif-24436180",
    "https://tenor.com/view/genshin-impact-notyouaverageflight-nyaf-gif-21823908",
    "https://tenor.com/view/genshin-impact-gif-24892023",
    "https://tenor.com/view/baizhu-genshin-impact-oh-my-goodness-gracious-gif-26433727",
    "https://tenor.com/view/dvalin-genshin-genshin-impact-oh-my-goodness-goodness-gracious-gif-24455999",
    "https://tenor.com/view/diluc-diluc-genshin-impact-genshin-impact-diluc-diluc-ragnvindr-darknight-hero-gif-25755023",
    "https://tenor.com/view/oh-my-goodness-gracious-meme-oh-my-goodness-gracious-amber-genshin-impact-genshin-gif-24325773",
    "https://tenor.com/view/fischl-fischl_skin-genshin_impact-gif-26118138",
    "https://tenor.com/view/hu-tao-genshin-impact-genshin-genshin-meme-gif-24589126",
    "https://tenor.com/view/andrew-curtis-genshin-impact-genshin-irl-gif-25759033",
]

@bot.event
async def on_message(message: Message):
    if not bot.is_ready():
        return 
    if message.author.bot:
        return 
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return 
    
    if message.author in member_cache and contains_genshin(message.content):
        gif_url = await get_gif_url()
        author = message.author
        username = author.display_name
        avatar_url = None
        if author.avatar is not None:
            avatar_url = author.avatar.url
            
        channel = message.channel
        message = await retry_webhook_send(3, channel, gif_url, username, avatar_url)
        await asyncio.sleep(10)
        await message.delete()
            
async def retry_webhook_send(max_retries: int, channel: MessageableChannel, gif_url: str, username: str, avatar_url: Optional[str]) -> Message:
    for _ in range(max_retries):
        if channel not in webhook_cache:
            webhook_cache[channel] = await channel.create_webhook(name="Genshinsultinator webhook")
        webhook = webhook_cache[channel]
        try:
            return await webhook.send(
                gif_url,
                username=username,
                avatar_url=avatar_url,
            )
        except discord.errors.NotFound:
            webhook_cache[channel] = await channel.create_webhook(name="Genshinsultinator webhook")
        except Exception as exc:
            raise exc 
    return None
    
@bot.event
async def on_command_error(ctx: Context, error: commands.errors.CommandError):
    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send(f"Command not found. Try using `{bot.command_prefix}help`")
        return
    raise error
    
@bot.command()
async def add(ctx: Context, *names: str):
    """Add space-separated members to the insultinator. Use name, nickname, or name#discriminator to lookup. If no names are supplied, adds yourself."""
    guild = ctx.guild
    if guild is None:
        return
    
    if len(names) == 0:
        author = ctx.message.author
        member_cache.add(author)
        await ctx.send(f"Successfully added: {author.name}#{author.discriminator}")
        return
        
    for name in names:
        member = guild.get_member_named(name)
        if member is None:
            await ctx.send(f"Failed to find member with name: {name}")
            continue
        member_cache.add(member)
        await ctx.send(f"Successfully added: {member.name}#{member.discriminator}")

@bot.command()
async def clear(ctx: Context):
    """Clear existing webhooks."""
    await asyncio.gather(*map(lambda webhook: webhook.delete(), filter(lambda webhook: webhook.guild == ctx.guild, webhook_cache.values())))
    await ctx.send("Cleared webhooks")
    
def gif_generator() -> Iterator[str]:
    previous = random.choice(gif_cache)
    yield previous 
    while True:
        gif_cache.remove(previous)
        current = random.choice(gif_cache)
        yield current
        gif_cache.append(previous)
        previous = current
    
def _make_get_gif_url() -> Callable[[], Awaitable[str]]:
    generator = gif_generator()
    lock = asyncio.Lock()
    async def get_gif_url() -> str:
        await lock.acquire()
        gif_url = next(generator)
        lock.release()
        return gif_url
    return get_gif_url

_get_gif_url = _make_get_gif_url()
async def get_gif_url() -> str:
    return await _get_gif_url()

def scrape_genshin_characters() -> list[str]:
    r = requests.get("https://genshin.gg/")
    r.raise_for_status()
    soup = BeautifulSoup(r.content, features="html.parser")
    genshin_characters = []
    character_list_div = soup.find("div", attrs={"class": "character-list"})
    if character_list_div is None:
        return genshin_characters
    for character_portrait_a in character_list_div.find_all("a", attrs={"class": "character-portrait"}):
        character_portrait_h2 = character_portrait_a.find("h2")
        if character_portrait_h2 is None:
            continue
        genshin_characters.append(character_portrait_h2.get_text())
    return genshin_characters
        
def _make_contains_genshin_character() -> Callable[[], bool]:
    try:
        genshin_characters = scrape_genshin_characters()
    except requests.HTTPError:
        def always_true(content: str) -> Literal[True]:
            return True
        return always_true 
    else:
        genshin_characters_lower = list(map(lambda content: content.lower(), genshin_characters))
        def contains_genshin_character(content: str) -> bool:
            content = content.lower()
            for genshin_character in genshin_characters_lower:
                if len(find_near_matches(genshin_character, content, max_l_dist=0)) > 0:
                    return True
            return False
        return contains_genshin_character

_contains_genshin_character = _make_contains_genshin_character()
def contains_genshin_character(content: str) -> bool:
    return _contains_genshin_character(content)

def contains_genshin_fuzzy(content: str) -> bool:
    return len(find_near_matches("genshin", content.lower(), max_l_dist=1)) > 0

def contains_genshin(content: str) -> bool:
    return contains_genshin_fuzzy(content) or contains_genshin_character(content)

bot.run(DISCORD_TOKEN)