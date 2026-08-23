# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_enter_exit.py
#
# Waystone 2: enter()/exit() como camada semantica de add_character()/
# remove_character(), reproduzindo o exemplo do prompt.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.scene import Canvas
from src.MyNovellib.character import Character
from src.MyNovellib.engine import Engine
from src.MyNovellib.dialogue import speak
from src.MyNovellib.story import enter, exit as story_exit

jef = Character("Jef")
jef.add_emotion("normal", idle="assets/char/jefer/jefer.png")

ken = Character("Ken")
ken.add_emotion("normal", idle="assets/char/ken/ken.png")
ken.emotion("normal")

campo = Canvas("campo", "assets/fundos/campo.jpg", 1920, 1080)
campo.add_character(ken, 3, scale=0.5)

story = [
    speak(ken, "Tem alguem ai?", delay=0.1),
    enter(jef, position=1),
    speak(jef, "Oi.", delay=0.1),
    story_exit(jef),
    speak(ken, "Ue...", delay=0.1),
]

# jef nao deve existir na cena antes da historia comecar
assert "Jef" not in campo.characters

engine = Engine()
engine.run(campo, story)

# depois da historia (enter seguido de exit), jef nao deve mais estar na cena
assert "Jef" not in campo.characters
# e ken (que nunca saiu) continua
assert "Ken" in campo.characters

print("OK: enter() adiciona e exit() remove corretamente durante a historia")
