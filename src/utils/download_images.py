import os
import requests
from tqdm import tqdm
import time
import re
from io import BytesIO
from PIL import Image

def sanitize_filename(name):
    # Characters that are invalid in Windows filenames:
    # < > : " / \ | ? *
    name = re.sub(r'[<>:"/\\|?*]', '_', name)

    # Windows also doesn't like filenames ending in a space or period
    name = name.rstrip(' .')

    return name

import os


def get_downloaded_card_image_sets(output_dir: str):
    """Return set names for directories containing card images."""

    if not os.path.isdir(output_dir):
        return []

    downloaded_sets = []

    for set_name in os.listdir(output_dir):
        set_path = os.path.join(output_dir, set_name)

        if not os.path.isdir(set_path):
            continue

        # Check whether the directory contains at least one file
        has_cards = any(
            os.path.isfile(
                os.path.join(set_path, filename)
            )
            for filename in os.listdir(set_path)
        )

        if has_cards:
            downloaded_sets.append(set_name)

    return downloaded_sets


def download_set_images(
        set_code: str,
        output_dir: str,
        base_api_url='https://api.scryfall.com/cards/search?q=set:',
        request_timeout: int = None,
        size: str = 'normal',
        include_collectors_num_in_name: bool = False
):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
                  'image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }

    # Get all cards in the set
    url = base_api_url + set_code
    cards = []

    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        cards.extend(data["data"])

        url = data.get("next_page") if data["has_more"] else None

    print(f"Found {len(cards)} cards")

    # Download images
    for i, card in tqdm(
        enumerate(cards, 1),
        total=len(cards)
    ):
        name = card["name"]
        collector_number = card["collector_number"]

        # -----------------------------------------
        # Determine filename
        # -----------------------------------------

        if include_collectors_num_in_name:
            filename = f"{name}-{collector_number}.jpg"
        else:
            filename = f"{name}.jpg"

        filename = sanitize_filename(filename)

        filepath = os.path.join(
            output_dir,
            filename
        )

        # -----------------------------------------
        # Normal single-faced card
        # -----------------------------------------

        if "image_uris" in card:

            image_url = card["image_uris"][size]

            image_response = requests.get(
                image_url,
                headers=headers
            )
            image_response.raise_for_status()

            with open(filepath, "wb") as f:
                f.write(image_response.content)

        # -----------------------------------------
        # Double-faced / adventure card
        # -----------------------------------------

        elif "card_faces" in card:

            faces = card["card_faces"]

            if len(faces) < 2:
                print(f"Skipping {name} — unexpected number of faces")
                continue

            images = []

            for face in faces:
                if "image_uris" not in face:
                    print(f"Skipping {name} — face has no image URI")
                    images = []
                    break

                image_url = face["image_uris"][size]

                image_response = requests.get(
                    image_url,
                    headers=headers
                )
                image_response.raise_for_status()

                image = Image.open(
                    BytesIO(image_response.content)
                ).convert("RGB")

                images.append(image)

            if not images:
                continue

            # Make all faces the same size
            width = max(image.width for image in images)
            height = max(image.height for image in images)

            resized_images = []

            for image in images:
                if image.size != (width, height):
                    image = image.resize(
                        (width, height),
                        Image.Resampling.LANCZOS
                    )

                resized_images.append(image)

            # Put faces side-by-side
            combined = Image.new(
                "RGB",
                (width * len(resized_images), height)
            )

            for index, image in enumerate(resized_images):
                combined.paste(
                    image,
                    (index * width, 0)
                )

            combined.save(
                filepath,
                format="JPEG",
                quality=90
            )

        # -----------------------------------------
        # Unknown image structure
        # -----------------------------------------

        else:
            print(f"Skipping {name} — no image URI")
            continue

        if request_timeout is not None:
            time.sleep(request_timeout)
            

if __name__ == '__main__':
    SET_CODE = "MSH"
    OUTPUT_DIR = os.path.join('data', 'card_images', f"{SET_CODE}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    download_set_images(
        SET_CODE,
        OUTPUT_DIR
    )

