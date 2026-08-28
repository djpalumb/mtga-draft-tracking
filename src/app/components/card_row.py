import tkinter as tk
from tkinter import ttk
import os
import re
from src.utils.download_images import sanitize_filename
from PIL import Image, ImageTk
from glob import glob

from src.app.style import (
    CARD_COLOR_MAP, 
    GRADE_COLOR_MAP,
    RARITY_COLOR_MAP
)
def get_card_color(identity):
    if identity is None or identity == "" or not isinstance(identity, str):
        return CARD_COLOR_MAP[""]

    if len(identity) > 1:
        return CARD_COLOR_MAP["MULTICOLOR"]

    return CARD_COLOR_MAP.get(identity, "#FFFFFF")

def rarity_symbol(rarity):
    rarity = rarity.lower()

    color = RARITY_COLOR_MAP.get(rarity, "#808080")

    return {
        "text": "◯",
        "color": color
    }


def mana_cost_to_icons(
    mana_cost: str, 
    assets_dir: str = os.path.join("assets", "mana")
) -> list[str]:
    """
    Converts a Scryfall mana cost string (e.g. "{3}{R}{R}")
    into a list of image filenames.

    Unknown symbols are ignored.

    Example:
        "{3}{R}{R}" -> [
            "assets/mana-3.png",
            "assets/mana-r.png",
            "assets/mana-r.png"
        ]
    """

    if not mana_cost:
        return []

    symbols = re.findall(r"\{([^}]*)\}", mana_cost)

    results = []

    for symbol in symbols:
        filename = None

        # -------------------------
        # Simple numbers (0-20, 100, etc.)
        # -------------------------
        if symbol.isdigit():
            filename = f"mana-{symbol}.png"

        else:
            key = symbol.lower()

            # Hybrid mana uses "/"
            key = key.replace("/", "")

            # Phyrexian mana
            key = key.replace("/p", "p")

            # Snow, Tap, Untap, etc. remain unchanged
            filename = f"mana-{key}.png"

        full_path = os.path.join(assets_dir, filename)

        if os.path.exists(full_path):
            results.append(full_path)

    return results


def show_card_image_on_hover(
    widget, 
    card_name, 
    set_code,
    images_dir=os.path.join("data","card_images")
):
    """
    Attach a hover handler to a Tkinter widget that displays the card's
    image in a small popup window.

    The card image is expected at:
        {images_dir}/{set_code}/{sanitized_card_name}.jpg

    Returns the hover callbacks so they can optionally be managed later.
    """

    card_dir = os.path.join(images_dir, set_code)

    # First try the exact filename
    exact_path = os.path.join(
        card_dir,
        sanitize_filename(card_name) + ".jpg"
    )

    if os.path.isfile(exact_path):
        image_path = exact_path
    else:
        # Fall back to any file beginning with the sanitized card name
        pattern = os.path.join(
            card_dir,
            sanitize_filename(card_name) + "*.jpg"
        )

        matches = glob(pattern)

        if matches:
            image_path = matches[0]
        else:
            print(f"Card image not found: {exact_path}")
            return
    
    popup = None
    popup_image = None

    def on_enter(event):
        nonlocal popup, popup_image

        # Don't create multiple popups
        if popup is not None:
            return

        try:
            image = Image.open(image_path)

            # Example: 40% size
            new_width = int(image.width * 0.4)
            new_height = int(image.height * 0.4)

            image = image.resize(
                (new_width, new_height),
                Image.Resampling.LANCZOS
            )

            popup_image = ImageTk.PhotoImage(image)

            popup = tk.Toplevel(widget)
            popup.overrideredirect(True)
            popup.attributes("-topmost", True)

            label = tk.Label(
                popup,
                image=popup_image,
                bg="black",
                bd=1,
                relief="solid"
            )
            label.pack()

            popup.update_idletasks()

            popup_width = popup.winfo_width()
            popup_height = popup.winfo_height()

            screen_width = popup.winfo_screenwidth()
            screen_height = popup.winfo_screenheight()

            widget_x = widget.winfo_rootx()
            widget_y = widget.winfo_rooty()
            widget_width = widget.winfo_width()
            widget_height = widget.winfo_height()

            gap = 5

            # -----------------------------------------
            # Try right
            # -----------------------------------------

            x = widget_x + widget_width + gap
            y = widget_y

            if x + popup_width <= screen_width:
                # Fits on the right
                pass

            # -----------------------------------------
            # Try left
            # -----------------------------------------

            elif widget_x - popup_width - gap >= 0:
                x = widget_x - popup_width - gap


            # -----------------------------------------
            # Nothing fits perfectly
            # Clamp to screen
            # -----------------------------------------

            else:
                # Center horizontally over the widget
                x = widget_x + (widget_width - popup_width) // 2

                # Put it above if possible, otherwise below
                if widget_y >= popup_height + gap:
                    y = widget_y - popup_height - gap
                else:
                    y = widget_y + widget_height + gap

            # -----------------------------------------
            # Final screen boundary protection
            # -----------------------------------------

            x = max(5, min(x, screen_width - popup_width - 5))
            y = max(5, min(y, screen_height - popup_height - 5))

            popup.geometry(f"+{x}+{y}")

        except Exception as e:
            print(f"Failed to display card image: {image_path}")
            print(e)

    def on_leave(event):
        nonlocal popup, popup_image

        if popup is not None:
            popup.destroy()
            popup = None
            popup_image = None

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

    return on_enter, on_leave


class CardRow(tk.Frame):
    def __init__(
        self,
        parent,
        name,
        wr,
        identity,
        grade,
        rarity,
        picked,
        mana_cost='',
        set_code=None,
    ):
        super().__init__(parent, bg="#1e1e1e")
        self.name = name
        self.wr = wr
        self.identity = identity
        self.grade = grade
        self.picked = picked
        self.rarity = rarity
        self.mana_cost = mana_cost
        self.set_code = set_code

        self.build()


    def build(self):
        frame_color = get_card_color(self.identity)

        # Make the first column (card name) expand
        self.grid_columnconfigure(0, weight=1)

        #
        # -------------------------
        # Card name section
        # -------------------------
        #

        name_frame = tk.Frame(
            self,
            bg=frame_color
        )
        name_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 5)
        )

        # Name expands, mana stays right
        name_frame.grid_columnconfigure(1, weight=1)

        rarity = rarity_symbol(self.rarity)

        # Rarity
        tk.Label(
            name_frame,
            text="◆",
            fg=rarity["color"],
            bg=frame_color,
            font=("Segoe UI Symbol", 12, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=(6, 2),
            pady=4
        )

        # Card name
        tk.Label(
            name_frame,
            text=self.name,
            fg="black",
            bg=frame_color,
            anchor="w",
            font=("Segoe UI", 11),
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(0, 6),
            pady=4
        )

        # Mana frame
        mana_frame = tk.Frame(
            name_frame,
            bg=frame_color
        )

        mana_frame.grid(
            row=0,
            column=2,
            sticky="e",
            padx=(0, 6)
        )

        # Mana symbols
        self.mana_images = []

        if "nan" not in str(self.mana_cost).lower():
            for icon_path in mana_cost_to_icons(self.mana_cost):
                img = tk.PhotoImage(file=icon_path)
                img = img.subsample(4)

                self.mana_images.append(img)

                tk.Label(
                    mana_frame,
                    image=img,
                    bg=frame_color,
                    bd=0,
                    highlightthickness=0
                ).pack(side="left")

        #
        # -------------------------
        # Win Rate
        # -------------------------
        #

        wr_text = "---" if "nan" in str(self.wr) else f"{self.wr:.1%}"

        tk.Label(
            self,
            text=wr_text,
            width=10,
            bg=GRADE_COLOR_MAP[self.grade],
            fg="black",
            font=("Segoe UI", 11),
            pady=4
        ).grid(
            row=0,
            column=1,
            padx=5
        )

        #
        # -------------------------
        # Grade
        # -------------------------
        #

        tk.Label(
            self,
            text=self.grade,
            width=5,
            bg=GRADE_COLOR_MAP[self.grade],
            fg="black",
            font=("Segoe UI", 11),
            pady=4
        ).grid(
            row=0,
            column=2
        )

        #
        # -------------------------
        # Picked
        # -------------------------
        #

        tk.Label(
            self,
            text="★" if self.picked else "",
            fg="#FFD700",
            bg="#1e1e1e",
            width=2,
            font=("Segoe UI", 12, "bold"),
            pady=4
        ).grid(
            row=0,
            column=3
        )

        if self.set_code:
            show_card_image_on_hover(
                self,
                self.name,
                self.set_code
            )