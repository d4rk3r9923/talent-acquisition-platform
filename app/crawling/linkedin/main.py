from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
from time import sleep
import pandas as pd
import re
from itertools import count
import time
import random


# List of country-specific domains to rotate domains in get url
DOMAINS = [
    "us", "ca", "uk", "de", "fr", "au", "jp", "cn", "in", "br",
    "ru", "it", "es", "mx", "kr", "se", "nl", "ch", "pl", "ar",
    "za", "ng", "ie", "sg", "fi", "dk", "no", "hk", "tw", "il",
    "ae", "at", "cz", "hu", "pt", "cl", "ro", "my", "th", "vn",
    "ph", "co", "pe", "bg", "sk", "lt", "lv", "ee", "si", "by",
    "is", "mt", "cy", "jo", "qa", "kh", "lk", "bd", "pk", "vn",
    "ua", "kz", "uz", "am", "ge", "md", "mk", "ba", "hr", "rs",
    "cy", "tt", "jm", "gh", "ke", "tz", "ug", "rw", "zm", "mw",
    "zw", "lr", "sl", "tg", "sn", "ci", "cm", "ne", "ng", "dj"
]

# LinkedIn login function
def loginLinkedIn(driver, username, password):
    driver.get("https://www.linkedin.com/login")
    time.sleep(5)
    driver.find_element(By.ID, "username").send_keys(username)
    time.sleep(5)
    driver.find_element(By.ID, "password").send_keys(password)
    time.sleep(5)
    driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
    time.sleep(5)

def expandSeeMore(driver):    
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        see_more_buttons = driver.find_elements(By.XPATH, "//button[text()='…see more']")
        for button in see_more_buttons:
            try:
                ActionChains(driver).move_to_element(button).click(button).perform()
                time.sleep(5)  
            except Exception as e:
                print(f"Error clicking 'See more' button: {e}")

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        time.sleep(5)

        


# Helper functions for cleaning data
def trimListBeforeMatch(lst, matchString):
    for i, string in enumerate(lst):
        if string.startswith(matchString):
            return lst[:i]
    return lst

def removeDuplicateLines(inputString):
    lines = inputString.split('\n')
    seen = set()
    unique_lines = [line for line in lines if line not in seen and not seen.add(line)]
    return '\n'.join(unique_lines)

def excludeStartingWith(lst, matchString):
    return [string for string in lst if not string.startswith(matchString)]

def cleanShowAllPattern(inputString):
    return re.sub(r'Show all \d+ \w+', '', inputString).strip()

def extractSectionsFromList(dataList):
    extracted_data = {}
    for item in dataList:
        section_header, first_phrase = item.split('\n', 1)
        if section_header == "More profiles to browse":
            break
        extracted_data[section_header] = first_phrase
    return extracted_data


# Crawl and process profile data
def extractProfileData(driver):
    profile_components = driver.find_elements(By.XPATH, '//*[@data-view-name="profile-card"]')
    lst = [component.text for component in profile_components]

    result_list = trimListBeforeMatch(lst, "Interest")
    result_list = [removeDuplicateLines(item) for item in result_list]
    result_list = excludeStartingWith(result_list, "Activity")
    result_list = [cleanShowAllPattern(item) for item in result_list]
    result_list = extractSectionsFromList(result_list)
    return result_list


# Scrape profile information and add URL
def scrapeLinkedInProfile(driver, profileUrl):
    profileUrl = profileUrl[:8] + random.choice(DOMAINS) + "." + profileUrl[8:]
    time.sleep(10)
    driver.get(profileUrl)
    time.sleep(10)
    # removePopUp(driver)
    # time.sleep(5)
    expandSeeMore(driver)
    time.sleep(5) 
    profile_info = {
        "url": profileUrl,  # Include URL in the profile data
        "name": getTextContent(driver, By.CSS_SELECTOR, "h1.text-heading-xlarge"),
        "headline": getTextContent(driver, By.CSS_SELECTOR, "div.text-body-medium.break-words"),
        "location": getTextContent(driver, By.CSS_SELECTOR, "span.text-body-small.inline.t-black--light.break-words")
    }

    profile_data = extractProfileData(driver)
    profile_info.update(profile_data)
    return profile_info


# Helper function to get text from elements
def getTextContent(driver, by, value):
    try:
        return driver.find_element(by, value).text
    except:
        return None


# Process list of dictionaries and merge keys
def mergeProfileData(dictList):
    all_keys = set(key for d in dictList for key in d.keys())
    return [{key: d.get(key, None) for key in all_keys} for d in dictList]


# Main scraping process
def runLinkedInScraper(driver, df):
    try:
        all_profiles = []
        for url in tqdm(df["url"]):
            try:
                profile_info = scrapeLinkedInProfile(driver, url)
                all_profiles.append(profile_info)
            except Exception as e:
                print(f"Error scraping {url}: {e}")

        processed_profiles = mergeProfileData(all_profiles)
        profiles_df = pd.DataFrame(processed_profiles)

        # profiles_df.to_csv("linkedinProfiles.csv", index=False)
        return profiles_df
    finally:
        driver.quit()


# Click X on Pop-up to skip login in LinkedIn
def removePopUp(driver):
    try:
        driver.find_element(By.XPATH, "/html/body/div[2]/div/div/section/button").click()
    except:
        pass
    time.sleep(1)

# Google search to collect LinkedIn profile URLs
def collectProfileUrlsFromGoogle(driver, categories, locations, maxPage=2):
    profile_urls = []
    
    for location in locations:
        for category in categories:
            url = f'https://google.com/search?q=site:linkedin.com/in AND {category} AND "{location}" -Company -LLC'
            driver.get(url)
            sleep(1)

            for i in count(start=1, step=1):
                try:
                    WebDriverWait(driver, 3).until(
                        EC.frame_to_be_available_and_switch_to_it(
                            (By.XPATH, "//iframe[starts-with(@name, 'a-') and starts-with(@src, 'https://www.google.com/recaptcha')]")
                        )
                    )
                    input("CAPTCHA detected, please solve it manually and press Enter to continue...")
                except:
                    pass

                elements = driver.find_elements(By.CSS_SELECTOR, 'a[jsname="UWckNb"]')
                profile_urls.extend([(location, category, ele.get_attribute('href')) for ele in elements])
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                sleep(1)
                
                try:
                    driver.find_element(By.ID, "pnnext").click()
                    sleep(1)
                except:
                    print(f'{url} - end page at: {i}')
                    break

                if i == maxPage:
                    print(f'{url} - end page at: {i}')
                    break

    return pd.DataFrame(profile_urls, columns=["location", "category", "url"]).replace('vn.', '', regex=True)


# Script entry point
if __name__ == "__main__":
    # Settings
    categories = ["AI Engineer", "HR", "Graphic Designer", "Finance", "Business"]
    locations = ["Ho Chi Minh"]
    max_page = 2
    username = "yaki81203@gmail.com"
    password = "Nguyen113446779"
    startpoint = 0
    endpoint = 30

    # Initialize WebDriver with options
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--headless=new")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service(executable_path="chromedriver-win64/chromedriver.exe")
    driver = webdriver.Chrome(options=options)
    time.sleep(5)

    # Collect LinkedIn profile URLs
    # profile_data = collectProfileUrlsFromGoogle(driver, categories, locations, max_page)

    # Log in to LinkedIn
    loginLinkedIn(driver, username=username, password=password)

    # Scrape LinkedIn profiles and save the data
    profile_data = pd.read_csv("data/nguyen_dataset.csv")[startpoint:endpoint]
    # print(profile_data)
    df = runLinkedInScraper(driver, profile_data)
    df.to_csv(f"dataset{startpoint}_{endpoint}.csv", index=False)
