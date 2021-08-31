from asyncio.windows_events import NULL
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
option.binary_location = os.environ.get("CHROME")
option.add_argument("--headless")
option.add_argument("--disable-gpu")
option.add_argument("--no-sandbox")
option.add_argument("--disable-software-rasterizer")

driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER"),options=option)
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
        driver.find_element_by_xpath("//*[@id='btnConfirm2']").click()
        driver.find_element_by_xpath("//*[@id='schul_name_input']").click()
        driver.find_element_by_xpath("//*[@id='sidolabel']").send_keys(sido)
        driver.find_element_by_xpath("//*[@id='crseScCode']").send_keys(schoollevel)
        driver.find_element_by_xpath("//*[@id='orgname']").send_keys(schoolname)
        driver.find_element_by_xpath("//*[@id='softBoardListLayer']/div[2]/div[1]/table/tbody/tr[3]/td[2]/button").click()
        time.sleep(0.1)
        driver.find_element_by_xpath("//*[@id='softBoardListLayer']/div[2]/div[1]/ul/li/a").click()
        driver.find_element_by_xpath("//*[@id='softBoardListLayer']/div[2]/div[2]/input").click()
        driver.find_element_by_xpath("//*[@id='user_name_input']").send_keys(studentname)
        driver.find_element_by_xpath("//*[@id='birthday_input']").send_keys(studentbirthday)
        driver.find_element_by_xpath("//*[@id='btnConfirm']").click()
        time.sleep(1.5)
        driver.find_element_by_xpath("//*[@id='password']").click()
        chars = list(studentpw)
        for c in chars :
            for i in range(4,10) : 
                if TryFindElement("//*[@id='password_mainDiv']/div[" + str(i) + "]/a[contains(@aria-label, '" + c + "')]") :
                    driver.find_element_by_xpath("//*[@id='password_mainDiv']/div[" + str(i) + "]/a[contains(@aria-label, '" + c + "')]").click()
        driver.find_element_by_xpath("//*[@id='btnConfirm']").click()
        time.sleep(1)
        driver.find_element_by_class_name("btn").click()
        time.sleep(1)
        for i in range(1,4) :
            driver.find_element_by_xpath("//*[@id='container']/div/div/div[2]/div[2]/dl[" + str(i) + "]/dd/ul/li[1]/label").click()
        driver.find_element_by_xpath("//*[@id='btnConfirm']").click()
        time.sleep(0.5)
        driver.execute_script("window.history.go(-1)")
        time.sleep(1)
        state = driver.find_element_by_class_name("btn").text
        now = datetime.datetime.now()
        sendmsg = "[" + now.strftime('%Y-%m-%d %H:%M') + "]에 [" + state + "]으로 자가진단을 처리하였습니다"
    except Exception:
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
    if message.content == '!set' :
        global logchannel
        logchannel = message.channel
        msg = await logchannel.send("자가진단 로그가 " + str(logchannel) + "(으)로 설정되었습니다")
        time.sleep(5)
        await msg.delete()

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
