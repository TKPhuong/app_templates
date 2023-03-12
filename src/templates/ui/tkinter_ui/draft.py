import tkinter as tk
from PIL import Image, ImageTk
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Combobox


class MainMenu:
    def __init__(self, parent, menu_items):
        self.parent = parent
        self.menu_items = menu_items
        self.create_menu()

    def create_menu(self):
        menubar = tk.Menu(self.parent)

        for item in self.menu_items:
            label = item.get("label", "")
            command = item.get("command", None)
            menu = tk.Menu(menubar, tearoff=0)

            for subitem in item.get("submenu", []):
                sublabel = subitem.get("label", "")
                subcommand = subitem.get("command", None)
                menu.add_command(label=sublabel, command=subcommand)

            menubar.add_cascade(label=label, menu=menu)

        self.parent.config(menu=menubar)


class ToolBar:
    def __init__(
        self, parent, buttons, row=0, column=0, columnspan=1, rowspan=1, sticky="nsew"
    ):
        self.parent = parent
        self.buttons = buttons
        self.row = row
        self.column = column
        self.columnspan = columnspan
        self.rowspan = rowspan
        self.sticky = sticky
        self.create_toolbar()

    def create_toolbar(self):
        toolbar = tk.Frame(self.parent, bd=1, relief=tk.RAISED)

        for index, button in enumerate(self.buttons):
            text = button.get("text", "")
            command = button.get("command", None)
            button = tk.Button(toolbar, text=text, command=command)
            button.grid(row=0, column=index, padx=2, pady=2)

        toolbar.grid(
            row=self.row,
            column=self.column,
            columnspan=self.columnspan,
            rowspan=self.rowspan,
            sticky=self.sticky,
        )


class StatusBar:
    def __init__(
        self, parent, labels, row=1, column=0, columnspan=1, rowspan=1, sticky="ew"
    ):
        self.parent = parent
        self.labels = labels
        self.row = row
        self.column = column
        self.columnspan = columnspan
        self.rowspan = rowspan
        self.sticky = sticky
        self.create_status_bar()

    def create_status_bar(self):
        statusbar = tk.Frame(self.parent, bd=1, relief=tk.SUNKEN)

        for index, label_dict in enumerate(self.labels):
            text = label_dict.get("text", "")
            side = label_dict.get("side", "w")
            sticky = {"left": "w", "right": "e"}.get(side, "w")
            label = tk.Label(statusbar, text=text)
            label.grid(row=0, column=index, padx=2, pady=2, sticky=sticky)

        statusbar.grid(
            row=self.row,
            column=self.column,
            columnspan=self.columnspan,
            rowspan=self.rowspan,
            sticky=self.sticky,
        )


class UI(tk.Tk):
    def __init__(self, settings):
        super().__init__()
        self.title(settings["title"])
        self.geometry(settings["size"])
        self.settings = settings

        # configure the row and column properties for the main window and
        #  add the widgets to the main window using the grid layout manager.
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # create main menu
        MainMenu(self, self.settings.get("main_menu_items", []))

        # create toolbar
        ToolBar(
            self,
            self.settings.get("toolbar_buttons", []),
            row=0,
            column=0,
            sticky="nsew",
        )

        # create status bar
        StatusBar(
            self,
            self.settings.get("status_bar_labels", []),
            row=6,
            column=0,
            sticky="ew",
        )

        # add widgets to the main window
        self.add_widgets()

    def add_widgets(self):
        widgets = self.settings.get("widgets", [])

        for widget in widgets:
            wtype = widget.get("type", "label")
            padx = widget.get("padx", 0)
            pady = widget.get("pady", 0)
            wig_args = {}
            row = widget.get("row", 1)
            column = widget.get("column", 0)
            columnspan = widget.get("columnspan", 1)
            rowspan = widget.get("rowspan", 1)

            if wtype == "label":
                text = widget.get("text", "")
                label = tk.Label(self, text=text)
                label.grid(
                    row=row,
                    column=column,
                    columnspan=columnspan,
                    rowspan=rowspan,
                    padx=padx,
                    pady=pady,
                    sticky="nsew",
                )
            elif wtype == "button":
                text = widget.get("text", "")
                command = widget.get("command", None)
                button = tk.Button(self, text=text, command=command)
                button.grid(
                    row=row,
                    column=column,
                    columnspan=columnspan,
                    rowspan=rowspan,
                    padx=padx,
                    pady=pady,
                    sticky="nsew",
                )
            elif wtype == "image":
                img_path = widget.get("path", "")
                img = Image.open(img_path)
                photo = ImageTk.PhotoImage(img)
                label = tk.Label(self, image=photo)
                label.photo = photo
                label.grid(
                    row=row,
                    column=column,
                    columnspan=columnspan,
                    rowspan=rowspan,
                    padx=padx,
                    pady=pady,
                    sticky="nsew",
                )
            elif wtype == "scrolltext":
                text = widget.get("text", "")
                st = ScrolledText(self)
                st.insert(tk.END, text)
                st.grid(
                    row=row,
                    column=column,
                    columnspan=columnspan,
                    rowspan=rowspan,
                    padx=padx,
                    pady=pady,
                    sticky="nsew",
                )
            elif wtype == "combo":
                values = widget.get("values", [])
                default = widget.get("default", "")
                cb = Combobox(self, values=values)
                cb.current(values.index(default))
                cb.grid(
                    row=row,
                    column=column,
                    columnspan=columnspan,
                    rowspan=rowspan,
                    padx=padx,
                    pady=pady,
                    sticky="nsew",
                )
            else:
                pass

    def run(self):
        self.mainloop()


if __name__ == "__main__":
    import os

    current_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(current_dir, "resources/sample_img.png")
    settings = {
        "title": "My App",
        "size": "1200x900",
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
            {"text": "Line 1", "side": "left", "sticky": "w"},
            {"text": "Line 2", "side": "left", "sticky": "w"},
            {"text": "Line 3", "side": "right", "sticky": "w"},
        ],
        "widgets": [
            {
                "type": "label",
                "text": "Hello, World!",
                "padx": 20,
                "pady": 20,
                "columnspan": 3,
                "rowspan": None,
                "row": 1,
                "column": 1,
            },
            {
                "type": "button",
                "text": "Click me!",
                "command": None,
                "padx": 20,
                "pady": 20,
                "columnspan": 3,
                "rowspan": None,
                "row": 2,
                "column": 1,
            },
            {
                "type": "label",
                "text": "Goodbye, World!",
                "padx": 20,
                "pady": 20,
                "columnspan": 3,
                "rowspan": None,
                "row": 3,
                "column": 0,
            },
            {
                "type": "image",
                "path": img_path,
                "columnspan": 3,
                "rowspan": None,
                "row": 4,
                "column": 0,
            },
            {
                "type": "scrolltext",
                "text": "This is a ScrolledText widget.\n" * 20,
                "padx": 20,
                "pady": 20,
                "columnspan": 3,
                "rowspan": None,
                "row": 5,
                "column": 0,
            },
            {
                "type": "combo",
                "values": ["Option 1", "Option 2", "Option 3"],
                "default": "Option 2",
                "columnspan": 1,
                "rowspan": None,
                "row": 4,
                "column": 1,
            },
        ],
    }

app = App(settings)
app.run()
