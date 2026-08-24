# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_studio_delete_entities.py
#
# Hardening, Waystone "studio delete entities": botão "Delete" no
# Character Editor, no Scene Editor e no resumo de história. Pede
# confirmação (diferente de "Remove Emotion") e bloqueia via
# StudioError se o personagem estiver em uso numa cena/história --
# nunca remove em cascata.
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

from src.MyNovellib.studio.app import StudioApp

root = tk.Tk()
root.withdraw()
app = StudioApp(root=root)

tmp_dir = tempfile.mkdtemp(prefix="mynovel_test_deleteentities_")
try:
    app.create_new_project("Projeto Delete", tmp_dir, "800", "600")

    app.create_character("Mika")

    # --- Character Editor mostra o botão "Delete Character" ---
    botoes = [
        w for w in app.properties_content.winfo_children()
        if isinstance(w, tk.Button) and w.cget("text") == "Delete Character"
    ]
    assert len(botoes) == 1

    app.create_character("Sem Uso")
    app.create_scene("Praça", background="assets/backgrounds/praca.png")

    # --- Scene Editor mostra o botão "Delete Scene" ---
    botoes = [
        w for w in app.properties_content.winfo_children()
        if isinstance(w, tk.Button) and w.cget("text") == "Delete Scene"
    ]
    assert len(botoes) == 1

    app.create_story("Intro")

    # coloca "mika" na cena, pra provar o bloqueio de referência
    app.project.scenes["praca"].add_character("mika", position=1)

    original_askyesno = messagebox.askyesno
    original_showerror = messagebox.showerror

    # --- confirmação "Não": nada muda ---
    messagebox.askyesno = lambda *a, **k: False
    try:
        app._delete_character("sem_uso")
    finally:
        messagebox.askyesno = original_askyesno
    assert "sem_uso" in app.project.characters

    # --- confirmação "Sim" + personagem em uso: StudioError vira
    # messagebox, personagem continua lá ---
    erros = []
    messagebox.askyesno = lambda *a, **k: True
    messagebox.showerror = lambda titulo, msg: erros.append(msg)
    try:
        app._delete_character("mika")
    finally:
        messagebox.askyesno = original_askyesno
        messagebox.showerror = original_showerror

    assert len(erros) == 1
    assert "mika" in app.project.characters

    # --- confirmação "Sim" + personagem livre: remove de verdade ---
    app.dirty = False
    messagebox.askyesno = lambda *a, **k: True
    try:
        app._delete_character("sem_uso")
    finally:
        messagebox.askyesno = original_askyesno

    assert "sem_uso" not in app.project.characters
    assert app.dirty is True

    # --- Delete Scene: sem bloqueio (nada referencia cena por chave) ---
    app.explorer.selection_set("scene:praca")
    app._on_explorer_select()
    assert isinstance(app.scene_canvas, tk.Canvas)  # Scene Editor aberto

    messagebox.askyesno = lambda *a, **k: True
    try:
        app._delete_scene("praca")
    finally:
        messagebox.askyesno = original_askyesno
    assert "praca" not in app.project.scenes

    # --- Delete Story: mesma coisa, e mostra o botão no resumo de
    # história (ainda sem Story Editor de verdade) ---
    app.explorer.selection_set("story:intro")
    app._on_explorer_select()

    botoes_delete = [
        w for w in app.properties_content.winfo_children()
        if isinstance(w, tk.Button) and w.cget("text") == "Delete Story"
    ]
    assert len(botoes_delete) == 1

    messagebox.askyesno = lambda *a, **k: True
    try:
        app._delete_story("intro")
    finally:
        messagebox.askyesno = original_askyesno
    assert "intro" not in app.project.stories

    app.dirty = False
    app.on_close()

finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)

print("OK: Delete Character/Scene/Story pedem confirmação e bloqueiam remoção de personagem em uso")
