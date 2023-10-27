from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.by import By
import psutil
from datetime import datetime
import public_ip as ip
from selenium.webdriver.chrome.service import Service
import logging
import requests as r
import sys

def set_chrome_options() -> Options:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--start-maximized")
    chrome_prefs = {}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    return chrome_options

def logit(msg, logType = "info"):
    if logType == "info":
        logging.info('  --- ' + str(msg))
    if logType == "error":
        logging.error('  --- ' + str(msg))
    print(datetime.now().strftime("%d.%m.%Y %H:%M:%S") +  '  --- ' + str(msg))

def getIP():
    try:
        IPv4 = ip.get()
        return IPv4
    except Exception as e:
        logit('An exception occurred while getting the IP: ' + str(e), logType="error")
        if "tie between" in str(e):
            logit('It seems that you have IPv6.')
    finally:
        logit('Trying to get the IPv4 ....')
        req = r.get('https://checkip.amazonaws.com')
        if req.status_code == 200 and req.text.count('.') == 3:
            IPv4 = req.text
            logit('IPv4 found: ' + IPv4)
            return IPv4
        req = r.get('http://api.ipify.org/')
        if req.status_code == 200 and req.text.count('.') == 3:
            IPv4 = req.text
            logit('IPv4 found: ' + IPv4)
            return IPv4
        req = r.get('https://ipinfo.io/ip')
        if req.status_code == 200 and req.text.count('.') == 3:
            IPv4 = req.text
            logit('IPv4 found: ' + IPv4)
            return IPv4
    logit("Fatal error: IP can't be retreived")
    return False

def updateDashboardIP(newip, oldip, username, password, gsNumber, firstRun = False):
    try:
        for proce in psutil.process_iter():
            if proce.name() == 'chrome' or proce.name() == 'chromedriver':
                proce.kill()
                logit('Killed old chromedriver Processes')
    except:
        pass
        time.sleep(5)

    try:
        logit('navigate to www.defli-wallet.com')
        service = Service(executable_path="/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=set_chrome_options())
        driver.set_window_size(1024, 768)
        driver.maximize_window()
        driver.get("https://defli-wallet.com/")
        time.sleep(5)


        logit('loging in....')
        driver.find_element(By.XPATH, "//button[contains(text(),\'Login')]").click()  #click on the login button
        #driver.find_element(By.XPATH, "/html/body/div[1]/button[1]").click()
        emailEl = driver.find_element(By.XPATH, "/html/body/div[4]/input[1]")    
        if "email" in emailEl.get_attribute("type"):
            emailEl.send_keys(username)
        #driver.find_element(By.XPATH, "/html/body/div[4]/input[2]").send_keys(password)
        passwordEl = driver.find_element(By.XPATH, "/html/body/div[4]/input[2]")
        if "password" in passwordEl.get_attribute("type"):
            passwordEl.send_keys(password)
        #driver.find_element(By.XPATH, "/html/body/div[4]/button").click()
        loginEl = driver.find_element(By.XPATH, "/html/body/div[4]/button")
        if "Login" in loginEl.text:
            #driver.save_screenshot("logindata.png")
            loginEl.click()
            logit('login successful')
            #driver.save_screenshot("IN1.png")
        else: 
            logit('login failed')
            logit('Script stopped. ')
            driver.quit()
            sys.exit()
        time.sleep(4)
        #driver.save_screenshot("IN2.png")

        

        logit('navigate to wwww.defli-wallet.com/gs' + str(gsNumber))
        driver.get("https://defli-wallet.com/gs" + str(gsNumber))
        time.sleep(4)
        #driver.save_screenshot("gs.png")
        

        logit('click Set IP Button')
        setIPbtn = driver.find_element(By.XPATH, "//button[contains(text(),\'Set IP')]")
        setIPbtn.click()
        #driver.save_screenshot("setip.png")
        #(driver.find_elements(By.XPATH, "//div//button[1]"))[0].click()


        logit('entering the new IP .....')
        enterNewIp1 = driver.find_element(By.XPATH, "//div//input[1]")
        enterNewIp2 = driver.find_element(By.XPATH, "//html/body/div[4]/input")
        if "IP Address" in enterNewIp1.get_attribute("placeholder"):
            enterNewIp1.send_keys(newip)
            driver.save_screenshot("enterip1.png")
        elif "IP Address" in enterNewIp2.get_attribute("placeholder"):
            enterNewIp2.send_keys(newip)
            driver.save_screenshot("enterip2.png")
        else:
            logit("The Xpath for the input element for the IP has changed!" ,logType="error")
            logit('Script stopped. ')
            driver.quit()
            sys.exit()


        logit('click on the Save Button .....')
        SubmitEl1 = (driver.find_elements(By.XPATH, "//div"))[1]
        SubmitEl2 = driver.find_element(By.XPATH, "//html/body/div[4]/button")
        try: 
            if "Submit" in SubmitEl1.get_attribute("innerHTML"):
                SubmitEl1.click()
        except: 
            logit("Failed to click the Submit IP Button, trying again ... ", logType="error")
            try:
                if "Submit" in SubmitEl2.get_attribute("innerHTML"):
                   SubmitEl2.click()
            except: 
                logit("Failed to click the Submit IP Button!", logType="error")
                logit("The Xpath for the Submit IP Button has changed!", logType="error")
                logit('Script stopped. ')
                driver.quit()
                sys.exit()

        time.sleep(5)
        driver.quit()
    except Exception as e:
        logit('An exception occurred while updating the IP: ' + str(e), logType="error")
        return
    logit('The IP was successful updated from ' + oldip + ' to ' + newip)

def main(argv):
    logging.basicConfig(filename='ipwatcher.log', level=logging.INFO, format='%(asctime)s %(message)s')
    logit('DeFli IP-Watcher has started.')
    actualIP = "22.22.22.22"
    logit('Actual IP: ' + actualIP)

    while True:
        try:
            checkIP = getIP()
            if checkIP != False and checkIP != actualIP:
                logit('The IP has changed from ' + actualIP + " to " + checkIP)
                updateDashboardIP(checkIP, actualIP, "example@email.com", "your_defli_wallet_password", "1") #the one in "1" tells that you want to run the script for the Ground Station 1, replace the 1 with your station number if needed.
                actualIP = checkIP
                print("PRESS CTRL + C TO STOP THE SCRIPT")
            else:
                logit('The IP is not changed. Actual IP: ' + actualIP)
            time.sleep(3500) # this is in seconds
        except Exception as e:
            logit('Error: ' + str(e), logType="error")
            logit('Script stopped. ')
            break

if __name__ == "__main__":
   main(sys.argv[1:])
