# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_studio_story_edit_action.py
#
# Hardening, Waystone "story edit and remove action": clicar numa
# Action da lista do Story Editor abre os campos dela pra editar
# (pré-preenchidos, mesmo builder do Add Action) + Update Action/
# Remove Action. O tipo da Action não é editável -- trocar de tipo é
# remover e adicionar de novo.
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
from src.MyNovellib.project.model import Project

root = tk.Tk()
root.withdraw()
app = StudioApp(root=root)

tmp_dir = tempfile.mkdtemp(prefix="mynovel_test_editaction_")
try:
    app.create_new_project("Projeto Edit Action", tmp_dir, "800", "600")
    app.create_character("Mika")
    app.add_emotion("mika", "normal", idle="assets/backgrounds/praca.png")
    app.add_emotion("mika", "feliz", idle="assets/backgrounds/quarto.png")
    app.create_story("Intro")

    app.add_story_action("intro", "speak", character="mika", text="Oi!")
    app.add_story_action("intro", "pause", duration=1)
    app.add_story_action("intro", "exit", character="mika")

    # --- sem seleção: painel mostra a instrução, sem Update/Remove ---
    botoes = [
        w for w in app.story_action_properties_frame.winfo_children()
        if isinstance(w, tk.Button)
    ]
    assert botoes == []

    # --- selecionar a primeira Action mostra os campos PRÉ-PREENCHIDOS ---
    app.story_listbox.selection_set(0)
    app._on_story_action_select()

    labels = [
        w.cget("text") for w in app.story_action_properties_frame.winfo_children()
        if isinstance(w, tk.Label)
    ]
    assert "Action: speak" in labels

    # os botões estão dentro de um Frame filho (buttons_row) -- procura
    # recursivamente
    def achar_botoes(widget):
        encontrados = []
        for filho in widget.winfo_children():
            if isinstance(filho, tk.Button):
                encontrados.append(filho)
            encontrados.extend(achar_botoes(filho))
        return encontrados

    botoes = {b.cget("text"): b for b in achar_botoes(app.story_action_properties_frame)}
    assert set(botoes) == {"Update Action", "Remove Action"}

    # --- update_story_action(): a versão testável direta ---
    app.dirty = False
    atualizado = app.update_story_action("intro", 0, character="mika", text="Oi de novo!")

    assert atualizado is True
    assert app.project.stories["intro"].actions[0].fields["text"] == "Oi de novo!"
    assert app.dirty is True
    # a listbox reflete a mudança, e a seleção continua na mesma Action
    assert "Oi de novo!" in app.story_listbox.get(0)
    assert app.story_listbox.curselection() == (0,)

    # --- update com campo obrigatório faltando: StudioError vira
    # messagebox, nada muda ---
    erros = []
    original_showerror = messagebox.showerror
    messagebox.showerror = lambda titulo, msg: erros.append(msg)
    try:
        assert app.update_story_action("intro", 0, character="mika") is False  # falta "text"
    finally:
        messagebox.showerror = original_showerror
    assert len(erros) == 1
    assert app.project.stories["intro"].actions[0].fields["text"] == "Oi de novo!"  # não mudou

    # --- remove_story_action(): remove de verdade, listbox encolhe ---
    app.dirty = False
    total_antes = len(app.project.stories["intro"].actions)
    app._remove_story_action(1)  # remove o "pause"

    assert len(app.project.stories["intro"].actions) == total_antes - 1
    assert app.story_listbox.size() == total_antes - 1
    assert [a.type for a in app.project.stories["intro"].actions] == ["speak", "exit"]
    assert app.dirty is True

    app.dirty = False
    app.on_close()

finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)

# =================================================================
# Persistência: editar e remover Action -> salvar -> fechar -> reabrir
# -> mudanças continuam lá.
# =================================================================

tmp_dir2 = tempfile.mkdtemp(prefix="mynovel_test_editaction_persist_")
try:
    root2 = tk.Tk()
    root2.withdraw()
    app2 = StudioApp(root=root2)
    app2.create_new_project("Persistencia Edit Action", tmp_dir2, "800", "600")
    app2.create_character("Ken")
    app2.create_story("Historia")

    app2.add_story_action("historia", "speak", character="ken", text="Original")
    app2.add_story_action("historia", "pause", duration=2)

    app2.update_story_action("historia", 0, character="ken", text="Editado")
    app2._remove_story_action(1)

    app2.save_project()
    app2.on_close()

    root3 = tk.Tk()
    root3.withdraw()
    app3 = StudioApp(root=root3)
    app3.load_project(app2.project_path)

    acoes = app3.project.stories["historia"].actions
    assert len(acoes) == 1
    assert acoes[0].fields["text"] == "Editado"

    app3.on_close()

    reloaded = Project.load(app2.project_path)
    assert reloaded.stories["historia"].actions[0].fields["text"] == "Editado"

finally:
    shutil.rmtree(tmp_dir2, ignore_errors=True)

print("OK: clicar numa Action da lista abre os campos pra editar (Update Action) ou remover (Remove Action)")
