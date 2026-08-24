# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_studio_dirty_state.py
#
# Studio Update, Waystone 11: o mecanismo de dirty (self.dirty,
# mark_dirty()) já existia desde o Waystone 5, e todo editor real
# (Character Editor, Scene Editor -- Waystones 7-9) já chama
# mark_dirty() em cada edição. O que faltava era só a indicação
# VISUAL: o título da janela mostra "MyNovel Studio — MeuJogo *"
# quando há alterações não salvas, e "MyNovel Studio — MeuJogo" (sem
# "*") quando não há.
#
# self.dirty agora é property (não atributo simples): QUALQUER jeito
# de mudá-lo -- mark_dirty(), Save, carregar projeto, ou até
# "app.dirty = True" direto (como os outros arquivos de teste já
# fazem) -- atualiza o título sozinho.
#
# Usa tkinter DE VERDADE com root.withdraw() -- nunca aparece nada na
# tela.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk

from src.MyNovellib.studio.app import StudioApp, APP_TITLE
from src.MyNovellib.project.model import Project
from src.MyNovellib.project.character_data import CharacterData
from src.MyNovellib.project.scene_data import SceneData


def build_project():

    project = Project(name="MeuJogo", resolution=(960, 540))

    mika = CharacterData("Mika")
    mika.add_emotion("normal", idle="assets/backgrounds/praca.png")
    project.characters["mika"] = mika

    cena = SceneData(name="praca", background="assets/backgrounds/praca.png")
    cena.add_character("mika", position=2, scale=0.5)
    project.scenes["praca"] = cena

    project.loaded_from = "exemples/project_demo"  # onde os assets existem de verdade
    return project


root = tk.Tk()
root.withdraw()
app = StudioApp(root=root)

# --- sem projeto: só o nome do app, sem indicação nenhuma ---
assert app.root.title() == APP_TITLE
assert app.dirty is False

# --- carregar um projeto: título ganha " — nome", sem "*" (recém
# carregado não tem alterações) ---
app.project = build_project()
app._on_project_loaded()

assert app.dirty is False
assert app.root.title() == f"{APP_TITLE} — MeuJogo"

# --- mark_dirty() marca E atualiza o título com "*" ---
app.mark_dirty()

assert app.dirty is True
assert app.root.title() == f"{APP_TITLE} — MeuJogo *"

# --- Save limpa o dirty E o "*" some do título de novo ---
app.project_path = os.path.join(
    __import__("tempfile").mkdtemp(prefix="mynovel_test_dirtytitle_"), "meujogo.mynovel"
)
app.save_project()

assert app.dirty is False
assert app.root.title() == f"{APP_TITLE} — MeuJogo"

# --- edição real no Character Editor (add_emotion) também chega no
# título -- não só chamando mark_dirty() direto ---
app.add_emotion("mika", "feliz", idle="assets/backgrounds/praca.png")

assert app.dirty is True
assert app.root.title() == f"{APP_TITLE} — MeuJogo *"

app.save_project()
assert app.root.title() == f"{APP_TITLE} — MeuJogo"

# --- edição real no Scene Editor (_apply_scene_field, como o arraste
# e os campos numéricos usam) também chega no título ---
app.explorer.selection_set("scene:praca")
app._on_explorer_select()
app._apply_scene_field(0, "scale", "0.8", float)

assert app.dirty is True
assert app.root.title() == f"{APP_TITLE} — MeuJogo *"

app.save_project()
assert app.root.title() == f"{APP_TITLE} — MeuJogo"

# --- "app.dirty = True/False" direto (como os outros testes já
# fazem) continua funcionando -- E também atualiza o título, de graça,
# porque dirty é property ---
app.dirty = True
assert app.root.title() == f"{APP_TITLE} — MeuJogo *"

app.dirty = False
assert app.root.title() == f"{APP_TITLE} — MeuJogo"

# --- carregar outro projeto: título reflete o novo nome, sem "*" ---
app.dirty = False
app.load_project("exemples/project_demo/project.mynovel")

assert app.dirty is False
assert app.root.title() == f"{APP_TITLE} — Project Demo"

app.on_close()

print("OK: título da janela mostra \"*\" quando há alterações não salvas, em qualquer editor, e some ao salvar")
