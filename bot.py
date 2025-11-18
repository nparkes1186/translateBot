import discord
from discord.ext import commands
import os
import aiohttp

# ---------- CONFIG ----------
TOKEN = os.getenv("DISCORD_TOKEN")
# Map flag emojis → LibreTranslate language codes
LANG_MAP = {
    "🇬🇧": "en",  # UK English
    "🇪🇸": "es",  # Spanish
    "🇫🇷": "fr",  # French
    "🇩🇪": "de",  # German
    "🇫🇮": "fi",  # Finnish
    "🇳🇴": "no",  # Norwegian
    "🇸🇪": "sv",  # Swedish
}

INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.reactions = True

bot = commands.Bot(command_prefix="!", intents=INTENTS)


async def translate_text(text, target_lang):
    """Translate text using LibreTranslate's public API."""
    url = "https://libretranslate.com/translate"

    payload = {
        "q": text,
        "source": "auto",
        "target": target_lang,
        "format": "text"
    }

    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, data=payload) as response:
                if response.status != 200:
                    return None
                data = await response.json()
                return data.get("translatedText", None)
    except:
        return None


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.event
async def on_raw_reaction_add(payload):
    # Ignore bot reactions
    if payload.user_id == bot.user.id:
        return

    emoji = str(payload.emoji)

    # Check if the emoji is one of our language flags
    if emoji not in LANG_MAP:
        return

    # Get target language
    target_lang = LANG_MAP[emoji]

    # Fetch the channel & message
    channel = bot.get_channel(payload.channel_id)
    if channel is None:
        return

    message = await channel.fetch_message(payload.message_id)

    # Don't translate empty or bot messages
    if not message.content or message.author.bot:
        return

    original_text = message.content

    # Validate message length
    if len(original_text) > 5000:
        await channel.send("⚠️ Message too long to translate.")
        return

    # Translate
    translated = await translate_text(original_text, target_lang)

    if translated is None:
        await channel.send("⚠️ Translation failed.")
        return

    # Send translation beneath the original message
    await message.reply(f"**Translated to {target_lang}:**\n{translated}")


bot.run(TOKEN)