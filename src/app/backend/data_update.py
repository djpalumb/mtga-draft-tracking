import tkinter as tk
from tkinter import ttk
import os

from datetime import datetime

from src.utils.pull_17lands_data import (
    pull_cards_wr_table,
    pull_all_cardlist,
    get_cards_data_as_of,
    get_most_recent_winrate_files
)


def pull_cards_data():
    today = datetime.now().strftime("%Y-%m-%d")
    return pull_all_cardlist(
        os.path.join(
            "data",
            f"all-cards-{today}.csv"
        )
    )


def pull_cards_winrate(set_abv):
    return pull_cards_wr_table(
        expansion=set_abv,
        output_name=(
            f"card-ratings-{set_abv.replace(' ','+')}-{datetime.now().strftime('%Y-%m-%d')}.csv"
        )
    )


class UpdateDataPage(ttk.Frame):
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
        box = ttk.LabelFrame(
            self,
            text=" Card Data ",
            padding=15
        )
        box.pack(
            fill="x",
            pady=10
        )

        ttk.Label(
            box,
            text="Current data:"
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
            padx=10
        )

        current = get_cards_data_as_of()

        if current:
            self.card_date_label.config(
                text=current["date"]
            )

        self.update_card_data_button = ttk.Button(
            box,
            text="Update Cards",
            command=self.update_cards
        )
        self.update_card_data_button.grid(
            row=1,
            column=0,
            columnspan=2,
            pady=15
        )

    def build_winrate_section(self):
        box = ttk.LabelFrame(
            self,
            text=" Winrate Data ",
            padding=15
        )
        box.pack(
            fill="x",
            pady=10
        )

        ttk.Label(
            box,
            text="Set:"
        ).grid(
            row=0,
            column=0
        )
        self.wr_set_entry = ttk.Entry(box)
        self.wr_set_entry.grid(
            row=0,
            column=1,
            padx=10
        )

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
            height=6
        )

        self.wr_table.heading("set", text="Set")
        self.wr_table.heading("date", text="Downloaded")

        self.wr_table.column("set", width=80, anchor="center")
        self.wr_table.column("date", width=120, anchor="center")

        self.refresh_winrate_table()

        self.wr_table.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=10,
            pady=(15, 0)
        )

        self.update_wr_button = ttk.Button(
            box,
            text="Update Winrates",
            command=self.update_winrates
        )

        self.update_wr_button.grid(
            row=2,
            column=0,
            columnspan=2,
            pady=15
        )

    def update_cards(self):
        self.status_label.config(
            text="Downloading card data..."
        )

        self.update_card_data_button.config(
            text="Downloading...",
            state="disabled"
        )
        self.update_idletasks() 

        success = pull_cards_data()

        date = get_cards_data_as_of()
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
            text="Update Cards",
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