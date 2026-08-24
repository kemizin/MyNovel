# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_studio_save.py
#
# Studio Update, Waystone 5: File -> Save / Save As (reaproveitando
# Project.save() já existente) e proteção ao fechar com alterações
# não salvas.
#
# Usa tkinter DE VERDADE com root.withdraw() -- nunca aparece nada na
# tela. messagebox.askyesnocancel/showerror são substituídos por
# espiões nos testes que precisam, pra nunca abrir um dialog real
# esperando clique.

import os
import sys
import json
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
import tkinter.messagebox as messagebox

from src.MyNovellib.studio.app import StudioApp, APP_TITLE

_TclError = tk.TclError

tmp_dir = tempfile.mkdtemp(prefix="mynovel_test_studio_save_")


def new_app():
    root = tk.Tk()
    root.withdraw()
    return StudioApp(root=root)


try:
    # --- Save/Save As comecam desabilitados, habilitam ao carregar um
    # projeto ---
    app = new_app()
    assert str(app.menus["File"].entrycget("Save", "state")) == "disabled"

    ok = app.create_new_project("Projeto Save", tmp_dir, "640", "480")
    assert ok is True
    assert app.dirty is False  # projeto recem-criado nao tem alteracoes pendentes

    assert str(app.menus["File"].entrycget("Save", "state")) == "normal"
    assert str(app.menus["File"].entrycget("Save As...", "state")) == "normal"
    assert str(app.toolbar_buttons["Save"].cget("state")) == "normal"

    # --- save_project(): grava no mesmo lugar de onde foi carregado ---
    project_path = os.path.join(tmp_dir, "Projeto Save", "project.mynovel")

    app.project.name = "Projeto Save (renomeado em memória)"  # simula uma edição
    app.mark_dirty()
    assert app.dirty is True

    app.save_project()

    assert app.dirty is False
    with open(project_path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["name"] == "Projeto Save (renomeado em memória)"

    # --- save_project_as(): grava num caminho novo e passa a ser o
    # "local" do projeto dali pra frente ---
    novo_path = os.path.join(tmp_dir, "copia.mynovel")
    app.mark_dirty()
    app._save_project_to(novo_path)  # equivalente ao que Save As faria apos o file dialog

    assert app.dirty is False
    assert os.path.isfile(novo_path)
    assert app.project.loaded_from == os.path.dirname(novo_path)

    # dali pra frente, Save (sem As) grava no NOVO local
    app.project.name = "Depois do Save As"
    app.mark_dirty()
    app.save_project()

    with open(novo_path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["name"] == "Depois do Save As"

    app.on_close()

    # =================================================================
    # Protecao ao fechar com alteracoes nao salvas.
    # =================================================================

    # --- sem alteracoes (dirty=False): fecha direto, sem perguntar nada ---
    app_limpo = new_app()
    app_limpo.create_new_project("Sem Alteracoes", tmp_dir, "640", "480")
    assert app_limpo.dirty is False

    perguntas = []
    original_askyesnocancel = messagebox.askyesnocancel
    messagebox.askyesnocancel = lambda *a, **k: perguntas.append(1) or True

    try:
        app_limpo.on_close()
    finally:
        messagebox.askyesnocancel = original_askyesnocancel

    assert perguntas == []  # nao perguntou nada
    try:
        app_limpo.root.winfo_exists()
        assert False, "esperava TclError -- deveria ter fechado sem perguntar"
    except _TclError:
        pass

    # --- com alteracoes, respondendo "Sim" (salvar e fechar) ---
    app_sim = new_app()
    app_sim.create_new_project("Responde Sim", tmp_dir, "640", "480")
    caminho_sim = os.path.join(tmp_dir, "Responde Sim", "project.mynovel")

    app_sim.project.name = "Alterado antes de fechar"
    app_sim.mark_dirty()

    messagebox.askyesnocancel = lambda *a, **k: True  # "Sim"
    try:
        app_sim.on_close()
    finally:
        messagebox.askyesnocancel = original_askyesnocancel

    with open(caminho_sim, encoding="utf-8") as f:
        data = json.load(f)
    assert data["name"] == "Alterado antes de fechar"  # foi salvo

    try:
        app_sim.root.winfo_exists()
        assert False, "esperava TclError -- deveria ter fechado"
    except _TclError:
        pass

    # --- com alteracoes, respondendo "Nao" (fecha sem salvar) ---
    app_nao = new_app()
    app_nao.create_new_project("Responde Nao", tmp_dir, "640", "480")
    caminho_nao = os.path.join(tmp_dir, "Responde Nao", "project.mynovel")

    app_nao.project.name = "Isso NAO deveria ser salvo"
    app_nao.mark_dirty()

    messagebox.askyesnocancel = lambda *a, **k: False  # "Não"
    try:
        app_nao.on_close()
    finally:
        messagebox.askyesnocancel = original_askyesnocancel

    with open(caminho_nao, encoding="utf-8") as f:
        data = json.load(f)
    assert data["name"] == "Responde Nao"  # NAO foi salvo -- continua o nome original

    try:
        app_nao.root.winfo_exists()
        assert False, "esperava TclError -- deveria ter fechado mesmo sem salvar"
    except _TclError:
        pass

    # --- com alteracoes, respondendo "Cancelar" (nao fecha) ---
    app_cancela = new_app()
    app_cancela.create_new_project("Responde Cancela", tmp_dir, "640", "480")
    app_cancela.mark_dirty()

    messagebox.askyesnocancel = lambda *a, **k: None  # "Cancelar"
    try:
        app_cancela.on_close()
    finally:
        messagebox.askyesnocancel = original_askyesnocancel

    assert app_cancela.root.winfo_exists()  # continua aberta
    assert app_cancela.dirty is True  # ainda marcada como suja

    # limpeza manual (sem passar pelo dirty-check, ja testamos ele)
    app_cancela.dirty = False
    app_cancela.on_close()

    print("OK: Save/Save As reaproveitam Project.save(), e o fechamento protege alterações não salvas (Sim/Não/Cancelar)")

finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)
