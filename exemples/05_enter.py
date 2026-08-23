# Exemplo: enter(character, position, scale=0.5, offset_x=0, offset_y=0)
#
# enter() é a entrada NARRATIVA de um personagem: um acontecimento da
# história ("o personagem entrou na cena"), não uma configuração
# inicial. Tecnicamente faz o mesmo que add_character(), mas dentro
# da lista `story` -- compare com 03_add_character.py.
#
# Roda com: .venv/Scripts/python.exe exemples/05_enter.py

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.scene import Canvas
from src.MyNovellib.character import Character
from src.MyNovellib.engine import Engine
from src.MyNovellib.dialogue import speak
from src.MyNovellib.story import enter

ken = Character("Ken")
ken.add_emotion("normal", idle="assets/char/ken/ken.png", talking="assets/char/ken/ken_falando.png")
ken.emotion("normal")

jef = Character("Jef")
jef.add_emotion("normal", idle="assets/char/jefer/jefer.png", talking="assets/char/jefer/jefer_falano.png")
jef.emotion("normal")

campo = Canvas("campo", "assets/fundos/campo.jpg", 1920, 1080)

# Só o Ken está na cena no começo -- Jef ainda nem existe no campo.
campo.add_character(ken, position=3, scale=0.5)

story = [
    speak(ken, "Tem alguem ai?", delay=1.5),

    # enter() adiciona o Jef à cena AGORA, como parte da história.
    # A tela já mostra ele aparecendo antes da próxima fala.
    enter(jef, position=1, scale=0.5),

    speak(jef, "Cheguei!", delay=1.5),
]

engine = Engine()
engine.run(campo, story)
