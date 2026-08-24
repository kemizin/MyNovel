# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_studio_new_project.py
#
# Studio Update, Waystone 4: File -> New Project cria um projeto de
# verdade (create_project() já existente, sem duplicar) e o Studio
# abre o projeto recém-criado.
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

from src.MyNovellib.studio.app import StudioApp, APP_TITLE
from src.MyNovellib.project.model import Project

tmp_dir = tempfile.mkdtemp(prefix="mynovel_test_studio_new_")

try:
    root = tk.Tk()
    root.withdraw()
    app = StudioApp(root=root)

    # --- criar o projeto de verdade ---
    ok = app.create_new_project("Teste Waystone 4", tmp_dir, "800", "600")
    assert ok is True

    project_path = os.path.join(tmp_dir, "Teste Waystone 4", "project.mynovel")
    assert os.path.isfile(project_path)

    # --- o Studio abre o projeto recem-criado (nao so cria no disco) ---
    assert app.project is not None
    assert app.project.name == "Teste Waystone 4"
    assert app.project.resolution == (800, 600)
    assert app.root.title() == f"{APP_TITLE} — Teste Waystone 4"
    assert app.explorer.get_children() == ("project",)
    assert app.explorer.item("project", "text") == "Teste Waystone 4"

    # --- validacao: nome vazio ---
    erros = []
    original_showerror = messagebox.showerror
    messagebox.showerror = lambda titulo, msg: erros.append(msg)

    try:
        assert app.create_new_project("", tmp_dir, "800", "600") is False
        assert app.create_new_project("Outro", tmp_dir, "abc", "600") is False  # largura invalida
        assert app.create_new_project("Outro", tmp_dir, "800", "0") is False    # altura invalida
        # criar em cima do mesmo projeto (pasta ja existe e nao esta vazia)
        assert app.create_new_project("Teste Waystone 4", tmp_dir, "800", "600") is False
    finally:
        messagebox.showerror = original_showerror

    assert len(erros) == 4
    # nenhum desses erros trocou o projeto que ja estava aberto
    assert app.project.name == "Teste Waystone 4"

    # --- o dialogo de verdade constroi sem excecao (sem clicar em
    # nada -- a logica de criacao ja foi testada direto acima) ---
    root3 = tk.Tk()
    root3.withdraw()
    app3 = StudioApp(root=root3)

    dialog = app3._open_new_project_dialog()
    assert isinstance(dialog, tk.Toplevel)
    assert dialog.title() == "New Project"
    dialog.destroy()
    app3.on_close()

    app.on_close()

    # =================================================================
    # Persistencia pedida explicitamente: criar -> fechar Studio ->
    # abrir novamente -> carregar projeto -> verificar persistencia.
    # =================================================================

    root2 = tk.Tk()
    root2.withdraw()
    app2 = StudioApp(root=root2)  # "Studio reaberto" -- instancia nova, do zero

    app2.load_project(project_path)

    assert app2.project.name == "Teste Waystone 4"
    assert app2.project.resolution == (800, 600)

    # e tambem confere direto pelo Project System, sem passar pelo Studio
    reloaded = Project.load(project_path)
    assert reloaded.name == "Teste Waystone 4"
    assert reloaded.resolution == (800, 600)

    app2.on_close()

finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)

print("OK: File -> New Project cria (create_project() reaproveitado), abre no Studio, e persiste entre sessões")
