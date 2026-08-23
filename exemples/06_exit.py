# Exemplo: exit(character)
#
# exit() é a saída NARRATIVA de um personagem -- o equivalente
# semântico de remove_character() (veja 04_remove_character.py), só
# que pensado como um acontecimento da história ("o personagem saiu").
#
# IMPORTANTE: "exit" é o nome de uma função do Python (usada pra
# fechar o interpretador). Por isso, ao importar, é comum dar um
# apelido: `from src.MyNovellib.story import exit as sair`.
#
# Roda com: .venv/Scripts/python.exe exemples/06_exit.py

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.scene import Canvas
from src.MyNovellib.character import Character
from src.MyNovellib.engine import Engine
from src.MyNovellib.dialogue import speak
from src.MyNovellib.story import exit as sair

ken = Character("Ken")
ken.add_emotion("normal", idle="assets/char/ken/ken.png", talking="assets/char/ken/ken_falando.png")
ken.emotion("normal")

jef = Character("Jef")
jef.add_emotion("normal", idle="assets/char/jefer/jefer.png", talking="assets/char/jefer/jefer_falano.png")
jef.emotion("normal")

campo = Canvas("campo", "assets/fundos/campo.jpg", 1920, 1080)
campo.add_character(ken, position=3, scale=0.5)
campo.add_character(jef, position=1, scale=0.5)

story = [
    speak(jef, "Preciso ir.", delay=1.5),

    # sair() (exit) remove o Jef da cena, como parte da história.
    sair(jef),

    speak(ken, "E ele foi embora.", delay=1.5),
]

engine = Engine()
engine.run(campo, story)
