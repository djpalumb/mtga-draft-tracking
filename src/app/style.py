import tkinter as tk
from tkinter import ttk

CARD_COLOR_MAP = {
    "U": "#5297D6",
    "W": "#BDAF91",
    "B": "#6B5B73",
    "G": "#6FA36B",
    "R": "#C96B5B",
    "":"#CAD1D1",
    "MULTICOLOR": "#B18F1E"
}

RARITY_COLOR_MAP = {
    "common": "#212121",      # black/dark gray
    "uncommon": "#B9DCEB",    # silver
    "rare": "#E6CD8C",        # gold
    "mythic": "#F54C05",      # orange
}

GRADE_COLOR_MAP = {
    "S": "#C35BC7",
    "A": "#6FBF73",
    "B": "#56A3D9",
    "C": "#D2B35A",
    "D": "#D18B5C",
    "F": "#C66A6A",
}

def configure_style(application):
    style = ttk.Style()
    style.theme_use("clam")
    bg = "#1e1e1e"
    panel = "#2a2a2a"
    text = "#eeeeee"

    application.root.configure(bg=bg)

    style.configure(
        ".",
        background=bg,
        foreground=text,
        font=("Segoe UI", 11)
    )

    style.configure(
        "TFrame",
        background=bg
    )

    style.configure(
        "Card.TFrame",
        background=panel
    )

    style.configure(
        "TLabel",
        background=bg,
        foreground=text
    )

    style.configure(
        "Title.TLabel",
        font=("Segoe UI", 22, "bold")
    )

    style.configure(
        "Subtitle.TLabel",
        font=("Segoe UI", 12)
    )

    style.configure(
        "TButton",
        padding=(12, 8),
        font=("Segoe UI", 11)
    )


    style.configure(
        "TButton",
        background="#333333",
        foreground="#eeeeee",
        padding=(12, 8),
        font=("Segoe UI", 11)
    )

    style.map(
        "TButton",
        background=[
            ("active", "#555555"),
            ("pressed", "#222222")
        ],
        foreground=[
            ("active", "#ffffff"),
            ("pressed", "#ffffff")
        ]
    )

    style.configure("Custom.TEntry", foreground="black")
    style.configure(
        "TEntry",
        fieldbackground="#333333",
        foreground="#eeeeee",
        insertcolor="#eeeeee"
    )

    style.map(
        "TEntry",
        fieldbackground=[
            ("focus", "#444444")
        ],
        foreground=[
            ("focus", "#ffffff")
        ]
    )

    style.configure(
        "Treeview",
        background="#333333",
        foreground="#eeeeee",
        fieldbackground="#333333",
        borderwidth=0,
        rowheight=24
    )

    style.map(
        "Treeview",
        background=[("selected", "#4a6984")],
        foreground=[("selected", "#ffffff")]
    )

    style.configure(
        "Treeview.Heading",
        background="#444444",
        foreground="#eeeeee",
        relief="flat",
        font=("Segoe UI", 10, "bold")
    )

    style.map(
        "Treeview.Heading",
        background=[("active", "#555555")]
    )

    style.configure(
        "TLabelframe",
        background=panel,
        foreground=text
    )

    style.configure(
        "TLabelframe.Label",
        background=panel,
        foreground=text,
        font=("Segoe UI", 11, "bold")
    )

    style.configure(
        "Modern.Vertical.TScrollbar",
        background="#3a3a3a",
        troughcolor="#252525",
        bordercolor="#252525",
        arrowcolor="#888888",
        width=8
    )

    style.map(
        "Modern.Vertical.TScrollbar",
        background=[
            ("active", "#555555"),
            ("pressed", "#666666")
        ]
    )