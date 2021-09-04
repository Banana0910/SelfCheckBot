from discord.ext.commands.core import check
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

logchannel = None

checkRequestblock = False
ip = "119.28.155.202:9999"
errored = False
stack = 0
repeatcount = 0

def TryFindElement(Tdriver,xpath) :
    try :
        Tdriver.find_element_by_xpath(xpath)
    except NoSuchElementException :
        return False
    return True

def job() :
    global sendmsg,stack,errored,ip,repeatcount
    Proxy = ip
    webdriver.DesiredCapabilities.CHROME['proxy'] = {
        "httpProxy": Proxy,
        "ftpProxy": Proxy,
        "sslProxy": Proxy,
        "proxyType": "MANUAL"
    }
    webdriver.DesiredCapabilities.CHROME['acceptSslCerts']=True
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
    try :
        driver.get("https://hcs.eduro.go.kr/#/loginHome")
        if TryFindElement(driver, "//*[@id='btnConfirm2']") :
            driver.find_element_by_xpath("//*[@id='btnConfirm2']").click()
        else :
            time.sleep(3)
            text = driver.find_element_by_xpath("/html/body/h1").text
            sendmsg = text + "(이)가 감지됨으로써 자가진단을 중지 합니다"
            stack = 0
            return None
        driver.find_element_by_xpath("//*[@id='schul_name_input']").click()
        driver.find_element_by_xpath("//*[@id='sidolabel']").send_keys(sido)
        driver.find_element_by_xpath("//*[@id='crseScCode']").send_keys(schoollevel)
        driver.find_element_by_xpath("//*[@id='orgname']").send_keys(schoolname)
        driver.find_element_by_xpath("//*[@id='softBoardListLayer']/div[2]/div[1]/table/tbody/tr[3]/td[2]/button").click()
        time.sleep(5)
        driver.find_element_by_xpath("//*[@id='softBoardListLayer']/div[2]/div[1]/ul/li/a").click()
        driver.find_element_by_xpath("//*[@id='softBoardListLayer']/div[2]/div[2]/input").click()
        driver.find_element_by_xpath("//*[@id='user_name_input']").send_keys(studentname)
        driver.find_element_by_xpath("//*[@id='birthday_input']").send_keys(studentbirthday)
        driver.find_element_by_xpath("//*[@id='btnConfirm']").click()
        time.sleep(30)
        if TryFindElement(driver, "//*[@id='btnConfirm']") :
            sendmsg = "비밀번호 입력 중 확인 버튼 감지됨"
        time.sleep(1)
        driver.find_element_by_xpath("//*[@id='WriteInfoForm']/table/tbody/tr/td/input[1]").click()
        chars = list(studentpw)
        for c in chars :
            for i in range(4,10) :  
                if TryFindElement(driver, "//*[@id='password_mainDiv']/div[" + str(i) + "]/a[contains(@aria-label, '" + c + "')]") :
                    driver.find_element_by_xpath("//*[@id='password_mainDiv']/div[" + str(i) + "]/a[contains(@aria-label, '" + c + "')]").click()
        driver.find_element_by_xpath("//*[@id='btnConfirm']").click()
        time.sleep(10)
        driver.find_element_by_class_name("btn").click()
        time.sleep(10)
        for i in range(1,4) :
            driver.find_element_by_xpath("//*[@id='container']/div/div/div[2]/div[2]/dl[" + str(i) + "]/dd/ul/li[1]/label").click()
        driver.find_element_by_xpath("//*[@id='btnConfirm']").click()
        time.sleep(0.5)
        driver.execute_script("window.history.go(-1)")
        time.sleep(2)
        state = driver.find_element_by_class_name("btn").text
        now = datetime.datetime.now()
        sendmsg = "[" + now.strftime('%Y-%m-%d %H:%M') + "]에 [" + state + "]으로 자가진단을 처리하였습니다"
    except Exception as e:
        print(str(e))
        driver.quit()
        now = datetime.datetime.now()
        stack = stack + 1
        if stack >= repeatcount :
            sendmsg = "[" + now.strftime('%Y-%m-%d %H:%M') + "] 자가진단 중 " + str(stack) + "번의 시도에도 불구하고 문제가 발생하여 실패하였습니다"
            stack = 0
            return None
        errored = True
        return None

@bot.event
async def on_ready():
    checkpending.start()

@bot.event
async def on_message(message) :
    content = message.content
    global logchannel, ip, checkRequestblock, repeatcount
    if content == '!set' :
        logchannel = message.channel
        msg = await logchannel.send("자가진단 로그가 " + str(logchannel) + "(으)로 설정되었습니다")
    elif content.startswith('!run') :
        await logchannel.send("자가진단 실행")
        job()
    elif content.startswith("!setip") :
        l = content.split()
        if len(l) < 2 :
            await logchannel.send("설정할 ip 주소를 입력하세요 (예 : !setip 000.000.00.00:0000)")
        else :
            ip = l[1]
            await logchannel.send("프록시 ip가 [" + ip + "]로 설정이 되었습니다")
    elif content.startswith("!repeat") :
        l = content.split()
        if len(l) < 2:
            await logchannel.send("설정할 반복 횟수를 입력하세요 (예 : !repeat 10)")
        else :
            repeatcount = int(l[1])
            await logchannel.send("반복 횟수를 " + str(repeatcount) +"번으로 설정하였습니다")
            

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
