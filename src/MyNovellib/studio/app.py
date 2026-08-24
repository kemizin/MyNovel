# Shell do MyNovel Studio: janela principal, menu, toolbar, área
# principal e status bar. Ainda sem funcionalidade real além de abrir/
# fechar -- cada Waystone seguinte liga um pedaço desta interface ao
# Project System existente (src/MyNovellib/project/).

import tkinter as tk
from tkinter import messagebox

APP_TITLE = "MyNovel Studio"


class StudioApp:

    # `root`: um tk.Tk() já existente (útil pra testes, que criam o
    # root e chamam .withdraw() antes de construir a interface). Sem
    # isso, cria um novo.
    def __init__(self, root=None):

        self.root = root if root is not None else tk.Tk()

        self.root.title(APP_TITLE)
        self.root.geometry("1024x700")
        self.root.minsize(640, 480)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self._build_menu()
        self._build_toolbar()
        self._build_main_area()
        self._build_status_bar()

        self.set_status("Pronto.")

    # --- Menu -------------------------------------------------------------

    def _build_menu(self):

        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="New Project...", command=self._not_implemented)
        file_menu.add_command(label="Open Project...", command=self._not_implemented)
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self._not_implemented)
        file_menu.add_command(label="Save As...", command=self._not_implemented)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)
        menubar.add_cascade(label="File", menu=file_menu)

        # New/Open/Save/Save As ainda não existem -- ficam desabilitados
        # até os Waystones que os implementam (não fingir que funcionam).
        for label in ("New Project...", "Open Project...", "Save", "Save As..."):
            file_menu.entryconfig(label, state=tk.DISABLED)

        edit_menu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        scene_menu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Scene", menu=scene_menu)

        build_menu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Build", menu=build_menu)

        help_menu = tk.Menu(menubar, tearoff=False)
        help_menu.add_command(label="About MyNovel Studio", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

        self.menubar = menubar
        # exposto pra quem precisar inspecionar/estender um menu específico
        # (Waystones seguintes, e os testes) sem duplicar a estrutura.
        self.menus = {
            "File": file_menu,
            "Edit": edit_menu,
            "Scene": scene_menu,
            "Build": build_menu,
            "Help": help_menu,
        }

    # --- Toolbar ------------------------------------------------------

    def _build_toolbar(self):

        self.toolbar = tk.Frame(self.root, relief=tk.RAISED, bd=1)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        self.toolbar_buttons = {}

        # espelha os comandos de File que ainda não existem -- mesma
        # regra: desabilitado até o Waystone que implementa cada um.
        for label in ("New", "Open", "Save"):
            button = tk.Button(
                self.toolbar,
                text=label,
                command=self._not_implemented,
                state=tk.DISABLED,
            )
            button.pack(side=tk.LEFT, padx=2, pady=2)
            self.toolbar_buttons[label] = button

    # --- Área principal -------------------------------------------------

    def _build_main_area(self):

        self.main_area = tk.Frame(self.root)
        self.main_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.main_area_placeholder = tk.Label(
            self.main_area,
            text="Nenhum projeto aberto.\nUse File → Open Project para começar.",
            fg="gray40",
            justify=tk.CENTER,
        )
        self.main_area_placeholder.pack(expand=True)

    # --- Status bar -----------------------------------------------------

    def _build_status_bar(self):

        self.status_bar = tk.Label(
            self.root, text="", anchor="w", relief=tk.SUNKEN, bd=1
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def set_status(self, text):
        self.status_bar.config(text=text)

    # --- Ações --------------------------------------------------------

    def _not_implemented(self):
        messagebox.showinfo(
            APP_TITLE, "Esta funcionalidade ainda não foi implementada."
        )

    def _show_about(self):
        messagebox.showinfo(
            APP_TITLE,
            "MyNovel Studio\n\n"
            "Editor visual para criar Visual Novels com a biblioteca MyNovel, "
            "sem precisar escrever Python.",
        )

    def on_close(self):
        self.root.destroy()

    def run(self):
        self.root.mainloop()
