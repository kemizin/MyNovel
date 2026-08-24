# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_studio_create_story.py
#
# Hardening, Waystone "studio create story": Edit > New Story cria uma
# StoryData de verdade (via StudioCore) -- vazia, sem Action nenhuma
# (não existe Story Editor nesta fase pra preencher o conteúdo; isso
# é o próximo bloco do plano de hardening).
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

# --- Edit > New Story começa desabilitado, sem projeto aberto ---
assert str(app.menus["Edit"].entrycget("New Story...", "state")) == "disabled"

tmp_dir = tempfile.mkdtemp(prefix="mynovel_test_createstory_")
try:
    app.create_new_project("Projeto Historias", tmp_dir, "800", "600")

    assert str(app.menus["Edit"].entrycget("New Story...", "state")) == "normal"

    # --- create_story(): cria de verdade e seleciona no Explorer ---
    app.dirty = False
    criado = app.create_story("Introdução")

    assert criado is True
    assert "introducao" in app.project.stories
    assert app.project.stories["introducao"].name == "Introdução"
    assert app.project.stories["introducao"].actions == []
    assert app.dirty is True
    assert app.root.title() == f"{APP_TITLE} — Projeto Historias *"

    assert app.explorer.selection() == ("story:introducao",)

    # ainda não existe Story Editor -- selecionar mostra o resumo de
    # sempre, com "Ações: 0"
    assert "Ações: 0" in app.properties_label.cget("text")

    # --- nome vazio: StudioError vira messagebox, nada é criado ---
    total_antes = len(app.project.stories)
    erros = []
    original_showerror = messagebox.showerror
    messagebox.showerror = lambda titulo, msg: erros.append(msg)

    try:
        assert app.create_story("") is False
    finally:
        messagebox.showerror = original_showerror

    assert len(erros) == 1
    assert len(app.project.stories) == total_antes

    # --- nome repetido gera uma chave diferente (não sobrescreve) ---
    app.create_story("Introdução")
    assert "introducao_2" in app.project.stories

    # --- diálogo de verdade constrói sem exceção (sem clicar em nada) ---
    dialog = app._open_new_story_dialog()
    assert isinstance(dialog, tk.Toplevel)
    assert dialog.title() == "New Story"
    dialog.destroy()

    app.dirty = False
    app.on_close()

finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)

# =================================================================
# Persistência: criar história -> salvar -> fechar -> reabrir ->
# história continua lá.
# =================================================================

tmp_dir2 = tempfile.mkdtemp(prefix="mynovel_test_createstory_persist_")
try:
    root2 = tk.Tk()
    root2.withdraw()
    app2 = StudioApp(root=root2)
    app2.create_new_project("Persistencia Historia", tmp_dir2, "800", "600")

    app2.create_story("Capítulo 1")

    app2.save_project()
    app2.on_close()

    root3 = tk.Tk()
    root3.withdraw()
    app3 = StudioApp(root=root3)
    app3.load_project(app2.project_path)

    assert "capitulo_1" in app3.project.stories
    assert app3.project.stories["capitulo_1"].name == "Capítulo 1"

    app3.on_close()

    reloaded = Project.load(app2.project_path)
    assert "capitulo_1" in reloaded.stories

finally:
    shutil.rmtree(tmp_dir2, ignore_errors=True)

print("OK: Edit > New Story cria uma StoryData de verdade, vazia")
