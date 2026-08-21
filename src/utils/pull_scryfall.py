import os
import requests
import pandas as pd
import csv
import gzip
import json
import requests
from datetime import datetime
import re
from typing import List


def get_card_mana_costs(
    card_name_list: List[str],
    scryfall_data_filepath: str
):
    """
    Retrieve mana costs for a list of Magic cards.

    Args:
        card_name_list: List of card names to lookup.
        scryfall_data_filepath: Path to the Scryfall card CSV export.

    Returns:
        DataFrame containing card names and mana costs.
        If no Scryfall file is provided, returns the cards with empty
        mana cost values.
    """

    df = pd.DataFrame({"name": card_name_list})

    if scryfall_data_filepath is None:
        df["mana_cost"] = ""
        return df[["name", "mana_cost"]]

    scryfall_df = pd.read_csv(scryfall_data_filepath)

    df = df.merge(
        scryfall_df,
        on="name",
        how="left"
    )

    return df[["name", "mana_cost"]]


def get_scryfall_data_as_of(data_dir="data"):
    """
    Find the newest Scryfall card CSV export in a directory.

    Expected filename format:
        scryfall-cards-YYYY-MM-DD.csv

    Returns:
        Dictionary containing:
            date: Date string of newest dataset.
            filepath: Path to newest CSV file.

        Returns None if no Scryfall CSV files are found.
    """

    pattern = re.compile(
        r"scryfall-cards-(?P<date>\d{4}-\d{2}-\d{2})\.csv"
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


def get_scryfall_info(
    output_csv: str,
    url: str = 'https://api.scryfall.com/bulk-data',
    download_gzip_outfile:str = os.path.join('data', 'scryfall_cards.jsonl.gz')
):
    """
    Download Scryfall's latest Oracle Cards bulk dataset and convert it
    into a simplified CSV used by the draft tracker.

    The generated CSV contains card metadata needed by the overlay,
    including mana costs, colors, rarity, and card text.
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }

    # Get the latest Oracle Cards download URL
    bulk = requests.get(url, headers=headers).json()

    oracle = next(
        item for item in bulk["data"]
        if item["type"] == "oracle_cards"
    )

    download_url = oracle["jsonl_download_uri"]

    print("Downloading...")
    response = requests.get(download_url, headers=headers)
    response.raise_for_status()

    with open(download_gzip_outfile, "wb") as f:
        f.write(response.content)

    print("Extracting and writing CSV...")

    fields = [
        "name",
        "mana_cost",
        "cmc",
        "colors",
        "color_identity",
        "type_line",
        "oracle_text",
        "power",
        "toughness",
        "loyalty",
        "rarity",
        "set",
        "collector_number",
        "arena_id"
    ]

    try:

        with gzip.open(download_gzip_outfile, "rt", encoding="utf-8") as infile, \
            open(output_csv, "w", newline="", encoding="utf-8") as outfile:

            writer = csv.DictWriter(outfile, fieldnames=fields)
            writer.writeheader()

            for line in infile:
                card = json.loads(line)

                writer.writerow({
                    "name": card.get("name", ""),
                    "mana_cost": card.get("mana_cost", ""),
                    "cmc": card.get("cmc", ""),
                    "colors": ",".join(card.get("colors", [])),
                    "color_identity": ",".join(card.get("color_identity", [])),
                    "type_line": card.get("type_line", ""),
                    "oracle_text": card.get("oracle_text", "").replace("\n", " "),
                    "power": card.get("power", ""),
                    "toughness": card.get("toughness", ""),
                    "loyalty": card.get("loyalty", ""),
                    "rarity": card.get("rarity", ""),
                    "set": card.get("set", ""),
                    "collector_number": card.get("collector_number", ""),
                })

        # Delete the gz file
        os.remove(download_gzip_outfile)

        print("Done!")

    except Exception as e:
        return False

    return True


if __name__ == '__main__':
    today = datetime.now().strftime("%Y-%m-%d")
    os.path.join('data', f'scryfall-cards-{today}.csv'),
    get_scryfall_info()