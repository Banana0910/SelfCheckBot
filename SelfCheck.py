from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from discord.ext import commands,tasks
import schedule,time,os,discord,datetime,asyncio

sido = "경상남도"
schoollevel = "중학교"
schoolname = "봉림중학교"

studentname = "이대현"
studentbirthday = "061110"
studentpw = "0910"

sendmsg = '0'

game = discord.Game("자가진단 대기")
bot = commands.Bot(command_prefix='!',status=discord.Status.online,activity=game)

bot.remove_command("help")

option = webdriver.ChromeOptions()
option.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
option.add_argument("--headless")
option.add_argument("--disable-gpu")
option.add_argument("--no-sandbox")
option.add_argument("--disable-software-rasterizer")

driver = webdriver.Chrome(os.environ.get("CHROMEDRIVER_PATH"),options=option)
logchannel = None

errored = False
stack = 0

def TryFindElement(xpath) :
    try :
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException :
        return False
    return True

def job() :
    global sendmsg,stack,errored
    print("job 실행됨")
    sendmsg = "job 실행됨"

@bot.event
async def on_ready():
    checkpending.start()

@bot.event
async def on_message(message) :
    if message.content == '!set' :
        global logchannel
        logchannel = message.channel
        msg = await logchannel.send("자가진단 로그가 " + str(logchannel) + "(으)로 설정되었습니다")
        time.sleep(5)
        await msg.delete()

@tasks.loop(seconds=1)
async def checkpending() :
    print("im here")
    global logchannel, sendmsg, errored
    if len(str(sendmsg)) > 2 :
        await logchannel.send(sendmsg)
        sendmsg = '0'

    if errored == True :
        now = datetime.datetime.now()
        await logchannel.send("[" + now.strftime('%Y-%m-%d %H:%M') + "] 자가진단 중 문제가 발생하였습니다 1초 후에 다시 시도하겠습니다 (중첩 수 : " + str(stack) + ")")
        errored = False
        job()
    schedule.run_pending()

schedule.every().monday.at("08:00:00").do(job)
schedule.every().tuesday.at("08:00:00").do(job)
schedule.every().wednesday.at("08:00:00").do(job)
schedule.every().thursday.at("06:42:00").do(job)
schedule.every().friday.at("08:00:00").do(job)

access_token = os.environ['BOT_TOKEN']
bot.run(access_token)
