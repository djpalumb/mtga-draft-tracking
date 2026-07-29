import tkinter as tk
import pandas as pd
import os

from src.utils.winrates import (
    get_cards_winrate_by_id,
    get_winrate_grade_cutoffs,
    CARD_WINRATE_FILEPATH_MSH,
)
from src.utils.pull_17lands_data import get_cards_data_as_of
from src.utils.logfile_parser import parse_through_draft_logs

# ------------------------------------------------------------------
# Hardcoded testing logfile
# ------------------------------------------------------------------
TEST_LOG = os.path.join("test_files", "sample_draft_logs.txt")


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
    "S": "#FFD700",
    "A": "#6FA36B",
    "B": "#6FA8DC",
    "C": "#D8C48A",
    "D": "#C96B5B",
    "F": "#6B5B73",
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


class DraftViewerApp(tk.Frame):
    def __init__(self, parent, show_menu):
        super().__init__(parent)

        self.pack(fill="both", expand=True, padx=10, pady=10)
        self.show_menu = show_menu

        self.grade_cutoffs = get_winrate_grade_cutoffs(
            CARD_WINRATE_FILEPATH_MSH
        )

        all_cards_filepath = get_cards_data_as_of()["filepath"]
        self.cards_filepath = all_cards_filepath

        # ---------------------------------------------------------
        # Parse draft log for existing draft
        # ---------------------------------------------------------
        with open(TEST_LOG, "r", encoding="utf-8") as f:
            logfile_lines = f.readlines()

        self.draft = parse_through_draft_logs(logfile_lines)

        if self.draft is None:
            self.indices = []
        else:
            self.indices = sorted(self.draft.seen.keys())

        if len(self.indices) == 0:
            self.current_index = None
        else:
            # Start on latest seen
            self.current_index = len(self.indices) - 1

        self.refresh()

    # ==============================================================
    # Navigation
    # ==============================================================

    def prev_pick(self):
        if self.current_index is None:
            return

        if self.current_index > 0:
            self.current_index -= 1
            self.refresh()

    def next_pick(self):
        if self.current_index is None:
            return

        if self.current_index < len(self.indices) - 1:
            self.current_index += 1
            self.refresh()

    # ==============================================================
    # Refresh
    # ==============================================================
    def refresh(self):

        for widget in self.winfo_children():
            widget.destroy()

        if self.current_index is None:
            tk.Label(
                self,
                text="No draft found."
            ).pack()

            tk.Button(
                self,
                text="Back",
                command=self.show_menu
            ).pack(pady=20)

            return

        pack, pick = self.indices[self.current_index]

        seen = self.draft.get_seen(pack, pick)
        picked = self.draft.get_pick(pack, pick)
        missing = self.draft.get_known_missing(pack, pick)

        # -----------------------------
        # Header
        # -----------------------------

        tk.Label(
            self,
            text="MTG Draft Viewer",
            font=("Arial", 18, "bold")
        ).pack(pady=(0, 5))

        tk.Label(
            self,
            text=f"Pack {pack}   Pick {pick}",
            font=("Arial", 14)
        ).pack(pady=(0, 10))

        # -----------------------------
        # Navigation
        # -----------------------------

        nav = tk.Frame(self)
        nav.pack(pady=10)

        tk.Button(
            nav,
            text="< Previous",
            command=self.prev_pick,
            state=(
                "normal"
                if self.current_index > 0
                else "disabled"
            )
        ).pack(side="left", padx=5)

        tk.Button(
            nav,
            text="Next >",
            command=self.next_pick,
            state=(
                "normal"
                if self.current_index < len(self.indices)-1
                else "disabled"
            )
        ).pack(side="left", padx=5)

        tk.Button(
            self,
            text="Back To Main Menu",
            command=self.show_menu
        ).pack(pady=20)


        # -----------------------------
        # Current Pack
        # -----------------------------

        tk.Label(
            self,
            text="Cards Currently In Pack",
            font=("Arial", 13, "bold")
        ).pack(anchor="w")

        tk.Frame(
            self,
            height=2,
            bg="black"
        ).pack(fill="x", pady=(0, 5))


        df = get_cards_winrate_by_id(
            card_ids=seen,
            card_ids_ref_filepath=self.cards_filepath
        )

        df = df.sort_values(
            "GIH WR",
            ascending=False,
            ignore_index=True
        )

        for _, row in df.iterrows():

            grade = get_winrate_grade(
                row["GIH WR"],
                self.grade_cutoffs
            )

            card_id = row["id"]

            selected = False

            if picked is not None:
                if isinstance(picked, list):
                    selected = card_id in picked
                else:
                    selected = card_id == picked

            self.add_card(
                row["name"],
                row["GIH WR"],
                row["color_identity"],
                grade,
                picked=selected
            )


        # -----------------------------
        # Known Missing
        # -----------------------------

        if len(missing) > 0:

            tk.Label(
                self,
                text="Known Missing (Taken Since Last Seen)",
                font=("Arial", 13, "bold")
            ).pack(anchor="w", pady=(15, 0))

            tk.Frame(
                self,
                height=2,
                bg="black"
            ).pack(fill="x", pady=(0, 5))


            missing_df = get_cards_winrate_by_id(
                card_ids=missing,
                card_ids_ref_filepath=self.cards_filepath
            )

            missing_df = missing_df.sort_values(
                "GIH WR",
                ascending=False,
                ignore_index=True
            )


            for _, row in missing_df.iterrows():

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

    # ==============================================================
    # Card row
    # ==============================================================

    def add_card(
        self,
        name,
        winrate,
        identity,
        grade,
        picked=False,
    ):

        if picked:
            outer = tk.Frame(
                self,
                bg="black",
                padx=2,
                pady=2
            )
            outer.pack(fill="x", pady=3)

            row = tk.Frame(outer)
            row.pack(fill="x")

        else:
            row = tk.Frame(self)
            row.pack(fill="x", pady=3)


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

        if 'nan' in str(winrate):
            wr_box = tk.Label(
                row,
                text=f"--",
                bg=GRADE_COLOR_MAP[grade],
                width=8,
                relief="solid",
                borderwidth=1
            )
        else:
            wr_box = tk.Label(
                row,
                text=f"{winrate:.1%}",
                bg=GRADE_COLOR_MAP[grade],
                width=8,
                relief="solid",
                borderwidth=1
            )

        wr_box.pack(side="left", padx=5)


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
    root.title("Draft Viewer")

    app = DraftViewerApp(root, lambda: None)

    root.mainloop()