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
from bs4 import BeautifulSoup
import re
import pandas as pd
from pathlib import Path

def get_most_recent_winrate_files(data_dir="data"):
    """
    Returns a dict mapping each set code to the path of its most recent
    winrate CSV file.

    Example return:
    {
        "BLB": Path("data/card-ratings-BLB-2026-07-20.csv"),
        "FDN": Path("data/card-ratings-FDN-2026-06-15.csv"),
    }
    """
    pattern = re.compile(r"^card-ratings-(.+)-(\d{4}-\d{2}-\d{2})\.csv$")

    newest = {}

    for path in Path(data_dir).glob("card-ratings-*.csv"):
        match = pattern.match(path.name)
        if not match:
            continue

        set_code, date_str = match.groups()
        date = datetime.strptime(date_str, "%Y-%m-%d").date()

        if set_code not in newest or date > newest[set_code][0]:
            newest[set_code] = (date, path)

    return {set_code: path for set_code, (_, path) in newest.items()}
    

def get_cards_data_as_of(data_dir="data"):
    """
    Determine the most recent cards data file.

    Looks for files named:
        all-cards-{yyyy-mm-dd}.csv

    Returns:
        dict:
        {
            "date": "2026-07-29",
            "filepath": "data/all-cards-MSH-2026-07-29.csv"
        }

        Returns None if no matching file exists.
    """

    pattern = re.compile(
        r"all-cards-(?P<date>\d{4}-\d{2}-\d{2})\.csv"
    )

    latest = None

    for filename in os.listdir(data_dir):
        match = pattern.match(filename)

        if match:
            file_date = datetime.strptime(
                match.group("date"),
                "%Y-%m-%d"
            )

            entry = {
                "date": match.group("date"),
                "filepath": os.path.join(data_dir, filename),
                "datetime": file_date
            }

            if latest is None or file_date > latest["datetime"]:
                latest = entry

    if latest:
        # Remove internal comparison field
        latest.pop("datetime")

    return latest


def pull_all_cardlist(
    output_file: str,
    csv_url: str = 'https://17lands-public.s3.amazonaws.com/analysis_data/cards/cards.csv',
):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }

    try:
        output = requests.get(csv_url, headers=headers)
        csv_data = output.text.replace('\r\n', '\n')
        csv_data = csv_data.replace('\n\n', '\n')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(csv_data) 
    except Exception as e:
        print(f'Failed all-card pull: {e}')
        return False

    return True


def pull_cards_wr_table(
    expansion: str,
    output_name: str,
    base_url: str = 'https://www.17lands.com/card_data?expansion={exp}&format=PremierDraft&time_period=ALL_TIME&view=table&columns=picked%2Cplayed%2Copening%2Cdrawn%2CeverInHand%2CnotSeen%2Cimprovement%2Cseen' 
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
    try:
        full_url = base_url.replace('{exp}', expansion)

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
        # Delete if it already exists
        if os.path.exists(new_name):
            os.remove(new_name)
            print(f'Removed existing file with same name as destination: {new_name}')

        os.rename(newest, new_name)

        print("Saved as", new_name)

        return True

    except Exception as e:
        print(f"Failed to download {expansion}: {e}")
        return False

    finally:
        if driver:
            driver.quit()


if __name__ == '__main__':
    # pull_all_cardlist('test.csv')

    expansion_code = 'MSH'
    today = datetime.now().strftime("%Y-%m-%d")
    pull_cards_wr_table(expansion_code, f'card-ratings-{expansion_code}-{today}.csv')