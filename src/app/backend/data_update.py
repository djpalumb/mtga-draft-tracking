import pandas as pd
import os
from src.utils.pull_17lands_data import pull_cards_wr_table, pull_all_cardlist, get_cards_data_as_of
from datetime import datetime
import re
import tkinter as tk
import time

def pull_cards_data():
    today = datetime.now().strftime("%Y-%m-%d")
    success = pull_all_cardlist(os.path.join('data', f'all-cards-{today}.csv'))
    return success


def pull_cards_winrate(set_abv):
    success = pull_cards_wr_table(
        expansion=set_abv,
        output_name=f'card-ratings-{set_abv.replace(' ','+')}-{datetime.now().strftime("%Y-%m-%d")}.csv'
    )
    return success


class UpdateDataPage(tk.Frame):

    def __init__(self, parent, show_menu):
        super().__init__(parent)

        self.show_menu = show_menu

        self.pack(fill="both", expand=True)

        self.build_ui()


    def build_ui(self):

        title = tk.Label(
            self,
            text="Update Data",
            font=("Arial", 18)
        )
        title.pack(pady=20)


        #
        # Card Data Section
        #

        card_frame = tk.LabelFrame(
            self,
            text="Card Data",
            padx=10,
            pady=10
        )

        card_frame.pack(
            fill="x",
            padx=20,
            pady=10
        )


        tk.Label(
            card_frame,
            text="Current data date:"
        ).grid(row=0, column=0, sticky="w")


        self.card_date_entry = tk.Entry(
            card_frame,
            width=25
        )
        self.card_date_entry.grid(
            row=0,
            column=1,
            padx=5
        )


        # Populate current values
        current = get_cards_data_as_of()

        if current:
            self.card_date_entry.insert(
                0,
                current["date"]
            )


        tk.Button(
            card_frame,
            text="Update Cards Data",
            command=self.update_cards
        ).grid(
            row=2,
            column=0,
            columnspan=2,
            pady=10
        )


        #
        # Winrate Data Section
        #

        wr_frame = tk.LabelFrame(
            self,
            text="Winrate Data",
            padx=10,
            pady=10
        )

        wr_frame.pack(
            fill="x",
            padx=20,
            pady=10
        )


        tk.Label(
            wr_frame,
            text="Set:"
        ).grid(row=0, column=0)


        self.wr_set_entry = tk.Entry(
            wr_frame,
            width=25
        )

        self.wr_set_entry.grid(
            row=0,
            column=1,
            padx=5
        )


        tk.Button(
            wr_frame,
            text="Update Winrate Data",
            command=self.update_winrates
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            pady=10
        )

        # Status message
        self.status_label = tk.Label(
            self,
            text="",
            font=("Arial", 10)
        )
        self.status_label.pack(pady=5)


        tk.Button(
            self,
            text="Back",
            command=self.show_menu
        ).pack(pady=20)


    def update_cards(self):
        """
        Hook for your backend function.
        """
        print(
            f"Updating all-card data"
        )

        self.status_label.config(
            text="Fetching and downloading, please wait up to 30 sec ..."
        )

        success = pull_cards_data()

        if success:
            self.status_label.config(
                text="✓ Card data updated successfully"
            )
        else:
            self.status_label.config(
                text="✗ Fetch or Download Failed"
            )


    def update_winrates(self):
        set_name = self.wr_set_entry.get()

        print(
            f"Updating winrate data for {set_name}"
        )

        self.status_label.config(
            text="Fetching and downloading, please wait up to 30 sec ..."
        )

        success = pull_cards_winrate(set_name)

        if success:
            self.status_label.config(
                text="✓ Winrate data updated successfully"
            )
        else:
            self.status_label.config(
                text="✗ Could not find set or update failed"
            )