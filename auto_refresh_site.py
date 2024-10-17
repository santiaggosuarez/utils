from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time

CHROMEDRIVER_PATH = ""

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH))
driver.get("https://www.google.com"
time.sleep(120)
           
try:
    while True:
        driver.refresh()
        time.sleep(2)
except KeyboardInterrupt:
    driver.quit()
