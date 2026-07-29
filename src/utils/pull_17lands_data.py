import requests
import os
import pandas
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
import glob

BASE_URL = 'https://www.17lands.com/card_data?expansion={exp}&format=PremierDraft&time_period=ALL_TIME&view=table&columns=picked%2Cplayed%2Copening%2Cdrawn%2CeverInHand%2CnotSeen%2Cimprovement%2Cseen'

def pull_table(
    expansion: str,
    output_name: str
):
    """
    Uses headless chrome webdriver to pull exported card winrate data for a given expansion off 17 lands
    Download will look for most recent csv file in download folder and rename it to output name
    
    Args
        expansion - str
            code for expansion (e.g. MSH)
        output_name - str
            name for output csv file
    """
    full_url = BASE_URL.replace('{exp}', expansion)

    download_dir = os.path.join(os.getcwd(), 'data')

    options = webdriver.ChromeOptions()
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        },
    )

    # Run without opening a window
    options.add_argument("--headless=new")

    # Recommended for stability
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)

    driver.get(full_url)

    export = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//div[@role='alert' and normalize-space()='Export data']"
        ))
    )

    driver.execute_script("arguments[0].click();", export)

    # Wait for the dropdown and click the option that starts with "Download"
    download_option = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//*[starts-with(normalize-space(.), 'Download')]"
            )
        )
    )
    download_option.click()

    print("Download triggered!")

    # Wait for download to start
    time.sleep(2)

    timeout = time.time() + 30  # 30 second timeout

    while True:
        csvs = glob.glob(os.path.join(download_dir, "*.csv"))
        partials = glob.glob(os.path.join(download_dir, "*.crdownload"))

        # New CSV in last 1 min
        recent_csvs = [
            f for f in csvs
            if time.time() - os.path.getmtime(f) < 60
        ]
        if recent_csvs:
            newest = max(recent_csvs, key=os.path.getmtime)
            break

        # New partial download exists
        if partials:
            newest = max(partials, key=os.path.getmtime)
            break

        if time.time() > timeout:
            raise TimeoutError("No download appeared.")

        time.sleep(0.25)

    # If it's still downloading, wait until the size stops changing
    if newest.endswith(".crdownload"):
        while True:
            size1 = os.path.getsize(newest)
            time.sleep(0.5)
            size2 = os.path.getsize(newest)

            if size1 == size2:
                break

        # Chrome may have renamed it after the download finished.
        # If so, use the newest recent CSV instead.
        csvs = glob.glob(os.path.join(download_dir, "*.csv"))
        recent_csvs = [
            f for f in csvs
            if time.time() - os.path.getmtime(f) < 1
        ]

        if recent_csvs:
            newest = max(recent_csvs, key=os.path.getmtime)

    # Rename to desired filename
    new_name = os.path.join(download_dir, output_name)
    os.rename(newest, new_name)

    print("Saved as", new_name)


if __name__ == '__main__':
    expansion_code = 'MSH'
    today = datetime.now().strftime("%Y-%m-%d")
    pull_table(expansion_code, f'card-ratings-{expansion_code}-{today}.csv')