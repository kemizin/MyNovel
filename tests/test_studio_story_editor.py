# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_studio_story_editor.py
#
# Hardening, Waystone "story editor": selecionar uma história abre o
# Story Editor -- por enquanto, uma lista ordenada e somente-leitura
# das Actions (cada linha usando ActionData.describe(), sem
# reimplementar formatação no Studio). Adicionar/editar/remover/
# reordenar Action são os próximos waystones.
#
# Usa tkinter DE VERDADE com root.withdraw() -- nunca aparece nada na
# tela.

import os
import sys
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.studio.app import StudioApp
from src.MyNovellib.project.model import Project
from src.MyNovellib.project.story_data import StoryData

root = tk.Tk()
root.withdraw()
app = StudioApp(root=root)

app.load_project("exemples/project_demo/project.mynovel")

app.explorer.selection_set("story:intro")
app._on_explorer_select()

# --- lista mostra as Actions na ordem certa, cada uma com o texto de
# ActionData.describe() ---
intro = app.project.stories["intro"]

assert isinstance(app.story_listbox, tk.Listbox)
assert app.story_listbox.size() == len(intro.actions) == 6

linhas = app.story_listbox.get(0, tk.END)
assert list(linhas) == [action.describe() for action in intro.actions]

# a primeira e a última Action do demo, pra confirmar que é texto de
# verdade e não um placeholder
assert linhas[0].startswith("enter mika")
assert linhas[-1].startswith("exit mika")

# --- história vazia: lista vazia, sem erro ---
app.project.stories["vazia"] = StoryData(name="vazia")
app._refresh_explorer()

app.explorer.selection_set("story:vazia")
app._on_explorer_select()

assert app.story_listbox.size() == 0

# --- trocar de história reconstrói a lista (não acumula linhas da
# história anterior) ---
app.explorer.selection_set("story:intro")
app._on_explorer_select()
assert app.story_listbox.size() == 6

# --- Runtime (Canvas/Engine) nunca importado só de olhar uma história ---
assert "src.MyNovellib.scene" not in sys.modules
assert "src.MyNovellib.engine" not in sys.modules

app.dirty = False  # só navegação nesta parte -- close-protection é testado em test_studio_save.py
app.on_close()

# =================================================================
# Sobre um projeto recém-criado pelo próprio Studio (New Story +
# Character Editor futuro ainda não populam Actions -- aqui só
# confirma que uma história vinda de create_story() também abre
# corretamente, vazia).
# =================================================================

import tempfile, shutil

tmp_dir = tempfile.mkdtemp(prefix="mynovel_test_storyeditor_")
try:
    root2 = tk.Tk()
    root2.withdraw()
    app2 = StudioApp(root=root2)
    app2.create_new_project("Projeto Story Editor", tmp_dir, "800", "600")
    app2.create_story("Intro")

    assert isinstance(app2.story_listbox, tk.Listbox)
    assert app2.story_listbox.size() == 0

    app2.dirty = False  # create_story() marcou dirty -- não é o que este bloco testa
    app2.on_close()

finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)

print("OK: selecionar uma história abre o Story Editor com a lista ordenada de Actions (somente leitura)")
