import tkinter as tk
from tkinter import ttk

from src.app.backend.draft_tracker_page import DraftViewerApp
from src.app.backend.data_update import UpdateDataPage

class MainApp:
    def __init__(self, root):
        self.root = root

        self.root.title("MTGA Helper")
        self.root.geometry("700x800")
        self.root.minsize(600, 600)

        self.configure_style()

        self.container = ttk.Frame(root)
        self.container.pack(
            fill="both",
            expand=True
        )

        self.show_menu()


    def configure_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        bg = "#1e1e1e"
        panel = "#2a2a2a"
        text = "#eeeeee"

        self.root.configure(bg=bg)

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

    def clear_frame(self):
        for widget in self.container.winfo_children():
            widget.destroy()


    def show_menu(self):
        self.clear_frame()
        frame = ttk.Frame(self.container)
        frame.pack(expand=True)

        ttk.Label(
            frame,
            text="MTGA Helper",
            style="Title.TLabel"
        ).pack(pady=(40, 10))


        ttk.Label(
            frame,
            text="Draft tools and data management",
            style="Subtitle.TLabel"
        ).pack(
            pady=(0, 40)
        )

        ttk.Button(
            frame,
            text="Draft Tracker",
            width=25,
            command=self.show_draft_tracker
        ).pack(pady=8)

        ttk.Button(
            frame,
            text="Update Data",
            width=25,
            command=self.show_update_page
        ).pack(pady=8)


    def show_draft_tracker(self):
        self.clear_frame()
        DraftViewerApp(
            self.container,
            self.show_menu
        )

    def show_update_page(self):
        self.clear_frame()
        UpdateDataPage(
            self.container,
            self.show_menu
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()