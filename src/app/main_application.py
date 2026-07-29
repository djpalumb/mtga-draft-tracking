import tkinter as tk
from tkinter import ttk

from src.app.backend.draft_tracker_page import DraftViewerApp
from src.app.backend.data_update import UpdateDataPage
from src.app.frontend.style import configure_style

class MainApp:
    def __init__(self, root):
        self.root = root

        self.root.title("MTGA Helper")
        self.root.geometry("700x800")
        self.root.minsize(600, 600)

        configure_style(self)

        self.container = ttk.Frame(root)
        self.container.pack(
            fill="both",
            expand=True
        )

        self.show_menu()


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