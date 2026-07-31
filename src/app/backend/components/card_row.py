import tkinter as tk
from tkinter import ttk
import os
import re

from src.app.frontend.style import (
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
        mana_cost=''
    ):
        super().__init__(parent, bg="#1e1e1e")
        self.name = name
        self.wr = wr
        self.identity = identity
        self.grade = grade
        self.picked = picked
        self.rarity = rarity
        self.mana_cost = mana_cost

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

    """
    def build(self):
        # Function to build the card row ui

        # -----------------------------
        # Card Name Section
        # -----------------------------
        frame_color = get_card_color(self.identity)

        name_frame = tk.Frame(
            self,
            bg=frame_color,
            width=360      # Adjust this to taste
        )

        name_frame.pack(
            side="left",
            padx=(0, 5)
        )

        # Keep the frame this width regardless of contents
        name_frame.pack_propagate(False)

        # Middle column grows/shrinks
        name_frame.grid_columnconfigure(1, weight=1)

        rarity = rarity_symbol(self.rarity)

        # -----------------------------
        # Rarity
        # -----------------------------

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

        # -----------------------------
        # Name
        # -----------------------------

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

        # -----------------------------
        # Mana Cost
        # -----------------------------

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

        # Keep references to images
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

        # Winrate Text
        wr_text = "---" if "nan" in str(self.wr).lower() else f"{self.wr:.1%}"
        tk.Label(
            self,
            text=wr_text,
            width=10,
            bg=GRADE_COLOR_MAP[self.grade],
            fg="black",
            font=("Segoe UI", 11),
            pady=4
        ).pack(
            side="left",
            padx=5
        )

        # Grade Text
        tk.Label(
            self,
            text=self.grade,
            width=5,
            bg=GRADE_COLOR_MAP[self.grade],
            fg="black",
            font=("Segoe UI", 11),
            pady=4
        ).pack(
            side="left"
        )

        # Picked Label
        tk.Label(
            self,
            text="★" if self.picked else "",
            fg="#FFD700",
            bg="#1e1e1e",
            width=2,
            font=("Segoe UI", 12, "bold"),
            pady=4
        ).pack(
            side="left"
        )
    """