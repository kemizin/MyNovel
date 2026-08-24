# Shell do MyNovel Studio: janela principal, menu, toolbar, área
# principal e status bar. Ainda sem funcionalidade real além de abrir/
# fechar -- cada Waystone seguinte liga um pedaço desta interface ao
# Project System existente (src/MyNovellib/project/).

import os

import tkinter as tk
from tkinter import messagebox, filedialog, ttk

from src.MyNovellib.project.model import Project
from src.MyNovellib.project.directory import create_project

APP_TITLE = "MyNovel Studio"


class StudioApp:

    # `root`: um tk.Tk() já existente (útil pra testes, que criam o
    # root e chamam .withdraw() antes de construir a interface). Sem
    # isso, cria um novo.
    def __init__(self, root=None):

        self.root = root if root is not None else tk.Tk()

        self.project = None
        self.project_path = None  # caminho exato do .mynovel aberto/salvo
        self.dirty = False

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

        # espelha os comandos de File -- mesma regra do menu: Save só
        # faz sentido com um projeto aberto.
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

    # Cria o projeto de verdade: valida os campos, reaproveita
    # create_project() (Project System Update, sem duplicar nenhuma
    # lógica de criação) e abre o projeto recém-criado no Studio.
    # Retorna True em sucesso, False se algo for inválido (e mostra o
    # erro correspondente) -- o diálogo usa o retorno pra saber se
    # pode se fechar.
    def create_new_project(self, name, location, width, height):

        name = (name or "").strip()
        location = (location or "").strip()

        if not name:
            messagebox.showerror(APP_TITLE, "Informe um nome para o projeto.")
            return False

        if not location:
            messagebox.showerror(APP_TITLE, "Informe onde o projeto deve ser criado.")
            return False

        try:
            width = int(width)
            height = int(height)

            if width <= 0 or height <= 0:
                raise ValueError

        except (TypeError, ValueError):
            messagebox.showerror(
                APP_TITLE, "Largura e altura precisam ser números inteiros positivos."
            )
            return False

        project_path = os.path.join(location, name)

        try:
            directory = create_project(project_path, name=name, resolution=(width, height))

        except FileExistsError as error:
            messagebox.showerror(
                APP_TITLE, f"Não foi possível criar o projeto:\n\n{error}"
            )
            return False

        self.load_project(directory.project_file)

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
    # Reaproveita Project.load() -- nenhuma lógica de carregamento
    # duplicada aqui.
    def load_project(self, path):

        try:
            project = Project.load(path)

        except (FileNotFoundError, ValueError) as error:
            messagebox.showerror(
                APP_TITLE, f"Não foi possível abrir o projeto:\n\n{error}"
            )
            return

        self.project = project
        self.project_path = os.path.abspath(path)
        self._on_project_loaded()

    def _on_project_loaded(self):

        self.root.title(f"{APP_TITLE} — {self.project.name}")
        self.set_status(f'Projeto "{self.project.name}" carregado.')
        self.dirty = False
        self._set_save_enabled(True)
        self._refresh_explorer()
        self._refresh_asset_browser()

    def _set_save_enabled(self, enabled):

        state = tk.NORMAL if enabled else tk.DISABLED

        self.menus["File"].entryconfig("Save", state=state)
        self.menus["File"].entryconfig("Save As...", state=state)
        self.toolbar_buttons["Save"].config(state=state)

    # Chamado por qualquer edição futura (Character/Scene/Story/
    # Project) pra marcar que existem alterações não salvas. Ainda
    # sem indicação visual no título (isso é o próximo Waystone,
    # Dirty State) -- aqui só o mecanismo que a proteção ao fechar
    # (on_close) e o Save já usam.
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

    # Reconstrói o painel Properties pro item selecionado. Character
    # tem um editor de verdade (Waystone 7); todo o resto continua
    # como resumo somente-leitura (com thumbnail sob demanda, se o
    # item for um asset de imagem).
    def _show_properties(self, iid):

        for widget in self.properties_content.winfo_children():
            widget.destroy()

        if iid.startswith("character:"):
            self._build_character_editor(iid.split(":", 1)[1])
            return

        self._build_readonly_properties(self._describe_selection(iid), thumbnail_iid=iid)

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

        if kind == "story":
            data = project.stories[key]
            return f"História: {data.name}\nAções: {len(data.actions)}"

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

        data = self.project.characters[character_key]

        del data.emotions[emotion_name]
        self.mark_dirty()

        self._show_properties(f"character:{character_key}")

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
    # direto. Reaproveita CharacterData.add_emotion() (Project System
    # Update, Waystone 5), inclusive a validação de lá (idle não
    # vazio).
    def add_emotion(self, character_key, name, idle, talking=""):

        data = self.project.characters[character_key]

        name = (name or "").strip()
        idle = (idle or "").strip()
        talking = (talking or "").strip() or None

        # CharacterData.add_emotion() só valida "idle" -- "name" vazio
        # é checado aqui, no nível da interface.
        if not name:
            messagebox.showerror(APP_TITLE, "Informe um nome para a emoção.")
            return False

        try:
            data.add_emotion(name, idle=idle, talking=talking)

        except ValueError as error:
            messagebox.showerror(APP_TITLE, str(error))
            return False

        self.mark_dirty()
        self._show_properties(f"character:{character_key}")

        return True

    # --- Salvar -------------------------------------------------------
    #
    # Usa Project.save() diretamente (Project System Update, Waystone
    # 2) -- nenhum sistema de persistência paralelo.

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

        self.project.save(path)

        self.project_path = os.path.abspath(path)
        self.project.loaded_from = os.path.dirname(self.project_path)

        self.dirty = False
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
