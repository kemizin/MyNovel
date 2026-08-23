# Exemplo: Canvas.add_character(character, position, scale=0.5,
#                                offset_x=0, offset_y=0)
#
# add_character() é uma operação de CONFIGURAÇÃO da cena: é assim que
# você coloca os personagens que já devem estar visíveis desde o
# primeiro frame, antes da história começar. Para personagens que
# "entram" durante a história, use enter() (veja 05_enter.py).
#
# position vai de 1 a 3 (25%, 50%, 75% da largura da tela). scale
# ajusta o tamanho do sprite; offset_x/offset_y fazem ajustes finos.
#
# Roda com: .venv/Scripts/python.exe exemples/03_add_character.py

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.scene import Canvas
from src.MyNovellib.character import Character
from src.MyNovellib.engine import Engine
from src.MyNovellib.dialogue import speak

ken = Character("Ken")
ken.add_emotion("normal", idle="assets/char/ken/ken.png", talking="assets/char/ken/ken_falando.png")
ken.emotion("normal")

jef = Character("Jef")
jef.add_emotion("normal", idle="assets/char/jefer/jefer.png", talking="assets/char/jefer/jefer_falano.png")
jef.emotion("normal")

campo = Canvas("campo", "assets/fundos/campo.jpg", 1920, 1080)

# Os dois já aparecem desde o primeiro frame, em posições diferentes
# e com escalas diferentes -- tudo configurado ANTES da história.
campo.add_character(ken, position=1, scale=0.5)
campo.add_character(jef, position=3, scale=0.35, offset_y=30)

story = [
    speak(ken, "Nos dois ja estavamos aqui desde o inicio.", delay=1.5),
    speak(jef, "Isso, o add_character() monta a cena antes da historia comecar.", delay=2),
]

engine = Engine()
engine.run(campo, story)
