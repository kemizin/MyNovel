# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_studio_story_reorder_actions.py
#
# Hardening, Waystone "story reorder actions": botões "▲ Move Up"/
# "▼ Move Down" no painel de edição de uma Action trocam ela de lugar
# com a vizinha -- a ordem da lista é a ordem de execução da história,
# então isso é o único jeito de reorganizar sem remover e adicionar de
# novo.
#
# Usa tkinter DE VERDADE com root.withdraw() -- nunca aparece nada na
# tela.

import os
import sys
import tempfile
import shutil
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.studio.app import StudioApp
from src.MyNovellib.project.model import Project


def achar_botoes(widget):
    encontrados = []
    for filho in widget.winfo_children():
        if isinstance(filho, tk.Button):
            encontrados.append(filho)
        encontrados.extend(achar_botoes(filho))
    return encontrados


root = tk.Tk()
root.withdraw()
app = StudioApp(root=root)

tmp_dir = tempfile.mkdtemp(prefix="mynovel_test_reorderactions_")
try:
    app.create_new_project("Projeto Reorder", tmp_dir, "800", "600")
    app.create_character("Mika")
    app.create_story("Intro")

    app.add_story_action("intro", "speak", character="mika", text="Um")
    app.add_story_action("intro", "speak", character="mika", text="Dois")
    app.add_story_action("intro", "speak", character="mika", text="Três")

    def textos():
        return [a.fields["text"] for a in app.project.stories["intro"].actions]

    assert textos() == ["Um", "Dois", "Três"]

    # --- move_story_action(): a versão testável direta ---
    app.dirty = False
    app.story_listbox.selection_set(1)  # "Dois"
    app.move_story_action("intro", 1, -1)  # sobe

    assert textos() == ["Dois", "Um", "Três"]
    assert app.dirty is True
    # a seleção segue a Action que se moveu (agora no índice 0)
    assert app.story_listbox.curselection() == (0,)
    assert app.story_listbox.get(0) == app.project.stories["intro"].actions[0].describe()

    app.move_story_action("intro", 0, 1)  # desce de volta
    assert textos() == ["Um", "Dois", "Três"]
    assert app.story_listbox.curselection() == (1,)

    # --- já na ponta: no-op, não marca dirty, seleção não se perde ---
    app.dirty = False
    app.story_listbox.selection_set(0)
    app.move_story_action("intro", 0, -1)  # já é o primeiro
    assert textos() == ["Um", "Dois", "Três"]
    assert app.dirty is False
    assert app.story_listbox.curselection() == (0,)

    # --- botões desabilitados na ponta, habilitados no meio ---
    #
    # selection_set() programático (diferente de um clique real) NÃO
    # limpa a seleção anterior sozinho -- isso é comportamento do
    # bind de clique do "browse" mode, não do método. Por isso
    # selection_clear() explícito antes de cada nova seleção abaixo,
    # senão curselection() acumula índices de seleções antigas.
    app.story_listbox.selection_clear(0, tk.END)
    app.story_listbox.selection_set(0)
    app._on_story_action_select()
    botoes = {b.cget("text"): b for b in achar_botoes(app.story_action_properties_frame)}
    assert str(botoes["▲ Move Up"].cget("state")) == "disabled"
    assert str(botoes["▼ Move Down"].cget("state")) == "normal"

    app.story_listbox.selection_clear(0, tk.END)
    app.story_listbox.selection_set(2)
    app._on_story_action_select()
    botoes = {b.cget("text"): b for b in achar_botoes(app.story_action_properties_frame)}
    assert str(botoes["▲ Move Up"].cget("state")) == "normal"
    assert str(botoes["▼ Move Down"].cget("state")) == "disabled"

    app.story_listbox.selection_clear(0, tk.END)
    app.story_listbox.selection_set(1)
    app._on_story_action_select()
    botoes = {b.cget("text"): b for b in achar_botoes(app.story_action_properties_frame)}
    assert str(botoes["▲ Move Up"].cget("state")) == "normal"
    assert str(botoes["▼ Move Down"].cget("state")) == "normal"

    # --- clicar de verdade no botão "▼ Move Down" da Action do meio move ---
    botoes["▼ Move Down"].invoke()
    assert textos() == ["Um", "Três", "Dois"]

    app.dirty = False
    app.on_close()

finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)

# =================================================================
# Persistência: reordenar -> salvar -> fechar -> reabrir -> ordem
# continua a que ficou.
# =================================================================

tmp_dir2 = tempfile.mkdtemp(prefix="mynovel_test_reorderactions_persist_")
try:
    root2 = tk.Tk()
    root2.withdraw()
    app2 = StudioApp(root=root2)
    app2.create_new_project("Persistencia Reorder", tmp_dir2, "800", "600")
    app2.create_character("Ken")
    app2.create_story("Historia")

    app2.add_story_action("historia", "speak", character="ken", text="Primeira")
    app2.add_story_action("historia", "exit", character="ken")
    app2.add_story_action("historia", "pause", duration=1)

    app2.move_story_action("historia", 2, -1)  # "pause" fica no meio

    app2.save_project()
    app2.on_close()

    root3 = tk.Tk()
    root3.withdraw()
    app3 = StudioApp(root=root3)
    app3.load_project(app2.project_path)

    assert [a.type for a in app3.project.stories["historia"].actions] == [
        "speak", "pause", "exit"
    ]

    app3.on_close()

    reloaded = Project.load(app2.project_path)
    assert [a.type for a in reloaded.stories["historia"].actions] == ["speak", "pause", "exit"]

finally:
    shutil.rmtree(tmp_dir2, ignore_errors=True)

print("OK: Move Up/Move Down reordenam as Actions da história, preservando seleção e persistindo")
