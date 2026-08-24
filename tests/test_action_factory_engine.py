# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_action_factory_engine.py
#
# Project System Update, Waystone 8: prova que a Engine executa
# Actions vindas da Action Factory exatamente como executaria Actions
# escritas direto em Python -- ela não sabe (nem precisa saber) a
# origem.
#
# Roda headless (SDL_VIDEODRIVER=dummy).

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.scene import Canvas
from src.MyNovellib.character import Character
from src.MyNovellib.engine import Engine
from src.MyNovellib.project.story_data import StoryData
from src.MyNovellib.project.action_factory import build_story

jef = Character("Jef")
jef.add_emotion("normal", idle="assets/char/jefer/jefer.png")
jef.add_emotion("bravo", idle="assets/char/jefer/jefer_soco.png")
jef.emotion("normal")

ken = Character("Ken")
ken.add_emotion("normal", idle="assets/char/ken/ken.png")
ken.emotion("normal")

campo = Canvas("campo", "assets/fundos/campo.jpg", 800, 600)
campo.add_character(ken, position=3, scale=0.5)

# Historia inteira vinda de "dados" (o que seria lido de um
# project.mynovel), sem NENHUM speak()/emotion()/... escrito na mao.
story_data = StoryData(name="intro")
story_data.add_action("speak", character="ken", text="Tem alguém aí?", delay=0.02, speed=0.005)
story_data.add_action("enter", character="jef", position=1, scale=0.5)
story_data.add_action("emotion", character="jef", emotion="bravo")
story_data.add_action("speak", character="jef", text="EU ESTOU AQUI!", delay=0.02, speed=0.005)
story_data.add_action("move", character="jef", position=2)
story_data.add_action("pause", duration=0.1)
story_data.add_action("exit", character="jef")

story = build_story(story_data, {"jef": jef, "ken": ken})

# antes de rodar, jef ainda nem esta na cena
assert "Jef" not in campo.characters

engine = Engine()
engine.run(campo, story)

# depois da historia (enter -> emotion -> move -> exit), jef entrou,
# ficou bravo, se moveu, e saiu de novo -- exatamente como aconteceria
# se essas Actions tivessem sido escritas direto em Python.
assert "Jef" not in campo.characters  # saiu no final (exit)
assert jef.current_emotion == "bravo"  # emotion() aplicado antes do exit
assert "Ken" in campo.characters  # nunca saiu

print("OK: a Engine executa Actions vindas da Action Factory igual a Actions escritas em Python")
