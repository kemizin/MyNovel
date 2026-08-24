# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_studio_play.py
#
# Studio Update, Waystone 10: botão Play executa o projeto pela
# Engine EXISTENTE (create_runtime(), Project Runtime Loading) --
# nenhuma Engine paralela -- e o Studio continua aberto depois.
#
# Roda headless (SDL_VIDEODRIVER=dummy): o mesmo código real
# (pygame.init/display/event/flip) roda de ponta a ponta, só sem
# desenhar na tela -- ver test_studio_play_visual.py (não
# automatizado, rodado manualmente uma vez) pra confirmação visual
# real de duas janelas separadas.

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import sys
import tkinter as tk
import tkinter.messagebox as messagebox

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.studio.app import StudioApp
from src.MyNovellib.project.model import Project
from src.MyNovellib.project.character_data import CharacterData
from src.MyNovellib.project.scene_data import SceneData
from src.MyNovellib.project.story_data import StoryData
from src.MyNovellib.engine import Engine

REPO_ROOT = os.path.dirname(os.path.abspath(__file__)) and os.getcwd()


def build_quick_project():
    """Projeto pequeno com delay= em tudo, pra terminar sozinho
    (sem precisar simular input) -- rapido o bastante pro teste."""

    project = Project(name="Projeto Play", resolution=(480, 270))

    mika = CharacterData("Mika")
    mika.add_emotion("normal", idle="assets/backgrounds/praca.png")
    project.characters["mika"] = mika

    cena = SceneData(name="praca", background="assets/backgrounds/praca.png")
    project.scenes["praca"] = cena

    intro = StoryData(name="intro")
    intro.add_action("enter", character="mika", position=2, scale=0.3)
    intro.add_action("speak", character="mika", text="Oi!", speed=0.005, delay=0.02)
    intro.add_action("pause", duration=0.05)
    intro.add_action("exit", character="mika")
    project.stories["intro"] = intro

    project.loaded_from = "exemples/project_demo"  # onde praca.png existe de verdade
    return project


root = tk.Tk()
root.withdraw()
app = StudioApp(root=root)

# --- Play comeca desabilitado, habilita ao carregar um projeto ---
assert str(app.toolbar_buttons["Play"].cget("state")) == "disabled"
assert str(app.menus["Build"].entrycget("Play", "state")) == "disabled"

app.project = build_quick_project()
app._on_project_loaded()

assert str(app.toolbar_buttons["Play"].cget("state")) == "normal"
assert str(app.menus["Build"].entrycget("Play", "state")) == "normal"

# --- Play sem projeto nenhum e um no-op seguro ---
app.project, projeto_guardado = None, app.project
app.play_project()  # nao deve levantar excecao
app.project = projeto_guardado

# --- Play executa de verdade pela Engine EXISTENTE, e o Studio
# continua de pe depois ---
mika = app.project.characters["mika"]
praca = app.project.scenes["praca"]

assert "Mika" not in praca.characters  # so entra durante a historia

app.play_project()

assert "Mika" not in praca.characters  # saiu no final (Action "exit")
assert app.root.winfo_exists()  # <-- o Studio continua aberto
assert "de volta ao Studio" in app.status_bar.cget("text")

# --- nenhuma Engine paralela: o runtime usado por play_project() e
# uma instancia da MESMA classe Engine do Runtime existente ---
runtime = app.project.create_runtime()
assert isinstance(runtime.engine, Engine)
assert type(runtime.engine) is Engine  # nao uma subclasse/alternativa

# --- projeto com mais de uma cena/historia: play_project() nao
# consegue decidir sozinho -- mostra erro (sem UI de escolha ainda),
# nao trava nem adivinha errado ---
app.project.scenes["outra"] = SceneData(name="outra", background="assets/backgrounds/praca.png")

erros = []
original_showerror = messagebox.showerror
messagebox.showerror = lambda titulo, msg: erros.append(msg)

try:
    app.play_project()
finally:
    messagebox.showerror = original_showerror

assert len(erros) == 1
assert app.root.winfo_exists()  # mesmo com erro, o Studio continua aberto

app.on_close()

print("OK: Play roda o projeto pela Engine existente (sem Engine paralela) e o Studio continua aberto depois")
