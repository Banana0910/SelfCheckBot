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

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")

driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
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
    try :
        driver.get("https://hcs.eduro.go.kr/#/loginHome")
        print(driver.find_element_by_xpath("/html/body/h1").text)
        state = "lol"
        now = datetime.datetime.now()
        sendmsg = "[" + now.strftime('%Y-%m-%d %H:%M') + "]에 [" + state + "]으로 자가진단을 처리하였습니다"
    except Exception as e:
        print(str(e))
        now = datetime.datetime.now()
        if stack > 2 :
            sendmsg = "[" + now.strftime('%Y-%m-%d %H:%M') + "] 자가진단 중 3번의 시도에도 불구하고 문제가 발생하여 실패하였습니다"
            stack = 0
            return None
        stack = stack + 1
        errored = True
        return None

@bot.event
async def on_ready():
    checkpending.start()

@bot.event
async def on_message(message) :
    content = message.content
    global logchannel
    if content == '!set' :
        logchannel = message.channel
        msg = await logchannel.send("자가진단 로그가 " + str(logchannel) + "(으)로 설정되었습니다")
        time.sleep(5)
        await msg.delete()
    elif content == '!run' :
        await logchannel.send("자가진단 실행")
        job()

@tasks.loop(seconds=1)
async def checkpending() :
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
schedule.every().thursday.at("08:00:00").do(job)
schedule.every().friday.at("08:00:00").do(job)

access_token = os.environ['BOT_TOKEN']
bot.run(access_token)
