import tkinter as tk
from tkinter import ttk
import pandas as pd
from src.utils.winrates import get_cards_winrate_by_id, get_winrate_grade_cutoffs, CARD_WINRATE_FILEPATH_MSH
import os
import re

test_log = os.path.join('test_files', 'sample_draft_logs.txt')
with open(test_log, 'r') as f:
    text = f.read()

matches = re.findall(r'"PackCards":"(.*)"\}', text)
first_pack = [int(x) for x in matches[0].split(',')]


COLOR_MAP = {
    "U": "#6FA8DC",  # deeper muted blue
    "W": "#D8C48A",  # parchment gold
    "B": "#6B5B73",  # dark muted purple/black
    "G": "#6FA36B",  # forest green
    "R": "#C96B5B",  # muted red
    "": "#9E9E9E",   # darker neutral gray
}

MULTICOLOR = "#C9A227"  # richer gold

GRADE_COLOR_MAP = {
    "S": "#FFD700",
    "A": "#6FA36B",
    "B": "#6FA8DC",
    "C": "#D8C48A",
    "D": "#C96B5B",
    "F": "#6B5B73",
}

def get_card_color(identity):
    """
    Determine background color based on MTG color identity.
    """
    if identity is None or identity == "" or not isinstance(identity, str):
        return COLOR_MAP[""]

    # Multicolor
    if len(identity) > 1:
        return MULTICOLOR

    return COLOR_MAP.get(identity, "#FFFFFF")

def get_winrate_grade(winrate, cutoffs):
    if winrate >= cutoffs["S"]:
        return "S"
    elif winrate >= cutoffs["A"]:
        return "A"
    elif winrate >= cutoffs["B"]:
        return "B"
    elif winrate >= cutoffs["C"]:
        return "C"
    elif winrate >= cutoffs["D"]:
        return "D"
    else:
        return "F"


class RankedCardsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MTGA Ranked Cards")
        self.root.geometry("500x600")

        self.frame = tk.Frame(root)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Get grade cutoffs
        self.grade_cutoffs = get_winrate_grade_cutoffs(
            CARD_WINRATE_FILEPATH_MSH
        )

        self.refresh()

    def refresh(self):
        # Clear existing cards
        for widget in self.frame.winfo_children():
            widget.destroy()

        df = get_cards_winrate_by_id(first_pack)

        # Sort by win rate
        df = df.sort_values("GIH WR", ascending=False, ignore_index=True)

        for _, row in df.iterrows():
            grade = get_winrate_grade(
                row["GIH WR"],
                self.grade_cutoffs
            )

            self.add_card(
                row["name"],
                row["GIH WR"],
                row["color_identity"],
                grade
            )

    def add_card(self, name, winrate, identity, grade):
        row = tk.Frame(self.frame)
        row.pack(fill="x", pady=3)

        # Card name box
        name_box = tk.Label(
            row,
            text=name,
            bg=get_card_color(identity),
            width=35,
            anchor="w",
            padx=5,
            relief="solid",
            borderwidth=1
        )
        name_box.pack(side="left")

        # Win rate box
        wr_box = tk.Label(
            row,
            text=f"{winrate:.1%}",
            bg=GRADE_COLOR_MAP[grade],
            width=8,
            relief="solid",
            borderwidth=1
        )
        wr_box.pack(side="left", padx=5)

        # Grade box
        grade_box = tk.Label(
            row,
            text=grade,
            bg=GRADE_COLOR_MAP[grade],
            width=4,
            relief="solid",
            borderwidth=1
        )
        grade_box.pack(side="left")


if __name__ == "__main__":
    root = tk.Tk()
    app = RankedCardsApp(root)
    root.mainloop()