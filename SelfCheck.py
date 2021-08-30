import asyncio,discord,os
from discord.ext import commands
from random import *

game = discord.Game("틱톡 감시")
bot = commands.Bot(command_prefix='!',status=discord.Status.online,activity=game)

bot.remove_command("help")
    
@bot.event
async def on_message(message):
    message_content = message.content
    if message.author.bot:
            return None
        
    if message_content.lower().find("tiktok") >= 0 or message_content.lower().find("vt.com") >= 0:
        await message.channel.send("틱톡은 우리 나라에선 금지다")
        await message.delete()
        
    if message_content.find("트럼프") >= 0:
        i = randint(1,6)
        if i == 1:
            await message.channel.send("왜 불렀는가??")
        elif i == 2:
            await message.channel.send("나는 틱톡을 우리 나라에서 금지 시켰지..")
        elif i == 3:
            await message.channel.send("무슨 문제라도 있는가?")
        elif i == 4:
            await message.channel.send("틱톡은 없어져야 한다고 생각하네")
        elif i == 5:
            await message.channel.send("바이든 Go Fuck Your Self")
        elif i == 6:
            await message.channel.send("음.. 이 방에 '아벌구'가 있는듯하구만")
            
    elif message_content.find("바이든") >= 0:
        i = randint(1,4)
        if i == 1:
            await message.channel.send("어우 저 씹새키")
        elif i == 2:
            await message.channel.send("바이든 뒤졌으면^^")
        elif i == 3:
            await message.channel.send("바이든 그는 왜 살고 있는걸까요")
        elif i == 4:
            await message.channel.send("선거 내가 이긴건데.. ㄲㅂ")
            
    await bot.process_commands(message)
access_token = os.environ['BOT_TOKEN']
bot.run(access_token)
