import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
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
import pyautogui
from dotenv import load_dotenv

load_dotenv()

VIECLAM24h_USERNAME = os.environ.get("VIECLAM24h_USERNAME")
VIECLAM24H_PASSWORD = os.environ.get("VIECLAM24H_PASSWORD")

options = Options()
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")

prefs = {
    "download.default_directory": os.path.join(os.getcwd(), 'Resume'),  
    "download.prompt_for_download": False,  
    "directory_upgrade": True,  
    "safebrowsing.enabled": True,
    "profile.default_content_setting_values.automatic_downloads": 1  
}
options.add_experimental_option("prefs", prefs)

def loginLVieclam24h(driver, url, username, password):
    driver.get(url)
    time.sleep(2)

    driver.find_element(By.NAME, "email").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
    time.sleep(2)
    driver.find_element(By.XPATH, "//button[text()='Để sau']").click()
    return driver

def downloadResumes(driver, links):
    for link in links:
        try:
            driver.get(link)
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[text()='File đính kèm']"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(1)
            download_icon = pyautogui.locateOnScreen('component/download.png', confidence=0.8)
            time.sleep(1)
            if download_icon:
                pyautogui.click(download_icon)
                time.sleep(1)
                save_icon = pyautogui.locateOnScreen('component/saveAs.png', confidence=0.8)
                if save_icon:
                    pyautogui.click(save_icon)
                else:
                    print("Can't find save icon")
                print("Download button clicked.")
            else:
                print("Download icon not found on the screen.")
            time.sleep(4)

        except Exception as e:
            print(f"Error processing {link}: {e}")
            time.sleep(1)

def main(driver, csv_file_path,start = 0):

    df = pd.read_csv(csv_file_path)
    links = df["Link"][start:].tolist() 

    download_folder = os.path.join(os.getcwd(), 'Resume')
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    downloadResumes(driver, links)
    driver.quit()

if __name__ == "__main__":
    driver = webdriver.Chrome(options=options)

    url = "https://ntd.vieclam24h.vn/tim-kiem-ung-vien-nhanh?per_page=10&salary_min=22220000&updated_at="
    loginLVieclam24h(driver, url, VIECLAM24h_USERNAME, VIECLAM24H_PASSWORD)
    csv_file_path = "path_to_pdf"

    main(driver, csv_file_path)
