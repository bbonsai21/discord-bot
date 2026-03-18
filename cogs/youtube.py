import os
from pathlib import Path
import asyncio
import time

from yt_dlp import YoutubeDL

import privileges
from disnake.ext import commands
from disnake import File
from disnake import ApplicationCommandInteraction as ACI

from shared import SERVER_GUILD_ID, COOLDOWN_TIME, MAX_CACHE_SIZE
from shared import  cooldowns  

download_cache = {}  # {link: file_path}

MAX_FILE_SIZE = 24 * 1024 * 1024  # 24MB to be safe
DOWNLOAD_DIR = Path("./download")
DOWNLOAD_DIR.mkdir(exist_ok=True)

YT_DLP_OPTS = {"format": "worst[ext=mp4]/worst", # smallest format
                "outtmpl": str(DOWNLOAD_DIR / "%(id)s.%(ext)s"),
                "quiet": True,
                "no_warnings": True,}

async def download_video(link: str) -> tuple[str, str]:
    loop = asyncio.get_running_loop()
    downloaded_file = None
    
    def hook(d):
        nonlocal downloaded_file
        if d['status'] == 'finished':
            downloaded_file = d.get("filename")
    
    opts = YT_DLP_OPTS.copy()
    opts['progress_hooks'] = [hook]
    
    try:
        await loop.run_in_executor(
            None, 
            lambda: YoutubeDL(opts).download([link])
        )
    except Exception as e:
        return None, f"Download failed: {str(e)}"
    
    if not downloaded_file or not os.path.exists(downloaded_file):
        return None, "File not found after download"

    file_size = os.path.getsize(downloaded_file)
    if file_size > MAX_FILE_SIZE:
        os.remove(downloaded_file)
        return None, f"File too large ({file_size / 1024 / 1024:.1f}MB). Discord limit is 25MB."
    
    return downloaded_file, None

class YT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
    name="youtube",
    description="Download a YT video",
    guild_ids=[SERVER_GUILD_ID]
    )
    async def youtube(self, interaction: ACI, link: str):
        await interaction.response.defer()
        
        user_id = interaction.user.id
        
        if link in download_cache:
            cached_path = download_cache[link]
            if os.path.exists(cached_path):
                await interaction.followup.send(file=File(cached_path))
                return
            else:
                del download_cache[link]  # Clean up dead cache entry
        
        if user_id not in privileges.admins:
            if user_id in cooldowns:
                elapsed = time.time() - cooldowns[user_id]
                if elapsed < COOLDOWN_TIME:
                    await interaction.followup.send(
                        f"Cooldown active. Wait {int(COOLDOWN_TIME - elapsed)}s"
                    )
                    return
            cooldowns[user_id] = time.time()
        
        file_path, error = await download_video(link)
        
        if error:
            await interaction.followup.send(f"❌ {error}")
            return
        
        await interaction.followup.send(file=File(file_path))
        
        if len(download_cache) >= MAX_CACHE_SIZE:
            oldest_link = next(iter(download_cache))
            old_path = download_cache.pop(oldest_link)
            if os.path.exists(old_path):
                os.remove(old_path)
        
        download_cache[link] = file_path



def setup(bot):
    bot.add_cog(YT(bot))