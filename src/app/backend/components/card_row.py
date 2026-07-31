import tkinter as tk
from tkinter import ttk
import os

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
class CardRow(tk.Frame):
    def __init__(
        self,
        parent,
        name,
        wr,
        identity,
        grade,
        rarity,
        picked
    ):
        super().__init__(parent, bg="#1e1e1e")
        self.name = name
        self.wr = wr
        self.identity = identity
        self.grade = grade
        self.picked = picked
        self.rarity = rarity

        self.build()

    def build(self):
        # Function to build the card row ui

        # Frame for rarity symbol plus card name
        name_frame = tk.Frame(
            self,
            bg=get_card_color(self.identity)
        )
        name_frame.pack(side="left", padx=(0, 5))

        rarity = rarity_symbol(self.rarity)

        tk.Label(
            name_frame,
            text="◆",
            fg=rarity["color"],
            bg=get_card_color(self.identity),
            font=("Segoe UI Symbol", 12, "bold"),
        ).pack(side="left", padx=(6, 2), pady=4)

        tk.Label(
            name_frame,
            text=self.name,
            fg="black",
            bg=get_card_color(self.identity),
            width=33,
            anchor="w",
            font=("Segoe UI", 11),
        ).pack(side="left", padx=(0, 8), pady=4)

        # Winrate Text
        wr_text = "---" if "nan" in str(self.wr) else f"{self.wr:.1%}"
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