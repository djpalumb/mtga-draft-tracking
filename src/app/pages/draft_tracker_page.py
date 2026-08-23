import tkinter as tk
from tkinter import ttk
import os

from src.utils.winrates import (
    get_cards_winrate_by_id,
    get_winrate_grade_cutoffs
)
from src.utils.pull_17lands_data import (
    get_most_recent_winrate_files,
    get_cards_data_as_of
)
from src.utils.read_local_card_data import (
    get_local_cards_data_as_of
)
from src.utils.pull_scryfall import(
    get_scryfall_data_as_of,
    get_card_mana_costs
)
from src.utils.logfile_parser import (
    parse_through_draft_logs,
    DraftLogListener
)
from src.app.components import (
    card_row
)

LOGFILE_PATH = os.path.join(
    os.path.expanduser("~"),
    "AppData",
    "LocalLow",
    "Wizards Of The Coast",
    "MTGA",
    "Player.log"
)
TEST_LOGFILE_PATH = os.path.join('test_files','sample_draft_logs.log')


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
    """Main draft tracking interface for MTGA.

    Monitors the MTGA Player.log file for draft events,
    determines the current pack/pick state, and displays
    card recommendations using 17Lands winrate data and
    Scryfall metadata.
    """
    def __init__(
        self, 
        parent, 
        show_menu,
        test_mode: bool = False
    ):
        super().__init__(parent)
        self.show_menu = show_menu
        self.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        self.test_mode = test_mode
        self.logfile_path = TEST_LOGFILE_PATH if self.test_mode else LOGFILE_PATH

        # Get Cards
        try:
            self.cards_filepath = get_local_cards_data_as_of()["filepath"]
        except Exception as e:
            self.cards_filepath = None

        # Get scryfall info
        try:
            self.scryfall_filepath = get_scryfall_data_as_of()["filepath"]
        except Exception as e:
            self.scryfall_filepath = None

        self.init_draft_info()

        # Build panel
        self.refresh()
        
        # Setup listener
        self.listener = DraftLogListener(
            self.logfile_path,
            self.draft,
        )
        self.listener_running = True

        self.after(250, self.check_log_updates)


    def set_card_winrate_info(self):
        try:
            self.card_winrate_file = get_most_recent_winrate_files()[self.draft_expansion]

            # Get cutoffs
            self.grade_cutoffs = get_winrate_grade_cutoffs(
                self.card_winrate_file
            )
        except Exception as e:
            self.card_winrate_file = None
            self.grade_cutoffs = None


    def init_draft_info(self):
        # Parse latest draft
        with open(self.logfile_path, "r",encoding="utf-8") as f:
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
            max(len(self.indices) - 1, 0)
            if self.indices
            else None
        )

        # Get set information
        if self.draft is None:
            self.draft_expansion = None
            self.card_winrate_file = None
        else:
            self.draft_expansion = self.draft.expansion

            if self.draft_expansion is None:
                self.card_winrate_file = None
            else:
                self.set_card_winrate_info()

    def check_log_updates(self):
        # Page has been destroyed
        if not self.listener_running:
            return

        changed = self.listener.poll()
        if changed:
            # Check if we are on the last index
            if self.current_index is not None and self.current_index >= len(self.indices) - 1:
                on_last_pack = True
            else:
                on_last_pack = False

            # Update draft
            self.draft = self.listener.draft

            # Check if the expansion changed
            if self.draft_expansion != self.draft.expansion:
                self.draft_expansion = self.draft.expansion
                self.set_card_winrate_info()

            self.indices = (
                sorted(self.draft.seen.keys())
                if self.draft
                else []
            )

            # If we were on the last index before, keep us on the last (now different pack)
            if on_last_pack:
                self.current_index = max(len(self.indices) - 1, 0)
            elif (
                # If we're past the end (e.g. a new draft started), jump to the newest pick.
                self.current_index is None
                or self.current_index >= len(self.indices)
            ):
                self.current_index = max(len(self.indices) - 1, 0)

            self.refresh()

        self.after(250, self.check_log_updates)

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

    # Skip ahead to current (last) pick
    def current_pick(self):
        if self.indices:
            self.current_index = len(self.indices) - 1
            self.refresh()

    def back(self):
        # Go back to menu
        self.listener_running = False
        self.listener.close()

        self.show_menu()

    def destroy(self):
        # On application end, cleanup listener
        self.listener_running = False
        if hasattr(self, "listener"):
            self.listener.close()
        super().destroy()

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
        elif self.draft_expansion is None:
            ttk.Label(
                self,
                text="Unable to determine draft expansion set",
                style="TLabel"
            ).pack(pady=30)

            ttk.Button(
                self,
                text="Back",
                command=self.show_menu
            ).pack()

            return
        elif self.card_winrate_file is None:
            ttk.Label(
                self,
                text=f"No card winrate file found for draft expansion: {self.draft_expansion}",
                style="TLabel"
            ).pack(pady=30)

            ttk.Button(
                self,
                text="Back",
                command=self.show_menu
            ).pack()

            return
        elif self.cards_filepath is None:
            ttk.Label(
                self,
                text="Unable to find card reference file, please download on other page.",
                style="TLabel"
            ).pack(pady=30)

            ttk.Button(
                self,
                text="Back",
                command=self.show_menu
            ).pack()

            return
        elif self.current_index >= len(self.indices):
            if len(self.indices) == 0:
                ttk.Label(
                self,
                    text="Waiting for draft to start",
                    style="TLabel"
                ).pack(pady=30)
    
                ttk.Button(
                    self,
                    text="Back",
                    command=self.show_menu
                ).pack()

                return
            else:
                self.current_index = len(self.indices) - 1

        ########################################
        ## Panel Info
        ########################################

        current_pack, current_pick = self.indices[self.current_index]
        latest_pack, latest_pick = self.indices[-1]
        
        ttk.Label(
            self,
            text="Draft Viewer",
            style="Title.TLabel"
        ).pack(
            anchor="c"
        )

        ttk.Label(
            self,
            text=(
                f"Set: {self.draft_expansion}"
                f"    |    "
                f"Viewing: Pack {current_pack} • Pick {current_pick}"
                f"    |    "
                f"Current: Pack {latest_pack} • Pick {latest_pick}"
            ),
        ).pack(
            anchor="c",
            pady=0,
        )

        nav = ttk.Frame(self)
        nav.pack(
            pady=10
        )

        ########################################
        ## Navigation
        ########################################

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

        state = (
            "disabled"
            if self.current_index == len(self.indices) - 1
            else "normal"
        )

        ttk.Button(
            nav,
            text="Go to Current",
            command=self.current_pick,
            state=state,
        ).pack(
            side="left",
            padx=5,
            pady=10
        )

        ########################################
        ## Pack Cards
        ########################################

        seen = self.draft.get_seen(current_pack, current_pick)
        picked = self.draft.get_pick(current_pack, current_pick)
        missing = self.draft.get_known_missing(
            current_pack,
            current_pick
        )

        # Get card winrates and mana costs
        df = get_cards_winrate_by_id(
            seen,
            card_ids_ref_filepath=self.cards_filepath,
            card_winrate_ref_filepath=self.card_winrate_file
        )
        df = df.sort_values(
            "GIH WR",
            ascending=False
        )

        cost_df = get_card_mana_costs(
            df['name'].to_list(),
            scryfall_data_filepath=self.scryfall_filepath
        )[['name', 'mana_cost']]

        df = df.merge(
            cost_df,
            on='name',
            how='left'
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
                row["rarity"],
                selected,
                row["mana_cost"]
            )

        ########################################
        ## Known Missing Cards
        ########################################

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
                card_ids_ref_filepath=self.cards_filepath,
                card_winrate_ref_filepath=self.card_winrate_file
            )
            missing_df = missing_df.sort_values(
                "GIH WR",
                ascending=False,
                ignore_index=True
            )

            missing_cost_df = get_card_mana_costs(
                missing_df['name'].to_list(),
                scryfall_data_filepath=self.scryfall_filepath
            )[['name', 'mana_cost']]
    
            missing_df = missing_df.merge(
                missing_cost_df,
                on='name',
                how='left'
            )

            for _, row in missing_df.iterrows():
                grade = get_winrate_grade(
                    row["GIH WR"],
                    self.grade_cutoffs
                )

                self.card_row(
                    frame,
                    row["name"],
                    row["GIH WR"],
                    row["color_identity"],
                    grade,
                    row["rarity"],
                    False,
                    row["mana_cost"]
                )

        ########################################
        ## Menu Button
        ########################################

        ttk.Button(
            self,
            text="Back",
            command=self.back
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
        rarity,
        picked,
        mana_cost
    ):

        row = card_row.CardRow(
            parent,
            name,
            wr,
            identity,
            grade,
            rarity,
            picked,
            mana_cost
        )
        row.pack(fill="x", pady=1)