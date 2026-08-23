# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_pause.py
#
# Waystone 4: pause(duration) mantem a cena na tela por `duration`
# segundos, sem exigir input.

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.scene import Canvas
from src.MyNovellib.character import Character
from src.MyNovellib.engine import Engine
from src.MyNovellib.dialogue import speak
from src.MyNovellib.story import pause

ken = Character("Ken")
ken.add_emotion("normal", idle="assets/char/ken/ken.png")
ken.emotion("normal")

campo = Canvas("campo", "assets/fundos/campo.jpg", 1920, 1080)
campo.add_character(ken, 3, scale=0.5)

PAUSE_SECONDS = 0.5

story = [
    speak(ken, "Espera...", delay=0.1),
    pause(PAUSE_SECONDS),
    speak(ken, "...", delay=0.1),
]

engine = Engine()

start = time.time()
engine.run(campo, story)
elapsed = time.time() - start

# a historia toda (2 speaks com delay=0.1 + pause de 0.5s) tem que
# durar pelo menos o tempo do pause -- senao pause() nao esta
# bloqueando de verdade.
assert elapsed >= PAUSE_SECONDS, (
    f"esperava pelo menos {PAUSE_SECONDS}s, rodou em {elapsed:.2f}s"
)

print(f"OK: historia com pause({PAUSE_SECONDS}) levou {elapsed:.2f}s")
