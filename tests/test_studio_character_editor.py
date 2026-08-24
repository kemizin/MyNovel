# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_studio_character_editor.py
#
# Studio Update, Waystone 7: Character Editor -- edita CharacterData
# (dado de projeto), nunca o Character de Runtime.
#
# Usa tkinter DE VERDADE com root.withdraw() -- nunca aparece nada na
# tela.

import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
import tkinter.messagebox as messagebox

from src.MyNovellib.studio.app import StudioApp
from src.MyNovellib.project.model import Project

root = tk.Tk()
root.withdraw()
app = StudioApp(root=root)

app.load_project("exemples/project_demo/project.mynovel")
mika = app.project.characters["mika"]

# --- selecionar o personagem abre o editor, com Name preenchido e a
# emocao "normal" com Idle/Talking preenchidos ---
app.explorer.selection_set("character:mika")
app._on_explorer_select()

def find_widgets(parent, cls):
    achados = []
    for w in parent.winfo_children():
        if isinstance(w, cls):
            achados.append(w)
        achados.extend(find_widgets(w, cls))
    return achados


name_entries = find_widgets(app.properties_content, tk.Entry)
assert name_entries[0].get() == "Mika"

buttons = [b.cget("text") for b in find_widgets(app.properties_content, tk.Button)]
assert "+ Add Emotion" in buttons
assert "Remove Emotion" in buttons

# --- editar o Name atualiza CharacterData.name (nao o Character de
# Runtime -- este modulo nem importa Character) e marca dirty ---
assert "src.MyNovellib.character" not in sys.modules

app.dirty = False
name_entries[0].delete(0, tk.END)
name_entries[0].insert(0, "Mika Renomeada")

assert mika.name == "Mika Renomeada"
assert app.dirty is True

# a arvore reflete o novo nome
assert app.explorer.item("character:mika", "text") == "Mika Renomeada"

# --- editar Idle/Talking da emocao "normal" atualiza CharacterData ---
idle_entry, talking_entry = find_widgets(app.properties_content, tk.Entry)[1:3]

app.dirty = False
talking_entry.delete(0, tk.END)
talking_entry.insert(0, "assets/characters/mika/novo_talking.png")

assert mika.emotions["normal"]["talking"] == "assets/characters/mika/novo_talking.png"
assert app.dirty is True

# --- add_emotion(): adiciona de verdade, sem passar pelo dialogo ---
app.dirty = False
ok = app.add_emotion("mika", "feliz", "assets/characters/mika/feliz_idle.png", "")
assert ok is True
assert app.dirty is True
assert mika.emotions["feliz"] == {
    "idle": "assets/characters/mika/feliz_idle.png",
    "talking": None,
}

# --- add_emotion(): valida nome e idle vazios (sem abrir dialog real
# -- messagebox.showerror substituido por espiao) ---
erros = []
original_showerror = messagebox.showerror
messagebox.showerror = lambda titulo, msg: erros.append(msg)

try:
    assert app.add_emotion("mika", "", "algum_idle.png") is False
    assert app.add_emotion("mika", "sem_idle", "") is False
finally:
    messagebox.showerror = original_showerror

assert len(erros) == 2
assert "feliz" in mika.emotions  # as tentativas invalidas nao mexeram no que ja existia

# --- _remove_emotion(): remove de verdade ---
app.dirty = False
app._remove_emotion("mika", "feliz")
assert "feliz" not in mika.emotions
assert app.dirty is True

# --- o dialogo de "Add Emotion" constroi sem excecao ---
dialog = app._open_add_emotion_dialog("mika")
assert isinstance(dialog, tk.Toplevel)
assert dialog.title() == "Add Emotion"
dialog.destroy()

# fecha sem passar pela protecao de dirty (ja coberta em
# test_studio_save.py) -- aqui so queremos fechar a janela
app.dirty = False
app.on_close()

# =================================================================
# Fluxo completo: Studio edita CharacterData -> Save -> Runtime
# posteriormente le esses dados do disco (sem passar pelo Studio).
# =================================================================

tmp_dir = tempfile.mkdtemp(prefix="mynovel_test_chareditor_")
try:
    root2 = tk.Tk()
    root2.withdraw()
    app2 = StudioApp(root=root2)

    app2.create_new_project("Editar Personagem", tmp_dir, "800", "600")

    from src.MyNovellib.project.character_data import CharacterData
    app2.project.characters["heroi"] = CharacterData("Heroi")
    app2.project.characters["heroi"].add_emotion("normal", idle="assets/heroi_idle.png")
    app2._refresh_explorer()

    app2.explorer.selection_set("character:heroi")
    app2._on_explorer_select()

    campos = find_widgets(app2.properties_content, tk.Entry)
    campos[0].delete(0, tk.END)
    campos[0].insert(0, "Heroi Editado")

    app2.save_project()
    app2.on_close()

    reloaded = Project.load(os.path.join(tmp_dir, "Editar Personagem", "project.mynovel"))
    assert reloaded.characters["heroi"].name == "Heroi Editado"

finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)

print("OK: Character Editor edita CharacterData (nunca o Character de Runtime), e as alteracoes persistem via Save")
