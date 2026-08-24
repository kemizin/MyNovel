# Shell do MyNovel Studio: janela principal, menu, toolbar, área
# principal e status bar. Ainda sem funcionalidade real além de abrir/
# fechar -- cada Waystone seguinte liga um pedaço desta interface ao
# Project System existente (src/MyNovellib/project/).

import os

import tkinter as tk
from tkinter import messagebox, filedialog, ttk

from src.MyNovellib.studio.core import StudioCore, StudioError

APP_TITLE = "MyNovel Studio"


class StudioApp:

    # `root`: um tk.Tk() já existente (útil pra testes, que criam o
    # root e chamam .withdraw() antes de construir a interface). Sem
    # isso, cria um novo.
    def __init__(self, root=None):

        self.root = root if root is not None else tk.Tk()

        # StudioCore concentra a lógica de negócio (validar, criar,
        # carregar, salvar) sem tocar em Tkinter -- StudioApp só chama
        # o Core e traduz o resultado em tela/messagebox. project/
        # project_path/dirty (abaixo) delegam pra lá.
        self.core = StudioCore()
        self._update_title()

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
        file_menu.add_command(label="New Project...", command=self.new_project)
        file_menu.add_command(label="Open Project...", command=self.open_project)
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.save_project)
        file_menu.add_command(label="Save As...", command=self.save_project_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)
        menubar.add_cascade(label="File", menu=file_menu)

        # Save/Save As só fazem sentido com um projeto aberto -- ficam
        # desabilitados até New/Open Project carregarem um.
        for label in ("Save", "Save As..."):
            file_menu.entryconfig(label, state=tk.DISABLED)

        edit_menu = tk.Menu(menubar, tearoff=False)
        edit_menu.add_command(
            label="New Character...", command=self.new_character, state=tk.DISABLED
        )
        edit_menu.add_command(
            label="New Scene...", command=self.new_scene, state=tk.DISABLED
        )
        edit_menu.add_command(
            label="New Story...", command=self.new_story, state=tk.DISABLED
        )
        menubar.add_cascade(label="Edit", menu=edit_menu)

        scene_menu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Scene", menu=scene_menu)

        build_menu = tk.Menu(menubar, tearoff=False)
        build_menu.add_command(label="Play", command=self.play_project, state=tk.DISABLED)
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

        # espelha os comandos de File/Build -- mesma regra dos menus:
        # Save/Play só fazem sentido com um projeto aberto.
        commands = {
            "New": self.new_project,
            "Open": self.open_project,
            "Save": self.save_project,
        }

        for label, command in commands.items():
            button = tk.Button(
                self.toolbar,
                text=label,
                command=command,
                state=tk.DISABLED if label == "Save" else tk.NORMAL,
            )
            button.pack(side=tk.LEFT, padx=2, pady=2)
            self.toolbar_buttons[label] = button

        play_button = tk.Button(
            self.toolbar,
            text="▶ Play",
            command=self.play_project,
            state=tk.DISABLED,
            fg="dark green",
        )
        play_button.pack(side=tk.LEFT, padx=(12, 2), pady=2)
        self.toolbar_buttons["Play"] = play_button

    # --- Área principal: sidebar (Project / Assets) + Properties (direita) --

    _PLACEHOLDER_TEXT = "Nenhum projeto aberto.\nUse File → Open Project para começar."

    # tipo de Asset -> categoria mostrada no Asset Browser
    ASSET_CATEGORY_LABELS = {
        "character_sprite": "Characters",
        "background": "Backgrounds",
        "music": "Music",
        "voice": "Voices",
        "sfx": "SFX",
    }

    # tipos de asset que têm imagem (e por isso podem ter thumbnail)
    _IMAGE_ASSET_TYPES = {"character_sprite", "background"}

    def _build_main_area(self):

        self.main_area = tk.Frame(self.root)
        self.main_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # --- sidebar com abas: PROJECT (árvore) e ASSETS (asset browser) ---
        sidebar_frame = tk.Frame(self.main_area, width=240)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        sidebar_frame.pack_propagate(False)

        self.sidebar = ttk.Notebook(sidebar_frame)
        self.sidebar.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        project_tab = tk.Frame(self.sidebar)
        self.sidebar.add(project_tab, text="Project")

        self.explorer = ttk.Treeview(project_tab, show="tree")
        self.explorer.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.explorer.bind("<<TreeviewSelect>>", self._on_explorer_select)

        assets_tab = tk.Frame(self.sidebar)
        self.sidebar.add(assets_tab, text="Assets")

        self.asset_tree = ttk.Treeview(assets_tab, show="tree")
        self.asset_tree.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.asset_tree.bind("<<TreeviewSelect>>", self._on_asset_tree_select)

        # --- painel PROPERTIES: resumo somente-leitura (com thumbnail
        # sob demanda) para a maioria dos itens, ou um editor de
        # verdade quando o item tiver um (por enquanto só Character --
        # ver _show_properties/_build_character_editor). O conteúdo é
        # reconstruído a cada seleção (self.properties_content).
        properties_frame = tk.Frame(self.main_area)
        properties_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(
            properties_frame, text="PROPERTIES", anchor="w", font=("", 9, "bold")
        ).pack(fill=tk.X, padx=8, pady=(8, 0))

        self.properties_content = tk.Frame(properties_frame)
        self.properties_content.pack(fill=tk.BOTH, expand=True)

        self._build_readonly_properties(self._PLACEHOLDER_TEXT, thumbnail_iid=None)

        self.explorer_frame = sidebar_frame
        self.properties_frame = properties_frame

    # --- Status bar -----------------------------------------------------

    def _build_status_bar(self):

        self.status_bar = tk.Label(
            self.root, text="", anchor="w", relief=tk.SUNKEN, bd=1
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def set_status(self, text):
        self.status_bar.config(text=text)

    # --- Novo projeto ---------------------------------------------------
    #
    # Mesmo princípio do Open Project: new_project() só monta o
    # diálogo; create_new_project(...) faz o trabalho de verdade e é
    # testável direto, sem precisar simular clique no diálogo.

    def new_project(self):
        self._open_new_project_dialog()

    def _open_new_project_dialog(self):

        dialog = tk.Toplevel(self.root)
        dialog.title("New Project")
        dialog.transient(self.root)
        dialog.resizable(False, False)

        name_var = tk.StringVar(value="Minha Visual Novel")
        location_var = tk.StringVar(value=os.getcwd())
        width_var = tk.StringVar(value="1920")
        height_var = tk.StringVar(value="1080")

        pad = {"padx": 8, "pady": 4}

        tk.Label(dialog, text="Name:").grid(row=0, column=0, sticky="w", **pad)
        tk.Entry(dialog, textvariable=name_var, width=32).grid(
            row=0, column=1, columnspan=2, sticky="we", **pad
        )

        tk.Label(dialog, text="Location:").grid(row=1, column=0, sticky="w", **pad)
        tk.Entry(dialog, textvariable=location_var, width=32).grid(
            row=1, column=1, sticky="we", **pad
        )

        def browse_location():
            chosen = filedialog.askdirectory(title="Choose Location")
            if chosen:
                location_var.set(chosen)

        tk.Button(dialog, text="Browse...", command=browse_location).grid(
            row=1, column=2, **pad
        )

        tk.Label(dialog, text="Width:").grid(row=2, column=0, sticky="w", **pad)
        tk.Entry(dialog, textvariable=width_var, width=10).grid(
            row=2, column=1, sticky="w", **pad
        )

        tk.Label(dialog, text="Height:").grid(row=3, column=0, sticky="w", **pad)
        tk.Entry(dialog, textvariable=height_var, width=10).grid(
            row=3, column=1, sticky="w", **pad
        )

        def on_create():
            criado = self.create_new_project(
                name_var.get(), location_var.get(), width_var.get(), height_var.get()
            )
            if criado:
                dialog.destroy()

        tk.Button(dialog, text="Create", command=on_create).grid(
            row=4, column=0, columnspan=3, pady=(12, 8)
        )

        # exposto pra quem (testes) precisar inspecionar o diálogo
        self.new_project_dialog = dialog

        return dialog

    # Cria o projeto de verdade: repassa pro Core (validação + criação
    # + carregamento). Retorna True em sucesso, False se algo for
    # inválido (e mostra o erro correspondente) -- o diálogo usa o
    # retorno pra saber se pode se fechar.
    def create_new_project(self, name, location, width, height):

        try:
            self.core.create_new_project(name, location, width, height)

        except StudioError as error:
            messagebox.showerror(APP_TITLE, str(error))
            return False

        self._on_project_loaded()

        return True

    # --- Novo personagem --------------------------------------------------
    #
    # Mesmo princípio de New Project: new_character() só abre o
    # diálogo; create_character(...) faz o trabalho de verdade e é
    # testável direto. Só pede o nome -- o personagem nasce sem
    # nenhuma emoção ainda (mesmo estado que CharacterData(nome) já
    # tem em Python) e usa o "+ Add Emotion" que já existe no
    # Character Editor pra ganhar a primeira emoção, em vez de repetir
    # esses campos aqui também.

    def new_character(self):
        self._open_new_character_dialog()

    def _open_new_character_dialog(self):

        dialog = tk.Toplevel(self.root)
        dialog.title("New Character")
        dialog.transient(self.root)
        dialog.resizable(False, False)

        name_var = tk.StringVar()

        pad = {"padx": 8, "pady": 4}

        tk.Label(dialog, text="Name:").grid(row=0, column=0, sticky="w", **pad)
        entry = tk.Entry(dialog, textvariable=name_var, width=28)
        entry.grid(row=0, column=1, sticky="we", **pad)
        entry.focus_set()

        def on_create():
            criado = self.create_character(name_var.get())
            if criado:
                dialog.destroy()

        tk.Button(dialog, text="Create", command=on_create).grid(
            row=1, column=0, columnspan=2, pady=(12, 8)
        )

        self.new_character_dialog = dialog

        return dialog

    # Cria o personagem de verdade -- separado do diálogo, testável
    # direto. Repassa pro Core; ao terminar, seleciona o personagem
    # recém-criado no Explorer, já abrindo o Character Editor nele
    # (pronto pra "+ Add Emotion").
    def create_character(self, name):

        try:
            key = self.core.create_character(name)

        except StudioError as error:
            messagebox.showerror(APP_TITLE, str(error))
            return False

        self._update_title()  # o Core já marcou dirty
        self._refresh_explorer()

        item_id = f"character:{key}"
        self.explorer.selection_set(item_id)
        self._show_properties(item_id)

        return True

    # --- Nova cena ----------------------------------------------------
    #
    # Mesmo princípio: new_scene() só abre o diálogo; create_scene(...)
    # faz o trabalho de verdade. Background é pedido aqui na criação
    # (diferente do personagem/emoção) porque, ao contrário do
    # Character Editor, o Scene Editor ainda não tem campo nenhum pra
    # trocar o background depois -- sem perguntar agora, não teria
    # como definir isso pela interface.

    def new_scene(self):
        self._open_new_scene_dialog()

    def _open_new_scene_dialog(self):

        dialog = tk.Toplevel(self.root)
        dialog.title("New Scene")
        dialog.transient(self.root)
        dialog.resizable(False, False)

        name_var = tk.StringVar()
        background_var = tk.StringVar()

        pad = {"padx": 8, "pady": 4}

        tk.Label(dialog, text="Name:").grid(row=0, column=0, sticky="w", **pad)
        entry = tk.Entry(dialog, textvariable=name_var, width=28)
        entry.grid(row=0, column=1, sticky="we", **pad)
        entry.focus_set()

        tk.Label(dialog, text="Background:").grid(row=1, column=0, sticky="w", **pad)
        tk.Entry(dialog, textvariable=background_var, width=28).grid(
            row=1, column=1, sticky="we", **pad
        )
        tk.Button(
            dialog, text="Browse...", command=lambda: self._browse_sprite(background_var)
        ).grid(row=1, column=2, **pad)

        def on_create():
            criado = self.create_scene(name_var.get(), background_var.get())
            if criado:
                dialog.destroy()

        tk.Button(dialog, text="Create", command=on_create).grid(
            row=2, column=0, columnspan=3, pady=(12, 8)
        )

        self.new_scene_dialog = dialog

        return dialog

    # Cria a cena de verdade -- separado do diálogo, testável direto.
    # Repassa pro Core; ao terminar, seleciona a cena recém-criada no
    # Explorer, já abrindo o Scene Editor nela.
    def create_scene(self, name, background=""):

        try:
            key = self.core.create_scene(name, background)

        except StudioError as error:
            messagebox.showerror(APP_TITLE, str(error))
            return False

        self._update_title()  # o Core já marcou dirty
        self._refresh_explorer()

        item_id = f"scene:{key}"
        self.explorer.selection_set(item_id)
        self._show_properties(item_id)

        return True

    # --- Nova história --------------------------------------------------
    #
    # Mesmo princípio: new_story() só abre o diálogo; create_story(...)
    # faz o trabalho de verdade. Só o nome -- a história nasce sem
    # nenhuma Action ainda (não existe editor de história -- Story
    # Editor -- nesta fase; selecioná-la mostra o resumo somente-
    # leitura de sempre, "Ações: 0").

    def new_story(self):
        self._open_new_story_dialog()

    def _open_new_story_dialog(self):

        dialog = tk.Toplevel(self.root)
        dialog.title("New Story")
        dialog.transient(self.root)
        dialog.resizable(False, False)

        name_var = tk.StringVar()

        pad = {"padx": 8, "pady": 4}

        tk.Label(dialog, text="Name:").grid(row=0, column=0, sticky="w", **pad)
        entry = tk.Entry(dialog, textvariable=name_var, width=28)
        entry.grid(row=0, column=1, sticky="we", **pad)
        entry.focus_set()

        def on_create():
            criado = self.create_story(name_var.get())
            if criado:
                dialog.destroy()

        tk.Button(dialog, text="Create", command=on_create).grid(
            row=1, column=0, columnspan=2, pady=(12, 8)
        )

        self.new_story_dialog = dialog

        return dialog

    # Cria a história de verdade -- separado do diálogo, testável
    # direto. Repassa pro Core; ao terminar, seleciona a história
    # recém-criada no Explorer.
    def create_story(self, name):

        try:
            key = self.core.create_story(name)

        except StudioError as error:
            messagebox.showerror(APP_TITLE, str(error))
            return False

        self._update_title()  # o Core já marcou dirty
        self._refresh_explorer()

        item_id = f"story:{key}"
        self.explorer.selection_set(item_id)
        self._show_properties(item_id)

        return True

    # --- Projeto ------------------------------------------------------
    #
    # Só chama tkinter.filedialog aqui; carregar de fato fica em
    # load_project(path), separado de propósito -- assim dá pra testar
    # o carregamento sem precisar simular clique num file dialog.

    def open_project(self):

        path = filedialog.askopenfilename(
            title="Open Project",
            filetypes=[("MyNovel Project", "*.mynovel"), ("Todos os arquivos", "*.*")],
        )

        if not path:
            return  # usuário cancelou o dialog

        self.load_project(path)

    # Carrega um project.mynovel pelo caminho e atualiza a interface.
    # Repassa pro Core -- nenhuma lógica de carregamento duplicada
    # aqui.
    def load_project(self, path):

        try:
            self.core.load_project(path)

        except StudioError as error:
            messagebox.showerror(APP_TITLE, str(error))
            return

        self._on_project_loaded()

    def _on_project_loaded(self):

        self._update_title()  # o Core já limpou o dirty ao carregar
        self.set_status(f'Projeto "{self.project.name}" carregado.')
        self._set_project_actions_enabled(True)
        self._refresh_explorer()
        self._refresh_asset_browser()

    # Save/Save As/Play/New Character só fazem sentido com um projeto
    # aberto.
    def _set_project_actions_enabled(self, enabled):

        state = tk.NORMAL if enabled else tk.DISABLED

        self.menus["File"].entryconfig("Save", state=state)
        self.menus["File"].entryconfig("Save As...", state=state)
        self.menus["Build"].entryconfig("Play", state=state)
        self.menus["Edit"].entryconfig("New Character...", state=state)
        self.menus["Edit"].entryconfig("New Scene...", state=state)
        self.menus["Edit"].entryconfig("New Story...", state=state)
        self.toolbar_buttons["Save"].config(state=state)
        self.toolbar_buttons["Play"].config(state=state)

    # project/project_path/dirty vivem no Core (StudioCore) -- essas
    # properties só delegam pra lá, então tanto o resto do StudioApp
    # quanto o código existente de teste ("app.project = ...",
    # "app.dirty = True") continuam funcionando exatamente igual.
    @property
    def project(self):
        return self.core.project

    @project.setter
    def project(self, value):
        self.core.project = value

    @property
    def project_path(self):
        return self.core.project_path

    @project_path.setter
    def project_path(self, value):
        self.core.project_path = value

    # `dirty` é property (não atributo simples) justamente pra que
    # QUALQUER jeito de mudar seu valor -- mark_dirty(), Save, carregar
    # um projeto, ou até "app.dirty = True" direto (como os testes já
    # fazem) -- atualize o título da janela sozinho, sem precisar
    # lembrar de chamar mais nada em cada ponto de edição. O valor em
    # si mora no Core (self.core.dirty); só o efeito colateral de
    # atualizar o título é responsabilidade do StudioApp.
    @property
    def dirty(self):
        return self.core.dirty

    @dirty.setter
    def dirty(self, value):
        self.core.dirty = bool(value)
        self._update_title()

    # Título reflete o estado de dirty: "MyNovel Studio — MeuJogo *"
    # com alterações não salvas, "MyNovel Studio — MeuJogo" sem. Sem
    # projeto carregado ainda, só o nome do app.
    def _update_title(self):

        if self.project is None:
            self.root.title(APP_TITLE)
            return

        marcador = " *" if self.dirty else ""
        self.root.title(f"{APP_TITLE} — {self.project.name}{marcador}")

    # Chamado por qualquer edição (Character/Scene/Story/Project) pra
    # marcar que existem alterações não salvas -- a property acima já
    # cuida de refletir isso no título. A proteção ao fechar (on_close)
    # e o Save usam esse mesmo self.dirty.
    def mark_dirty(self):
        self.dirty = True

    # Repovoa o Project Explorer com a árvore do projeto carregado:
    #
    #     MeuJogo
    #     ├── Characters (Jef, Ken, ...)
    #     ├── Scenes (campo, quarto, ...)
    #     ├── Stories (intro, ...)
    #     └── Assets (...)
    #
    # Ainda não edita nada -- só navegação. Ao terminar, seleciona a
    # raiz e mostra o resumo do projeto no painel Properties.
    def _refresh_explorer(self):

        self.explorer.delete(*self.explorer.get_children())

        project = self.project

        self.explorer.insert("", "end", iid="project", text=project.name, open=True)

        self._insert_category("Characters", "character", sorted(project.characters))
        self._insert_category("Scenes", "scene", sorted(project.scenes))
        self._insert_category("Stories", "story", sorted(project.stories))
        self._insert_category("Assets", "asset", sorted(project.assets))

        self.explorer.selection_set("project")
        self._show_properties("project")

    def _insert_category(self, label, kind, keys):

        category_id = f"category:{kind}"

        self.explorer.insert("project", "end", iid=category_id, text=label, open=True)

        for key in keys:
            self.explorer.insert(category_id, "end", iid=f"{kind}:{key}", text=key)

    def _on_explorer_select(self, event=None):

        selection = self.explorer.selection()

        if not selection:
            return

        self._show_properties(selection[0])

    # --- Asset Browser --------------------------------------------------
    #
    # Painel ASSETS: os assets registrados no projeto, agrupados por
    # categoria (Characters/Backgrounds/Music/Voices/SFX). Só
    # visualização -- nenhum editor de asset ainda. A lista em si é só
    # texto (rápida, não abre nenhum arquivo); a imagem só é carregada
    # quando um asset É SELECIONADO (thumbnail sob demanda -- nunca
    # carrega tudo de uma vez).

    def _refresh_asset_browser(self):

        self.asset_tree.delete(*self.asset_tree.get_children())

        project = self.project
        por_categoria = {tipo: [] for tipo in self.ASSET_CATEGORY_LABELS}
        outros = []

        for asset_id, asset in project.assets.items():
            if asset.type in por_categoria:
                por_categoria[asset.type].append(asset_id)
            else:
                outros.append(asset_id)

        for tipo, label in self.ASSET_CATEGORY_LABELS.items():
            self._insert_asset_category(f"assetcat:{tipo}", label, sorted(por_categoria[tipo]))

        if outros:
            self._insert_asset_category("assetcat:other", "Other", sorted(outros))

    def _insert_asset_category(self, category_id, label, asset_ids):

        self.asset_tree.insert("", "end", iid=category_id, text=label, open=True)

        for asset_id in asset_ids:
            self.asset_tree.insert(category_id, "end", iid=f"asset:{asset_id}", text=asset_id)

    def _on_asset_tree_select(self, event=None):

        selection = self.asset_tree.selection()

        if not selection:
            return

        self._show_properties(selection[0])

    # Reconstrói o painel Properties pro item selecionado. Character e
    # Scene têm editor de verdade (Waystones 7 e 8); todo o resto
    # continua como resumo somente-leitura (com thumbnail sob demanda,
    # se o item for um asset de imagem).
    def _show_properties(self, iid):

        for widget in self.properties_content.winfo_children():
            widget.destroy()

        if iid.startswith("character:"):
            self._build_character_editor(iid.split(":", 1)[1])
            return

        if iid.startswith("scene:"):
            self._build_scene_editor(iid.split(":", 1)[1])
            return

        if iid.startswith("story:"):
            self._build_story_editor(iid.split(":", 1)[1])
            return

        self._build_readonly_properties(self._describe_selection(iid), thumbnail_iid=iid)

    # --- Story Editor -----------------------------------------------------
    #
    # Lista ordenada das Actions da história (a ordem é a ordem de
    # execução -- por isso Listbox, não Treeview: reordenar itens de
    # uma lista plana, waystone seguinte, é simples de fazer com
    # delete/insert). Cada linha usa ActionData.describe()
    # (project/story_data.py) -- o Studio não reimplementa esse texto.
    # "+ Add Action" adiciona ao final; clicar numa Action da lista
    # abre os campos dela pra editar (mesmo padrão do painel
    # Properties da Scene) + um botão pra remover. Reordenar ainda não
    # existe (próximo waystone).

    ACTION_TYPES = ("speak", "emotion", "move", "enter", "exit", "pause")

    def _build_story_editor(self, story_key):

        parent = self.properties_content
        data = self.project.stories[story_key]

        tk.Label(
            parent, text="STORY", anchor="w", font=("", 9, "bold")
        ).pack(fill=tk.X, padx=8, pady=(8, 0))

        tk.Label(
            parent,
            text=f"{len(data.actions)} ação(ões) -- em ordem de execução:",
            anchor="w",
            fg="gray40",
        ).pack(fill=tk.X, padx=8, pady=(4, 4))

        listbox = tk.Listbox(parent, activestyle="none")
        listbox.pack(fill=tk.X, padx=8)
        listbox.bind("<<ListboxSelect>>", self._on_story_action_select)

        for action in data.actions:
            listbox.insert(tk.END, action.describe())

        self.story_listbox = listbox
        self.story_editor_key = story_key

        tk.Button(
            parent,
            text="+ Add Action",
            command=lambda: self._open_add_action_dialog(story_key),
        ).pack(anchor="w", padx=8, pady=(8, 4))

        self.story_action_properties_frame = tk.Frame(parent)
        self.story_action_properties_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(4, 8))

        self._render_story_action_properties()

        tk.Button(
            parent,
            text="Delete Story",
            fg="red3",
            command=lambda: self._delete_story(story_key),
        ).pack(anchor="w", padx=8, pady=(0, 8))

    def _on_story_action_select(self, event=None):
        self._render_story_action_properties()

    # Repovoa só o CONTEÚDO da listbox (não reconstrói o Story Editor
    # inteiro) -- preserva a seleção atual quando ela ainda existe,
    # pra editar/atualizar uma Action não jogar o usuário de volta pro
    # "nada selecionado".
    def _refresh_story_listbox(self):

        selecionado = self.story_listbox.curselection()

        self.story_listbox.delete(0, tk.END)

        for action in self.project.stories[self.story_editor_key].actions:
            self.story_listbox.insert(tk.END, action.describe())

        if selecionado and selecionado[0] < self.story_listbox.size():
            self.story_listbox.selection_set(selecionado[0])

    # Painel abaixo da lista: sem seleção, um texto de instrução; com
    # uma Action selecionada, os campos dela (pré-preenchidos, mesmo
    # builder do diálogo Add Action) + Update Action/Remove Action. O
    # TIPO da Action não é editável aqui -- trocar de tipo muda por
    # completo quais campos são válidos, então é remover e adicionar
    # de novo, não editar.
    def _render_story_action_properties(self):

        for widget in self.story_action_properties_frame.winfo_children():
            widget.destroy()

        selection = self.story_listbox.curselection()

        if not selection:
            tk.Label(
                self.story_action_properties_frame,
                text="Clique numa Action na lista para editar.",
                fg="gray40",
                anchor="w",
            ).pack(fill=tk.X)
            return

        index = selection[0]
        data = self.project.stories[self.story_editor_key]

        if index >= len(data.actions):
            return

        action = data.actions[index]

        tk.Label(
            self.story_action_properties_frame,
            text=f"Action: {action.type}",
            anchor="w",
            font=("", 9, "bold"),
        ).pack(fill=tk.X, pady=(4, 6))

        fields_frame = tk.Frame(self.story_action_properties_frame)
        fields_frame.pack(fill=tk.X)

        field_vars = {}
        self._build_action_type_fields(fields_frame, action.type, field_vars, initial=action.fields)

        def on_update():

            try:
                kwargs = self._action_kwargs_from_vars(action.type, field_vars)

            except ValueError as error:
                messagebox.showerror(APP_TITLE, str(error))
                return

            self.update_story_action(self.story_editor_key, index, **kwargs)

        buttons_row = tk.Frame(self.story_action_properties_frame)
        buttons_row.pack(fill=tk.X, pady=(8, 0))

        tk.Button(buttons_row, text="Update Action", command=on_update).pack(side=tk.LEFT)
        tk.Button(
            buttons_row,
            text="Remove Action",
            fg="red3",
            command=lambda: self._remove_story_action(index),
        ).pack(side=tk.LEFT, padx=(8, 0))

        # desabilitados na ponta -- não tem pra onde mover ali (mesmo
        # feedback de "Save"/"Play" desabilitados sem projeto aberto:
        # o botão em si já diz o que é possível fazer agora).
        tk.Button(
            buttons_row,
            text="▲ Move Up",
            state=tk.NORMAL if index > 0 else tk.DISABLED,
            command=lambda: self.move_story_action(self.story_editor_key, index, -1),
        ).pack(side=tk.LEFT, padx=(8, 0))
        tk.Button(
            buttons_row,
            text="▼ Move Down",
            state=tk.NORMAL if index < len(data.actions) - 1 else tk.DISABLED,
            command=lambda: self.move_story_action(self.story_editor_key, index, 1),
        ).pack(side=tk.LEFT, padx=(4, 0))

    # Substitui os campos da Action selecionada -- separado do botão,
    # testável direto. Mantém a seleção (só a listbox é repovoada, não
    # o editor inteiro) pra continuar mostrando a mesma Action editada.
    def update_story_action(self, story_key, index, **fields):

        try:
            self.core.update_story_action(story_key, index, **fields)

        except StudioError as error:
            messagebox.showerror(APP_TITLE, str(error))
            return False

        self._update_title()  # o Core já marcou dirty
        self._refresh_story_listbox()
        self._render_story_action_properties()

        return True

    def _remove_story_action(self, index):

        try:
            self.core.remove_story_action(self.story_editor_key, index)

        except StudioError as error:
            messagebox.showerror(APP_TITLE, str(error))
            return

        self._update_title()  # o Core já marcou dirty
        self._refresh_story_listbox()
        self._render_story_action_properties()

    # Troca a Action de `index` de lugar com a vizinha (delta=-1/+1).
    # Diferente de update/remove, a seleção não fica no MESMO índice
    # depois -- segue a Action que se moveu (novo_index, devolvido
    # pelo Core) pra continuar mostrando a mesma Action selecionada,
    # só que na posição nova.
    def move_story_action(self, story_key, index, delta):

        try:
            novo_index = self.core.move_story_action(story_key, index, delta)

        except StudioError as error:
            messagebox.showerror(APP_TITLE, str(error))
            return

        self._update_title()  # o Core já marcou dirty (se moveu de verdade)

        self.story_listbox.delete(0, tk.END)
        for action in self.project.stories[story_key].actions:
            self.story_listbox.insert(tk.END, action.describe())

        self.story_listbox.selection_set(novo_index)
        self._render_story_action_properties()

    def _delete_story(self, story_key):

        nome = self.project.stories[story_key].name

        if not messagebox.askyesno(APP_TITLE, f'Remover a história "{nome}"?'):
            return

        try:
            self.core.delete_story(story_key)

        except StudioError as error:
            messagebox.showerror(APP_TITLE, str(error))
            return

        self._update_title()  # o Core já marcou dirty
        self._refresh_explorer()

    # Diálogo com campos que mudam de acordo com o tipo escolhido --
    # mesma ideia do Add Emotion (nome/idle/talking), só que aqui o
    # conjunto de campos depende do tipo de Action. `fields_frame` é
    # reconstruído a cada troca de tipo; `field_vars` guarda os
    # StringVar atuais (rebuild_fields() esvazia e repopula o dict).
    def _open_add_action_dialog(self, story_key):

        dialog = tk.Toplevel(self.root)
        dialog.title("Add Action")
        dialog.transient(self.root)
        dialog.resizable(False, False)

        pad = {"padx": 8, "pady": 4}

        type_var = tk.StringVar(value=self.ACTION_TYPES[0])

        tk.Label(dialog, text="Type:").grid(row=0, column=0, sticky="w", **pad)
        type_combo = ttk.Combobox(
            dialog, textvariable=type_var, values=self.ACTION_TYPES,
            state="readonly", width=24,
        )
        type_combo.grid(row=0, column=1, sticky="we", **pad)

        fields_frame = tk.Frame(dialog)
        fields_frame.grid(row=1, column=0, columnspan=2, sticky="we")

        field_vars = {}

        def rebuild_fields(event=None):
            for widget in fields_frame.winfo_children():
                widget.destroy()
            field_vars.clear()
            self._build_action_type_fields(fields_frame, type_var.get(), field_vars)

        type_combo.bind("<<ComboboxSelected>>", rebuild_fields)
        rebuild_fields()

        def on_add():

            try:
                kwargs = self._action_kwargs_from_vars(type_var.get(), field_vars)

            except ValueError as error:
                messagebox.showerror(APP_TITLE, str(error))
                return

            criado = self.add_story_action(story_key, type_var.get(), **kwargs)

            if criado:
                dialog.destroy()

        tk.Button(dialog, text="Add", command=on_add).grid(
            row=2, column=0, columnspan=2, pady=(12, 8)
        )

        self.add_action_dialog = dialog

        return dialog

    # Monta os campos de um tipo de Action em `parent`, guardando um
    # StringVar por campo em `field_vars` (chave = nome do campo, igual
    # ActionData.fields usa). "Character" aparece pra todos os tipos
    # menos "pause" -- sempre um combobox com os personagens do
    # projeto (não dá pra digitar um personagem que não existe).
    #
    # `initial` (opcional) pré-preenche os campos com valores já
    # existentes -- usado tanto por Add Action (sem initial, tudo
    # vazio) quanto por editar uma Action já na lista (initial =
    # action.fields), reaproveitando o mesmo layout pros dois casos.
    def _build_action_type_fields(self, parent, action_type, field_vars, initial=None):

        initial = initial or {}
        pad = {"padx": 8, "pady": 4}
        row = 0
        character_combo = None

        def valor_inicial(campo):
            valor = initial.get(campo)
            return "" if valor is None else str(valor)

        if action_type != "pause":

            tk.Label(parent, text="Character:").grid(row=row, column=0, sticky="w", **pad)

            character_var = tk.StringVar(value=valor_inicial("character"))
            character_combo = ttk.Combobox(
                parent, textvariable=character_var,
                values=sorted(self.project.characters), state="readonly", width=22,
            )
            character_combo.grid(row=row, column=1, sticky="we", **pad)
            field_vars["character"] = character_var
            row += 1

        if action_type == "speak":

            tk.Label(parent, text="Text:").grid(row=row, column=0, sticky="w", **pad)
            text_var = tk.StringVar(value=valor_inicial("text"))
            tk.Entry(parent, textvariable=text_var, width=30).grid(
                row=row, column=1, sticky="we", **pad
            )
            field_vars["text"] = text_var

        elif action_type == "emotion":

            tk.Label(parent, text="Emotion:").grid(row=row, column=0, sticky="w", **pad)
            emotion_var = tk.StringVar(value=valor_inicial("emotion"))
            emotion_combo = ttk.Combobox(
                parent, textvariable=emotion_var, values=(), state="disabled", width=22,
            )
            emotion_combo.grid(row=row, column=1, sticky="we", **pad)
            field_vars["emotion"] = emotion_var

            # a lista de emoções depende de qual personagem está
            # escolhido -- popula de acordo com o personagem atual
            # (já pré-preenchido, ao editar) e atualiza de novo sempre
            # que o personagem mudar (aí sim limpando a emoção, que
            # provavelmente não existe mais pro personagem novo).
            def refresh_emotion_options(reset):

                character_data = self.project.characters.get(field_vars["character"].get())
                opcoes = sorted(character_data.emotions) if character_data else []

                emotion_combo.config(values=opcoes, state="readonly" if opcoes else "disabled")

                if reset:
                    emotion_var.set("")

            character_combo.bind(
                "<<ComboboxSelected>>", lambda event=None: refresh_emotion_options(reset=True)
            )
            refresh_emotion_options(reset=False)

        elif action_type in ("move", "enter"):

            for campo, rotulo in (
                ("position", "Position:"), ("scale", "Scale:"),
                ("offset_x", "Offset X:"), ("offset_y", "Offset Y:"),
            ):
                tk.Label(parent, text=rotulo).grid(row=row, column=0, sticky="w", **pad)
                var = tk.StringVar(value=valor_inicial(campo))
                tk.Entry(parent, textvariable=var, width=12).grid(
                    row=row, column=1, sticky="w", **pad
                )
                field_vars[campo] = var
                row += 1

        elif action_type == "pause":

            tk.Label(parent, text="Duration (s):").grid(row=row, column=0, sticky="w", **pad)
            duration_var = tk.StringVar(value=valor_inicial("duration"))
            tk.Entry(parent, textvariable=duration_var, width=12).grid(
                row=row, column=1, sticky="w", **pad
            )
            field_vars["duration"] = duration_var

        # "exit" não tem campo além de Character, já montado acima.

    # Lê os StringVar de `field_vars` e monta os kwargs pra
    # add_story_action()/StoryData.add_action() -- position/scale/
    # offset em move/enter são opcionais (campo em branco = não entra
    # nos kwargs); position é obrigatório em enter (ActionData exige).
    # Levanta ValueError com mensagem pronta pra mostrar em qualquer
    # campo inválido -- é o Studio validando ENTRADA de diálogo (tipo/
    # formato), não regra de domínio (isso já mora no Project System,
    # ver Fase A do hardening).
    def _action_kwargs_from_vars(self, action_type, field_vars):

        kwargs = {}

        if "character" in field_vars:
            character = field_vars["character"].get()
            if not character:
                raise ValueError("Escolha um personagem.")
            kwargs["character"] = character

        if action_type == "speak":

            text = field_vars["text"].get()
            if not text.strip():
                raise ValueError("Informe o texto da fala.")
            kwargs["text"] = text

        elif action_type == "emotion":

            emotion = field_vars["emotion"].get()
            if not emotion:
                raise ValueError("Escolha uma emoção.")
            kwargs["emotion"] = emotion

        elif action_type in ("move", "enter"):

            posicao = field_vars["position"].get().strip()

            if action_type == "enter" and not posicao:
                raise ValueError("Position é obrigatório em enter.")

            if posicao:
                kwargs["position"] = int(posicao)

            escala = field_vars["scale"].get().strip()
            if escala:
                kwargs["scale"] = float(escala)

            offset_x = field_vars["offset_x"].get().strip()
            if offset_x:
                kwargs["offset_x"] = int(offset_x)

            offset_y = field_vars["offset_y"].get().strip()
            if offset_y:
                kwargs["offset_y"] = int(offset_y)

        elif action_type == "pause":

            duracao = field_vars["duration"].get().strip()
            if not duracao:
                raise ValueError("Informe a duração.")
            kwargs["duration"] = float(duracao)

        return kwargs

    # Adiciona a Action de verdade -- separado do diálogo, testável
    # direto. Repassa pro Core; ao terminar, reconstrói o Story Editor
    # pra mostrar a Action nova na lista.
    def add_story_action(self, story_key, action_type, **fields):

        try:
            self.core.add_story_action(story_key, action_type, **fields)

        except StudioError as error:
            messagebox.showerror(APP_TITLE, str(error))
            return False

        self._update_title()  # o Core já marcou dirty
        self._show_properties(f"story:{story_key}")

        return True

    # Resumo somente-leitura: thumbnail (se aplicável) + texto.
    def _build_readonly_properties(self, text, thumbnail_iid):

        self.properties_image_label = tk.Label(self.properties_content)
        self.properties_image_label.pack(padx=8, pady=(8, 0))

        self.properties_label = tk.Label(
            self.properties_content,
            text=text,
            justify=tk.LEFT,
            anchor="nw",
            fg="gray40",
            padx=8,
            pady=8,
        )
        self.properties_label.pack(fill=tk.BOTH, expand=True)

        self._update_properties_thumbnail(thumbnail_iid)

    # Mostra a thumbnail do asset selecionado (se ele tiver imagem) no
    # painel Properties, ou some com a thumbnail se não tiver.
    # tkinter.PhotoImage (nativo, sem Pillow) -- suporta PNG direto.
    def _update_properties_thumbnail(self, iid):

        image = self._load_thumbnail(iid) if iid is not None else None

        self.properties_image_label.config(image=image or "")
        self.properties_image_label.image = image  # guarda a referência (senão o Tk descarta)

    def _load_thumbnail(self, iid):

        if not iid.startswith("asset:") or self.project is None:
            return None

        asset = self.project.assets.get(iid.split(":", 1)[1])

        if asset is None or asset.type not in self._IMAGE_ASSET_TYPES:
            return None

        path = self._resolve_project_path(asset.path)

        if not os.path.isfile(path):
            return None

        try:
            image = tk.PhotoImage(file=path)

        except tk.TclError:
            return None  # formato que o tkinter não sabe abrir (ex: JPEG)

        maior_lado = max(image.width(), image.height())
        fator = max(1, maior_lado // 96)

        if fator > 1:
            image = image.subsample(fator, fator)

        return image

    # Caminho guardado no projeto (relativo à pasta do projeto) ->
    # caminho de verdade, igual à resolução usada pelo Runtime
    # (project/runtime_loader.py), sem precisar importar aquele
    # módulo aqui (que puxaria Character/Canvas/Engine/pygame só pra
    # mostrar uma thumbnail).
    def _resolve_project_path(self, path):

        if os.path.isabs(path):
            return path

        base = (self.project.loaded_from if self.project else None) or os.getcwd()

        return os.path.join(base, path)

    # Monta o texto do painel Properties pro item selecionado na
    # árvore -- linguagem simples, sem termos internos (nome/imagem/
    # emoção, não "asset id"/"registry key").
    def _describe_selection(self, iid):

        project = self.project

        if iid == "project":
            return self._project_summary_text()

        if iid.startswith("category:"):
            return self._category_summary_text(iid.split(":", 1)[1])

        if iid.startswith("assetcat:"):
            tipo = iid.split(":", 1)[1]
            label = self.ASSET_CATEGORY_LABELS.get(tipo, "Other")
            quantidade = len(self.asset_tree.get_children(iid))
            return f"{label}: {quantidade}"

        kind, _, key = iid.partition(":")

        if kind == "character":
            data = project.characters[key]
            emocoes = ", ".join(sorted(data.emotions)) or "(nenhuma)"
            return f"Personagem: {data.name}\nEmoções: {emocoes}"

        if kind == "scene":
            data = project.scenes[key]
            return (
                f"Cena: {data.name}\n"
                f"Fundo: {data.background or '(nenhum)'}\n"
                f"Música: {data.music or '(nenhuma)'}\n"
                f"Personagens na cena: {len(data.characters)}"
            )

        if kind == "asset":
            data = project.assets[key]
            return f"Asset: {data.id}\nTipo: {data.type}\nCaminho: {data.path}"

        return ""

    def _project_summary_text(self):

        project = self.project
        largura, altura = project.resolution
        nomes_das_cenas = ", ".join(sorted(project.scenes)) or "(nenhuma)"

        return (
            f"Nome: {project.name}\n"
            f"Resolução: {largura} × {altura}\n"
            f"Cenas: {nomes_das_cenas}\n"
            f"Assets: {len(project.assets)}"
        )

    def _category_summary_text(self, kind):

        project = self.project

        rotulos = {
            "character": ("Personagens", project.characters),
            "scene": ("Cenas", project.scenes),
            "story": ("Histórias", project.stories),
            "asset": ("Assets", project.assets),
        }

        nome, colecao = rotulos[kind]

        return f"{nome}: {len(colecao)}"

    # --- Character Editor -------------------------------------------
    #
    # Primeiro editor de verdade do Studio. Edita CharacterData (dado
    # de projeto) -- NUNCA o Character de Runtime (src/MyNovellib/
    # character.py), que nem é importado aqui. O fluxo é:
    #
    #     Studio edita CharacterData -> File > Save grava no projeto
    #     -> o Runtime transforma CharacterData em Character depois
    #        (Project Runtime Loading), quando o projeto for rodado.
    #
    # Nada aqui salva em disco sozinho -- só marca dirty (mark_dirty).

    def _build_character_editor(self, character_key):

        data = self.project.characters[character_key]
        parent = self.properties_content

        tk.Label(
            parent, text="CHARACTER", anchor="w", font=("", 9, "bold")
        ).pack(fill=tk.X, padx=8, pady=(8, 0))

        name_row = tk.Frame(parent)
        name_row.pack(fill=tk.X, padx=8, pady=(8, 4))
        tk.Label(name_row, text="Name:", width=8, anchor="w").pack(side=tk.LEFT)

        name_var = tk.StringVar(value=data.name)
        tk.Entry(name_row, textvariable=name_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )

        def on_name_change(*_):

            novo_nome = name_var.get().strip()

            if not novo_nome or novo_nome == data.name:
                return

            data.name = novo_nome
            self.mark_dirty()

            item_id = f"character:{character_key}"
            if self.explorer.exists(item_id):
                self.explorer.item(item_id, text=novo_nome)

        name_var.trace_add("write", on_name_change)

        tk.Label(
            parent, text="Emotions:", anchor="w", font=("", 9, "bold")
        ).pack(fill=tk.X, padx=8, pady=(12, 0))

        emotions_area = tk.Frame(parent)
        emotions_area.pack(fill=tk.BOTH, expand=True, padx=8)

        for emotion_name in sorted(data.emotions):
            self._build_emotion_row(emotions_area, data, character_key, emotion_name)

        tk.Button(
            parent,
            text="+ Add Emotion",
            command=lambda: self._open_add_emotion_dialog(character_key),
        ).pack(anchor="w", padx=8, pady=(8, 8))

        tk.Button(
            parent,
            text="Delete Character",
            fg="red3",
            command=lambda: self._delete_character(character_key),
        ).pack(anchor="w", padx=8, pady=(0, 8))

    def _build_emotion_row(self, parent, data, character_key, emotion_name):

        sprites = data.emotions[emotion_name]

        row = tk.LabelFrame(parent, text=emotion_name, padx=6, pady=4)
        row.pack(fill=tk.X, pady=4)

        idle_var = tk.StringVar(value=sprites.get("idle") or "")
        talking_var = tk.StringVar(value=sprites.get("talking") or "")

        def on_idle_change(*_):
            data.emotions[emotion_name]["idle"] = idle_var.get().strip()
            self.mark_dirty()

        def on_talking_change(*_):
            valor = talking_var.get().strip()
            data.emotions[emotion_name]["talking"] = valor or None
            self.mark_dirty()

        idle_var.trace_add("write", on_idle_change)
        talking_var.trace_add("write", on_talking_change)

        idle_row = tk.Frame(row)
        idle_row.pack(fill=tk.X)
        tk.Label(idle_row, text="Idle:", width=8, anchor="w").pack(side=tk.LEFT)
        tk.Entry(idle_row, textvariable=idle_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        tk.Button(
            idle_row, text="Browse...", command=lambda: self._browse_sprite(idle_var)
        ).pack(side=tk.LEFT, padx=(4, 0))

        talking_row = tk.Frame(row)
        talking_row.pack(fill=tk.X, pady=(2, 0))
        tk.Label(talking_row, text="Talking:", width=8, anchor="w").pack(side=tk.LEFT)
        tk.Entry(talking_row, textvariable=talking_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        tk.Button(
            talking_row,
            text="Browse...",
            command=lambda: self._browse_sprite(talking_var),
        ).pack(side=tk.LEFT, padx=(4, 0))

        tk.Button(
            row,
            text="Remove Emotion",
            fg="red3",
            command=lambda: self._remove_emotion(character_key, emotion_name),
        ).pack(anchor="e", pady=(4, 0))

    def _browse_sprite(self, string_var):

        path = filedialog.askopenfilename(
            title="Choose Image",
            filetypes=[("Images", "*.png *.gif *.ppm *.pgm"), ("Todos os arquivos", "*.*")],
        )

        if path:
            string_var.set(path)

    def _remove_emotion(self, character_key, emotion_name):

        self.core.remove_emotion(character_key, emotion_name)

        self._update_title()  # o Core já marcou dirty
        self._show_properties(f"character:{character_key}")

    # Pede confirmação (diferente de Remove Emotion -- apagar um
    # personagem inteiro é mais impactante que apagar uma emoção, e
    # não tem "desfazer") antes de repassar pro Core, que bloqueia com
    # StudioError se o personagem estiver em uso em alguma cena/
    # história (nunca remove em cascata).
    def _delete_character(self, character_key):

        nome = self.project.characters[character_key].name

        if not messagebox.askyesno(APP_TITLE, f'Remover o personagem "{nome}"?'):
            return

        try:
            self.core.delete_character(character_key)

        except StudioError as error:
            messagebox.showerror(APP_TITLE, str(error))
            return

        self._update_title()  # o Core já marcou dirty
        self._refresh_explorer()

    def _open_add_emotion_dialog(self, character_key):

        dialog = tk.Toplevel(self.root)
        dialog.title("Add Emotion")
        dialog.transient(self.root)
        dialog.resizable(False, False)

        name_var = tk.StringVar()
        idle_var = tk.StringVar()
        talking_var = tk.StringVar()

        pad = {"padx": 8, "pady": 4}

        tk.Label(dialog, text="Emotion name:").grid(row=0, column=0, sticky="w", **pad)
        tk.Entry(dialog, textvariable=name_var, width=28).grid(
            row=0, column=1, columnspan=2, sticky="we", **pad
        )

        tk.Label(dialog, text="Idle:").grid(row=1, column=0, sticky="w", **pad)
        tk.Entry(dialog, textvariable=idle_var, width=28).grid(
            row=1, column=1, sticky="we", **pad
        )
        tk.Button(
            dialog, text="Browse...", command=lambda: self._browse_sprite(idle_var)
        ).grid(row=1, column=2, **pad)

        tk.Label(dialog, text="Talking (optional):").grid(
            row=2, column=0, sticky="w", **pad
        )
        tk.Entry(dialog, textvariable=talking_var, width=28).grid(
            row=2, column=1, sticky="we", **pad
        )
        tk.Button(
            dialog, text="Browse...", command=lambda: self._browse_sprite(talking_var)
        ).grid(row=2, column=2, **pad)

        def on_add():

            criado = self.add_emotion(
                character_key, name_var.get(), idle_var.get(), talking_var.get()
            )

            if criado:
                dialog.destroy()

        tk.Button(dialog, text="Add", command=on_add).grid(
            row=3, column=0, columnspan=3, pady=(12, 8)
        )

        self.add_emotion_dialog = dialog

        return dialog

    # Adiciona a emoção de verdade -- separado do diálogo, testável
    # direto. Repassa pro Core (que reaproveita CharacterData.
    # add_emotion() e a validação de lá) -- o Studio não valida nada
    # por conta própria, só mostra o StudioError que vier de lá.
    def add_emotion(self, character_key, name, idle, talking=""):

        try:
            self.core.add_emotion(character_key, name, idle, talking)

        except StudioError as error:
            messagebox.showerror(APP_TITLE, str(error))
            return False

        self._update_title()  # o Core já marcou dirty
        self._show_properties(f"character:{character_key}")

        return True

    # --- Scene Editor ---------------------------------------------------
    #
    # Primeiro canvas visual do Studio: mostra o background e os
    # personagens de uma cena (SceneData), na posição/escala/offset
    # certos. Ainda não é um editor profissional -- sem
    # drag-and-drop; clicar num personagem seleciona, e os valores
    # (Position/Scale/Emotion/Offset X/Offset Y) são editados
    # numericamente no painel Properties.
    #
    # Reaproveita a MESMA fórmula de posição que a Engine usa
    # (draw_characters() em engine.py: 1/2/3 -> 25%/50%/75% da
    # largura, pés alinhados embaixo) -- é matemática de layout
    # simples e estável, não a lógica de execução da Engine (loop de
    # eventos, timing, Actions). Sem isso reproduzido aqui, não
    # existiria NENHUM preview visual possível (uma Surface do pygame
    # não entra dentro de um tk.Canvas).
    #
    # Edita SceneData/SceneCharacter (Project Data) -- Canvas de
    # Runtime (src/MyNovellib/scene.py) não é importado aqui.

    SCENE_PREVIEW_MAX_WIDTH = 480
    SCENE_X_POSITIONS = {1: 0.25, 2: 0.50, 3: 0.75}

    def _build_scene_editor(self, scene_key):

        parent = self.properties_content
        data = self.project.scenes[scene_key]

        tk.Label(
            parent, text="SCENE", anchor="w", font=("", 9, "bold")
        ).pack(fill=tk.X, padx=8, pady=(8, 0))

        width, height = data.resolution or self.project.resolution
        factor = max(1, round(width / self.SCENE_PREVIEW_MAX_WIDTH))

        canvas = tk.Canvas(
            parent,
            width=max(1, width // factor),
            height=max(1, height // factor),
            bg="gray20",
            highlightthickness=1,
            highlightbackground="gray50",
        )
        canvas.pack(padx=8, pady=8)
        canvas.bind("<ButtonPress-1>", self._on_scene_canvas_press)
        canvas.bind("<B1-Motion>", self._on_scene_canvas_drag)
        canvas.bind("<ButtonRelease-1>", self._on_scene_canvas_release)

        self.scene_canvas = canvas
        self.scene_editor_key = scene_key
        self.scene_preview_factor = factor
        self.scene_selected_index = None
        self._scene_canvas_images = []
        self._scene_item_bounds = {}
        self._scene_drag = None

        self.scene_properties_frame = tk.Frame(parent)
        self.scene_properties_frame.pack(fill=tk.X, padx=8, pady=(0, 8))

        # fora de scene_properties_frame de propósito -- aquele frame é
        # reconstruído a cada seleção de personagem (_render_scene_properties),
        # e o botão de apagar a cena inteira não deve piscar/mudar com isso.
        tk.Button(
            parent,
            text="Delete Scene",
            fg="red3",
            command=lambda: self._delete_scene(scene_key),
        ).pack(anchor="w", padx=8, pady=(0, 8))

        self._render_scene_canvas()
        self._render_scene_properties()

    # Pede confirmação, repassa pro Core (que hoje não bloqueia --
    # nada no modelo de dados referencia uma cena por chave, ver
    # StudioCore.delete_scene) e atualiza o Explorer.
    def _delete_scene(self, scene_key):

        nome = self.project.scenes[scene_key].name

        if not messagebox.askyesno(APP_TITLE, f'Remover a cena "{nome}"?'):
            return

        try:
            self.core.delete_scene(scene_key)

        except StudioError as error:
            messagebox.showerror(APP_TITLE, str(error))
            return

        self._update_title()  # o Core já marcou dirty
        self._refresh_explorer()

    # Redesenha o canvas inteiro (background + personagens + contorno
    # de seleção). Chamado sempre que algo muda -- é uma cena estática
    # (sem animação ainda), redesenhar tudo é simples e barato o
    # bastante pra esse tamanho de preview.
    def _render_scene_canvas(self):

        canvas = self.scene_canvas
        canvas.delete("all")

        data = self.project.scenes[self.scene_editor_key]
        factor = self.scene_preview_factor

        self._scene_canvas_images = []
        self._scene_item_bounds = {}

        bg_image = self._load_scaled_image(data.background, factor)

        if bg_image is not None:
            canvas.create_image(0, 0, anchor="nw", image=bg_image)
            self._scene_canvas_images.append(bg_image)

        for index, placement in enumerate(data.characters):
            self._draw_scene_character(canvas, placement, index, factor)

        if self.scene_selected_index in self._scene_item_bounds:
            x, y, w, h = self._scene_item_bounds[self.scene_selected_index]
            canvas.create_rectangle(
                x, y, x + w, y + h, outline="yellow", width=2, tags=("selection",)
            )

    def _load_scaled_image(self, path, factor):

        if not path:
            return None

        resolved = self._resolve_project_path(path)

        if not os.path.isfile(resolved):
            return None

        try:
            image = tk.PhotoImage(file=resolved)
        except tk.TclError:
            return None

        if factor > 1:
            image = image.subsample(factor, factor)

        return image

    # Sprite "idle" a usar no preview: a emoção do placement, se
    # registrada; senão a primeira emoção cadastrada (em ordem
    # alfabética), só pra sempre ter algo pra mostrar.
    def _character_sprite_for_preview(self, character_key, emotion_name):

        character_data = self.project.characters.get(character_key)

        if character_data is None or not character_data.emotions:
            return None

        nome = emotion_name if emotion_name in character_data.emotions else sorted(character_data.emotions)[0]

        return character_data.emotions[nome]["idle"]

    def _draw_scene_character(self, canvas, placement, index, factor):

        sprite_path = self._character_sprite_for_preview(placement.character, placement.emotion)

        if not sprite_path:
            return

        resolved = self._resolve_project_path(sprite_path)

        if not os.path.isfile(resolved):
            return

        try:
            image = tk.PhotoImage(file=resolved)
        except tk.TclError:
            return

        # combina a redução do preview com a escala do personagem.
        # PhotoImage só reduz (subsample) -- scale >= 1 não amplia
        # além do tamanho do preview; aproximação aceitável pra um
        # editor que ainda não é profissional.
        escala = max(placement.scale, 0.01)
        combined_factor = max(1, round(factor / escala)) if escala < 1 else factor

        if combined_factor > 1:
            image = image.subsample(combined_factor, combined_factor)

        self._scene_canvas_images.append(image)

        canvas_width = int(canvas["width"])
        canvas_height = int(canvas["height"])

        center_x = int(canvas_width * self.SCENE_X_POSITIONS.get(placement.position, 0.5))
        x = center_x - image.width() // 2 + int(placement.offset_x / factor)
        y = canvas_height - image.height() + int(placement.offset_y / factor)

        canvas.create_image(x, y, anchor="nw", image=image, tags=(f"placement:{index}",))

        self._scene_item_bounds[index] = (x, y, image.width(), image.height())

    # Clique: seleciona o personagem (ou desseleciona, se for fora de
    # qualquer um) e guarda o estado inicial do arraste, caso o mouse
    # se mova em seguida com o botão pressionado.
    def _on_scene_canvas_press(self, event):

        canvas = event.widget
        itens = canvas.find_overlapping(event.x, event.y, event.x, event.y)

        for item in reversed(itens):
            for tag in canvas.gettags(item):

                if tag.startswith("placement:"):

                    index = int(tag.split(":", 1)[1])
                    self._select_scene_character(index)

                    placement = self.project.scenes[self.scene_editor_key].characters[index]

                    self._scene_drag = {
                        "index": index,
                        "start_x": event.x,
                        "start_y": event.y,
                        "offset_x": placement.offset_x,
                        "offset_y": placement.offset_y,
                    }

                    return

        self._scene_drag = None
        self._select_scene_character(None)

    # Arrastar: move o personagem em tempo real, ajustando
    # offset_x/offset_y (a posição -- slot 1/2/3 -- continua a mesma;
    # arrastar faz um ajuste fino, igual os campos numéricos de
    # Offset X/Y já permitiam, só que com o mouse).
    def _on_scene_canvas_drag(self, event):

        drag = self._scene_drag

        if drag is None:
            return

        data = self.project.scenes[self.scene_editor_key]

        if drag["index"] >= len(data.characters):
            return

        placement = data.characters[drag["index"]]
        factor = self.scene_preview_factor

        delta_x = int((event.x - drag["start_x"]) * factor)
        delta_y = int((event.y - drag["start_y"]) * factor)

        placement.offset_x = drag["offset_x"] + delta_x
        placement.offset_y = drag["offset_y"] + delta_y

        self.mark_dirty()
        self._render_scene_canvas()
        self._render_scene_properties()

    def _on_scene_canvas_release(self, event):
        self._scene_drag = None

    def _select_scene_character(self, index):

        self.scene_selected_index = index
        self._render_scene_canvas()
        self._render_scene_properties()

    # Painel Properties da Scene: Character (informativo -- trocar de
    # personagem não é editável ainda), Position/Scale/Offset X/
    # Offset Y (numéricos) e Emotion (lista das emoções cadastradas
    # pro personagem).
    def _render_scene_properties(self):

        for widget in self.scene_properties_frame.winfo_children():
            widget.destroy()

        data = self.project.scenes[self.scene_editor_key]
        index = self.scene_selected_index

        if index is None or index >= len(data.characters):
            tk.Label(
                self.scene_properties_frame,
                text="Clique num personagem na cena para editar.",
                fg="gray40",
                anchor="w",
            ).pack(fill=tk.X)
            return

        placement = data.characters[index]

        tk.Label(
            self.scene_properties_frame,
            text=f"Character: {placement.character}",
            anchor="w",
            font=("", 9, "bold"),
        ).pack(fill=tk.X, pady=(4, 6))

        self._build_scene_numeric_field(
            "Position:", placement.position,
            lambda valor: self._apply_scene_field(index, "position", valor, int),
        )
        self._build_scene_numeric_field(
            "Scale:", placement.scale,
            lambda valor: self._apply_scene_field(index, "scale", valor, float),
        )
        self._build_scene_emotion_field(placement)
        self._build_scene_numeric_field(
            "Offset X:", placement.offset_x,
            lambda valor: self._apply_scene_field(index, "offset_x", valor, int),
        )
        self._build_scene_numeric_field(
            "Offset Y:", placement.offset_y,
            lambda valor: self._apply_scene_field(index, "offset_y", valor, int),
        )

    def _build_scene_numeric_field(self, label, initial, on_commit):

        row = tk.Frame(self.scene_properties_frame)
        row.pack(fill=tk.X, pady=2)

        tk.Label(row, text=label, width=10, anchor="w").pack(side=tk.LEFT)

        var = tk.StringVar(value=str(initial))
        entry = tk.Entry(row, textvariable=var)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        def commit(event=None):
            on_commit(var.get())

        entry.bind("<Return>", commit)
        entry.bind("<FocusOut>", commit)

    def _build_scene_emotion_field(self, placement):

        row = tk.Frame(self.scene_properties_frame)
        row.pack(fill=tk.X, pady=2)

        tk.Label(row, text="Emotion:", width=10, anchor="w").pack(side=tk.LEFT)

        character_data = self.project.characters.get(placement.character)
        opcoes = sorted(character_data.emotions) if character_data else []

        var = tk.StringVar(value=placement.emotion or "")
        combo = ttk.Combobox(
            row,
            textvariable=var,
            values=opcoes,
            state="readonly" if opcoes else "disabled",
        )
        combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        def on_select(event=None):
            placement.emotion = var.get() or None
            self.mark_dirty()
            self._render_scene_canvas()

        combo.bind("<<ComboboxSelected>>", on_select)

    # `parse` só faz a conversão de tipo (str -> int/float) -- quem valida
    # o VALOR (position precisa ser 1/2/3, scale precisa ser > 0) é o
    # próprio SceneCharacter (property setter, ver project/scene_data.py),
    # não o Studio nem o Core. Repassa pro Core; um valor ruim ou um
    # tipo inválido chegam aqui do mesmo jeito, como StudioError.
    def _apply_scene_field(self, index, field, raw_value, parse):

        try:
            self.core.apply_scene_field(self.scene_editor_key, index, field, raw_value, parse)

        except StudioError as error:
            messagebox.showerror(APP_TITLE, str(error))
            self._render_scene_properties()  # volta pro valor antigo
            return

        self._update_title()  # o Core já marcou dirty

        self._render_scene_canvas()
        self._render_scene_properties()

    # --- Play ---------------------------------------------------------
    #
    #     Studio -> Project -> create_runtime() -> Runtime -> Game
    #
    # Reaproveita a Engine existente (Project System Update, Waystone
    # 9) -- NENHUMA Engine paralela. create_runtime() trabalha em cima
    # do Project em memória (não precisa estar salvo em disco antes --
    # Play sempre reflete o estado atual, mesmo com alterações não
    # salvas).
    #
    # Integração: engine.run() é uma chamada bloqueante comum, feita
    # aqui de dentro do callback do botão -- ela abre a JANELA DO JOGO
    # (pygame) e só retorna quando a história termina ou a janela do
    # jogo é fechada. Como isso acontece dentro do próprio callback da
    # Tkinter mainloop, a janela do Studio fica sem processar eventos
    # (visualmente parada) enquanto o jogo roda -- exatamente como
    # aconteceria com qualquer diálogo modal -- e volta a responder
    # normalmente assim que engine.run() retorna. É a integração mais
    # direta que a arquitetura atual já permite, sem precisar rodar
    # pygame numa thread separada (frágil -- SDL não é pensado pra
    # isso) nem criar um processo/Engine paralelos.
    def play_project(self):

        if self.project is None:
            return

        try:
            runtime = self.project.create_runtime()

        except Exception as error:
            messagebox.showerror(
                APP_TITLE, f"Não foi possível preparar o projeto para rodar:\n\n{error}"
            )
            return

        self.set_status(f'Rodando "{self.project.name}"...')

        try:
            runtime.run()

        except ValueError as error:
            # ProjectRuntime.run() levanta isso quando há mais de uma
            # cena/história e nenhuma foi escolhida -- ainda não existe
            # UI pra escolher, então mostramos o motivo em vez de
            # adivinhar ou travar.
            messagebox.showerror(APP_TITLE, f"Não foi possível rodar o projeto:\n\n{error}")

        except Exception as error:
            messagebox.showerror(APP_TITLE, f"Erro ao rodar o projeto:\n\n{error}")

        self.set_status(f'"{self.project.name}" -- de volta ao Studio.')

    # --- Salvar -------------------------------------------------------
    #
    # O salvamento em si (Project.save()) mora no Core -- nenhum
    # sistema de persistência paralelo aqui.

    def save_project(self):

        if self.project is None:
            return

        if self.project_path is None:
            # nunca foi salvo em lugar nenhum ainda -- pede onde salvar,
            # igual Save As.
            self.save_project_as()
            return

        self._save_project_to(self.project_path)

    def save_project_as(self):

        if self.project is None:
            return

        path = filedialog.asksaveasfilename(
            title="Save Project As",
            defaultextension=".mynovel",
            filetypes=[("MyNovel Project", "*.mynovel")],
        )

        if not path:
            return  # usuário cancelou

        self._save_project_to(path)

    # Onde o salvamento de fato acontece -- separado pra ser testável
    # sem precisar simular o file dialog do Save As.
    def _save_project_to(self, path):

        self.core.save_project_to(path)

        self._update_title()  # o Core já limpou o dirty ao salvar
        self.set_status(f'Projeto "{self.project.name}" salvo.')

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

    # Protege alterações não salvas: se houver alguma (self.dirty),
    # pergunta antes de fechar. Sim salva e fecha; Não fecha sem
    # salvar; Cancelar mantém a janela aberta.
    def on_close(self):

        if self.dirty:

            resposta = messagebox.askyesnocancel(
                APP_TITLE,
                f'O projeto "{self.project.name}" tem alterações não salvas.\n'
                f"Deseja salvar antes de sair?",
            )

            if resposta is None:  # Cancelar
                return

            if resposta is True:  # Sim
                self.save_project()

        self.root.destroy()

    def run(self):
        self.root.mainloop()
