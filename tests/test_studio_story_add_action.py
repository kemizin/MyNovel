# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_studio_story_add_action.py
#
# Hardening, Waystone "story add action": botão "+ Add Action" no
# Story Editor abre um diálogo cujos campos mudam de acordo com o
# tipo escolhido (speak/emotion/move/enter/exit/pause) -- mesmo
# princípio do "+ Add Emotion" já existente.
#
# Usa tkinter DE VERDADE com root.withdraw() -- nunca aparece nada na
# tela.

import os
import sys
import tempfile
import shutil
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.studio.app import StudioApp
from src.MyNovellib.project.model import Project

root = tk.Tk()
root.withdraw()
app = StudioApp(root=root)

tmp_dir = tempfile.mkdtemp(prefix="mynovel_test_addaction_")
try:
    app.create_new_project("Projeto Actions", tmp_dir, "800", "600")
    app.create_character("Mika")
    app.add_emotion("mika", "normal", idle="assets/backgrounds/praca.png")
    app.add_emotion("mika", "feliz", idle="assets/backgrounds/quarto.png")
    app.create_story("Intro")

    app.dirty = False

    # --- add_story_action(): a versão testável direta (mesmo padrão
    # de add_emotion/create_character) -- sem passar pelo diálogo ---
    criado = app.add_story_action("intro", "speak", character="mika", text="Oi!")

    assert criado is True
    assert len(app.project.stories["intro"].actions) == 1
    assert app.story_listbox.size() == 1  # a lista já reflete a Action nova
    assert app.story_listbox.get(0) == app.project.stories["intro"].actions[0].describe()
    assert app.dirty is True

    # --- _action_kwargs_from_vars(): lê os campos certos por tipo ---
    def fake_vars(**valores):
        return {chave: tk.StringVar(value=valor) for chave, valor in valores.items()}

    kwargs = app._action_kwargs_from_vars(
        "enter", fake_vars(character="mika", position="2", scale="0.6", offset_x="", offset_y="")
    )
    assert kwargs == {"character": "mika", "position": 2, "scale": 0.6}

    kwargs = app._action_kwargs_from_vars("pause", fake_vars(duration="1.5"))
    assert kwargs == {"duration": 1.5}

    kwargs = app._action_kwargs_from_vars("exit", fake_vars(character="mika"))
    assert kwargs == {"character": "mika"}

    # campo obrigatório vazio levanta ValueError com mensagem clara
    for tipo, valores, motivo in (
        ("speak", dict(character="mika", text=""), "texto vazio"),
        ("emotion", dict(character="mika", emotion=""), "emoção vazia"),
        ("enter", dict(character="mika", position="", scale="", offset_x="", offset_y=""), "position obrigatório em enter"),
        ("pause", dict(duration=""), "duration vazio"),
        ("speak", dict(character="", text="oi"), "personagem não escolhido"),
    ):
        try:
            app._action_kwargs_from_vars(tipo, fake_vars(**valores))
            assert False, f"esperava ValueError ({motivo})"
        except ValueError:
            pass

    # tipo/valor não numérico também vira ValueError (Position/Scale
    # esperam número)
    try:
        app._action_kwargs_from_vars(
            "enter", fake_vars(character="mika", position="abc", scale="", offset_x="", offset_y="")
        )
        assert False, "esperava ValueError (position não numérico)"
    except ValueError:
        pass

    # --- diálogo de verdade: campos mudam com o tipo, character é
    # sempre combobox com os personagens do projeto ---
    dialog = app._open_add_action_dialog("intro")
    assert isinstance(dialog, tk.Toplevel)
    assert dialog.title() == "Add Action"
    dialog.destroy()

    # --- _build_action_type_fields: monta os campos certos por tipo,
    # e a emoção cascadeia a partir do personagem escolhido ---
    frame = tk.Frame(app.root)
    field_vars = {}
    app._build_action_type_fields(frame, "speak", field_vars)
    assert set(field_vars) == {"character", "text"}

    frame2 = tk.Frame(app.root)
    field_vars2 = {}
    app._build_action_type_fields(frame2, "pause", field_vars2)
    assert set(field_vars2) == {"duration"}  # "pause" não tem Character

    frame3 = tk.Frame(app.root)
    field_vars3 = {}
    app._build_action_type_fields(frame3, "emotion", field_vars3)
    assert set(field_vars3) == {"character", "emotion"}

    character_combo = [
        w for w in frame3.winfo_children()
        if isinstance(w, ttk.Combobox) and str(w.cget("textvariable")) == str(field_vars3["character"])
    ][0]
    assert set(character_combo.cget("values")) == {"mika"}

    field_vars3["character"].set("mika")
    character_combo.event_generate("<<ComboboxSelected>>")
    assert field_vars3["emotion"].get() == ""  # limpa ao trocar de personagem

    # --- erro do Core (tipo não suportado) vira messagebox ---
    erros = []
    original_showerror = messagebox.showerror
    messagebox.showerror = lambda titulo, msg: erros.append(msg)
    try:
        assert app.add_story_action("intro", "choice", options=["A"]) is False
    finally:
        messagebox.showerror = original_showerror
    assert len(erros) == 1
    assert len(app.project.stories["intro"].actions) == 1  # não adicionou nada

    app.dirty = False
    app.on_close()

finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)

# =================================================================
# Persistência: adicionar Action -> salvar -> fechar -> reabrir ->
# Action continua lá, na ordem certa.
# =================================================================

tmp_dir2 = tempfile.mkdtemp(prefix="mynovel_test_addaction_persist_")
try:
    root2 = tk.Tk()
    root2.withdraw()
    app2 = StudioApp(root=root2)
    app2.create_new_project("Persistencia Action", tmp_dir2, "800", "600")
    app2.create_character("Ken")

    app2.create_story("Nova Historia")
    app2.add_story_action("nova_historia", "speak", character="ken", text="Uma")
    app2.add_story_action("nova_historia", "pause", duration=1)
    app2.add_story_action("nova_historia", "exit", character="ken")

    app2.save_project()
    app2.on_close()

    root3 = tk.Tk()
    root3.withdraw()
    app3 = StudioApp(root=root3)
    app3.load_project(app2.project_path)

    acoes = app3.project.stories["nova_historia"].actions
    assert [a.type for a in acoes] == ["speak", "pause", "exit"]
    assert acoes[0].fields["text"] == "Uma"

    app3.on_close()

    reloaded = Project.load(app2.project_path)
    assert [a.type for a in reloaded.stories["nova_historia"].actions] == ["speak", "pause", "exit"]

finally:
    shutil.rmtree(tmp_dir2, ignore_errors=True)

print("OK: + Add Action monta campos por tipo e adiciona a Action à história")
