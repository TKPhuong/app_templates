import tkinter as tk
from PIL import Image, ImageTk
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Combobox


class App(tk.Tk):
    def __init__(self, **kwargs):
        super().__init__()

        self.title("My App")
        self.default_width = 500
        self.default_height = 400

        # configure the row and column properties
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # load settings from kwargs or use defaults
        self.main_menu_items = kwargs.get("main_menu_items", [])
        self.toolbar_buttons = kwargs.get("toolbar_buttons", [])
        self.status_bar_labels = kwargs.get("status_bar_labels", [])
        self.widgets = kwargs.get("widgets", [])

        # create main menu
        self.create_main_menu()

        # create toolbar
        self.create_toolbar()

        # create status bar
        self.create_status_bar()

        # add widgets to the main window
        self.add_widgets()

    def create_main_menu(self):
        # create main menu items and add them to the menu bar
        menubar = tk.Menu(self)

        for item in self.main_menu_items:
            label = item.get("label", "")
            command = item.get("command", None)
            menu = tk.Menu(menubar, tearoff=0)
            for subitem in item.get("submenu", []):
                sublabel = subitem.get("label", "")
                subcommand = subitem.get("command", None)
                menu.add_command(label=sublabel, command=subcommand)
            menubar.add_cascade(label=label, menu=menu)

        self.config(menu=menubar)

    def create_toolbar(self):
        # create toolbar buttons and add them to a toolbar frame
        toolbar = tk.Frame(self, bd=1, relief=tk.RAISED)

        for button in self.toolbar_buttons:
            text = button.get("text", "")
            command = button.get("command", None)
            button = tk.Button(toolbar, text=text, command=command)
            button.pack(side=tk.LEFT, padx=2, pady=2)

        toolbar.pack(side=tk.TOP, fill=tk.X)

    def create_status_bar(self):
        # create status bar labels and add them to the main window
        statusbar = tk.Label(self, bd=1, relief=tk.SUNKEN, anchor=tk.W)

        for label in self.status_bar_labels:
            text = label.get("text", "")
            side = label.get("side", tk.LEFT)
            label = tk.Label(statusbar, text=text)
            label.pack(side=side)

        statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    def add_widgets(self):
        # add other widgets to the main window (e.g. buttons, labels, etc.)
        for widget in self.widgets:
            wtype = widget.get("type", "label")
            padx = widget.get("padx", 0)
            pady = widget.get("pady", 0)
            wig_args = {}
            x = widget.get("x", None)
            y = widget.get("y", None)
            width = widget.get("width", None)
            height = widget.get("height", None)
            if wtype == "label":
                text = widget.get("text", "")
                label = tk.Label(self, text=text)
                label.pack(padx=padx, pady=pady)
                label.place(x=x, y=y, width=width, height=height)
            elif wtype == "button":
                text = widget.get("text", "")
                command = widget.get("command", None)
                button = tk.Button(self, text=text, command=command)
                button.pack(padx=padx, pady=pady)
                button.place(x=x, y=y, width=width, height=height)
            elif wtype == "image":
                img_path = widget.get("path", "")
                img = Image.open(img_path)
                photo = ImageTk.PhotoImage(img)
                label = tk.Label(self, image=photo)
                label.photo = photo  # store the PhotoImage object as an attribute of the label object
                label.pack(padx=padx, pady=pady)
                label.place(x=x, y=y, width=width, height=height)
            elif wtype == "scrolltext":
                text = widget.get("text", "")
                st = ScrolledText(self)
                st.insert(tk.END, text)
                st.pack(padx=padx, pady=pady)
                st.place(x=x, y=y, width=width, height=height)
            elif wtype == "combo":
                values = widget.get("values", [])
                default = widget.get("default", "")
                cb = Combobox(self, values=values)
                cb.current(values.index(default))
                cb.pack(padx=padx, pady=pady)
                cb.place(x=x, y=y, width=width, height=height)
            else:
                pass

    def resize_window(self, width=None, height=None):
        if width is None:
            width = self.default_width
        if height is None:
            height = self.default_height
        self.geometry(f"{width}x{height}")


if __name__ == "__main__":
    import os

    current_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(current_dir, "resources/sample_img.png")
    APPW, APPH = 1200, 720
    settings = {
        "main_menu_items": [
            {
                "label": "File",
                "submenu": [
                    {"label": "New", "command": None},
                    {"label": "Open", "command": None},
                    {"label": "Save", "command": None},
                ],
            },
            {
                "label": "Edit",
                "submenu": [
                    {"label": "Cut", "command": None},
                    {"label": "Copy", "command": None},
                    {"label": "Paste", "command": None},
                ],
            },
            {"label": "Help", "command": None},
        ],
        "toolbar_buttons": [
            {"text": "New", "command": None},
            {"text": "Open", "command": None},
            {"text": "Save", "command": None},
            {"text": "Cut", "command": None},
            {"text": "Copy", "command": None},
            {"text": "Paste", "command": None},
        ],
        "status_bar_labels": [
            {"text": "Line 1", "side": tk.LEFT},
            {"text": "Line 2", "side": tk.LEFT},
            {"text": "Line 3", "side": tk.RIGHT},
        ],
        "widgets": [
            {
                "type": "label",
                "text": "Hello, World!",
                "padx": 20,
                "pady": 20,
                "x": APPW // 2,
                "y": APPH // 4,
            },
            {
                "type": "button",
                "text": "Click me!",
                "command": None,
                "padx": 20,
                "pady": 20,
                "width": 300,
                "height": 100,
            },
            {
                "type": "label",
                "text": "Goodbye, World!",
                "padx": 20,
                "pady": 20,
                "x": APPW * 3 // 4,
                "y": APPH // 4,
                "width": 300,
                "height": 100,
            },
            {"type": "image", "path": img_path, "padx": 20, "pady": 20},
            {
                "type": "scrolltext",
                "text": "This is a ScrolledText widget.\n" * 20,
                "x": APPW // 2 - 250,
                "y": APPH * 3 // 4,
                "width": 500,
                "height": 100,
            },
            {
                "type": "combo",
                "values": ["Option 1", "Option 2", "Option 3"],
                "default": "Option 2",
            },
        ],
    }

    app = App(**settings)
    app.resize_window(width=APPW, height=APPH)
    app.mainloop()
