# Exemplo: pause(duration)
#
# Mantém a cena parada na tela por `duration` segundos, sem exigir
# input do jogador. Útil para criar um "respiro" dramático entre
# falas, ou para dar tempo de uma mudança visual (emotion/move) ser
# percebida antes da próxima fala.
#
# Roda com: .venv/Scripts/python.exe exemples/08_pause.py

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.scene import Canvas
from src.MyNovellib.character import Character
from src.MyNovellib.engine import Engine
from src.MyNovellib.dialogue import speak
from src.MyNovellib.story import pause

ken = Character("Ken")
ken.add_emotion("normal", idle="assets/char/ken/ken.png", talking="assets/char/ken/ken_falando.png")
ken.emotion("normal")

campo = Canvas("campo", "assets/fundos/campo.jpg", 1920, 1080)
campo.add_character(ken, position=2, scale=0.6)

story = [
    speak(ken, "Espera...", delay=0.5),

    # a cena fica parada por 2 segundos, sem precisar de espaço/clique.
    pause(2),

    speak(ken, "...", delay=0.5),
    pause(1),
    speak(ken, "Prontinho, terminou a pausa.", delay=1.5),
]

engine = Engine()
engine.run(campo, story)
