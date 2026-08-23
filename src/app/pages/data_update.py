import tkinter as tk
from tkinter import ttk
import os
from datetime import datetime

from src.utils.pull_17lands_data import (
    pull_cards_wr_table,
    pull_all_cardlist,
    get_most_recent_winrate_files,
    get_cards_data_as_of
)
from src.utils.pull_scryfall import (
    get_scryfall_info,
    get_scryfall_data_as_of
)
from src.utils.read_local_card_data import (
    get_local_cards_data_as_of,
    export_arena_cards
)


# This has been phased out in favor of local card database as it updates quicker
def pull_cards_data():
    """Download the latest 17Lands card ID data and save locally."""
    today = datetime.now().strftime("%Y-%m-%d")
    return pull_all_cardlist(
        os.path.join(
            "data",
            f"all-cards-{today}.csv"
        )
    )
# Newer card database setup
def pull_local_cards_data():
    """Use local SQLite file to get card mappings"""
    today = datetime.now().strftime("%Y-%m-%d")
    return export_arena_cards(
        os.path.join(
            'data',
            f'arena-cards-{today}.csv'
        )
    )


def pull_scryfall_data():
    """Download the latest Scryfall card metadata and save locally."""
    today = datetime.now().strftime("%Y-%m-%d")
    return get_scryfall_info(
        os.path.join(
            "data",
            f"scryfall-cards-{today}.csv"
        )
    )

def pull_cards_winrate(set_abv):
    """Download card winrate data for a specific MTGA set."""
    return pull_cards_wr_table(
        expansion=set_abv,
        output_name=(
            f"card-ratings-{set_abv.replace(' ','+')}-{datetime.now().strftime('%Y-%m-%d')}.csv"
        )
    )


class UpdateDataPage(ttk.Frame):
    """GUI page for downloading and managing external card data.

    Provides controls for updating:
    - 17Lands card identifiers
    - Scryfall card metadata
    - 17Lands winrate tables
    """
    def __init__(self, parent, show_menu):
        super().__init__(parent)
        self.show_menu = show_menu
        self.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=25
        )
        self.build_ui()


    def refresh_winrate_table(self):
        """Refresh displayed winrate files from local storage."""
        # Clear existing rows
        for item in self.wr_table.get_children():
            self.wr_table.delete(item)

        files = get_most_recent_winrate_files()

        for set_name in sorted(files):
            path = files[set_name]
            date = path.stem.rsplit("-", 3)[-3:]
            date = "-".join(date)
            self.wr_table.insert("", "end", values=(set_name, date))

    def build_ui(self):
        """Construct all widgets on the update page."""
        ttk.Label(
            self,
            text="Update Data",
            style="Title.TLabel"
        ).pack(
            anchor="w",
            pady=(0,25)
        )

        self.build_card_section()
        self.build_winrate_section()

        self.status_label = ttk.Label(
            self,
            text=""
        )

        self.status_label.pack(
            pady=15
        )

        ttk.Button(
            self,
            text="← Back",
            command=self.show_menu
        ).pack()


    def build_card_section(self):
        """UI Section where user downloads card information"""
        box = ttk.LabelFrame(
            self,
            text=" Card Data ",
            padding=15
        )
        box.pack(
            fill="x",
            pady=10
        )

        # -----------------------
        # Current Arena card data
        # -----------------------

        ttk.Label(
            box,
            text="Current Card Mapping As Of:"
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        self.card_date_label = ttk.Label(
            box,
            text=""
        )
        self.card_date_label.grid(
            row=0,
            column=1,
            padx=(10, 20),
            sticky="w"
        )

        current = get_local_cards_data_as_of()

        if current:
            self.card_date_label.config(
                text=current["date"]
            )

        self.update_card_data_button = ttk.Button(
            box,
            text="Update Card Mapping",
            command=self.update_cards
        )
        self.update_card_data_button.grid(
            row=0,
            column=2,
            padx=(0, 5)
        )

        # -----------------------
        # Scryfall data
        # -----------------------

        ttk.Label(
            box,
            text="Current Scryfall Card Data:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=(10, 0)
        )

        self.scryfall_date_label = ttk.Label(
            box,
            text=""
        )
        self.scryfall_date_label.grid(
            row=1,
            column=1,
            padx=(10, 20),
            sticky="w",
            pady=(10, 0)
        )

        scryfall_date = get_scryfall_data_as_of()

        if scryfall_date:
            self.scryfall_date_label.config(
                text=scryfall_date["date"]
            )

        self.update_scryfall_button = ttk.Button(
            box,
            text="Update Scryfall Cards",
            command=self.update_scryfall
        )
        self.update_scryfall_button.grid(
            row=1,
            column=2,
            padx=(0, 5),
            pady=(10, 0)
        )


    def build_winrate_section(self):
        """UI Section where user downloads 17lands card winrate data"""
        box = ttk.LabelFrame(
            self,
            text=" Winrate Data ",
            padding=15
        )
        box.pack(
            fill="x",
            pady=10
        )

        # -----------------------
        # Set input
        # -----------------------

        ttk.Label(
            box,
            text="Set:"
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        self.wr_set_entry = ttk.Entry(box)
        self.wr_set_entry.grid(
            row=0,
            column=1,
            columnspan=2,
            sticky="ew",
            padx=(10, 0)
        )

        # -----------------------
        # Downloaded winrates
        # -----------------------

        ttk.Label(
            box,
            text="Downloaded:"
        ).grid(
            row=1,
            column=0,
            sticky="nw",
            pady=(15, 0)
        )

        self.wr_table = ttk.Treeview(
            box,
            columns=("set", "date"),
            show="headings",
            height=5
        )

        self.scrollbar = ttk.Scrollbar(
            box,
            orient="vertical",
            style="Modern.Vertical.TScrollbar",
            command=self.wr_table.yview
        )

        self.wr_table.configure(
            yscrollcommand=self.scrollbar.set
        )

        self.wr_table.heading(
            "set",
            text="Set"
        )
        self.wr_table.heading(
            "date",
            text="Downloaded"
        )

        self.wr_table.column(
            "set",
            width=80,
            anchor="center"
        )
        self.wr_table.column(
            "date",
            width=120,
            anchor="center"
        )

        self.refresh_winrate_table()

        self.wr_table.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=(10, 0),
            pady=(15, 0)
        )

        self.scrollbar.grid(
            row=1,
            column=2,
            sticky="ns",
            padx=(5, 0),
            pady=(15, 0)
        )

        # Allow the table to expand horizontally
        box.columnconfigure(
            1,
            weight=1
        )

        # -----------------------
        # Update button
        # -----------------------

        self.update_wr_button = ttk.Button(
            box,
            text="Update Winrates",
            command=self.update_winrates
        )

        self.update_wr_button.grid(
            row=2,
            column=0,
            columnspan=3,
            pady=(15, 0)
        )

    def update_cards(self):
        self.status_label.config(
            text="Downloading card export..."
        )

        self.update_card_data_button.config(
            text="Processing...",
            state="disabled"
        )
        self.update_idletasks() 

        success = pull_local_cards_data()

        date = get_local_cards_data_as_of()
        if 'date' in date.keys():
            self.card_date_label.config(
                text=date['date']
            )

        self.status_label.config(
            text=(
                "✓ Cards updated"
                if success
                else "✗ Update failed"
            )
        )
        self.update_card_data_button.config(
            text="Update Card Mapping",
            state="normal"
        )
        self.update_idletasks() 

    def update_scryfall(self):
        self.status_label.config(
            text="Downloading card data..."
        )

        self.update_scryfall_button.config(
            text="Downloading...",
            state="disabled"
        )
        self.update_idletasks() 

        success = pull_scryfall_data()

        date = get_scryfall_data_as_of()
        if 'date' in date.keys():
            self.scryfall_date_label.config(
                text=date['date']
            )

        self.status_label.config(
            text=(
                "✓ Cards updated"
                if success
                else "✗ Update failed"
            )
        )
        self.update_scryfall_button.config(
            text="Update Scryfall Cards",
            state="normal"
        )
        self.update_idletasks() 

    def update_winrates(self):
        print('Running update winrates...')

        set_name = self.wr_set_entry.get()

        self.status_label.config(
            text="Downloading winrates..."
        )

        self.update_wr_button.config(
            text="Downloading...",
            state="disabled"
        )
        self.update_idletasks() 

        success = pull_cards_winrate(set_name)

        self.status_label.config(
            text=(
                "✓ Winrates updated"
                if success
                else "✗ Update failed"
            )
        )

        if success:
            self.refresh_winrate_table()

        self.update_wr_button.config(
            text="Update Winrates",
            state="normal"
        )
        self.update_idletasks() 