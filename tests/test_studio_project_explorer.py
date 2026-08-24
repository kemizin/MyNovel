# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_studio_project_explorer.py
#
# Studio Update, Waystone 3: painel PROJECT (árvore de navegação) --
# Characters/Scenes/Stories/Assets, e clicar num item mostra info no
# painel Properties.
#
# Usa tkinter DE VERDADE com root.withdraw() -- nunca aparece nada na
# tela.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk

from src.MyNovellib.studio.app import StudioApp

root = tk.Tk()
root.withdraw()
app = StudioApp(root=root)

# --- antes de carregar: arvore vazia ---
assert app.explorer.get_children() == ()

app.load_project("exemples/project_demo/project.mynovel")

# --- raiz = nome do projeto, com as 4 categorias pedidas, na ordem ---
root_children = app.explorer.get_children()
assert root_children == ("project",)

categorias = app.explorer.get_children("project")
assert categorias == ("category:character", "category:scene", "category:story", "category:asset")

rotulos_categorias = [app.explorer.item(c, "text") for c in categorias]
assert rotulos_categorias == ["Characters", "Scenes", "Stories", "Assets"]

# --- cada categoria lista os itens de verdade do Project Demo ---
personagens = app.explorer.get_children("category:character")
assert [app.explorer.item(i, "text") for i in personagens] == ["mika"]

cenas = app.explorer.get_children("category:scene")
assert [app.explorer.item(i, "text") for i in cenas] == ["praca"]

historias = app.explorer.get_children("category:story")
assert [app.explorer.item(i, "text") for i in historias] == ["intro"]

assets = app.explorer.get_children("category:asset")
assert set(app.explorer.item(i, "text") for i in assets) == {
    "mika.normal.idle", "mika.normal.talking", "praca.bg"
}

# --- selecionar a raiz mostra o resumo do projeto (mesmo do Waystone 2) ---
app.explorer.selection_set("project")
app._on_explorer_select()
assert "Project Demo" in app.properties_label.cget("text")

# --- selecionar uma categoria mostra a contagem ---
app.explorer.selection_set("category:character")
app._on_explorer_select()
assert app.properties_label.cget("text") == "Personagens: 1"

# --- selecionar um personagem abre o Character Editor (Waystone 7),
# nao mais um texto somente-leitura -- so confirma que o editor
# aparece; o comportamento dele em detalhe e testado em
# test_studio_character_editor.py ---
app.explorer.selection_set("character:mika")
app._on_explorer_select()
labels_do_editor = [
    w.cget("text") for w in app.properties_content.winfo_children()
    if isinstance(w, tk.Label)
]
assert "CHARACTER" in labels_do_editor

# --- selecionar uma cena mostra fundo/musica/quantidade de personagens ---
# --- selecionar uma cena abre o Scene Editor (Waystone 8), nao mais
# um texto somente-leitura -- so confirma que o canvas aparece; o
# comportamento dele em detalhe e testado em
# test_studio_scene_editor.py ---
app.explorer.selection_set("scene:praca")
app._on_explorer_select()
labels_da_cena = [
    w.cget("text") for w in app.properties_content.winfo_children()
    if isinstance(w, tk.Label)
]
assert "SCENE" in labels_da_cena
assert isinstance(app.scene_canvas, tk.Canvas)

# --- selecionar uma historia abre o Story Editor (Hardening, lista
# ordenada de Actions), nao mais um texto somente-leitura -- so
# confirma que a lista aparece com as 6 actions da story do demo; o
# comportamento dele em detalhe e testado em test_studio_story_editor.py ---
app.explorer.selection_set("story:intro")
app._on_explorer_select()
labels_da_historia = [
    w.cget("text") for w in app.properties_content.winfo_children()
    if isinstance(w, tk.Label)
]
assert "STORY" in labels_da_historia
assert isinstance(app.story_listbox, tk.Listbox)
assert app.story_listbox.size() == 6  # a story do demo tem 6 actions

# --- selecionar um asset mostra id/tipo/caminho ---
app.explorer.selection_set("asset:praca.bg")
app._on_explorer_select()
texto = app.properties_label.cget("text")
assert "praca.bg" in texto
assert "background" in texto

# --- linguagem simples no painel Properties -- nada de jargao interno ---
for termo_proibido in ("Registry Key", "Runtime Object", "Asset ID"):
    assert termo_proibido not in texto

app.on_close()

print("OK: Project Explorer navega Characters/Scenes/Stories/Assets e mostra Properties ao selecionar")
