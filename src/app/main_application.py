import tkinter as tk
from tkinter import ttk

from src.app.backend.draft_tracker_page import DraftViewerApp
from src.app.backend.data_update import UpdateDataPage

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MTGA Helper")
        self.root.geometry("700x900")

        self.container = tk.Frame(root)
        self.container.pack(fill="both", expand=True)

        self.show_menu()

    def clear_frame(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_menu(self):
        self.clear_frame()

        title = tk.Label(
            self.container,
            text="MTGA Helper",
            font=("Arial", 18)
        )
        title.pack(pady=30)

        draft_button = tk.Button(
            self.container,
            text="Draft Tracker",
            width=20,
            height=2,
            command=self.show_draft_tracker
        )
        draft_button.pack(pady=10)

        update_button = tk.Button(
            self.container,
            text="Update Data",
            width=20,
            height=2,
            command=self.show_update_page
        )
        update_button.pack(pady=10)


    def show_draft_tracker(self):
        self.clear_frame()

        # Create your existing tracker inside this frame
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