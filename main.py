import asyncio
import os
import aiohttp
from aiohttp import web
import discord
from discord.ext import commands, tasks

# --- Web Server (For Railway / Render Health Checks) ---
async def handle(request):
    return web.Response(text="Bot Alive")

async def run_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Web server running on port {port}", flush=True)

# --- Discord Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- Auto Meme Task ---
# Yahan aap time set kar sakte hain, jaise har 3 ghante mein: hours=3
# Agar minutes mein karna ho toh: minutes=30
@tasks.loop(hours=3)
async def send_auto_meme():
    channel_id = os.getenv("MEME_CHANNEL_ID")
    if not channel_id:
        print("❌ MEME_CHANNEL_ID is missing!")
        return

    channel = bot.get_channel(int(channel_id))
    if not channel:
        print("❌ Channel not found! Check your Channel ID.")
        return

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://meme-api.com/gimme") as response:
                if response.status == 200:
                    data = await response.json()
                    image_url = data.get("url")
                    title = data.get("title")
                    
                    embed = discord.Embed(title=title, color=discord.Color.random())
                    embed.set_image(url=image_url)
                    
                    await channel.send(embed=embed)
                    print("✅ Auto meme posted successfully!")
                else:
                    print("⚠️ Failed to fetch meme from API.")
    except Exception as e:
        print(f"❌ Error in auto_post_meme: {e}")

@send_auto_meme.before_loop
async def before_send_auto_meme():
    await bot.wait_until_ready()


@bot.event
async def on_ready():
    print(f"✅ DISCORD BOT IS ONLINE: {bot.user}", flush=True)
    if not send_auto_meme.is_running():
        send_auto_meme.start()


@bot.command()
async def ping(ctx):
    await ctx.send("Pong! 🏓 Auto meme bot is active!")


async def main():
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ DISCORD_TOKEN is missing!")
        return

    try:
        await asyncio.gather(
            run_server(),
            bot.start(token)
        )
    except Exception as e:
        print(f"❌ Error occurred: {e}", flush=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
