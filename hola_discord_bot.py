import discord
import asyncio
from datetime import datetime, timedelta
from pytz import timezone
import instaloader
import logging
import os

# Discord 봇 토큰

TOKEN = os.getenv('DISCORD_BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True  # 메시지 콘텐츠를 수신하기 위해 필요

client = discord.Client(intents=intents)

# Instaloader 사용하여 인스타그램 게시물 가져오는 함수
def get_latest_post(username):
    L = instaloader.Instaloader()
    profile = instaloader.Profile.from_username(L.context, username)
    latest_post = next(profile.get_posts())
    return latest_post.caption

# 봇이 메시지를 보낼 채널 ID를 저장하는 변수
scheduled_channel_id = None

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await schedule_posts()

@client.event
async def on_message(message):
    global scheduled_channel_id
    if message.author == client.user:
        return

    # 즉시 최신 게시물 전송
    if message.content == '#hola_here':
        try:
            post_url = get_latest_post('hola_pork')
            await message.channel.send(f'올라 술고기 오늘의 점심 메뉴 입니다!: {post_url}')
        except Exception as e:
            logging.error(f"Failed to send message: {e}")

    # 채널 설정
    elif message.content == '#hola_setup':
        scheduled_channel_id = message.channel.id
        await message.channel.send(f'이 채널이 아침 11시마다 메시지를 받도록 설정되었습니다.')

async def schedule_posts():
    await client.wait_until_ready()
    global scheduled_channel_id
    while not client.is_closed():
        now = datetime.now(timezone('Asia/Seoul'))
        if now.weekday() < 5 and now.hour == 11 and now.minute == 0:
            if scheduled_channel_id:
                channel = client.get_channel(scheduled_channel_id)
                if channel and channel.permissions_for(channel.guild.me).send_messages:
                    try:
                        post_url = get_latest_post('hola_pork')
                        await channel.send(f'Hola Pork의 최신 게시물입니다: {post_url}')
                    except discord.Forbidden:
                        logging.warning(f"Permission denied for channel: {channel.name} in guild: {channel.guild.name}")
                    except discord.HTTPException as e:
                        logging.error(f"Failed to send message: {e}")
                else:
                    logging.info("No suitable channel found or no permissions to send messages.")
            else:
                logging.info("No scheduled channel set.")
        await asyncio.sleep(60)  # 1분마다 체크

client.run(TOKEN)

