from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

def log_in(browser):
    id = open('id.txt')
    username = id.readline()
    password = id.readline()
    id.close()

    time.sleep(1)

    elem = browser.find_element_by_xpath("//button[@name='login']")
    elem.click()

    elem = browser.find_element_by_xpath("//input[@name='username']")
    elem.send_keys(username, Keys.ENTER)

    if password:
        time.sleep(.2)
        elem = browser.find_element_by_xpath("//input[@name='password']")
        elem.send_keys(password, Keys.ENTER)

def main():
    browser = webdriver.Chrome()
    browser.get('http://play.pokemonshowdown.com')
    log_in(browser)
    time.sleep(10)

main()