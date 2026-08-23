# Exemplo: move(character, position=None, scale=None, offset_x=None,
#                offset_y=None)
#
# Reposiciona/reenquadra um personagem que JÁ está na cena (via
# add_character() ou enter()). Qualquer parâmetro deixado como None
# mantém o valor atual -- move() nunca reseta o que você não informou.
#
# Roda com: .venv/Scripts/python.exe exemples/07_move.py

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.scene import Canvas
from src.MyNovellib.character import Character
from src.MyNovellib.engine import Engine
from src.MyNovellib.dialogue import speak
from src.MyNovellib.story import move, pause

jef = Character("Jef")
jef.add_emotion("normal", idle="assets/char/jefer/jefer.png", talking="assets/char/jefer/jefer_falano.png")
jef.emotion("normal")

campo = Canvas("campo", "assets/fundos/campo.jpg", 1920, 1080)
campo.add_character(jef, position=1, scale=0.4)

story = [
    speak(jef, "Comecei pequeno, la na esquerda.", delay=1.5),

    # Só muda a posição -- a escala continua 0.4.
    move(jef, position=2),
    pause(0.5),
    speak(jef, "Agora estou no centro, do mesmo tamanho.", delay=1.5),

    # Muda posição E escala juntas.
    move(jef, position=3, scale=0.8),
    pause(0.5),
    speak(jef, "E agora bem maior, na direita.", delay=1.5),

    # Só ajusta o offset (deslocamento fino), sem mudar posição/escala.
    move(jef, offset_y=-60),
    pause(0.5),
    speak(jef, "So subi um pouco, sem mudar de posicao ou tamanho.", delay=1.5),
]

engine = Engine()
engine.run(campo, story)
