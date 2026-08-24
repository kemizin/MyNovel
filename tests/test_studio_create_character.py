# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_studio_create_character.py
#
# Hardening, Waystone "studio create character": Edit > New Character
# cria um CharacterData de verdade (via StudioCore) e abre o Character
# Editor nele -- a maior lacuna apontada na auditoria: até aqui o
# Studio só EDITAVA personagens que já existiam.
#
# Usa tkinter DE VERDADE com root.withdraw() -- nunca aparece nada na
# tela.

import os
import sys
import tempfile
import shutil
import tkinter as tk
import tkinter.messagebox as messagebox

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.studio.app import StudioApp, APP_TITLE
from src.MyNovellib.project.model import Project

root = tk.Tk()
root.withdraw()
app = StudioApp(root=root)

# --- Edit > New Character começa desabilitado, sem projeto aberto ---
assert str(app.menus["Edit"].entrycget("New Character...", "state")) == "disabled"

tmp_dir = tempfile.mkdtemp(prefix="mynovel_test_createcharacter_")
try:
    app.create_new_project("Projeto Personagens", tmp_dir, "800", "600")
    # create_new_project() acima já é a versão testável direta (mesma
    # usada em todos os outros testes de Studio) -- ver test_studio_new_project.py

    assert str(app.menus["Edit"].entrycget("New Character...", "state")) == "normal"

    # --- create_character(): cria de verdade, seleciona no Explorer e
    # abre o Character Editor nele ---
    app.dirty = False
    criado = app.create_character("Mika")

    assert criado is True
    assert "mika" in app.project.characters
    assert app.project.characters["mika"].name == "Mika"
    assert app.project.characters["mika"].emotions == {}
    assert app.dirty is True
    assert app.root.title() == f"{APP_TITLE} — Projeto Personagens *"

    assert app.explorer.selection() == ("character:mika",)

    editor_labels = [
        w.cget("text") for w in app.properties_content.winfo_children()
        if isinstance(w, tk.Label)
    ]
    assert "CHARACTER" in editor_labels  # o editor de verdade abriu, não o resumo

    # --- nome vazio: StudioError vira messagebox, nada é criado ---
    erros = []
    original_showerror = messagebox.showerror
    messagebox.showerror = lambda titulo, msg: erros.append(msg)

    try:
        assert app.create_character("") is False
        assert app.create_character("   ") is False
    finally:
        messagebox.showerror = original_showerror

    assert len(erros) == 2
    assert len(app.project.characters) == 1  # nenhum dos erros criou nada

    # --- nome repetido gera uma chave diferente (não sobrescreve) ---
    app.create_character("Mika")
    assert "mika_2" in app.project.characters
    assert len(app.project.characters) == 2

    # --- diálogo de verdade constrói sem exceção (sem clicar em nada) ---
    dialog = app._open_new_character_dialog()
    assert isinstance(dialog, tk.Toplevel)
    assert dialog.title() == "New Character"
    dialog.destroy()

    # --- "+ Add Emotion" do Character Editor já existente funciona
    # normalmente sobre um personagem recém-criado (fluxo completo:
    # criar -> adicionar emoção -> salvar) ---
    app.add_emotion("mika", "normal", idle="assets/backgrounds/praca.png")
    assert "normal" in app.project.characters["mika"].emotions

    app.dirty = False
    app.on_close()

finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)

# =================================================================
# Persistência: criar personagem -> salvar -> fechar -> reabrir ->
# personagem continua lá.
# =================================================================

tmp_dir2 = tempfile.mkdtemp(prefix="mynovel_test_createcharacter_persist_")
try:
    root2 = tk.Tk()
    root2.withdraw()
    app2 = StudioApp(root=root2)
    app2.create_new_project("Persistencia Personagem", tmp_dir2, "800", "600")

    app2.create_character("Ken")
    app2.add_emotion("ken", "normal", idle="assets/backgrounds/praca.png")

    app2.save_project()
    app2.on_close()

    root3 = tk.Tk()
    root3.withdraw()
    app3 = StudioApp(root=root3)
    app3.load_project(app2.project_path)

    assert "ken" in app3.project.characters
    assert app3.project.characters["ken"].name == "Ken"
    assert "normal" in app3.project.characters["ken"].emotions

    app3.on_close()

    # confere também direto pelo Project System, sem passar pelo Studio
    reloaded = Project.load(app2.project_path)
    assert "ken" in reloaded.characters

finally:
    shutil.rmtree(tmp_dir2, ignore_errors=True)

print("OK: Edit > New Character cria um CharacterData de verdade e abre o Character Editor nele")
