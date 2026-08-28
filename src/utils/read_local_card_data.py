import csv
import glob
import sqlite3
from pathlib import Path
from datetime import datetime
import re 
import os

COLOR_MAP = {
    1: "W",
    2: "U",
    3: "B",
    4: "R",
    5: "G",
}


RARITY_MAP = {
    0: "token",
    1: "common", # basic lands and common lands
    2: "common",
    3: "uncommon",
    4: "rare",
    5: "mythic",
}

def clean_arena_name(name):
    if not name:
        return ""

    # Remove HTML/XML tags
    name = re.sub(r"<[^>]+>", "", name)

    # Decode common HTML entities
    name = name.replace("&amp;", "&")
    name = name.replace("&lt;", "<")
    name = name.replace("&gt;", ">")

    return name.strip()


def export_arena_cards(
        output_csv: str,
        arena_dir: str = r"C:\Program Files\Wizards of the Coast\MTGA\MTGA_Data\Downloads\Raw", 
    ):
    """Export MTG Arena GrpId -> card information to CSV."""

    processed = set()

    matches = glob.glob(
        str(Path(arena_dir) / "Raw_CardDatabase_*.mtga")
    )

    if not matches:
        raise FileNotFoundError(
            "Could not find Raw_CardDatabase_*.mtga"
        )

    db_path = matches[0]

    conn = sqlite3.connect(db_path)

    try:
        query = """
            SELECT
                c.GrpId,
                c.ExpansionCode,
                l.Loc AS name,
                c.Rarity,
                c.ColorIdentity,
                c.CollectorNumber,
                c.IsPrimaryCard,
                c.IsToken,
                c.IsDigitalOnly,
                c.IsRebalanced,
                c.Types,
                c.Subtypes
            FROM Cards c
            LEFT JOIN Localizations_enUS l
                ON c.TitleId = l.LocId
            WHERE c.GrpId IS NOT NULL
        """

        rows = conn.execute(query)

        with open(
            output_csv,
            "w",
            newline="",
            encoding="utf-8"
        ) as outfile:

            writer = csv.writer(outfile)

            writer.writerow([
                "id",
                "set",
                "name",
                "rarity",
                "color_identity",
                "collector_number",
                "is_primary",
                "is_token",
                "is_digital_only",
                "is_rebalanced",
                "types",
                "subtypes",
            ])

            count = 0

            for row in rows:
                (
                    grp_id,
                    set_code,
                    name,
                    rarity,
                    color_identity,
                    collector_number,
                    is_primary,
                    is_token,
                    is_digital_only,
                    is_rebalanced,
                    types,
                    subtypes,
                ) = row

                name = clean_arena_name(name)

                # Make sure we dont have a bunch of duplicates
                key = (grp_id, set_code)
                if key in processed:
                    continue
                else:
                    processed.add(key)


                # Decode rarity
                rarity = RARITY_MAP.get(rarity, f"unknown:{rarity}")

                # Decode color identity
                colors = []
                if color_identity:
                    for value in color_identity.split(","):
                        value = value.strip()

                        if value:
                            color = COLOR_MAP.get(int(value))
                            if color:
                                colors.append(color)

                color_identity = "".join(colors)

                # Convert Arena boolean integers to Python booleans
                is_primary = bool(is_primary)
                is_token = bool(is_token)
                is_digital_only = bool(is_digital_only)
                is_rebalanced = bool(is_rebalanced)

                writer.writerow([
                    grp_id,
                    set_code,
                    name,
                    rarity,
                    color_identity,
                    collector_number,
                    is_primary,
                    is_token,
                    is_digital_only,
                    is_rebalanced,
                    types,
                    subtypes,
                ])

                count += 1

        print(f"Exported {count:,} Arena cards to {output_csv}")

    except Exception as e:
        print(f'Error with card mapping setup: {e}')
        return False

    finally:
        conn.close()

    return True


def get_local_cards_data_as_of(data_dir="data"):
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
        r"arena-cards-(?P<date>\d{4}-\d{2}-\d{2})\.csv"
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



if __name__ == '__main__':
    today = datetime.now().strftime("%Y-%m-%d")
    export_arena_cards(
        f"data\\arena-cards-{today}.csv",
        r"C:\Program Files\Wizards of the Coast\MTGA\MTGA_Data\Downloads\Raw",
    )