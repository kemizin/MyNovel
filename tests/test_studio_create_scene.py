# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_studio_create_scene.py
#
# Hardening, Waystone "studio create scene": Edit > New Scene cria um
# SceneData de verdade (via StudioCore) e abre o Scene Editor nela.
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

# --- Edit > New Scene começa desabilitado, sem projeto aberto ---
assert str(app.menus["Edit"].entrycget("New Scene...", "state")) == "disabled"

tmp_dir = tempfile.mkdtemp(prefix="mynovel_test_createscene_")
try:
    app.create_new_project("Projeto Cenas", tmp_dir, "800", "600")

    assert str(app.menus["Edit"].entrycget("New Scene...", "state")) == "normal"

    # --- create_scene(): cria de verdade, seleciona no Explorer e
    # abre o Scene Editor nela ---
    app.dirty = False
    criado = app.create_scene("Praça", background="assets/backgrounds/praca.png")

    assert criado is True
    assert "praca" in app.project.scenes
    assert app.project.scenes["praca"].name == "Praça"
    assert app.project.scenes["praca"].background == "assets/backgrounds/praca.png"
    assert app.project.scenes["praca"].characters == []
    assert app.dirty is True
    assert app.root.title() == f"{APP_TITLE} — Projeto Cenas *"

    assert app.explorer.selection() == ("scene:praca",)
    assert isinstance(app.scene_canvas, tk.Canvas)  # o Scene Editor de verdade abriu

    # --- background é opcional ---
    app.create_scene("Vazia")
    assert app.project.scenes["vazia"].background is None

    # --- nome vazio: StudioError vira messagebox, nada é criado ---
    total_antes = len(app.project.scenes)
    erros = []
    original_showerror = messagebox.showerror
    messagebox.showerror = lambda titulo, msg: erros.append(msg)

    try:
        assert app.create_scene("") is False
    finally:
        messagebox.showerror = original_showerror

    assert len(erros) == 1
    assert len(app.project.scenes) == total_antes  # nao criou nada

    # --- nome repetido gera uma chave diferente (não sobrescreve) ---
    app.create_scene("Praça")
    assert "praca_2" in app.project.scenes

    # --- diálogo de verdade constrói sem exceção (sem clicar em nada) ---
    dialog = app._open_new_scene_dialog()
    assert isinstance(dialog, tk.Toplevel)
    assert dialog.title() == "New Scene"
    dialog.destroy()

    app.dirty = False
    app.on_close()

finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)

# =================================================================
# Persistência: criar cena -> salvar -> fechar -> reabrir -> cena
# continua lá.
# =================================================================

tmp_dir2 = tempfile.mkdtemp(prefix="mynovel_test_createscene_persist_")
try:
    root2 = tk.Tk()
    root2.withdraw()
    app2 = StudioApp(root=root2)
    app2.create_new_project("Persistencia Cena", tmp_dir2, "800", "600")

    app2.create_scene("Quarto", background="assets/backgrounds/quarto.png")

    app2.save_project()
    app2.on_close()

    root3 = tk.Tk()
    root3.withdraw()
    app3 = StudioApp(root=root3)
    app3.load_project(app2.project_path)

    assert "quarto" in app3.project.scenes
    assert app3.project.scenes["quarto"].name == "Quarto"
    assert app3.project.scenes["quarto"].background == "assets/backgrounds/quarto.png"

    app3.on_close()

    reloaded = Project.load(app2.project_path)
    assert "quarto" in reloaded.scenes

finally:
    shutil.rmtree(tmp_dir2, ignore_errors=True)

print("OK: Edit > New Scene cria um SceneData de verdade e abre o Scene Editor nela")
