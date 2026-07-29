import tkinter as tk
from tkinter import ttk
import os

from src.utils.winrates import (
    get_cards_winrate_by_id,
    get_winrate_grade_cutoffs,
    CARD_WINRATE_FILEPATH_MSH,
)

from src.utils.pull_17lands_data import get_cards_data_as_of
from src.utils.logfile_parser import parse_through_draft_logs
LOGFILE_PATH = os.path.join(
    os.path.expanduser("~"),
    "AppData",
    "LocalLow",
    "Wizards Of The Coast",
    "MTGA",
    "Player.log"
)
# LOGFILE_PATH = 'test_files\\sample_draft_logs.txt'
# TODO: remove test logfile path

COLOR_MAP = {
    "U": "#6FA8DC",
    "W": "#D8C48A",
    "B": "#6B5B73",
    "G": "#6FA36B",
    "R": "#C96B5B",
    "": "#9E9E9E",
}
MULTICOLOR = "#C9A227"

GRADE_COLOR_MAP = {
    "S": "#C35BC7",
    "A": "#6FBF73",
    "B": "#56A3D9",
    "C": "#D2B35A",
    "D": "#D18B5C",
    "F": "#C66A6A",
}

def get_card_color(identity):
    if identity is None or identity == "" or not isinstance(identity, str):
        return COLOR_MAP[""]

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
    

class DraftViewerApp(ttk.Frame):

    def __init__(self, parent, show_menu):
        super().__init__(parent)
        self.show_menu = show_menu
        self.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        # Get cutoffs
        self.grade_cutoffs = get_winrate_grade_cutoffs(
            CARD_WINRATE_FILEPATH_MSH
        )
        self.cards_filepath = get_cards_data_as_of()["filepath"]

        # Parse latest draft
        with open(LOGFILE_PATH, "r",encoding="utf-8") as f:
            logs = f.readlines()
        self.draft = parse_through_draft_logs(logs)


        # Get all of the draft picks numbers in order
        self.indices = (
            sorted(self.draft.seen.keys())
            if self.draft
            else []
        )

        # Get the current ind
        self.current_index = (
            len(self.indices)-1
            if self.indices
            else None
        )

        # Build panel
        self.refresh()


    # Function to display previous pick from what is currently showing
    def prev_pick(self):
        if self.current_index and self.current_index > 0:
            self.current_index -= 1
            self.refresh()

    # Function to display next pick from what is currently showing
    def next_pick(self):
        if (
            self.current_index is not None
            and self.current_index < len(self.indices)-1
        ):
            self.current_index += 1
            self.refresh()


    # Function to build page
    def refresh(self):
        for w in self.winfo_children():
            w.destroy()

        if self.current_index is None:
            ttk.Label(
                self,
                text="No draft found",
                style="Title.TLabel"
            ).pack(pady=30)

            ttk.Button(
                self,
                text="Back",
                command=self.show_menu
            ).pack()

            return

        pack, pick = self.indices[self.current_index]

        ttk.Label(
            self,
            text="Draft Viewer",
            style="Title.TLabel"
        ).pack(
            anchor="c"
        )

        ttk.Label(
            self,
            text=f"Pack {pack} • Pick {pick}"
        ).pack(
            anchor="c",
            pady=0
        )

        nav = ttk.Frame(self)
        nav.pack(
            pady=10
        )

        ttk.Button(
            nav,
            text="← Previous",
            command=self.prev_pick
        ).pack(
            side="left",
            padx=5,
            pady=10
        )

        ttk.Button(
            nav,
            text="Next →",
            command=self.next_pick
        ).pack(
            side="left",
            padx=5,
            pady=10
        )

        seen = self.draft.get_seen(pack,pick)
        picked = self.draft.get_pick(pack,pick)
        missing = self.draft.get_known_missing(
            pack,
            pick
        )

        df = get_cards_winrate_by_id(
            seen,
            self.cards_filepath
        )

        df = df.sort_values(
            "GIH WR",
            ascending=False
        )

        self.scroll = tk.Canvas(
            self,
            highlightthickness=0,
            bg="#1e1e1e"
        )
        self.scroll.pack(
            fill="both",
            expand=True
        )
        frame = ttk.Frame(
            self.scroll,
            style="TFrame"
        )
        self.scroll.bind(
            "<Configure>",
            lambda e: self.scroll.itemconfig(
                self.scroll_window,
                width=e.width
            )
        )
        self.scroll_window = self.scroll.create_window(
            (0,0),
            window=frame,
            anchor="nw"
        )

        for i, row in df.iterrows():
            grade = get_winrate_grade(
                row["GIH WR"],
                self.grade_cutoffs
            )

            if picked is not None:
                if isinstance(picked, list):
                    selected = row["id"] in picked
                else:
                    selected = row["id"] == picked
            else:
                selected = False

            self.card_row(
                frame,
                row["name"],
                row["GIH WR"],
                row["color_identity"],
                grade,
                selected
            )

        if missing:
            ttk.Label(
                frame,
                text="Known Missing (Taken Since Last Seen)",
                style="Subtitle.TLabel"
            ).pack(
                anchor="w",
                pady=(20,10)
            )

            missing_df = get_cards_winrate_by_id(
                missing,
                self.cards_filepath
            )
            missing_df = missing_df.sort_values(
                "GIH WR",
                ascending=False,
                ignore_index=True
            )

            for _, row in missing_df.iterrows():

                self.card_row(
                    frame,
                    row["name"],
                    row["GIH WR"],
                    row["color_identity"],
                    grade,
                    False
                )
        
        ttk.Button(
            self,
            text="Back",
            command=self.show_menu
        ).pack(
            pady=5
        )


    def card_row(
        self,
        parent,
        name,
        wr,
        identity,
        grade,
        picked
    ):

        row = tk.Frame(
            parent,
            bg="#1e1e1e"
        )
        row.pack(
            fill="x",
            pady=3
        )

        tk.Label(
            row,
            text=name,
            bg=get_card_color(identity),
            fg="black",
            width=35,
            anchor="w",
            padx=8
        ).pack(
            side="left",
            padx=(0,5)
        )

        if 'nan' in str(wr):
            tk.Label(
                row,
                text=f"---",
                width=10,
                bg=GRADE_COLOR_MAP[grade],
                fg="black"
            ).pack(
                side="left",
                padx=5
            )

        else:
            tk.Label(
                row,
                text=f"{wr:.1%}",
                width=10,
                bg=GRADE_COLOR_MAP[grade],
                fg="black"
            ).pack(
                side="left",
                padx=5
            )

        tk.Label(
            row,
            text=grade,
            width=5,
            bg=GRADE_COLOR_MAP[grade],
            fg="black"
        ).pack(
            side="left"
        )
        
        if picked:
            tk.Label(
                row,
                text="★",
                fg="#FFD700",
                bg="#1e1e1e",
                width=2,
                font=("Segoe UI", 12, "bold")
            ).pack(
                side="left"
            )
        else:
            tk.Label(
                row,
                text="",
                width=2,
                bg="#1e1e1e"
            ).pack(
                side="left"
            )
