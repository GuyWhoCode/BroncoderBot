from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import requests
from dotenv import load_dotenv
import os
from submission_handling.browser_state import *
import asyncio
import copy

desired_capabilities = DesiredCapabilities.CHROME
timeout = 10

my_browser_state = BrowserState()
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(desired_capabilities=desired_capabilities, options=options)

response_dict_base = {
        "msg": None,
        "err": False,
        "details":{
        }
    }

def exit():
    print( "Timed out waiting for page to load")
    my_browser_state.state = BROKEN
    driver.quit()

async def setup(question):
    my_browser_state.state = SETTING_UP
    driver.get('https://leetcode.com/accounts/login/?next=/profile/account/')
    try:
        element_present = EC.presence_of_element_located((By.ID, 'signin_btn'))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        exit()
    
    load_dotenv()
    driver.find_element(By.ID, "id_login").send_keys(os.environ.get("LEETCODE_USERNAME"))
    driver.find_element(By.ID, "id_password").send_keys(os.environ.get("LEETCODE_PASSWORD"))

    try:
        element_not_present = EC.invisibility_of_element((By.ID, 'initial-loading'))
        WebDriverWait(driver, timeout).until(element_not_present)
    except TimeoutException:
        exit()

    driver.find_element(By.ID, "signin_btn").click()

    try:
        element_present = EC.presence_of_element_located((By.ID, 'profile-app'))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        exit()

    driver.get("https://leetcode.com/problems/{}".format(question.get("titleSlug")))

    try:
        element_present = EC.invisibility_of_element((By.ID, 'initial-loading'))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        exit()
        
    try:
        element_present = EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "Got it!")]'))
        WebDriverWait(driver, timeout).until(element_present)
        driver.find_element(By.XPATH, '//*[contains(text(), "Got it!")]').click()
    except TimeoutException:
        pass
    

    driver.find_element(By.XPATH, "//*[@data-cy='lang-select']").click()
    driver.find_element(By.XPATH, "//li[contains(text(), 'Python3')]").click()
    driver.execute_script("document.getElementsByClassName(\"btns__1OeZ\")[0].innerHTML += '<textarea id=\"clipboard\" rows=\"4\" cols=\"50\">shit</textarea>'")
    my_browser_state.state = READY
    
async def typeCode(code):
    clipboard = driver.find_element(By.ID, 'clipboard')
    clipboard.click()
    actions = ActionChains(driver)
    actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
    actions.send_keys(code).perform()
    actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
    actions.key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()
    code_editor = driver.find_element(By.CLASS_NAME, 'CodeMirror-lines')
    code_editor.click()
    actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
    actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
    


async def submitAttachmentToLeetcode(attachment):
    if my_browser_state.state == BUSY:
        return {"msg": "Broncoder is currently busy. Eventually we'll add a queue system, but try again later", "err": True}
    if my_browser_state.state == SETTING_UP:
        return {"msg": "Broncoder is currently setting up. Please try again in a couple of seconds", "err": True}
    url = str(attachment)
    code = requests.get(url).text
    return await submitCode(code)

async def submitCode(code):
    response_dict = copy.deepcopy(response_dict_base)
    my_browser_state.state = BUSY
    print("attempting submission")
    await typeCode(code)
    driver.find_element(By.XPATH, '//button[@data-cy="submit-code-btn"]').click()
    try:
        element_present = EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Pending')]"))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        exit()
    await asyncio.sleep(5)
    try:
        element_present = EC.presence_of_element_located((By.XPATH, "//a[starts-with(@href, '/submissions/detail')]"))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        exit()
    result_url = driver.find_element(By.XPATH, "//a[starts-with(@href, '/submissions/detail')]").get_property("href")
    print(result_url)
    driver.execute_script("window.open()")
    driver.switch_to.window(driver.window_handles[1])
    driver.get(result_url)

    # wait until done loading
    try:
        element_present = EC.presence_of_element_located((By.CLASS_NAME, "testcase-table-re"))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        exit()
    
    response_dict["details"]["result_state"] = driver.find_element(By.ID, "result_state").get_attribute("innerText")
    print(response_dict["details"]["result_state"])
    if response_dict["details"]["result_state"] == "Accepted":
        response_dict["details"]["result_memory"] = driver.find_element(By.ID, "result_memory").get_attribute("innerText")
        response_dict["details"]["result_runtime"] = driver.find_element(By.ID, "result_runtime").get_attribute("innerText")
    response_dict["details"]["result_progress"] = driver.find_element(By.ID, "result_progress").get_attribute("innerText")
    print(response_dict["details"]["result_progress"])
    
    driver.execute_script("window.close()")
    driver.switch_to.window(driver.window_handles[0])
    my_browser_state.state = READY

    response_dict["msg"] = "Submission to leetcode.com completed"
    response_dict["err"] = False
    return response_dict
