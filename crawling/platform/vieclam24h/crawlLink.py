from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from time import sleep
import pandas as pd
import re
from itertools import count
import time
import os
load_dotenv()

VIECLAM24h_USERNAME = os.environ.get("VIECLAM24h_USERNAME")
VIECLAM24H_PASSWORD = os.environ.get("VIECLAM24H_PASSWORD")

options = Options()
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")

def loginLVieclam24h(driver, url, username, password):
    driver.get(url)
    time.sleep(2)

    driver.find_element(By.NAME, "email").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
    time.sleep(2)
    driver.find_element(By.XPATH, "//button[text()='Để sau']").click()
    return driver

def extract_hrefs(driver):
    # Find all elements with the given class
    elements = driver.find_elements(By.CLASS_NAME, "w-full.px-4.py-3.bg-white.border.rounded-sm.border-grey-light")

    hrefs = []
    for element in elements:
        # Check if the element contains an anchor tag or is an anchor tag itself
        anchor = element.find_element(By.TAG_NAME, 'a')
        if anchor:
            href = anchor.get_attribute('href')
            if href:  # Ensure the href exists
                hrefs.append(href)
    return hrefs

def scroll_to_bottom(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")  # Get the height of the page

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll to the bottom
        time.sleep(1)  # Wait for the new content to load

        # Calculate new scroll height and compare it with the last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:  # If heights are the same, we are at the bottom
            break
        last_height = new_height

def main(driver):
    for i in range(200):
        scroll_to_bottom(driver)
        hrefs = extract_hrefs(driver)
        df = pd.concat([df, pd.DataFrame(hrefs, columns=['Link'])], ignore_index=True)

        try:
            element = driver.find_element(By.XPATH, "//div[text()='Trang sau']")
            element.click()
            time.sleep(1) 
        except Exception as e:
            print(f"Error occurred: {e}")
            break 
if __name__ == "__main__":
    driver = webdriver.Chrome(options=options)
    url = "https://ntd.vieclam24h.vn/tim-kiem-ung-vien-nhanh?per_page=10&salary_min=22220000&updated_at="
    driver = loginLVieclam24h(driver, url, VIECLAM24h_USERNAME, VIECLAM24H_PASSWORD)
    main(driver)
